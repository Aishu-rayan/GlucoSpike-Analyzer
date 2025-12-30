"""
Effective Glycemic Load (eGL) Calculator with Profile-Based Risk Scoring

Calculates the effective insulin spike potential considering:
- Base Glycemic Load (GL)
- Fiber content (reduces net carbs)
- Protein content (slows gastric emptying)
- Fat content (delays carbohydrate absorption)
- User profile (diabetes status, insulin resistance, BMI, activity level, etc.)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class SpikeLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class RiskLevel(str, Enum):
    """Risk level considering user profile"""
    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class ProfileContext:
    """User profile context for personalized risk calculations"""
    has_insulin_resistance: bool = False
    diabetes_type: Optional[str] = None  # none, type1, type2, prediabetes
    diabetes_duration_years: Optional[float] = None
    bmi: Optional[float] = None
    activity_level: Optional[str] = None  # sedentary, light, moderate, active, very_active
    a1c: Optional[float] = None
    medications: Optional[list[str]] = None
    age: Optional[int] = None
    
    @property
    def is_diabetic(self) -> bool:
        return self.diabetes_type in ('type1', 'type2')
    
    @property
    def is_prediabetic(self) -> bool:
        return self.diabetes_type == 'prediabetes' or self.has_insulin_resistance


@dataclass
class NutritionInfo:
    """Nutritional information for a food item"""
    name: str
    gi: float
    carbs: float  # grams
    protein: float  # grams
    fat: float  # grams
    fiber: float  # grams
    serving_size: float  # grams
    portions: float = 1.0  # number of portions


@dataclass
class RiskScoreResult:
    """Profile-adjusted risk score result"""
    base_egl: float
    adjusted_score: float
    risk_level: RiskLevel
    profile_modifier: float  # Total profile-based modifier
    modifier_breakdown: dict  # Breakdown of modifiers
    warnings: list[str] = field(default_factory=list)
    personalized_tips: list[str] = field(default_factory=list)


@dataclass
class EGLResult:
    """Result of eGL calculation"""
    food_name: str
    portions: float
    serving_size: float
    
    # Nutritional breakdown (per actual serving)
    carbs: float
    protein: float
    fat: float
    fiber: float
    net_carbs: float
    
    # GL calculations
    gi: float
    base_gl: float
    effective_gl: float
    
    # Modifiers applied
    fiber_modifier: float
    protein_modifier: float
    fat_modifier: float
    total_modifier: float
    
    # Classification
    spike_level: SpikeLevel
    spike_level_before_modifiers: SpikeLevel
    
    # Recommendations
    recommendations: list[str]
    explanation: str
    
    # Profile-based risk (optional)
    risk_score: Optional[RiskScoreResult] = None


def calculate_fiber_modifier(fiber_grams: float) -> float:
    """
    Calculate fiber modifier based on fiber content.
    Higher fiber = lower insulin spike
    """
    if fiber_grams <= 2:
        return 0.0  # No reduction
    elif fiber_grams <= 5:
        return 0.10  # 10% reduction
    elif fiber_grams <= 10:
        return 0.15  # 15% reduction
    else:
        return 0.20  # 20% reduction (max)


def calculate_protein_modifier(protein_grams: float) -> float:
    """
    Calculate protein modifier based on protein content.
    Higher protein = slower gastric emptying = lower spike
    """
    if protein_grams < 5:
        return 0.0  # No reduction
    elif protein_grams < 15:
        return 0.10  # 10% reduction
    elif protein_grams < 25:
        return 0.15  # 15% reduction
    else:
        return 0.20  # 20% reduction (max)


def calculate_fat_modifier(fat_grams: float) -> float:
    """
    Calculate fat modifier based on fat content.
    Higher fat = delayed absorption = lower spike
    """
    if fat_grams < 5:
        return 0.0  # No reduction
    elif fat_grams < 15:
        return 0.10  # 10% reduction
    else:
        return 0.15  # 15% reduction (max)


def classify_spike_level(gl_value: float) -> SpikeLevel:
    """Classify the spike level based on GL value"""
    if gl_value <= 10:
        return SpikeLevel.LOW
    elif gl_value <= 19:
        return SpikeLevel.MODERATE
    else:
        return SpikeLevel.HIGH


def classify_risk_level(score: float, profile: Optional[ProfileContext] = None) -> RiskLevel:
    """Classify risk level based on adjusted score"""
    # Adjust thresholds for diabetic users
    if profile and profile.is_diabetic:
        if score <= 8:
            return RiskLevel.MINIMAL
        elif score <= 15:
            return RiskLevel.LOW
        elif score <= 25:
            return RiskLevel.MODERATE
        elif score <= 35:
            return RiskLevel.HIGH
        else:
            return RiskLevel.VERY_HIGH
    else:
        if score <= 10:
            return RiskLevel.MINIMAL
        elif score <= 20:
            return RiskLevel.LOW
        elif score <= 30:
            return RiskLevel.MODERATE
        elif score <= 40:
            return RiskLevel.HIGH
        else:
            return RiskLevel.VERY_HIGH


def calculate_profile_modifiers(profile: ProfileContext) -> tuple[float, dict]:
    """
    Calculate profile-based modifiers that increase risk.
    Returns (total_modifier, breakdown_dict)
    
    Modifiers increase the effective score for higher-risk individuals.
    """
    modifiers = {}
    
    # Insulin resistance modifier: +15-25%
    if profile.has_insulin_resistance:
        ir_mod = 0.15
        if profile.bmi and profile.bmi > 30:
            ir_mod = 0.25
        elif profile.bmi and profile.bmi > 25:
            ir_mod = 0.20
        modifiers['insulin_resistance'] = ir_mod
    
    # Diabetes type modifier
    if profile.diabetes_type == 'type2':
        modifiers['type2_diabetes'] = 0.20
    elif profile.diabetes_type == 'type1':
        modifiers['type1_diabetes'] = 0.10  # Lower modifier, different mechanism
    elif profile.diabetes_type == 'prediabetes':
        modifiers['prediabetes'] = 0.15
    
    # Duration modifier: +5-15% for longer duration
    if profile.diabetes_duration_years:
        if profile.diabetes_duration_years > 10:
            modifiers['diabetes_duration'] = 0.15
        elif profile.diabetes_duration_years > 5:
            modifiers['diabetes_duration'] = 0.10
        elif profile.diabetes_duration_years > 2:
            modifiers['diabetes_duration'] = 0.05
    
    # A1C modifier: +10-20% for higher A1C
    if profile.a1c:
        if profile.a1c > 8.0:
            modifiers['high_a1c'] = 0.20
        elif profile.a1c > 7.0:
            modifiers['elevated_a1c'] = 0.15
        elif profile.a1c > 6.5:
            modifiers['borderline_a1c'] = 0.10
    
    # Activity level modifier (negative = reduces risk)
    if profile.activity_level:
        activity_mods = {
            'very_active': -0.15,
            'active': -0.10,
            'moderate': -0.05,
            'light': 0.0,
            'sedentary': 0.10,
        }
        if profile.activity_level in activity_mods:
            mod = activity_mods[profile.activity_level]
            if mod != 0:
                modifiers['activity_level'] = mod
    
    # Age modifier
    if profile.age:
        if profile.age > 65:
            modifiers['age'] = 0.10
        elif profile.age > 55:
            modifiers['age'] = 0.05
    
    # Medication modifier (some reduce risk)
    if profile.medications:
        meds_lower = [m.lower() for m in profile.medications]
        if any('metformin' in m for m in meds_lower):
            modifiers['metformin'] = -0.10
        if any('ozempic' in m or 'semaglutide' in m or 'wegovy' in m for m in meds_lower):
            modifiers['glp1_agonist'] = -0.15
    
    # Calculate total modifier
    total = sum(modifiers.values())
    
    return total, modifiers


def generate_profile_warnings(profile: ProfileContext, risk_score: float, spike_level: SpikeLevel) -> list[str]:
    """Generate warnings specific to user's health profile"""
    warnings = []
    
    if profile.diabetes_type == 'type1':
        if spike_level in (SpikeLevel.HIGH, SpikeLevel.MODERATE):
            warnings.append("As a Type 1 diabetic, discuss carb counting and insulin dosing with your healthcare provider for this meal.")
    
    if profile.diabetes_type == 'type2':
        if spike_level == SpikeLevel.HIGH:
            warnings.append("This food may cause a significant blood sugar spike. Consider a smaller portion or pairing with protein/fiber.")
        if profile.a1c and profile.a1c > 7.0:
            warnings.append("Given your A1C level, monitoring blood sugar after this meal is recommended.")
    
    if profile.has_insulin_resistance and spike_level == SpikeLevel.HIGH:
        warnings.append("With insulin resistance, high-GL foods can be more challenging. Consider alternatives or portion control.")
    
    if profile.diabetes_type == 'prediabetes':
        if spike_level in (SpikeLevel.HIGH, SpikeLevel.MODERATE):
            warnings.append("To help prevent progression to diabetes, limiting high-GL foods is beneficial.")
    
    return warnings


