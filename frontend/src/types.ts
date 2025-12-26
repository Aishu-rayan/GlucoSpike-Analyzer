// API Response Types

export type SpikeLevel = 'low' | 'moderate' | 'high';

export interface FoodItem {
  name: string;
  estimated_grams: number;
  portions: number;
  confidence: string;
  found_in_database: boolean;
  database_match: string | null;
  gi?: number;
  carbs_per_100g?: number;
  protein_per_100g?: number;
  fat_per_100g?: number;
  fiber_per_100g?: number;
}

export interface NutritionBreakdown {
  carbs: number;
  protein: number;
  fat: number;
  fiber: number;
  net_carbs: number;
}

export interface EGLResult {
  food_name: string;
  portions: number;
  serving_size: number;
  nutrition: NutritionBreakdown;
  gi: number;
  base_gl: number;
  effective_gl: number;
  fiber_modifier: number;
  protein_modifier: number;
  fat_modifier: number;
  total_reduction_percent: number;
  spike_level: SpikeLevel;
  spike_level_before_modifiers: SpikeLevel;
  spike_improved: boolean;
  recommendations: string[];
  explanation: string;
}

export interface FoodAnalysis {
  foods: FoodItem[];
  meal_description: string;
  is_healthy_meal: boolean;
  health_notes: string;
  error?: string;
}

export interface ChatResponse {
  response: string;
  food_analysis: FoodAnalysis | null;
  egl_result: EGLResult | null;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  image?: string;
  foodAnalysis?: FoodAnalysis;
  eglResult?: EGLResult;
  timestamp: Date;
}

