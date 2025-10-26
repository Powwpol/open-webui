# Pulsai API Reference

Complete API documentation for all Pulsai endpoints.

**Base URL:** `http://localhost:8080/api/v1`

**Authentication:** Bearer token in `Authorization` header

---

## Table of Contents

- [Authentication](#authentication)
- [Inference API](#inference-api)
- [MCP API](#mcp-api)
- [Webhooks API](#webhooks-api)
- [Chat API](#chat-api)
- [Models API](#models-api)
- [Users API](#users-api)

---

## Authentication

All API requests require authentication via Bearer token:

```bash
Authorization: Bearer YOUR_TOKEN_HERE
```

### Get Token

```http
POST /api/v1/auths/signin
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your-password"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": "user_123",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

---

## Inference API

Unified inference across Ollama, vLLM, and external providers.

### Generate Completion

```http
POST /api/v1/inference/generate
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "model": "llama2",
  "messages": [
    {"role": "user", "content": "Hello!"}
  ],
  "temperature": 0.7,
  "max_tokens": 512,
  "backend": "ollama"
}
```

**Response:**
```json
{
  "model": "llama2",
  "content": "Hello! How can I help you today?",
  "finish_reason": "stop",
  "backend": "ollama",
  "latency_ms": 1245.3,
  "usage": {
    "prompt_tokens": 5,
    "completion_tokens": 8,
    "total_tokens": 13
  }
}
```

### Stream Completion

```http
POST /api/v1/inference/generate/stream
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "model": "llama2",
  "prompt": "Write a poem about AI",
  "stream": true,
  "backend": "vllm"
}
```

**Response:** Server-Sent Events (SSE)
```
data: In
data:  circuits
data:  deep
...
data: [DONE]
```

### List Models

```http
GET /api/v1/inference/models
Authorization: Bearer TOKEN
```

**Response:**
```json
{
  "ollama": [
    {
      "id": "llama2",
      "name": "llama2",
      "backend": "ollama",
      "capabilities": ["chat", "completion"]
    }
  ],
  "vllm": [
    {
      "id": "meta-llama/Llama-2-7b-chat-hf",
      "name": "meta-llama/Llama-2-7b-chat-hf",
      "backend": "vllm",
      "context_window": 4096,
      "capabilities": ["chat", "completion"]
    }
  ]
}
```

### Backend Status

```http
GET /api/v1/inference/backends/status
Authorization: Bearer TOKEN
```

**Response:**
```json
{
  "ollama": {
    "healthy": true,
    "latency_ms": 45.2,
    "models_count": 5,
    "request_count": 123,
    "status": "healthy"
  },
  "vllm": {
    "healthy": true,
    "latency_ms": 32.1,
    "models_count": 2,
    "request_count": 87,
    "status": "healthy"
  }
}
```

### Backend Health

```http
GET /api/v1/inference/backends/health
Authorization: Bearer TOKEN
```

**Response:**
```json
{
  "ollama": {
    "current_status": "healthy",
    "uptime_24h": 99.5,
    "avg_latency_ms": 45.2,
    "checks_count": 2880
  },
  "vllm": {
    "current_status": "healthy",
    "uptime_24h": 99.8,
    "avg_latency_ms": 32.1,
    "checks_count": 2880
  }
}
```

---

## MCP API

Manage Model Context Protocol servers and tools.

### List MCP Servers

```http
GET /api/v1/mcp/servers
Authorization: Bearer TOKEN
```

**Response:**
```json
[
  {
    "id": "pulsai-stdio-mcp",
    "name": "Pulsai Local MCP",
    "protocol": "stdio",
    "enabled": true,
    "config": {
      "command": ["python", "mcp-server/pulsai_mcp/server.py"]
    }
  }
]
```

### Add MCP Server

```http
POST /api/v1/mcp/servers
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "id": "custom-mcp",
  "name": "Custom MCP Server",
  "protocol": "http",
  "enabled": true,
  "config": {
    "url": "http://localhost:8100"
  }
}
```

### Get MCP Tools

```http
GET /api/v1/mcp/servers/{server_id}/tools
Authorization: Bearer TOKEN
```

**Response:**
```json
[
  {
    "name": "recursive_chat",
    "description": "Initiates a recursive chat",
    "parameters": [
      {
        "name": "prompt",
        "type": "string",
        "description": "Initial prompt",
        "required": true
      }
    ]
  }
]
```

### Get MCP Models

```http
GET /api/v1/mcp/servers/{server_id}/models
Authorization: Bearer TOKEN
```

### Send MCP Message

```http
POST /api/v1/mcp/servers/{server_id}/message
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "type": "tool_code",
  "payload": {
    "name": "recursive_chat",
    "parameters": {
      "prompt": "Hello world"
    }
  }
}
```

---

## Webhooks API

Event-driven webhooks for n8n and external integrations.

### List Webhooks

```http
GET /api/v1/webhooks?enabled_only=true
Authorization: Bearer TOKEN
```

**Response:**
```json
[
  {
    "id": "webhook_123",
    "name": "n8n Chat Events",
    "url": "http://n8n:5678/webhook/pulsai",
    "enabled": true,
    "event_filter": {
      "event_types": ["chat.created", "chat.completed"]
    },
    "max_retries": 3,
    "timeout": 30,
    "total_deliveries": 145,
    "successful_deliveries": 142,
    "failed_deliveries": 3
  }
]
```

### Create Webhook

```http
POST /api/v1/webhooks
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "name": "My Webhook",
  "url": "https://your-endpoint.com/webhook",
  "event_types": ["chat.created", "chat.completed"],
  "max_retries": 3,
  "timeout": 30,
  "custom_headers": {
    "X-Custom-Header": "value"
  }
}
```

**Response:**
```json
{
  "id": "webhook_abc123",
  "name": "My Webhook",
  "url": "https://your-endpoint.com/webhook",
  "secret": "whsec_d4e5f6g7h8i9...",
  "enabled": true,
  "created_at": "2025-10-19T18:30:00Z"
}
```

### Update Webhook

```http
PATCH /api/v1/webhooks/{webhook_id}
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "enabled": false,
  "event_types": ["chat.created"]
}
```

### Delete Webhook

```http
DELETE /api/v1/webhooks/{webhook_id}
Authorization: Bearer TOKEN
```

### Test Webhook

```http
POST /api/v1/webhooks/test
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "url": "https://your-endpoint.com/webhook",
  "event_type": "custom",
  "test_data": {
    "message": "Test payload"
  }
}
```

**Response:**
```json
{
  "success": true,
  "status_code": 200,
  "latency_ms": 245.6
}
```

### Get Statistics

```http
GET /api/v1/webhooks/statistics/overview
Authorization: Bearer TOKEN
```

**Response:**
```json
{
  "total_subscriptions": 5,
  "enabled_subscriptions": 4,
  "total_deliveries": 1234,
  "successful_deliveries": 1180,
  "failed_deliveries": 54,
  "success_rate": 95.62
}
```

### List Event Types

```http
GET /api/v1/webhooks/events/types
Authorization: Bearer TOKEN
```

**Response:**
```json
{
  "event_types": [
    {
      "type": "chat.created",
      "description": "Chat Created"
    },
    {
      "type": "chat.completed",
      "description": "Chat Completed"
    }
  ]
}
```

---

## Chat API

Manage conversations and messages.

### Create Chat

```http
POST /api/v1/chats/new
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "chat": {
    "name": "New Conversation",
    "models": ["llama2"]
  }
}
```

### Get Chat

```http
GET /api/v1/chats/{chat_id}
Authorization: Bearer TOKEN
```

### List Chats

```http
GET /api/v1/chats
Authorization: Bearer TOKEN
```

### Update Chat

```http
POST /api/v1/chats/{chat_id}
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "chat": {
    "title": "Updated Title"
  }
}
```

### Delete Chat

```http
DELETE /api/v1/chats/{chat_id}
Authorization: Bearer TOKEN
```

### Archive Chat

```http
GET /api/v1/chats/{chat_id}/archive
Authorization: Bearer TOKEN
```

---

## Models API

Manage available models across backends.

### List Models

```http
GET /api/v1/models
Authorization: Bearer TOKEN
```

### Add Model

```http
POST /api/v1/models/add
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "name": "llama2:latest"
}
```

### Remove Model

```http
DELETE /api/v1/models/delete
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "name": "llama2:latest"
}
```

### Pull Model (Ollama)

```http
POST /api/v1/ollama/pull
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "name": "llama2:latest",
  "stream": false
}
```

---

## Users API

User management and authentication.

### Get Current User

```http
GET /api/v1/users/me
Authorization: Bearer TOKEN
```

### Update User

```http
POST /api/v1/users/update
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "name": "New Name",
  "profile_image_url": "https://..."
}
```

### Change Password

```http
POST /api/v1/users/update/password
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "password": "current_password",
  "new_password": "new_password"
}
```

---

## Error Responses

All endpoints may return error responses:

### 400 Bad Request

```json
{
  "detail": "Invalid request parameters"
}
```

### 401 Unauthorized

```json
{
  "detail": "Invalid authentication credentials"
}
```

### 404 Not Found

```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Internal server error occurred"
}
```

---

## Rate Limiting

API requests are rate-limited:

- **Default**: 100 requests per minute per user
- **Burst**: 50 concurrent requests

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1697734800
```

