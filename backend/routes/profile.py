"""
User profile routes for onboarding and personalization settings.
"""

import json
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.engine import get_db
from db.models import User, Profile
from routes.auth import get_current_user

router = APIRouter(prefix="/api/profile", tags=["profile"])


# ============================================================================
# Schemas
# ============================================================================

class ProfileUpdate(BaseModel):
    """Profile update request - all fields optional"""
    display_name: Optional[str] = Field(None, max_length=100)
    age: Optional[int] = Field(None, ge=1, le=120)
    sex: Optional[str] = Field(None, pattern="^(male|female|other)$")
    height_cm: Optional[float] = Field(None, ge=50, le=300)
    weight_kg: Optional[float] = Field(None, ge=20, le=500)
    
    activity_level: Optional[str] = Field(None, pattern="^(sedentary|light|moderate|active|very_active)$")
    goals: Optional[str] = Field(None, pattern="^(weight_loss|maintenance|muscle_gain|health|diabetes_management)$")
    
    has_insulin_resistance: Optional[bool] = None
    diabetes_type: Optional[str] = Field(None, pattern="^(none|type1|type2|prediabetes|gestational)$")
    diabetes_duration_years: Optional[float] = Field(None, ge=0, le=100)
    
    a1c: Optional[float] = Field(None, ge=3, le=20)
    fasting_glucose: Optional[float] = Field(None, ge=30, le=600)
    
    medications: Optional[List[str]] = None
    conditions: Optional[dict] = None
    
    dietary_preferences: Optional[str] = Field(None, max_length=100)
    allergies: Optional[List[str]] = None


class OnboardingRequest(BaseModel):
    """Quick onboarding request - essential fields only"""
    display_name: Optional[str] = None
    
    # Health status (required for onboarding)
    health_status: str = Field(..., pattern="^(healthy|insulin_resistance|type1|type2|prediabetes)$")
    
    # Basic info
    age: Optional[int] = Field(None, ge=1, le=120)
    sex: Optional[str] = Field(None, pattern="^(male|female|other)$")
    
    # Goals
    goals: str = Field(default="health", pattern="^(weight_loss|maintenance|muscle_gain|health|diabetes_management)$")
    activity_level: str = Field(default="moderate", pattern="^(sedentary|light|moderate|active|very_active)$")


class ProfileResponse(BaseModel):
    """Full profile response"""
    id: int
    user_id: int
    
    display_name: Optional[str]
    age: Optional[int]
    sex: Optional[str]
    height_cm: Optional[float]
    weight_kg: Optional[float]
    bmi: Optional[float]
    
    activity_level: Optional[str]
    goals: Optional[str]
    
    has_insulin_resistance: bool
    diabetes_type: Optional[str]
    diabetes_duration_years: Optional[float]
    
    a1c: Optional[float]
    fasting_glucose: Optional[float]
    
    medications: Optional[List[str]]
    conditions: Optional[dict]
    
    dietary_preferences: Optional[str]
    allergies: Optional[List[str]]
    
    onboarding_completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProfileSummary(BaseModel):
    """Brief profile summary for risk calculations"""
    has_insulin_resistance: bool
    diabetes_type: Optional[str]
    diabetes_duration_years: Optional[float]
    bmi: Optional[float]
    activity_level: Optional[str]
    a1c: Optional[float]
    medications: Optional[List[str]]
    conditions: Optional[dict]


# ============================================================================
# Helper functions
# ============================================================================

def parse_json_field(value: Optional[str]) -> Optional[any]:
    """Parse a JSON string field"""
    if not value:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return None


def serialize_json_field(value: any) -> Optional[str]:
    """Serialize a value to JSON string"""
    if value is None:
        return None
    return json.dumps(value)


# ============================================================================
# Routes
# ============================================================================