def generate_profile_tips(profile: ProfileContext, nutrition: NutritionInfo, spike_level: SpikeLevel) -> list[str]:
    """Generate personalized tips based on user profile"""
    tips = []
    
    # Activity-based tips
    if profile.activity_level in ('sedentary', 'light'):
        tips.append("A short walk after eating can help reduce blood sugar spikes by up to 30%.")
    
    # Diabetes-specific tips
    if profile.is_diabetic:
        if spike_level == SpikeLevel.HIGH:
            tips.append("Consider eating vegetables or protein first, then carbs - this can reduce spike by 30-50%.")
        tips.append("Tracking your blood sugar response to this food can help personalize your diet.")
    
    # IR-specific tips
    if profile.has_insulin_resistance:
        tips.append("Apple cider vinegar (1-2 tbsp) before meals may help improve insulin sensitivity.")
        if nutrition.fiber < 5:
            tips.append("Adding a fiber supplement or psyllium husk can help slow glucose absorption.")
    
    # Weight management tips
    if profile.bmi and profile.bmi > 25:
        tips.append("Even a 5-10% weight loss can significantly improve insulin sensitivity.")
    
    # Medication tips
    if profile.medications:
        meds_lower = [m.lower() for m in profile.medications]
        if any('metformin' in m for m in meds_lower):
            tips.append("Taking metformin with meals helps both absorption and blood sugar control.")
    
    return tips[:4]  # Limit to 4 tips


