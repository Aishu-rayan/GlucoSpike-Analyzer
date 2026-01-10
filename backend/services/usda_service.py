"""
USDA FoodData Central API Integration

Fetches nutritional data from USDA's FoodData Central API
and caches results in the local SQLite database.

API Documentation: https://fdc.nal.usda.gov/api-guide
"""

import os
import httpx
from typing import Optional
from datetime import datetime, timedelta

from dotenv import load_dotenv

load_dotenv()

USDA_API_KEY = os.getenv("USDA_API_KEY")
USDA_BASE_URL = "https://api.nal.usda.gov/fdc/v1"

# Nutrient IDs for the data we need
NUTRIENT_IDS = {
    "energy": 1008,       # Energy (kcal)
    "protein": 1003,      # Protein
    "fat": 1004,          # Total lipid (fat)
    "carbs": 1005,        # Carbohydrate, by difference
    "fiber": 1079,        # Fiber, total dietary
    "sugars": 2000,       # Sugars, total
    "sodium": 1093,       # Sodium
}


class USDAService:
    """Service for interacting with USDA FoodData Central API"""
    
    def __init__(self, api_key: str = USDA_API_KEY):
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def search_foods(
        self, 
        query: str, 
        page_size: int = 25,
        data_type: Optional[list[str]] = None
    ) -> dict:
        """
        Search for foods in USDA database.
        
        Args:
            query: Search term
            page_size: Number of results (max 200)
            data_type: Filter by data type (e.g., ["Foundation", "SR Legacy", "Branded"])
        
        Returns:
            API response with food search results
        """
        url = f"{USDA_BASE_URL}/foods/search"
        
        params = {
            "api_key": self.api_key,
            "query": query,
            "pageSize": min(page_size, 200),
        }
        
        if data_type:
            params["dataType"] = ",".join(data_type)
        
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            print(f"USDA API error: {e}")
            return {"foods": [], "error": str(e)}
    
    async def get_food_details(self, fdc_id: int) -> Optional[dict]:
        """
        Get detailed nutritional information for a specific food.
        
        Args:
            fdc_id: USDA FoodData Central ID
        
        Returns:
            Food details including nutrients
        """
        url = f"{USDA_BASE_URL}/food/{fdc_id}"
        
        params = {
            "api_key": self.api_key,
        }
        
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            print(f"USDA API error: {e}")
            return None
    
    async def get_foods_batch(self, fdc_ids: list[int]) -> list[dict]:
        """
        Get details for multiple foods in one request.
        
        Args:
            fdc_ids: List of USDA FoodData Central IDs (max 20)
        
        Returns:
            List of food details
        """
        url = f"{USDA_BASE_URL}/foods"
        
        # API limits to 20 IDs per request
        fdc_ids = fdc_ids[:20]
        
        params = {
            "api_key": self.api_key,
        }
        
        data = {
            "fdcIds": fdc_ids,
        }
        
        try:
            response = await self.client.post(url, params=params, json=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            print(f"USDA API error: {e}")
            return []
    
    def extract_nutrients(self, food_data: dict) -> dict:
        """
        Extract relevant nutrients from USDA food data.
        
        Args:
            food_data: Raw food data from USDA API
        
        Returns:
            Dict with normalized nutrient values per 100g
        """
        nutrients = {}
        
        # Get nutrients array from food data
        food_nutrients = food_data.get("foodNutrients", [])
        
        for nutrient in food_nutrients:
            # Handle different response formats
            if "nutrient" in nutrient:
                nutrient_id = nutrient["nutrient"].get("id")
                amount = nutrient.get("amount", 0)
            else:
                nutrient_id = nutrient.get("nutrientId")
                amount = nutrient.get("value", 0)
            
            # Map to our nutrient names
            for name, usda_id in NUTRIENT_IDS.items():
                if nutrient_id == usda_id:
                    nutrients[name] = amount
                    break
        
        return {
            "calories_per_100g": nutrients.get("energy", 0),
            "protein_per_100g": nutrients.get("protein", 0),
            "fat_per_100g": nutrients.get("fat", 0),
            "carbs_per_100g": nutrients.get("carbs", 0),
            "fiber_per_100g": nutrients.get("fiber", 0),
            "sugars_per_100g": nutrients.get("sugars", 0),
        }
    
    def extract_serving_info(self, food_data: dict) -> dict:
        """
        Extract serving size information from USDA food data.
        
        Args:
            food_data: Raw food data from USDA API
        
        Returns:
            Dict with serving information
        """
        # Try to get serving size from food portions
        portions = food_data.get("foodPortions", [])
        
        if portions:
            # Use first portion as default serving
            portion = portions[0]
            return {
                "serving_size_g": portion.get("gramWeight", 100),
                "serving_description": portion.get("portionDescription", 
                    portion.get("modifier", "100g")),
            }
        
        # Default to 100g
        return {
            "serving_size_g": 100,
            "serving_description": "100g",
        }
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


async def search_and_cache_food(query: str, db_session) -> list[dict]:
    """
    Search USDA for a food and cache results in database.
    
    Args:
        query: Search term
        db_session: SQLAlchemy async session
    
    Returns:
        List of food results with nutritional data
    """
    from db.models import Food
    from sqlalchemy import select
    
    service = USDAService()
    
    try:
        # Search USDA
        results = await service.search_foods(
            query,
            page_size=10,
            data_type=["Foundation", "SR Legacy"]  # More reliable data
        )
        
        foods = []
        for item in results.get("foods", []):
            fdc_id = item.get("fdcId")
            description = item.get("description", "")
            
            # Extract nutrients from search results
            nutrients = service.extract_nutrients(item)
            
            # Check if already in our database
            existing = await db_session.execute(
                select(Food).where(Food.usda_fdc_id == fdc_id)
            )
            existing_food = existing.scalar_one_or_none()
            
            if not existing_food:
                # Create new food entry
                new_food = Food(
                    canonical_name=description.lower(),
                    usda_fdc_id=fdc_id,
                    usda_description=description,
                    carbs_per_100g=nutrients["carbs_per_100g"],
                    protein_per_100g=nutrients["protein_per_100g"],
                    fat_per_100g=nutrients["fat_per_100g"],
                    fiber_per_100g=nutrients["fiber_per_100g"],
                    calories_per_100g=nutrients["calories_per_100g"],
                    serving_size_g=100,
                    data_source="usda",
                )
                db_session.add(new_food)
            
            foods.append({
                "fdc_id": fdc_id,
                "name": description,
                "nutrients": nutrients,
            })
        
        await db_session.commit()
        return foods
        
    finally:
        await service.close()


async def get_food_from_usda(fdc_id: int, db_session) -> Optional[dict]:
    """
    Get detailed food data from USDA and cache it.
    
    Args:
        fdc_id: USDA FoodData Central ID
        db_session: SQLAlchemy async session
    
    Returns:
        Food data with nutrients and serving info
    """
    from db.models import Food
    from sqlalchemy import select
    
    service = USDAService()
    
    try:
        # Get details from USDA
        details = await service.get_food_details(fdc_id)
        
        if not details:
            return None
        
        nutrients = service.extract_nutrients(details)
        serving = service.extract_serving_info(details)
        
        # Update or create in database
        existing = await db_session.execute(
            select(Food).where(Food.usda_fdc_id == fdc_id)
        )
        food = existing.scalar_one_or_none()
        
        if food:
            # Update existing
            food.carbs_per_100g = nutrients["carbs_per_100g"]
            food.protein_per_100g = nutrients["protein_per_100g"]
            food.fat_per_100g = nutrients["fat_per_100g"]
            food.fiber_per_100g = nutrients["fiber_per_100g"]
            food.calories_per_100g = nutrients["calories_per_100g"]
            food.serving_size_g = serving["serving_size_g"]
            food.serving_description = serving["serving_description"]
            food.last_updated = datetime.utcnow()
        else:
            # Create new
            food = Food(
                canonical_name=details.get("description", "").lower(),
                usda_fdc_id=fdc_id,
                usda_description=details.get("description"),
                carbs_per_100g=nutrients["carbs_per_100g"],
                protein_per_100g=nutrients["protein_per_100g"],
                fat_per_100g=nutrients["fat_per_100g"],
                fiber_per_100g=nutrients["fiber_per_100g"],
                calories_per_100g=nutrients["calories_per_100g"],
                serving_size_g=serving["serving_size_g"],
                serving_description=serving["serving_description"],
                data_source="usda",
            )
            db_session.add(food)
        
        await db_session.commit()
        
        return {
            "fdc_id": fdc_id,
            "name": details.get("description"),
            "nutrients": nutrients,
            "serving": serving,
        }
        
    finally:
        await service.close()

