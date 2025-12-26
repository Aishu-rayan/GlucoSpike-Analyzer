"""
Food Analyzer Service

Uses OpenAI Vision API to identify foods from images
and estimate nutritional content.
"""

import os
import base64
from openai import OpenAI
from dotenv import load_dotenv
import json
import re

from database.gi_database import FOOD_DATABASE, get_food_data

load_dotenv()


def get_openai_client() -> OpenAI:
    """Get OpenAI client with API key"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    return OpenAI(api_key=api_key)


def encode_image_to_base64(image_bytes: bytes) -> str:
    """Convert image bytes to base64 string"""
    return base64.b64encode(image_bytes).decode("utf-8")


def analyze_food_image(image_bytes: bytes) -> dict:
    """
    Analyze a food image using OpenAI Vision API.
    Returns identified foods with estimated portions.
    """
    client = get_openai_client()
    
    # Encode image
    base64_image = encode_image_to_base64(image_bytes)
    
    # Create the prompt for food analysis
    system_prompt = """You are a nutrition expert AI that analyzes food images. 
Your task is to:
1. Identify all food items visible in the image
2. Estimate portion sizes
3. Provide nutritional estimates

Be specific about the food type (e.g., "brown rice" vs just "rice", "grilled chicken breast" vs just "chicken").

Always respond in valid JSON format."""

    user_prompt = f"""Analyze this food image and identify all food items.

For each food item, provide:
1. name: The specific name of the food (be specific, e.g., "white rice", "grilled chicken breast")
2. estimated_grams: Estimated weight in grams
3. portions: Number of standard servings (1.0 = one standard serving)
4. confidence: How confident you are (high/medium/low)

Also provide:
- meal_description: A brief description of the overall meal
- is_healthy_meal: true/false assessment
- health_notes: Brief health observations

Known foods in our database: {', '.join(list(FOOD_DATABASE.keys())[:50])}...

Respond ONLY with valid JSON in this exact format:
{{
    "foods": [
        {{
            "name": "food name",
            "estimated_grams": 150,
            "portions": 1.0,
            "confidence": "high"
        }}
    ],
    "meal_description": "Description of the meal",
    "is_healthy_meal": true,
    "health_notes": "Brief health notes"
}}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000,
            temperature=0.3
        )
        
        # Parse the response
        content = response.choices[0].message.content
        
        # Extract JSON from response (handle markdown code blocks)
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
        if json_match:
            content = json_match.group(1)
        
        result = json.loads(content)
        
        # Enrich with database information
        enriched_foods = []
        for food in result.get("foods", []):
            food_name = food.get("name", "").lower()
            db_data = get_food_data(food_name)
            
            if db_data:
                enriched_foods.append({
                    **food,
                    "found_in_database": True,
                    "database_match": db_data["name"],
                    "gi": db_data["gi"],
                    "carbs_per_100g": db_data["carbs"],
                    "protein_per_100g": db_data["protein"],
                    "fat_per_100g": db_data["fat"],
                    "fiber_per_100g": db_data["fiber"],
                    "standard_serving": db_data["serving_size"]
                })
            else:
                enriched_foods.append({
                    **food,
                    "found_in_database": False,
                    "database_match": None
                })
        
        result["foods"] = enriched_foods
        return result
        
    except json.JSONDecodeError as e:
        return {
            "error": f"Failed to parse AI response: {str(e)}",
            "raw_response": content if 'content' in locals() else None,
            "foods": []
        }
    except Exception as e:
        return {
            "error": str(e),
            "foods": []
        }


def get_food_recommendations(food_name: str, spike_level: str) -> str:
    """
    Get AI-powered recommendations for a specific food and spike level.
    """
    client = get_openai_client()
    
    prompt = f"""You are a nutrition expert helping someone manage their insulin levels for weight management and health (NOT diabetic).

The user is eating: {food_name}
Insulin spike level: {spike_level.upper()}

Provide 3-4 practical, friendly recommendations:
- If HIGH spike: How to reduce it (add protein/fat/fiber, portion control, timing)
- If MODERATE: How to optimize the meal
- If LOW: Positive reinforcement and tips to maintain

Keep it concise and actionable. Use emojis sparingly for friendliness."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Unable to generate recommendations: {str(e)}"


def generate_chat_response(
    user_message: str,
    food_analysis: dict | None = None,
    egl_result: dict | None = None
) -> str:
    """
    Generate a conversational response about the food analysis.
    """
    client = get_openai_client()
    
    system_prompt = """You are GlucoGuide, a friendly nutrition assistant that helps health-conscious people 
understand how their food choices affect insulin levels. 

Your audience is NOT diabetic - they are fitness enthusiasts, people trying to lose weight, 
or those wanting to maintain good health through smart eating.

Key principles:
- Be friendly and encouraging, not preachy
- Explain the science simply
- Focus on practical tips
- Use the Effective Glycemic Load (eGL) concept
- Celebrate good choices, gently guide on high-spike foods
- Always provide actionable advice

When discussing results:
- LOW spike (eGL ≤ 10): Celebrate! This is great for stable energy.
- MODERATE spike (eGL 11-19): Good, but can be optimized.
- HIGH spike (eGL ≥ 20): Help them understand why and how to reduce it."""

    messages = [{"role": "system", "content": system_prompt}]
    
    # Add context if available
    context = ""
    if food_analysis:
        context += f"\n\nFood Analysis Results:\n{json.dumps(food_analysis, indent=2)}"
    if egl_result:
        context += f"\n\neGL Calculation Results:\n{json.dumps(egl_result, indent=2)}"
    
    if context:
        messages.append({
            "role": "assistant",
            "content": f"[Context for this conversation: {context}]"
        })
    
    messages.append({"role": "user", "content": user_message})
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"I apologize, but I'm having trouble responding right now. Error: {str(e)}"

