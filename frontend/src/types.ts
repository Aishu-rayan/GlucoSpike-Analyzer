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
  attachments?: Attachment[];
}

// Auth types
export interface User {
  id: number;
  username: string;
  created_at: string;
  has_profile: boolean;
  onboarding_completed: boolean;
}

export interface AuthResponse {
  message: string;
  user: User | null;
}

// Chat history types
export interface ChatSummary {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  last_message_preview: string | null;
}

export interface Attachment {
  id: number;
  type: string;
  file_path: string;
  original_filename: string | null;
  mime_type: string | null;
}

export interface ChatMessage {
  id: number;
  role: string;
  content: string;
  created_at: string;
  attachments: Attachment[];
  egl_result_json: string | null;
  food_analysis_json: string | null;
}

export interface ChatWithMessages {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
  messages: ChatMessage[];
}

// Profile types
export interface Profile {
  id: number;
  user_id: number;
  display_name: string | null;
  age: number | null;
  sex: string | null;
  height_cm: number | null;
  weight_kg: number | null;
  bmi: number | null;
  activity_level: string | null;
  goals: string | null;
  has_insulin_resistance: boolean;
  diabetes_type: string | null;
  diabetes_duration_years: number | null;
  a1c: number | null;
  fasting_glucose: number | null;
  medications: string[] | null;
  conditions: Record<string, any> | null;
  dietary_preferences: string | null;
  allergies: string[] | null;
  onboarding_completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface OnboardingData {
  display_name?: string;
  health_status: 'healthy' | 'insulin_resistance' | 'type1' | 'type2' | 'prediabetes';
  age?: number;
  sex?: 'male' | 'female' | 'other';
  goals: string;
  activity_level: string;
}
