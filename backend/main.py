"""
GlucoGuide API - Insulin Spike Management Chatbot Backend

A FastAPI application that helps users understand the insulin spike 
potential of their food through image recognition and GL calculations.
Now with user accounts, chat history, and personalized recommendations.
"""

import os
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession

from database.gi_database import get_food_data, search_foods, FOOD_DATABASE
from services.egl_calculator import calculate_egl, calculate_meal_egl, NutritionInfo
from services.food_analyzer import analyze_food_image, generate_chat_response, generate_chat_response_stream
from models.schemas import (
    FoodAnalysisResponse, EGLResponse, NutritionBreakdown,
    ChatRequest, ChatResponse, AnalyzeRequest, FoodSearchResponse,
    SpikeLevel, FoodItem
)
from db.engine import init_db, get_db
from db.models import User, Profile
from routes.auth import router as auth_router, get_current_user, get_current_user_optional
from routes.chats import router as chats_router
from routes.profile import router as profile_router
from routes.usda import router as usda_router

# Load environment variables
load_dotenv()

# Ensure uploads directory exists
UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    print("GlucoGuide API starting up...")
    
    # Initialize database
    await init_db()
    print("Database initialized")
    
    # Seed initial data if needed
    from db.seed_data import seed_foods_and_gi
    try:
        await seed_foods_and_gi()
    except Exception as e:
        print(f"Seed data skipped or failed: {e}")
    
    print(f"Loaded {len(FOOD_DATABASE)} foods in memory database")
    yield
    print("GlucoGuide API shutting down...")


# Create FastAPI app
app = FastAPI(
    title="GlucoGuide API",
    description="Insulin Spike Management Chatbot - Analyze food and understand glycemic impact",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "https://gluco-guide.pragnyalabs.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(chats_router)
app.include_router(profile_router)
app.include_router(usda_router)


# ============================================================================
# Health Check
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": "GlucoGuide API",
        "version": "2.0.0",
        "message": "Welcome to GlucoGuide! Upload a food image or search for foods to analyze insulin spike potential.",
        "features": ["user_accounts", "chat_history", "personalized_recommendations"]
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": {
            "foods_loaded": len(FOOD_DATABASE),
            "status": "connected"
        },
        "openai": {
            "status": "configured" if os.getenv("OPENAI_API_KEY") else "not_configured"
        },
        "features": {
            "authentication": True,
            "chat_history": True,
            "user_profiles": True,
        }
    }


# ============================================================================
# Food Analysis Endpoints (now with optional auth for personalization)
# ============================================================================

