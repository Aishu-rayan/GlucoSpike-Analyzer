# Services module
from .egl_calculator import (
    calculate_egl, 
    calculate_meal_egl, 
    NutritionInfo, 
    EGLResult, 
    SpikeLevel,
    ProfileContext,
    RiskScoreResult,
    RiskLevel,
)
from .food_analyzer import analyze_food_image, generate_chat_response, get_food_recommendations
from .usda_service import USDAService, search_and_cache_food, get_food_from_usda

