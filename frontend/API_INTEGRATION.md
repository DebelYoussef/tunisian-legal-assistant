# API Integration Guide

This guide explains how to connect the frontend to your backend API.

## Quick Start

1. Set your API base URL:

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:3001/api
# or for production
NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api
```

2. Implement all endpoints in `lib/api.ts` (function signatures provided)

3. Test with the login page

## API Endpoints Required

All endpoints require these headers:
```
Content-Type: application/json
Authorization: Bearer {accessToken}  # Except auth/register and auth/login
```

### Authentication Endpoints

#### POST /auth/register
Create a new user account.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "Jean Dupont"
}
```

**Response (200)**:
```json
{
  "user": {
    "id": "uuid-here",
    "email": "user@example.com",
    "name": "Jean Dupont",
    "createdAt": "2024-01-15T10:30:00Z"
  },
  "token": {
    "accessToken": "eyJhbGciOiJIUzI1NiIs...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIs...",
    "expiresAt": 1705329000000,
    "userId": "uuid-here"
  }
}
```

**Errors**:
- 400: Email already exists, password too weak
- 422: Validation error

---

#### POST /auth/login
Authenticate user and get tokens.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response (200)**:
```json
{
  "user": { ... },  // Same as register
  "token": { ... }  // Same as register
}
```

**Errors**:
- 401: Invalid email/password
- 429: Too many login attempts

---

#### POST /auth/refresh
Refresh expired access token.

**Headers**: `Authorization: Bearer {refreshToken}`

**Response (200)**:
```json
{
  "token": {
    "accessToken": "new-token-here",
    "refreshToken": "new-refresh-token",
    "expiresAt": 1705329000000,
    "userId": "uuid-here"
  }
}
```

**Errors**:
- 401: Invalid/expired refresh token

---

### Chat Session Endpoints

#### POST /chat/sessions
Create a new chat session.

**Request**:
```json
{
  "title": "Questions sur le contrat de travail"
}
```

**Response (201)**:
```json
{
  "id": "session-uuid",
  "title": "Questions sur le contrat de travail",
  "createdAt": "2024-01-15T10:30:00Z",
  "updatedAt": "2024-01-15T10:30:00Z",
  "messageCount": 0
}
```

---

#### GET /chat/sessions
Get all sessions for current user.

**Query Params**: None (pagination optional)

**Response (200)**:
```json
[
  {
    "id": "session-1",
    "title": "Contrats de travail",
    "createdAt": "2024-01-15T10:30:00Z",
    "updatedAt": "2024-01-15T10:30:00Z",
    "messageCount": 5
  },
  {
    "id": "session-2",
    "title": "Droit immobilier",
    "createdAt": "2024-01-14T15:20:00Z",
    "updatedAt": "2024-01-14T15:20:00Z",
    "messageCount": 3
  }
]
```

**Sorting**: Most recent first

---

#### DELETE /chat/sessions/{sessionId}
Delete a chat session.

**Response (204)**: No content (success)

**Errors**:
- 404: Session not found
- 403: Not session owner

---

### Message Endpoints

#### POST /chat/sessions/{sessionId}/message
Send a message and get response.

**Request**:
```json
{
  "content": "Quels sont mes droits en cas de licenciement?"
}
```

**Response (200)**:
```json
{
  "id": "msg-uuid",
  "sessionId": "session-uuid",
  "role": "assistant",
  "content": "En droit tunisien, l'employeur doit respecter certaines conditions...",
  "sources": [
    {
      "title": "Code du travail tunisien",
      "url": "https://example.com/code-travail",
      "excerpt": "Article 45: Des conditions de licenciement...",
      "relevanceScore": 0.92
    },
    {
      "title": "Loi n° 2004-20",
      "url": "https://example.com/loi-2004",
      "excerpt": "Modifiant le code du travail...",
      "relevanceScore": 0.85
    }
  ],
  "createdAt": "2024-01-15T10:35:00Z"
}
```

**Implementation Notes**:
- Call RAG/LLM system with message
- Extract relevant law sources
- Return assistant response
- Include up to 3-5 sources with relevance scores

---

#### GET /chat/sessions/{sessionId}/messages
Get all messages for a session.

**Response (200)**:
```json
[
  {
    "id": "msg-1",
    "sessionId": "session-uuid",
    "role": "user",
    "content": "Quels sont mes droits du travail?",
    "createdAt": "2024-01-15T10:30:00Z"
  },
  {
    "id": "msg-2",
    "sessionId": "session-uuid",
    "role": "assistant",
    "content": "Selon le code tunisien...",
    "sources": [ ... ],
    "createdAt": "2024-01-15T10:31:00Z"
  }
]
```

**Pagination**: Optional limit/offset params

---

