"""
Pydantic models for API request/response schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class SpikeLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class FoodItem(BaseModel):
    """A single food item identified from image or input"""
    name: str
    estimated_grams: float = Field(default=100, ge=0)
    portions: float = Field(default=1.0, ge=0.1)
    confidence: str = Field(default="medium")
    found_in_database: bool = False
    database_match: Optional[str] = None
    gi: Optional[float] = None
    carbs_per_100g: Optional[float] = None
    protein_per_100g: Optional[float] = None
    fat_per_100g: Optional[float] = None
    fiber_per_100g: Optional[float] = None


class FoodAnalysisResponse(BaseModel):
    """Response from food image analysis"""
    foods: list[FoodItem]
    meal_description: str = ""
    is_healthy_meal: bool = True
    health_notes: str = ""
    error: Optional[str] = None


class NutritionBreakdown(BaseModel):
    """Nutritional breakdown for a food/meal"""
    carbs: float
    protein: float
    fat: float
    fiber: float
    net_carbs: float


class EGLResponse(BaseModel):
    """Response from eGL calculation"""
    food_name: str
    portions: float
    serving_size: float
    
    # Nutrition
    nutrition: NutritionBreakdown
    
    # GL values
    gi: float
    base_gl: float
    effective_gl: float
    
    # Modifiers
    fiber_modifier: float
    protein_modifier: float
    fat_modifier: float
    total_reduction_percent: float
    
    # Classification
    spike_level: SpikeLevel
    spike_level_before_modifiers: SpikeLevel
    spike_improved: bool
    
    # Guidance
    recommendations: list[str]
    explanation: str


class ChatMessage(BaseModel):
    """A chat message"""
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str


class ChatRequest(BaseModel):
    """Request for chat endpoint"""
    message: str
    include_context: bool = True


class ChatResponse(BaseModel):
    """Response from chat endpoint"""
    response: str
    food_analysis: Optional[FoodAnalysisResponse] = None
    egl_result: Optional[EGLResponse] = None


class AnalyzeRequest(BaseModel):
    """Request to analyze food by name (without image)"""
    food_name: str
    portions: float = Field(default=1.0, ge=0.1)


class FoodSearchResponse(BaseModel):
    """Response from food search"""
    query: str
    results: list[dict]
    count: int

