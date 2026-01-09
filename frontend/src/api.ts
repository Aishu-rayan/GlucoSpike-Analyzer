import { 
  ChatResponse, 
  EGLResult, 
  AuthResponse, 
  User, 
  ChatSummary, 
  ChatWithMessages, 
  ChatMessage,
  Profile,
  OnboardingData
} from './types';

const API_BASE = '/api';

// Helper for fetch with credentials (cookies)
async function fetchWithAuth(url: string, options: RequestInit = {}): Promise<Response> {
  return fetch(url, {
    ...options,
    credentials: 'include',
  });
}

// ============================================================================
// Auth API
// ============================================================================

export async function register(username: string, password: string): Promise<AuthResponse> {
  const response = await fetchWithAuth(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Registration failed');
  }

  return response.json();
}

export async function login(username: string, password: string): Promise<AuthResponse> {
  const response = await fetchWithAuth(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Login failed');
  }

  return response.json();
}

export async function logout(): Promise<void> {
  await fetchWithAuth(`${API_BASE}/auth/logout`, { method: 'POST' });
}

export async function getCurrentUser(): Promise<User | null> {
  try {
    const response = await fetchWithAuth(`${API_BASE}/auth/me`);
    if (!response.ok) return null;
    return response.json();
  } catch {
    return null;
  }
}

export async function checkAuth(): Promise<{ authenticated: boolean; user_id: number | null; username: string | null }> {
  try {
    const response = await fetchWithAuth(`${API_BASE}/auth/check`);
    return response.json();
  } catch {
    return { authenticated: false, user_id: null, username: null };
  }
}

// ============================================================================
// Chat History API
// ============================================================================

export async function listChats(search?: string): Promise<ChatSummary[]> {
  const url = search 
    ? `${API_BASE}/chats?search=${encodeURIComponent(search)}`
    : `${API_BASE}/chats`;
  
  const response = await fetchWithAuth(url);
  
  if (!response.ok) {
    throw new Error('Failed to load chats');
  }

  return response.json();
}

export async function createChat(title: string = 'New Chat'): Promise<ChatSummary> {
  const response = await fetchWithAuth(`${API_BASE}/chats`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title }),
  });

  if (!response.ok) {
    throw new Error('Failed to create chat');
  }

  return response.json();
}

export async function getChat(chatId: number): Promise<ChatWithMessages> {
  const response = await fetchWithAuth(`${API_BASE}/chats/${chatId}`);
  
  if (!response.ok) {
    throw new Error('Failed to load chat');
  }

  return response.json();
}

export async function updateChat(chatId: number, title: string): Promise<ChatSummary> {
  const response = await fetchWithAuth(`${API_BASE}/chats/${chatId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title }),
  });

  if (!response.ok) {
    throw new Error('Failed to update chat');
  }

  return response.json();
}

export async function deleteChat(chatId: number): Promise<void> {
  const response = await fetchWithAuth(`${API_BASE}/chats/${chatId}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    throw new Error('Failed to delete chat');
  }
}

export async function addMessage(
  chatId: number, 
  role: 'user' | 'assistant', 
  content: string,
  eglResultJson?: string,
  foodAnalysisJson?: string
): Promise<ChatMessage> {
  const response = await fetchWithAuth(`${API_BASE}/chats/${chatId}/messages`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      role, 
      content,
      egl_result_json: eglResultJson,
      food_analysis_json: foodAnalysisJson,
    }),
  });

  if (!response.ok) {
    throw new Error('Failed to add message');
  }

  return response.json();
}

export async function uploadImage(chatId: number, file: File, message: string = 'Analyze this food'): Promise<ChatMessage> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('message_content', message);

  const response = await fetchWithAuth(`${API_BASE}/chats/${chatId}/image`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error('Failed to upload image');
  }

  return response.json();
}

// ============================================================================
// Profile API
// ============================================================================

export async function getProfile(): Promise<Profile> {
  const response = await fetchWithAuth(`${API_BASE}/profile`);
  
  if (!response.ok) {
    throw new Error('Failed to load profile');
  }

  return response.json();
}

export async function updateProfile(data: Partial<Profile>): Promise<Profile> {
  const response = await fetchWithAuth(`${API_BASE}/profile`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error('Failed to update profile');
  }

  return response.json();
}

export async function completeOnboarding(data: OnboardingData): Promise<Profile> {
  const response = await fetchWithAuth(`${API_BASE}/profile/onboarding`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error('Failed to complete onboarding');
  }

  return response.json();
}

// ============================================================================
// Food Analysis API (existing, updated with credentials)
// ============================================================================

export async function analyzeImage(file: File, message: string = 'Analyze this food'): Promise<ChatResponse> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('message', message);

  const response = await fetchWithAuth(`${API_BASE}/analyze/image`, {
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
  const response = await fetchWithAuth(`${API_BASE}/analyze/food`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ food_name: foodName, portions }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to analyze food');
  }

  return response.json();
}

export async function chat(message: string): Promise<ChatResponse> {
  const response = await fetchWithAuth(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
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
    const response = await fetch(`${API_BASE}/health`);
    return response.ok;
  } catch {
    return false;
  }
}

// ============================================================================
// Image URL helper
// ============================================================================

export function getImageUrl(filePath: string): string {
  return `${API_BASE}/chats/uploads/${filePath}`;
}