@router.get("", response_model=ProfileResponse)
async def get_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the current user's profile"""
    result = await db.execute(
        select(Profile).where(Profile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return ProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        display_name=profile.display_name,
        age=profile.age,
        sex=profile.sex,
        height_cm=profile.height_cm,
        weight_kg=profile.weight_kg,
        bmi=profile.bmi,
        activity_level=profile.activity_level,
        goals=profile.goals,
        has_insulin_resistance=profile.has_insulin_resistance,
        diabetes_type=profile.diabetes_type,
        diabetes_duration_years=profile.diabetes_duration_years,
        a1c=profile.a1c,
        fasting_glucose=profile.fasting_glucose,
        medications=parse_json_field(profile.medications),
        conditions=parse_json_field(profile.conditions_json),
        dietary_preferences=profile.dietary_preferences,
        allergies=parse_json_field(profile.allergies),
        onboarding_completed=profile.onboarding_completed,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


@router.put("", response_model=ProfileResponse)
async def update_profile(
    request: ProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update the current user's profile"""
    result = await db.execute(
        select(Profile).where(Profile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Update fields if provided
    update_data = request.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        if field == "medications":
            profile.medications = serialize_json_field(value)
        elif field == "conditions":
            profile.conditions_json = serialize_json_field(value)
        elif field == "allergies":
            profile.allergies = serialize_json_field(value)
        elif hasattr(profile, field):
            setattr(profile, field, value)
    
    profile.updated_at = datetime.utcnow()
    
    return ProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        display_name=profile.display_name,
        age=profile.age,
        sex=profile.sex,
        height_cm=profile.height_cm,
        weight_kg=profile.weight_kg,
        bmi=profile.bmi,
        activity_level=profile.activity_level,
        goals=profile.goals,
        has_insulin_resistance=profile.has_insulin_resistance,
        diabetes_type=profile.diabetes_type,
        diabetes_duration_years=profile.diabetes_duration_years,
        a1c=profile.a1c,
        fasting_glucose=profile.fasting_glucose,
        medications=parse_json_field(profile.medications),
        conditions=parse_json_field(profile.conditions_json),
        dietary_preferences=profile.dietary_preferences,
        allergies=parse_json_field(profile.allergies),
        onboarding_completed=profile.onboarding_completed,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


@router.post("/onboarding", response_model=ProfileResponse)
async def complete_onboarding(
    request: OnboardingRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Complete the initial onboarding with essential health info"""
    result = await db.execute(
        select(Profile).where(Profile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Map health_status to profile fields
    if request.health_status == "healthy":
        profile.has_insulin_resistance = False
        profile.diabetes_type = "none"
    elif request.health_status == "insulin_resistance":
        profile.has_insulin_resistance = True
        profile.diabetes_type = "none"
    elif request.health_status == "prediabetes":
        profile.has_insulin_resistance = True
        profile.diabetes_type = "prediabetes"
    elif request.health_status == "type1":
        profile.has_insulin_resistance = False
        profile.diabetes_type = "type1"
    elif request.health_status == "type2":
        profile.has_insulin_resistance = True
        profile.diabetes_type = "type2"
    
    # Set other fields
    if request.display_name:
        profile.display_name = request.display_name
    if request.age:
        profile.age = request.age
    if request.sex:
        profile.sex = request.sex
    
    profile.goals = request.goals
    profile.activity_level = request.activity_level
    profile.onboarding_completed = True
    profile.updated_at = datetime.utcnow()
    
    return ProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        display_name=profile.display_name,
        age=profile.age,
        sex=profile.sex,
        height_cm=profile.height_cm,
        weight_kg=profile.weight_kg,
        bmi=profile.bmi,
        activity_level=profile.activity_level,
        goals=profile.goals,
        has_insulin_resistance=profile.has_insulin_resistance,
        diabetes_type=profile.diabetes_type,
        diabetes_duration_years=profile.diabetes_duration_years,
        a1c=profile.a1c,
        fasting_glucose=profile.fasting_glucose,
        medications=parse_json_field(profile.medications),
        conditions=parse_json_field(profile.conditions_json),
        dietary_preferences=profile.dietary_preferences,
        allergies=parse_json_field(profile.allergies),
        onboarding_completed=profile.onboarding_completed,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


@router.get("/summary", response_model=ProfileSummary)
async def get_profile_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a brief profile summary for risk calculations"""
    result = await db.execute(
        select(Profile).where(Profile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return ProfileSummary(
        has_insulin_resistance=profile.has_insulin_resistance,
        diabetes_type=profile.diabetes_type,
        diabetes_duration_years=profile.diabetes_duration_years,
        bmi=profile.bmi,
        activity_level=profile.activity_level,
        a1c=profile.a1c,
        medications=parse_json_field(profile.medications),
        conditions=parse_json_field(profile.conditions_json),
    )