def calculate_risk_score(egl: float, profile: ProfileContext) -> RiskScoreResult:
    """
    Calculate profile-adjusted risk score.
    
    Formula:
    Adjusted Score = eGL × (1 + profile_modifier)
    """
    profile_modifier, modifier_breakdown = calculate_profile_modifiers(profile)
    
    # Apply modifier to eGL
    adjusted_score = egl * (1 + profile_modifier)
    
    # Classify risk level
    risk_level = classify_risk_level(adjusted_score, profile)
    
    # Generate warnings
    spike_level = classify_spike_level(egl)
    warnings = generate_profile_warnings(profile, adjusted_score, spike_level)
    
    return RiskScoreResult(
        base_egl=egl,
        adjusted_score=adjusted_score,
        risk_level=risk_level,
        profile_modifier=profile_modifier,
        modifier_breakdown=modifier_breakdown,
        warnings=warnings,
        personalized_tips=[],  # Filled in later
    )


def generate_recommendations(
    spike_level: SpikeLevel,
    protein: float,
    fat: float,
    fiber: float,
    carbs: float,
    food_name: str,
    profile: Optional[ProfileContext] = None
) -> list[str]:
    """Generate personalized recommendations based on analysis"""
    recommendations = []
    
    # Profile-aware messaging
    if profile and profile.is_diabetic:
        severity_word = "significant" if spike_level == SpikeLevel.HIGH else "notable"
    else:
        severity_word = "high" if spike_level == SpikeLevel.HIGH else "moderate"
    
    if spike_level == SpikeLevel.HIGH:
        recommendations.append(f"This food has a {severity_word} insulin spike potential.")
        
        if protein < 10:
            recommendations.append("Add a protein source (chicken, fish, eggs, tofu) to slow digestion.")
        
        if fiber < 5:
            recommendations.append("Pair with fiber-rich vegetables or salad to reduce the spike.")
        
        if fat < 5:
            recommendations.append("Adding healthy fats (avocado, olive oil, nuts) can help.")
        
        recommendations.append("Consider reducing portion size by 25-50%.")
        
        if not profile or not profile.is_diabetic:
            recommendations.append("A 15-minute walk after eating can help manage blood sugar.")
        
    elif spike_level == SpikeLevel.MODERATE:
        recommendations.append(f"This food has a {severity_word} insulin spike potential.")
        
        if protein < 15:
            recommendations.append("Adding more protein would help reduce the spike.")
        
        if fiber < 5:
            recommendations.append("Adding fiber-rich foods would be beneficial.")
        
        recommendations.append("Safe to eat in moderation as part of a balanced meal.")
        
    else:  # LOW
        recommendations.append("This food has a low insulin spike potential.")
        recommendations.append("Safe to eat freely as part of your healthy diet.")
        
        if protein > 15:
            recommendations.append("Great protein content helps maintain stable blood sugar.")
        
        if fiber > 5:
            recommendations.append("Excellent fiber content for digestive health.")
    
    return recommendations