@app.post("/api/analyze/image", response_model=ChatResponse)
async def analyze_image(
    file: UploadFile = File(...),
    message: str = Form(default="Analyze this food"),
    current_user: User = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """
    Analyze a food image and calculate eGL.
    
    - Identifies foods in the image using AI
    - Looks up nutritional data
    - Calculates effective glycemic load
    - Provides recommendations (personalized if logged in)
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Read image
    try:
        image_bytes = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read image: {str(e)}")
    
    # Analyze image with AI
    analysis = analyze_food_image(image_bytes)
    
    if "error" in analysis and analysis["error"]:
        return ChatResponse(
            response=f"I had trouble analyzing your image: {analysis['error']}. Please try again with a clearer photo.",
            food_analysis=None,
            egl_result=None
        )
    
    # Calculate eGL for identified foods
    egl_result = None
    nutrition_infos = []
    
    for food in analysis.get("foods", []):
        if food.get("found_in_database"):
            db_match = food.get("database_match")
            food_data = get_food_data(db_match)
            
            if food_data:
                portions = food.get("portions", 1.0)
                nutrition_infos.append(NutritionInfo(
                    name=food_data["name"],
                    gi=food_data["gi"],
                    carbs=food_data["carbs"],
                    protein=food_data["protein"],
                    fat=food_data["fat"],
                    fiber=food_data["fiber"],
                    serving_size=food_data["serving_size"],
                    portions=portions
                ))
    
    # Calculate combined eGL if we have data
    if nutrition_infos:
        try:
            egl_calc = calculate_meal_egl(nutrition_infos)
            egl_result = EGLResponse(
                food_name=egl_calc.food_name,
                portions=egl_calc.portions,
                serving_size=egl_calc.serving_size,
                nutrition=NutritionBreakdown(
                    carbs=egl_calc.carbs,
                    protein=egl_calc.protein,
                    fat=egl_calc.fat,
                    fiber=egl_calc.fiber,
                    net_carbs=egl_calc.net_carbs
                ),
                gi=egl_calc.gi,
                base_gl=egl_calc.base_gl,
                effective_gl=egl_calc.effective_gl,
                fiber_modifier=egl_calc.fiber_modifier,
                protein_modifier=egl_calc.protein_modifier,
                fat_modifier=egl_calc.fat_modifier,
                total_reduction_percent=egl_calc.total_modifier * 100,
                spike_level=SpikeLevel(egl_calc.spike_level.value),
                spike_level_before_modifiers=SpikeLevel(egl_calc.spike_level_before_modifiers.value),
                spike_improved=egl_calc.spike_level != egl_calc.spike_level_before_modifiers,
                recommendations=egl_calc.recommendations,
                explanation=egl_calc.explanation
            )
        except Exception as e:
            print(f"Error calculating eGL: {e}")
    
    # Generate conversational response
    response_text = generate_chat_response(
        message,
        food_analysis=analysis,
        egl_result=egl_result.model_dump() if egl_result else None
    )
    
    # Create food analysis response
    food_analysis = FoodAnalysisResponse(
        foods=[FoodItem(**f) for f in analysis.get("foods", [])],
        meal_description=analysis.get("meal_description", ""),
        is_healthy_meal=analysis.get("is_healthy_meal", True),
        health_notes=analysis.get("health_notes", "")
    )
    
    return ChatResponse(
        response=response_text,
        food_analysis=food_analysis,
        egl_result=egl_result
    )


@app.post("/api/analyze/food", response_model=EGLResponse)
async def analyze_food_by_name(
    request: AnalyzeRequest,
    current_user: User = Depends(get_current_user_optional),
):
    """
    Analyze a food by name (without image).
    
    - Looks up food in database
    - Calculates effective glycemic load
    - Provides recommendations
    """
    food_data = get_food_data(request.food_name)
    
    if not food_data:
        raise HTTPException(
            status_code=404,
            detail=f"Food '{request.food_name}' not found in database. Try searching with /api/foods/search"
        )
    
    # Create nutrition info
    nutrition = NutritionInfo(
        name=food_data["name"],
        gi=food_data["gi"],
        carbs=food_data["carbs"],
        protein=food_data["protein"],
        fat=food_data["fat"],
        fiber=food_data["fiber"],
        serving_size=food_data["serving_size"],
        portions=request.portions
    )
    
    # Calculate eGL
    result = calculate_egl(nutrition)
    
    return EGLResponse(
        food_name=result.food_name,
        portions=result.portions,
        serving_size=result.serving_size,
        nutrition=NutritionBreakdown(
            carbs=result.carbs,
            protein=result.protein,
            fat=result.fat,
            fiber=result.fiber,
            net_carbs=result.net_carbs
        ),
        gi=result.gi,
        base_gl=result.base_gl,
        effective_gl=result.effective_gl,
        fiber_modifier=result.fiber_modifier,
        protein_modifier=result.protein_modifier,
        fat_modifier=result.fat_modifier,
        total_reduction_percent=result.total_modifier * 100,
        spike_level=SpikeLevel(result.spike_level.value),
        spike_level_before_modifiers=SpikeLevel(result.spike_level_before_modifiers.value),
        spike_improved=result.spike_level != result.spike_level_before_modifiers,
        recommendations=result.recommendations,
        explanation=result.explanation
    )


# ============================================================================
# Food Database Endpoints
# ============================================================================

@app.get("/api/foods/search", response_model=FoodSearchResponse)
async def search_food(q: str):
    """Search for foods in the database"""
    if len(q) < 2:
        raise HTTPException(status_code=400, detail="Search query must be at least 2 characters")
    
    results = search_foods(q)
    
    return FoodSearchResponse(
        query=q,
        results=results,
        count=len(results)
    )


@app.get("/api/foods")
async def list_foods(category: str = None, limit: int = 50):
    """List all foods or filter by category"""
    foods = []
    
    for name, data in FOOD_DATABASE.items():
        if category and data.get("category") != category:
            continue
        foods.append({"name": name, **data})
        
        if len(foods) >= limit:
            break
    
    return {
        "foods": foods,
        "count": len(foods),
        "total_in_database": len(FOOD_DATABASE)
    }


@app.get("/api/foods/categories")
async def list_categories():
    """List all food categories"""
    categories = set()
    for data in FOOD_DATABASE.values():
        if "category" in data:
            categories.add(data["category"])
    
    return {"categories": sorted(list(categories))}


# ============================================================================
# Chat Endpoint (legacy - still works without auth)
# ============================================================================

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    General chat endpoint for questions about nutrition and insulin.
    For persistent chat history, use /api/chats endpoints instead.
    """
    response = generate_chat_response(request.message)

    return ChatResponse(
        response=response,
        food_analysis=None,
        egl_result=None
    )


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """Stream chat response text as it is generated."""

    def gen():
        try:
            for chunk in generate_chat_response_stream(request.message):
                yield chunk
        except Exception as e:
            yield f"\n\n[stream_error] {str(e)}"

    return StreamingResponse(gen(), media_type="text/plain; charset=utf-8")


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    print(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