---

## Pagination

List endpoints support pagination:

```http
GET /api/v1/chats?page=1&limit=20
```

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 50, max: 100)

**Response:**
```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "pages": 8
}
```

---

## WebSocket API

Real-time events via WebSocket.

**Connection:**
```
ws://localhost:8080/ws
```

**Authentication:**
```json
{
  "type": "auth",
  "token": "YOUR_TOKEN"
}
```

**Events:**
```json
{
  "type": "chat.message",
  "data": {
    "chat_id": "chat_123",
    "message": {...}
  }
}
```

---

## SDK Examples

### Python

```python
import requests

BASE_URL = "http://localhost:8080/api/v1"
TOKEN = "your-token"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Generate completion
response = requests.post(
    f"{BASE_URL}/inference/generate",
    headers=headers,
    json={
        "model": "llama2",
        "messages": [{"role": "user", "content": "Hello!"}],
        "temperature": 0.7
    }
)

print(response.json())
```

### JavaScript

```javascript
const BASE_URL = 'http://localhost:8080/api/v1';
const TOKEN = 'your-token';

async function generateCompletion() {
  const response = await fetch(`${BASE_URL}/inference/generate`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${TOKEN}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      model: 'llama2',
      messages: [{role: 'user', content: 'Hello!'}],
      temperature: 0.7
    })
  });
  
  return await response.json();
}
```

### cURL

```bash
curl -X POST http://localhost:8080/api/v1/inference/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama2",
    "messages": [{"role": "user", "content": "Hello!"}],
    "temperature": 0.7
  }'
```

---

**Last Updated:** 19 octobre 2025  
**Version:** 1.0.0  
**API Version:** v1