def generate_explanation(result: 'EGLResult', profile: Optional[ProfileContext] = None) -> str:
    """Generate a clear explanation of the results"""
    
    explanation_parts = []
    
    # Header
    explanation_parts.append(f"**Analysis for {result.food_name.title()}**\n")
    
    # Nutritional breakdown
    explanation_parts.append("**Nutritional Breakdown (per serving):**")
    explanation_parts.append(f"- Carbohydrates: {result.carbs:.1f}g")
    explanation_parts.append(f"- Fiber: {result.fiber:.1f}g (Net Carbs: {result.net_carbs:.1f}g)")
    explanation_parts.append(f"- Protein: {result.protein:.1f}g")
    explanation_parts.append(f"- Fat: {result.fat:.1f}g")
    explanation_parts.append(f"- Glycemic Index: {result.gi:.0f}\n")
    
    # GL Calculation
    explanation_parts.append("**Glycemic Load Calculation:**")
    explanation_parts.append(f"- Base GL: {result.base_gl:.1f} ({result.spike_level_before_modifiers.value.upper()} spike)")
    
    if result.total_modifier > 0:
        explanation_parts.append(f"\n**Macronutrient Modifiers Applied:**")
        if result.fiber_modifier > 0:
            explanation_parts.append(f"- Fiber: -{result.fiber_modifier*100:.0f}% (fiber slows digestion)")
        if result.protein_modifier > 0:
            explanation_parts.append(f"- Protein: -{result.protein_modifier*100:.0f}% (protein slows gastric emptying)")
        if result.fat_modifier > 0:
            explanation_parts.append(f"- Fat: -{result.fat_modifier*100:.0f}% (fat delays absorption)")
        
        explanation_parts.append(f"\n- **Effective GL: {result.effective_gl:.1f}** ({result.spike_level.value.upper()} spike)")
        
        if result.spike_level != result.spike_level_before_modifiers:
            explanation_parts.append(f"- The protein, fat, and fiber in your meal reduced the spike from {result.spike_level_before_modifiers.value.upper()} to {result.spike_level.value.upper()}!")
    else:
        explanation_parts.append(f"- Effective GL: {result.effective_gl:.1f} (no significant modifiers)")
    
    # Profile-based risk score
    if result.risk_score and profile:
        explanation_parts.append(f"\n**Your Personal Risk Score:**")
        explanation_parts.append(f"- Adjusted Score: {result.risk_score.adjusted_score:.1f}")
        explanation_parts.append(f"- Risk Level: {result.risk_score.risk_level.value.upper()}")
        
        if result.risk_score.modifier_breakdown:
            explanation_parts.append(f"\n**Profile Factors:**")
            for factor, mod in result.risk_score.modifier_breakdown.items():
                direction = "+" if mod > 0 else ""
                explanation_parts.append(f"- {factor.replace('_', ' ').title()}: {direction}{mod*100:.0f}%")
        
        if result.risk_score.warnings:
            explanation_parts.append(f"\n**Important:**")
            for warning in result.risk_score.warnings:
                explanation_parts.append(f"- {warning}")
    
    return "\n".join(explanation_parts)


