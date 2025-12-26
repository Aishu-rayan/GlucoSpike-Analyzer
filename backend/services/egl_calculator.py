"""
Effective Glycemic Load (eGL) Calculator

Calculates the effective insulin spike potential considering:
- Base Glycemic Load (GL)
- Fiber content (reduces net carbs)
- Protein content (slows gastric emptying)
- Fat content (delays carbohydrate absorption)
"""

from dataclasses import dataclass
from enum import Enum


class SpikeLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


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


def generate_recommendations(
    spike_level: SpikeLevel,
    protein: float,
    fat: float,
    fiber: float,
    carbs: float,
    food_name: str
) -> list[str]:
    """Generate personalized recommendations based on analysis"""
    recommendations = []
    
    if spike_level == SpikeLevel.HIGH:
        recommendations.append("⚠️ This food has a high insulin spike potential.")
        
        if protein < 10:
            recommendations.append("💪 Add a protein source (chicken, fish, eggs, tofu) to slow digestion.")
        
        if fiber < 5:
            recommendations.append("🥗 Pair with fiber-rich vegetables or salad to reduce the spike.")
        
        if fat < 5:
            recommendations.append("🥑 Adding healthy fats (avocado, olive oil, nuts) can help.")
        
        recommendations.append("📏 Consider reducing portion size by 25-50%.")
        recommendations.append("🚶 A 15-minute walk after eating can help manage blood sugar.")
        
    elif spike_level == SpikeLevel.MODERATE:
        recommendations.append("⚡ This food has a moderate insulin spike potential.")
        
        if protein < 15:
            recommendations.append("💪 Adding more protein would help reduce the spike.")
        
        if fiber < 5:
            recommendations.append("🥗 Adding fiber-rich foods would be beneficial.")
        
        recommendations.append("✅ Safe to eat in moderation as part of a balanced meal.")
        
    else:  # LOW
        recommendations.append("✅ This food has a low insulin spike potential.")
        recommendations.append("👍 Safe to eat freely as part of your healthy diet.")
        
        if protein > 15:
            recommendations.append("💪 Great protein content helps maintain stable blood sugar.")
        
        if fiber > 5:
            recommendations.append("🌿 Excellent fiber content for digestive health.")
    
    return recommendations


def generate_explanation(result: 'EGLResult') -> str:
    """Generate a clear explanation of the results"""
    
    explanation_parts = []
    
    # Header
    explanation_parts.append(f"📊 **Analysis for {result.food_name.title()}**\n")
    
    # Nutritional breakdown
    explanation_parts.append("**Nutritional Breakdown (per serving):**")
    explanation_parts.append(f"• Carbohydrates: {result.carbs:.1f}g")
    explanation_parts.append(f"• Fiber: {result.fiber:.1f}g (Net Carbs: {result.net_carbs:.1f}g)")
    explanation_parts.append(f"• Protein: {result.protein:.1f}g")
    explanation_parts.append(f"• Fat: {result.fat:.1f}g")
    explanation_parts.append(f"• Glycemic Index: {result.gi:.0f}\n")
    
    # GL Calculation
    explanation_parts.append("**Glycemic Load Calculation:**")
    explanation_parts.append(f"• Base GL: {result.base_gl:.1f} ({result.spike_level_before_modifiers.value.upper()} spike)")
    
    if result.total_modifier > 0:
        explanation_parts.append(f"\n**Macronutrient Modifiers Applied:**")
        if result.fiber_modifier > 0:
            explanation_parts.append(f"• Fiber: -{result.fiber_modifier*100:.0f}% (fiber slows digestion)")
        if result.protein_modifier > 0:
            explanation_parts.append(f"• Protein: -{result.protein_modifier*100:.0f}% (protein slows gastric emptying)")
        if result.fat_modifier > 0:
            explanation_parts.append(f"• Fat: -{result.fat_modifier*100:.0f}% (fat delays absorption)")
        
        explanation_parts.append(f"\n• **Effective GL: {result.effective_gl:.1f}** ({result.spike_level.value.upper()} spike)")
        
        if result.spike_level != result.spike_level_before_modifiers:
            explanation_parts.append(f"• ✨ The protein, fat, and fiber in your meal reduced the spike from {result.spike_level_before_modifiers.value.upper()} to {result.spike_level.value.upper()}!")
    else:
        explanation_parts.append(f"• Effective GL: {result.effective_gl:.1f} (no significant modifiers)")
    
    return "\n".join(explanation_parts)


def calculate_egl(nutrition: NutritionInfo) -> EGLResult:
    """
    Calculate Effective Glycemic Load with all modifiers.
    
    Formula:
    1. Net Carbs = Total Carbs - Fiber
    2. Base GL = (GI × Net Carbs per serving) / 100
    3. Apply modifiers for fiber, protein, fat
    4. eGL = Base GL × (1 - fiber_mod) × (1 - protein_mod) × (1 - fat_mod)
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
    
    # Generate recommendations
    recommendations = generate_recommendations(
        spike_level, protein, fat, fiber, carbs, nutrition.name
    )
    
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
        explanation=""
    )
    
    # Generate explanation
    result.explanation = generate_explanation(result)
    
    return result


def calculate_meal_egl(foods: list[NutritionInfo]) -> EGLResult:
    """
    Calculate combined eGL for a meal with multiple food items.
    Combines all nutrients and calculates overall impact.
    """
    if not foods:
        raise ValueError("No foods provided")
    
    if len(foods) == 1:
        return calculate_egl(foods[0])
    
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
    
    return calculate_egl(combined)