### RAG Endpoints (Optional Direct Access)

#### POST /rag/query
Query legal database directly (for advanced use).

**Request**:
```json
{
  "query": "Droits du travail en Tunisie",
  "context": "Optional conversation context"
}
```

**Response (200)**:
```json
{
  "response": "Generated answer",
  "sources": [ ... ],
  "confidence": 0.85
}
```

---

#### GET /rag/search?q={query}
Search law sources.

**Query Params**:
- `q`: Search query (required)
- `limit`: Max results (default: 10)

**Response (200)**:
```json
[
  {
    "title": "Code du travail",
    "url": "...",
    "excerpt": "...",
    "relevanceScore": 0.92
  }
]
```

---

## Error Response Format

All errors follow this format:

```json
{
  "message": "Human-readable error message",
  "code": "ERROR_CODE",
  "status": 400
}
```

**Common Codes**:
- `INVALID_CREDENTIALS`: Login failed
- `INVALID_TOKEN`: Auth token invalid/expired
- `NOT_FOUND`: Resource not found
- `UNAUTHORIZED`: Missing auth
- `VALIDATION_ERROR`: Request validation failed
- `INTERNAL_ERROR`: Server error

**Example Error Response (400)**:
```json
{
  "message": "Email already registered",
  "code": "EMAIL_EXISTS",
  "status": 400
}
```

---

## Implementation Checklist

- [ ] Set `NEXT_PUBLIC_API_URL` in `.env.local`
- [ ] Implement POST /auth/register
- [ ] Implement POST /auth/login
- [ ] Implement POST /auth/refresh
- [ ] Implement POST /chat/sessions
- [ ] Implement GET /chat/sessions
- [ ] Implement DELETE /chat/sessions/{id}
- [ ] Implement POST /chat/sessions/{id}/message
- [ ] Implement GET /chat/sessions/{id}/messages
- [ ] Test login flow
- [ ] Test message sending
- [ ] Test session management

---

## Testing with cURL

Test endpoints directly:

```bash
# Register
curl -X POST http://localhost:3001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "name": "Test User"
  }'

# Login
curl -X POST http://localhost:3001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'

# Create session (use token from login)
curl -X POST http://localhost:3001/api/chat/sessions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{ "title": "Test Chat" }'
```

---

## Frontend Integration Example

```typescript
// app/chat/page.tsx
import { getChatSessions, createChatSession } from '@/lib/api'
import { useEffect, useState } from 'react'

export default function ChatPage() {
  const [sessions, setSessions] = useState([])

  useEffect(() => {
    // Load sessions on mount
    getChatSessions()
      .then(setSessions)
      .catch(err => console.error('Failed to load sessions:', err))
  }, [])

  const handleNewChat = async () => {
    try {
      const session = await createChatSession('New Chat')
      setSessions(prev => [session, ...prev])
    } catch (error) {
      console.error('Failed to create chat:', error)
    }
  }

  return (
    // Your UI here
    <button onClick={handleNewChat}>New Chat</button>
  )
}
```

---

## Environment Variables

Required for the app:

```bash
# .env.local

# API URL (required)
NEXT_PUBLIC_API_URL=http://localhost:3001/api

# Optional: Feature flags
NEXT_PUBLIC_DEMO_MODE=false
NEXT_PUBLIC_VERSION=1.0.0
```

---

## Security Best Practices

1. **HTTPS Only**: Always use HTTPS in production
2. **Token Storage**: Consider httpOnly cookies instead of localStorage
3. **CORS**: Configure proper CORS headers on backend
4. **Rate Limiting**: Implement rate limiting on auth endpoints
5. **Input Validation**: Validate all inputs on backend
6. **SQL Injection**: Use parameterized queries
7. **Token Expiry**: Keep access tokens short-lived (15-30 minutes)
8. **Refresh Tokens**: Use httpOnly, secure cookies for refresh tokens

---

## Monitoring & Logging

Add error tracking:

```typescript
// lib/api.ts - Add error logging

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    
    // Log to error tracking service
    if (process.env.NODE_ENV === 'production') {
      // Sentry, LogRocket, etc.
      captureException({
        message: error.message,
        status: response.status,
        endpoint: response.url,
      })
    }
    
    throw error
  }
  
  return response.json()
}
```

---

## Troubleshooting

**Q: "Failed to fetch" error**
A: Check CORS headers on backend and API URL in .env.local

**Q: Token expired errors**
A: Implement refresh token logic in handleResponse()

**Q: Login works but sessions fail to load**
A: Verify token is being sent in Authorization header

**Q: 401 errors on authenticated requests**
A: Check token format is "Bearer {token}"

---

For questions or issues, check the main guide: `FULL_PROJECT_GUIDE.md`
