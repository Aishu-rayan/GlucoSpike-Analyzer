"""
Glycemic Index and Nutrition Database
Data sourced from:
- University of Sydney GI Database
- USDA FoodData Central
- Harvard Health Publications
"""

# Comprehensive food database with GI values and macronutrients
# Format: food_name: {gi, carbs_per_100g, protein_per_100g, fat_per_100g, fiber_per_100g, serving_size_g}

FOOD_DATABASE = {
    # GRAINS & CEREALS
    "white rice": {
        "gi": 73,
        "carbs": 28,
        "protein": 2.7,
        "fat": 0.3,
        "fiber": 0.4,
        "serving_size": 150,
        "category": "grains"
    },
    "brown rice": {
        "gi": 50,
        "carbs": 23,
        "protein": 2.6,
        "fat": 0.9,
        "fiber": 1.8,
        "serving_size": 150,
        "category": "grains"
    },
    "basmati rice": {
        "gi": 58,
        "carbs": 25,
        "protein": 3.5,
        "fat": 0.4,
        "fiber": 0.4,
        "serving_size": 150,
        "category": "grains"
    },
    "quinoa": {
        "gi": 53,
        "carbs": 21,
        "protein": 4.4,
        "fat": 1.9,
        "fiber": 2.8,
        "serving_size": 150,
        "category": "grains"
    },
    "oatmeal": {
        "gi": 55,
        "carbs": 12,
        "protein": 2.5,
        "fat": 1.5,
        "fiber": 1.7,
        "serving_size": 250,
        "category": "grains"
    },
    "white bread": {
        "gi": 75,
        "carbs": 49,
        "protein": 9,
        "fat": 3.2,
        "fiber": 2.7,
        "serving_size": 30,
        "category": "grains"
    },
    "whole wheat bread": {
        "gi": 54,
        "carbs": 41,
        "protein": 13,
        "fat": 3.4,
        "fiber": 7,
        "serving_size": 30,
        "category": "grains"
    },
    "pasta": {
        "gi": 50,
        "carbs": 25,
        "protein": 5,
        "fat": 1.1,
        "fiber": 1.8,
        "serving_size": 180,
        "category": "grains"
    },
    "noodles": {
        "gi": 47,
        "carbs": 25,
        "protein": 4.5,
        "fat": 0.9,
        "fiber": 1.2,
        "serving_size": 180,
        "category": "grains"
    },
    
    # FRUITS
    "apple": {
        "gi": 36,
        "carbs": 14,
        "protein": 0.3,
        "fat": 0.2,
        "fiber": 2.4,
        "serving_size": 180,
        "category": "fruits"
    },
    "banana": {
        "gi": 51,
        "carbs": 23,
        "protein": 1.1,
        "fat": 0.3,
        "fiber": 2.6,
        "serving_size": 120,
        "category": "fruits"
    },
    "orange": {
        "gi": 43,
        "carbs": 12,
        "protein": 0.9,
        "fat": 0.1,
        "fiber": 2.4,
        "serving_size": 130,
        "category": "fruits"
    },
    "mango": {
        "gi": 51,
        "carbs": 15,
        "protein": 0.8,
        "fat": 0.4,
        "fiber": 1.6,
        "serving_size": 165,
        "category": "fruits"
    },
    "grapes": {
        "gi": 59,
        "carbs": 18,
        "protein": 0.7,
        "fat": 0.2,
        "fiber": 0.9,
        "serving_size": 150,
        "category": "fruits"
    },
    "watermelon": {
        "gi": 76,
        "carbs": 8,
        "protein": 0.6,
        "fat": 0.2,
        "fiber": 0.4,
        "serving_size": 150,
        "category": "fruits"
    },
    "strawberries": {
        "gi": 41,
        "carbs": 8,
        "protein": 0.7,
        "fat": 0.3,
        "fiber": 2,
        "serving_size": 150,
        "category": "fruits"
    },
    "blueberries": {
        "gi": 53,
        "carbs": 14,
        "protein": 0.7,
        "fat": 0.3,
        "fiber": 2.4,
        "serving_size": 150,
        "category": "fruits"
    },
    "pineapple": {
        "gi": 59,
        "carbs": 13,
        "protein": 0.5,
        "fat": 0.1,
        "fiber": 1.4,
        "serving_size": 150,
        "category": "fruits"
    },
    
    # VEGETABLES
    "potato": {
        "gi": 78,
        "carbs": 17,
        "protein": 2,
        "fat": 0.1,
        "fiber": 2.2,
        "serving_size": 150,
        "category": "vegetables"
    },
    "sweet potato": {
        "gi": 63,
        "carbs": 20,
        "protein": 1.6,
        "fat": 0.1,
        "fiber": 3,
        "serving_size": 150,
        "category": "vegetables"
    },
    "carrots": {
        "gi": 39,
        "carbs": 10,
        "protein": 0.9,
        "fat": 0.2,
        "fiber": 2.8,
        "serving_size": 80,
        "category": "vegetables"
    },
    "broccoli": {
        "gi": 10,
        "carbs": 7,
        "protein": 2.8,
        "fat": 0.4,
        "fiber": 2.6,
        "serving_size": 150,
        "category": "vegetables"
    },
    "spinach": {
        "gi": 15,
        "carbs": 3.6,
        "protein": 2.9,
        "fat": 0.4,
        "fiber": 2.2,
        "serving_size": 100,
        "category": "vegetables"
    },
    "corn": {
        "gi": 52,
        "carbs": 19,
        "protein": 3.2,
        "fat": 1.2,
        "fiber": 2.7,
        "serving_size": 150,
        "category": "vegetables"
    },
    "peas": {
        "gi": 48,
        "carbs": 14,
        "protein": 5.4,
        "fat": 0.4,
        "fiber": 5.7,
        "serving_size": 80,
        "category": "vegetables"
    },
    "tomato": {
        "gi": 15,
        "carbs": 3.9,
        "protein": 0.9,
        "fat": 0.2,
        "fiber": 1.2,
        "serving_size": 150,
        "category": "vegetables"
    },
    "cucumber": {
        "gi": 15,
        "carbs": 3.6,
        "protein": 0.7,
        "fat": 0.1,
        "fiber": 0.5,
        "serving_size": 100,
        "category": "vegetables"
    },
    
    # LEGUMES
    "lentils": {
        "gi": 32,
        "carbs": 20,
        "protein": 9,
        "fat": 0.4,
        "fiber": 7.9,
        "serving_size": 150,
        "category": "legumes"
    },
    "chickpeas": {
        "gi": 28,
        "carbs": 27,
        "protein": 9,
        "fat": 2.6,
        "fiber": 7.6,
        "serving_size": 150,
        "category": "legumes"
    },
    "black beans": {
        "gi": 30,
        "carbs": 24,
        "protein": 8.9,
        "fat": 0.5,
        "fiber": 8.7,
        "serving_size": 150,
        "category": "legumes"
    },
    "kidney beans": {
        "gi": 24,
        "carbs": 22,
        "protein": 8.7,
        "fat": 0.5,
        "fiber": 6.4,
        "serving_size": 150,
        "category": "legumes"
    },
    
    # DAIRY
    "milk": {
        "gi": 39,
        "carbs": 5,
        "protein": 3.4,
        "fat": 3.3,
        "fiber": 0,
        "serving_size": 250,
        "category": "dairy"
    },
    "yogurt": {
        "gi": 41,
        "carbs": 7,
        "protein": 3.5,
        "fat": 3.3,
        "fiber": 0,
        "serving_size": 200,
        "category": "dairy"
    },
    "greek yogurt": {
        "gi": 11,
        "carbs": 3.6,
        "protein": 10,
        "fat": 0.7,
        "fiber": 0,
        "serving_size": 170,
        "category": "dairy"
    },
    "cheese": {
        "gi": 0,
        "carbs": 1.3,
        "protein": 25,
        "fat": 33,
        "fiber": 0,
        "serving_size": 30,
        "category": "dairy"
    },
    
    # PROTEINS
    "chicken breast": {
        "gi": 0,
        "carbs": 0,
        "protein": 31,
        "fat": 3.6,
        "fiber": 0,
        "serving_size": 120,
        "category": "proteins"
    },
    "chicken": {
        "gi": 0,
        "carbs": 0,
        "protein": 27,
        "fat": 14,
        "fiber": 0,
        "serving_size": 120,
        "category": "proteins"
    },
    "salmon": {
        "gi": 0,
        "carbs": 0,
        "protein": 20,
        "fat": 13,
        "fiber": 0,
        "serving_size": 120,
        "category": "proteins"
    },
    "tuna": {
        "gi": 0,
        "carbs": 0,
        "protein": 30,
        "fat": 1,
        "fiber": 0,
        "serving_size": 120,
        "category": "proteins"
    },
    "eggs": {
        "gi": 0,
        "carbs": 1.1,
        "protein": 13,
        "fat": 11,
        "fiber": 0,
        "serving_size": 100,
        "category": "proteins"
    },
    "beef": {
        "gi": 0,
        "carbs": 0,
        "protein": 26,
        "fat": 15,
        "fiber": 0,
        "serving_size": 120,
        "category": "proteins"
    },
    "tofu": {
        "gi": 15,
        "carbs": 1.9,
        "protein": 8,
        "fat": 4.8,
        "fiber": 0.3,
        "serving_size": 120,
        "category": "proteins"
    },
    
    # SNACKS & SWEETS
    "chocolate": {
        "gi": 40,
        "carbs": 60,
        "protein": 5,
        "fat": 30,
        "fiber": 7,
        "serving_size": 40,
        "category": "sweets"
    },
    "ice cream": {
        "gi": 51,
        "carbs": 24,
        "protein": 3.5,
        "fat": 11,
        "fiber": 0.7,
        "serving_size": 100,
        "category": "sweets"
    },
    "cake": {
        "gi": 67,
        "carbs": 58,
        "protein": 5,
        "fat": 15,
        "fiber": 1,
        "serving_size": 80,
        "category": "sweets"
    },
    "cookies": {
        "gi": 62,
        "carbs": 68,
        "protein": 6,
        "fat": 20,
        "fiber": 2,
        "serving_size": 30,
        "category": "sweets"
    },
    "chips": {
        "gi": 56,
        "carbs": 53,
        "protein": 7,
        "fat": 33,
        "fiber": 4.4,
        "serving_size": 30,
        "category": "snacks"
    },
    "popcorn": {
        "gi": 65,
        "carbs": 78,
        "protein": 12,
        "fat": 4.3,
        "fiber": 15,
        "serving_size": 30,
        "category": "snacks"
    },
    
    # BEVERAGES
    "orange juice": {
        "gi": 50,
        "carbs": 10,
        "protein": 0.7,
        "fat": 0.2,
        "fiber": 0.2,
        "serving_size": 250,
        "category": "beverages"
    },
    "apple juice": {
        "gi": 41,
        "carbs": 11,
        "protein": 0.1,
        "fat": 0.1,
        "fiber": 0.2,
        "serving_size": 250,
        "category": "beverages"
    },
    "soda": {
        "gi": 63,
        "carbs": 11,
        "protein": 0,
        "fat": 0,
        "fiber": 0,
        "serving_size": 330,
        "category": "beverages"
    },
    "cola": {
        "gi": 63,
        "carbs": 11,
        "protein": 0,
        "fat": 0,
        "fiber": 0,
        "serving_size": 330,
        "category": "beverages"
    },
    
    # INDIAN FOODS
    "chapati": {
        "gi": 52,
        "carbs": 48,
        "protein": 11,
        "fat": 1.7,
        "fiber": 11,
        "serving_size": 40,
        "category": "grains"
    },
    "roti": {
        "gi": 52,
        "carbs": 48,
        "protein": 11,
        "fat": 1.7,
        "fiber": 11,
        "serving_size": 40,
        "category": "grains"
    },
    "naan": {
        "gi": 71,
        "carbs": 50,
        "protein": 9,
        "fat": 3.5,
        "fiber": 2,
        "serving_size": 90,
        "category": "grains"
    },
    "paratha": {
        "gi": 55,
        "carbs": 45,
        "protein": 8,
        "fat": 10,
        "fiber": 4,
        "serving_size": 80,
        "category": "grains"
    },
    "idli": {
        "gi": 77,
        "carbs": 20,
        "protein": 3.9,
        "fat": 0.4,
        "fiber": 0.8,
        "serving_size": 80,
        "category": "grains"
    },
    "dosa": {
        "gi": 77,
        "carbs": 30,
        "protein": 4,
        "fat": 1.2,
        "fiber": 0.7,
        "serving_size": 100,
        "category": "grains"
    },
    "biryani": {
        "gi": 60,
        "carbs": 25,
        "protein": 8,
        "fat": 7,
        "fiber": 1.5,
        "serving_size": 250,
        "category": "grains"
    },
    "dal": {
        "gi": 30,
        "carbs": 15,
        "protein": 7,
        "fat": 3,
        "fiber": 5,
        "serving_size": 150,
        "category": "legumes"
    },
    "paneer": {
        "gi": 0,
        "carbs": 1.2,
        "protein": 18,
        "fat": 22,
        "fiber": 0,
        "serving_size": 100,
        "category": "dairy"
    },
    "samosa": {
        "gi": 66,
        "carbs": 32,
        "protein": 4,
        "fat": 18,
        "fiber": 2,
        "serving_size": 100,
        "category": "snacks"
    },
    
    # COMMON MEALS
    "pizza": {
        "gi": 60,
        "carbs": 33,
        "protein": 11,
        "fat": 10,
        "fiber": 2.3,
        "serving_size": 107,
        "category": "meals"
    },
    "burger": {
        "gi": 66,
        "carbs": 24,
        "protein": 15,
        "fat": 14,
        "fiber": 1.3,
        "serving_size": 200,
        "category": "meals"
    },
    "french fries": {
        "gi": 75,
        "carbs": 41,
        "protein": 3.4,
        "fat": 15,
        "fiber": 3.8,
        "serving_size": 117,
        "category": "snacks"
    },
    "sandwich": {
        "gi": 55,
        "carbs": 30,
        "protein": 12,
        "fat": 8,
        "fiber": 3,
        "serving_size": 150,
        "category": "meals"
    },
    "salad": {
        "gi": 15,
        "carbs": 5,
        "protein": 2,
        "fat": 0.5,
        "fiber": 3,
        "serving_size": 150,
        "category": "vegetables"
    },
    "fried rice": {
        "gi": 68,
        "carbs": 30,
        "protein": 5,
        "fat": 8,
        "fiber": 1.5,
        "serving_size": 200,
        "category": "meals"
    },
    "sushi": {
        "gi": 52,
        "carbs": 22,
        "protein": 6,
        "fat": 1.5,
        "fiber": 0.8,
        "serving_size": 150,
        "category": "meals"
    },
    
    # NUTS & SEEDS
    "almonds": {
        "gi": 0,
        "carbs": 22,
        "protein": 21,
        "fat": 50,
        "fiber": 12,
        "serving_size": 30,
        "category": "nuts"
    },
    "walnuts": {
        "gi": 15,
        "carbs": 14,
        "protein": 15,
        "fat": 65,
        "fiber": 7,
        "serving_size": 30,
        "category": "nuts"
    },
    "peanuts": {
        "gi": 14,
        "carbs": 16,
        "protein": 26,
        "fat": 49,
        "fiber": 9,
        "serving_size": 30,
        "category": "nuts"
    },
    "cashews": {
        "gi": 22,
        "carbs": 30,
        "protein": 18,
        "fat": 44,
        "fiber": 3,
        "serving_size": 30,
        "category": "nuts"
    },
}


def get_food_data(food_name: str) -> dict | None:
    """Get food data by name (case-insensitive partial match)"""
    food_lower = food_name.lower().strip()
    
    # Exact match first
    if food_lower in FOOD_DATABASE:
        return {"name": food_lower, **FOOD_DATABASE[food_lower]}
    
    # Partial match
    for key in FOOD_DATABASE:
        if food_lower in key or key in food_lower:
            return {"name": key, **FOOD_DATABASE[key]}
    
    return None


def search_foods(query: str) -> list[dict]:
    """Search for foods matching query"""
    query_lower = query.lower().strip()
    results = []
    
    for key, data in FOOD_DATABASE.items():
        if query_lower in key:
            results.append({"name": key, **data})
    
    return results


def get_all_foods() -> list[str]:
    """Get list of all food names"""
    return list(FOOD_DATABASE.keys())

