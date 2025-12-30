"""
USDA FoodData Central API routes.
Exposes USDA food search and lookup functionality.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from db.engine import get_db
from services.usda_service import USDAService, search_and_cache_food, get_food_from_usda

router = APIRouter(prefix="/api/usda", tags=["usda"])


# ============================================================================
# Schemas
# ============================================================================

class NutrientInfo(BaseModel):
    calories_per_100g: float
    protein_per_100g: float
    fat_per_100g: float
    carbs_per_100g: float
    fiber_per_100g: float
    sugars_per_100g: float = 0


class USDAFoodResult(BaseModel):
    fdc_id: int
    name: str
    nutrients: NutrientInfo


class USDASearchResponse(BaseModel):
    query: str
    results: list[USDAFoodResult]
    count: int


class USDAFoodDetail(BaseModel):
    fdc_id: int
    name: str
    nutrients: NutrientInfo
    serving_size_g: float
    serving_description: str


# ============================================================================
# Routes
# ============================================================================

@router.get("/search", response_model=USDASearchResponse)
async def search_usda_foods(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Number of results"),
    db: AsyncSession = Depends(get_db),
):
    """
    Search USDA FoodData Central for foods.
    Results are cached in the local database.
    """
    try:
        results = await search_and_cache_food(q, db)
        
        return USDASearchResponse(
            query=q,
            results=[
                USDAFoodResult(
                    fdc_id=r["fdc_id"],
                    name=r["name"],
                    nutrients=NutrientInfo(**r["nutrients"]),
                )
                for r in results[:limit]
            ],
            count=len(results),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"USDA API error: {str(e)}")


@router.get("/food/{fdc_id}", response_model=USDAFoodDetail)
async def get_usda_food(
    fdc_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed nutritional information for a specific USDA food.
    """
    try:
        result = await get_food_from_usda(fdc_id, db)
        
        if not result:
            raise HTTPException(status_code=404, detail="Food not found in USDA database")
        
        return USDAFoodDetail(
            fdc_id=result["fdc_id"],
            name=result["name"],
            nutrients=NutrientInfo(**result["nutrients"]),
            serving_size_g=result["serving"]["serving_size_g"],
            serving_description=result["serving"]["serving_description"],
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"USDA API error: {str(e)}")


@router.get("/test")
async def test_usda_connection():
    """Test USDA API connection"""
    service = USDAService()
    try:
        results = await service.search_foods("apple", page_size=1)
        await service.close()
        
        if results.get("error"):
            return {"status": "error", "message": results["error"]}
        
        return {
            "status": "connected",
            "api_key_valid": len(results.get("foods", [])) > 0,
            "sample_result": results.get("foods", [{}])[0].get("description") if results.get("foods") else None,
        }
    except Exception as e:
        await service.close()
        return {"status": "error", "message": str(e)}