def calculate_egl(nutrition: NutritionInfo, profile: Optional[ProfileContext] = None) -> EGLResult:
    """
    Calculate Effective Glycemic Load with all modifiers.
    
    Formula:
    1. Net Carbs = Total Carbs - Fiber
    2. Base GL = (GI × Net Carbs per serving) / 100
    3. Apply modifiers for fiber, protein, fat
    4. eGL = Base GL × (1 - fiber_mod) × (1 - protein_mod) × (1 - fat_mod)
    5. If profile provided, calculate risk score
    """
    
    # Calculate per-serving values based on portions
    serving_multiplier = nutrition.portions
    carbs = nutrition.carbs * serving_multiplier
    protein = nutrition.protein * serving_multiplier
    fat = nutrition.fat * serving_multiplier
    fiber = nutrition.fiber * serving_multiplier
    
    # Calculate net carbs (subtract fiber from total carbs)
    net_carbs = max(0, carbs - fiber)
    
    # Calculate Base GL
    base_gl = (nutrition.gi * net_carbs) / 100
    
    # Calculate modifiers
    fiber_modifier = calculate_fiber_modifier(fiber)
    protein_modifier = calculate_protein_modifier(protein)
    fat_modifier = calculate_fat_modifier(fat)
    
    # Calculate total modifier effect
    total_modifier = 1 - ((1 - fiber_modifier) * (1 - protein_modifier) * (1 - fat_modifier))
    
    # Calculate Effective GL
    effective_gl = base_gl * (1 - fiber_modifier) * (1 - protein_modifier) * (1 - fat_modifier)
    
    # Classify spike levels
    spike_level_before = classify_spike_level(base_gl)
    spike_level = classify_spike_level(effective_gl)
    
    # Calculate risk score if profile provided
    risk_score = None
    if profile:
        risk_score = calculate_risk_score(effective_gl, profile)
        risk_score.personalized_tips = generate_profile_tips(profile, nutrition, spike_level)
    
    # Generate recommendations
    recommendations = generate_recommendations(
        spike_level, protein, fat, fiber, carbs, nutrition.name, profile
    )
    
    # Add profile-specific recommendations
    if risk_score and risk_score.personalized_tips:
        recommendations.extend([f"💡 {tip}" for tip in risk_score.personalized_tips[:2]])
    
    # Create result
    result = EGLResult(
        food_name=nutrition.name,
        portions=nutrition.portions,
        serving_size=nutrition.serving_size,
        carbs=carbs,
        protein=protein,
        fat=fat,
        fiber=fiber,
        net_carbs=net_carbs,
        gi=nutrition.gi,
        base_gl=base_gl,
        effective_gl=effective_gl,
        fiber_modifier=fiber_modifier,
        protein_modifier=protein_modifier,
        fat_modifier=fat_modifier,
        total_modifier=total_modifier,
        spike_level=spike_level,
        spike_level_before_modifiers=spike_level_before,
        recommendations=recommendations,
        explanation="",
        risk_score=risk_score,
    )
    
    # Generate explanation
    result.explanation = generate_explanation(result, profile)
    
    return result


def calculate_meal_egl(foods: list[NutritionInfo], profile: Optional[ProfileContext] = None) -> EGLResult:
    """
    Calculate combined eGL for a meal with multiple food items.
    Combines all nutrients and calculates overall impact.
    """
    if not foods:
        raise ValueError("No foods provided")
    
    if len(foods) == 1:
        return calculate_egl(foods[0], profile)
    
    # Combine all nutrients
    total_carbs = sum(f.carbs * f.portions for f in foods)
    total_protein = sum(f.protein * f.portions for f in foods)
    total_fat = sum(f.fat * f.portions for f in foods)
    total_fiber = sum(f.fiber * f.portions for f in foods)
    
    # Calculate weighted average GI based on carb contribution
    if total_carbs > 0:
        weighted_gi = sum(
            (f.gi * f.carbs * f.portions) for f in foods
        ) / total_carbs
    else:
        weighted_gi = 0
    
    # Create combined nutrition info
    meal_name = " + ".join([f.name.title() for f in foods])
    combined = NutritionInfo(
        name=meal_name,
        gi=weighted_gi,
        carbs=total_carbs,
        protein=total_protein,
        fat=total_fat,
        fiber=total_fiber,
        serving_size=sum(f.serving_size * f.portions for f in foods),
        portions=1.0
    )
    
    return calculate_egl(combined, profile)
