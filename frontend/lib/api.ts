import { getAccessToken, saveTokens, saveUser } from './auth'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001/api'

export interface ApiError {
  message: string
  code: string
  status: number
}

/**
 * Fetch with Bearer JWT authentication
 */
async function authenticatedFetch(
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> {
  const token = getAccessToken()
  const headers = new Headers(options.headers || {})

  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }

  headers.set('Content-Type', 'application/json')

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  })

  return response
}

/**
 * Handle API response and throw errors appropriately
 */
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw {
      message: error.message || 'An error occurred',
      code: error.code || 'UNKNOWN_ERROR',
      status: response.status,
    } as ApiError
  }

  return response.json()
}

// AUTH ENDPOINTS

export interface AuthResponse {
  access_token: string
}

export interface CurrentUser {
  id: string
  email: string
  created_at: string
}

/**
 * Register a new user
 * POST /auth/register
 */
export async function registerUser(email: string, password: string): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })

  const data = await handleResponse<AuthResponse>(response)
  saveTokens(data.access_token)
  return data
}

/**
 * Login user
 * POST /auth/login
 */
export async function loginUser(email: string, password: string): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })

  const data = await handleResponse<AuthResponse>(response)
  saveTokens(data.access_token)
  return data
}

/**
 * Get current authenticated user
 * GET /auth/me
 */
export async function getCurrentUser(): Promise<CurrentUser> {
  const response = await authenticatedFetch('/auth/me')
  return handleResponse<CurrentUser>(response)
}

// SESSIONS ENDPOINTS

export interface ChatSession {
  id: string
  title: string
  created_at: string
}

/**
 * Create a new chat session
 * POST /sessions
 */
export async function createChatSession(title: string): Promise<ChatSession> {
  const response = await authenticatedFetch('/sessions', {
    method: 'POST',
    body: JSON.stringify({ title }),
  })

  return handleResponse<ChatSession>(response)
}

/**
 * Get all chat sessions for current user
 * GET /sessions
 */
export async function getChatSessions(): Promise<ChatSession[]> {
  const response = await authenticatedFetch('/sessions')
  return handleResponse<ChatSession[]>(response)
}

/**
 * Delete a chat session
 * DELETE /sessions/{id}
 */
export async function deleteChatSession(sessionId: string): Promise<void> {
  const response = await authenticatedFetch(`/sessions/${sessionId}`, {
    method: 'DELETE',
  })

  // 204 No Content response
  if (response.status !== 204 && !response.ok) {
    const error = await response.json().catch(() => ({}))
    throw {
      message: error.message || 'Failed to delete session',
      code: error.code || 'DELETE_FAILED',
      status: response.status,
    } as ApiError
  }
}

// RAG QUERY ENDPOINT

export interface RagSource {
  text: string
  document_name: string
  score: number
}

export interface RagResponse {
  answer: string
  sources: RagSource[]
}

/**
 * Query the legal database with RAG
 * POST /rag/query
 */
export async function queryLegalDatabase(
  question: string,
  session_id: string
): Promise<RagResponse> {
  const response = await authenticatedFetch('/rag/query', {
    method: 'POST',
    body: JSON.stringify({ question, session_id }),
  })

  return handleResponse<RagResponse>(response)
}
