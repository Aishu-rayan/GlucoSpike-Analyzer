import { ChatResponse, EGLResult } from './types';

const API_BASE = '/api';

export async function analyzeImage(file: File, message: string = 'Analyze this food'): Promise<ChatResponse> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('message', message);

  const response = await fetch(`${API_BASE}/analyze/image`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to analyze image');
  }

  return response.json();
}

export async function analyzeFood(foodName: string, portions: number = 1): Promise<EGLResult> {
  const response = await fetch(`${API_BASE}/analyze/food`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ food_name: foodName, portions }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to analyze food');
  }

  return response.json();
}

export async function chat(message: string): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to send message');
  }

  return response.json();
}

export async function searchFoods(query: string): Promise<{ results: Array<{ name: string }> }> {
  const response = await fetch(`${API_BASE}/foods/search?q=${encodeURIComponent(query)}`);
  
  if (!response.ok) {
    throw new Error('Failed to search foods');
  }

  return response.json();
}

export async function healthCheck(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE.replace('/api', '')}/health`);
    return response.ok;
  } catch {
    return false;
  }
}

