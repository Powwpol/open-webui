# n8n Integration Guide - Pulsai

## Overview

Pulsai provides a comprehensive webhook system for integrating with **n8n** (workflow automation tool) and other external services. This enables event-driven automation based on chat activities, model updates, user actions, and system events.

---

## Features

- ✅ **20+ Event Types**: Chat, user, model, fine-tuning, system, and MCP events
- ✅ **Secure Webhooks**: HMAC-SHA256 signature verification
- ✅ **Retry Logic**: Automatic retry with exponential backoff (up to 10 retries)
- ✅ **Event Filtering**: Subscribe to specific event types
- ✅ **Custom Headers**: Add authentication or custom metadata
- ✅ **Statistics**: Track delivery success rates and performance
- ✅ **Test Endpoint**: Verify webhooks before deployment

---

## Quick Start

### 1. Start n8n

```bash
# Using Docker
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  n8nio/n8n

# Or with docker-compose.production.yaml
docker-compose -f docker-compose.production.yaml --profile n8n up -d
```

### 2. Create Webhook in n8n

1. Open n8n (http://localhost:5678)
2. Create new workflow
3. Add **Webhook** node
4. Configure:
   - **HTTP Method**: POST
   - **Path**: `/pulsai-webhook`
   - **Response**: JSON
5. Copy the webhook URL (e.g., `http://n8n:5678/webhook/pulsai-webhook`)

### 3. Register Webhook in Pulsai

```bash
curl -X POST http://localhost:8080/api/v1/webhooks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "n8n Chat Events",
    "url": "http://n8n:5678/webhook/pulsai-webhook",
    "event_types": [
      "chat.created",
      "chat.message.added",
      "chat.completed"
    ],
    "max_retries": 3,
    "timeout": 30
  }'
```

**Response:**
```json
{
  "id": "webhook_abc123",
  "name": "n8n Chat Events",
  "url": "http://n8n:5678/webhook/pulsai-webhook",
  "secret": "whsec_d4e5f6g7h8i9...",
  "enabled": true,
  "created_at": "2025-10-19T18:30:00Z"
}
```

**⚠️ Save the `secret`!** You'll need it to verify webhook signatures.

---

## Available Events

| Event Type | Description | Payload Keys |
|------------|-------------|--------------|
| **Chat Events** |
| `chat.created` | New chat started | `chat_id`, `user_id`, `title` |
| `chat.updated` | Chat modified | `chat_id`, `changes` |
| `chat.deleted` | Chat deleted | `chat_id`, `user_id` |
| `chat.message.added` | New message in chat | `chat_id`, `message_id`, `role`, `content` |
| `chat.completed` | Chat finished | `chat_id`, `message_count`, `duration_seconds` |
| **Model Events** |
| `model.added` | Model added to system | `model_id`, `model_name`, `backend` |
| `model.removed` | Model removed | `model_id` |
| `model.updated` | Model configuration changed | `model_id`, `updates` |
| **User Events** |
| `user.created` | New user registered | `user_id`, `email`, `name` |
| `user.updated` | User profile updated | `user_id`, `changes` |
| `user.deleted` | User account deleted | `user_id` |
| `user.login` | User logged in | `user_id`, `ip_address` |
| **Fine-Tuning Events** |
| `fine_tune.started` | Fine-tuning job started | `job_id`, `model_id`, `dataset_size` |
| `fine_tune.completed` | Fine-tuning finished | `job_id`, `metrics`, `duration_seconds` |
| `fine_tune.failed` | Fine-tuning failed | `job_id`, `error` |
| **System Events** |
| `backend.healthy` | Backend became healthy | `backend`, `latency_ms` |
| `backend.unhealthy` | Backend went down | `backend`, `error` |
| `system.error` | Critical system error | `error_type`, `message`, `stack_trace` |
| **MCP Events** |
| `mcp.server.added` | MCP server connected | `server_id`, `server_name`, `protocol` |
| `mcp.server.removed` | MCP server disconnected | `server_id` |
| `mcp.tool.executed` | MCP tool executed | `tool_name`, `server_id`, `result` |

---

## Example Workflows

### 1. Send Chat Summary to Slack

**n8n Workflow:**

```
[Webhook] → [Filter: chat.completed] → [Function: Format Message] → [Slack]
```

**Function Node:**
```javascript
const event = $input.item.json;
const message = `🎉 Chat completed!
  - ID: ${event.data.chat_id}
  - Messages: ${event.data.message_count}
  - Duration: ${event.data.duration_seconds}s`;

return { message };
```

### 2. Auto-Backup on Fine-Tuning Completion

**n8n Workflow:**

```
[Webhook] → [Filter: fine_tune.completed] → [HTTP Request: Download Model] → [Upload to S3]
```

### 3. User Onboarding Automation

**n8n Workflow:**

```
[Webhook] → [Filter: user.created] → [Branch]
  ├─> [Send Welcome Email]
  ├─> [Create Notion Entry]
  └─> [Log to Google Sheets]
```

### 4. System Health Monitoring

**n8n Workflow:**

```
[Webhook] → [Filter: backend.unhealthy] → [PagerDuty Alert]
```

---

## Webhook Security

### Verifying Signatures

All webhook requests include an `X-Pulsai-Signature` header with HMAC-SHA256 signature.

**n8n Function Node (Verify):**

```javascript
const crypto = require('crypto');

const payload = JSON.stringify($input.item.json);
const signature = $input.item.headers['x-pulsai-signature'].replace('sha256=', '');
const secret = 'YOUR_WEBHOOK_SECRET';

const expectedSignature = crypto
  .createHmac('sha256', secret)
  .update(payload)
  .digest('hex');

if (signature !== expectedSignature) {
  throw new Error('Invalid signature!');
}

return $input.item.json;
```

**Python Example:**
```python
import hmac
import hashlib

def verify_webhook(payload: bytes, signature: str, secret: str) -> bool:
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected_signature)

# Usage
signature = request.headers.get('X-Pulsai-Signature', '').replace('sha256=', '')
is_valid = verify_webhook(request.body, signature, 'YOUR_SECRET')
```

---

## API Reference

### List Webhooks

```bash
GET /api/v1/webhooks

# Query parameters:
# - enabled_only=true  (optional)
```

### Create Webhook

```bash
POST /api/v1/webhooks
Content-Type: application/json
Authorization: Bearer TOKEN

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

### Update Webhook

```bash
PATCH /api/v1/webhooks/{subscription_id}
Content-Type: application/json

{
  "enabled": false,
  "event_types": ["chat.created"]
}
```

### Delete Webhook

```bash
DELETE /api/v1/webhooks/{subscription_id}
```

### Test Webhook

```bash
POST /api/v1/webhooks/test
Content-Type: application/json

{
  "url": "https://your-endpoint.com/webhook",
  "event_type": "custom",
  "test_data": {
    "message": "This is a test"
  }
}
```

### Get Statistics

```bash
GET /api/v1/webhooks/statistics/overview

# Response:
{
  "total_subscriptions": 5,
  "enabled_subscriptions": 4,
  "total_deliveries": 1234,
  "successful_deliveries": 1180,
  "failed_deliveries": 54,
  "success_rate": 95.62
}
```

### Regenerate Secret

```bash
POST /api/v1/webhooks/{subscription_id}/regenerate-secret

# Response:
{
  "secret": "whsec_new_secret_here"
}
```

---

## Webhook Payload Format

All webhooks send a JSON payload with this structure:

```json
{
  "event_id": "evt_abc123def456",
  "event_type": "chat.created",
  "timestamp": "2025-10-19T18:30:00.000Z",
  "source": "pulsai",
  "user_id": "user_789",
  "data": {
    "chat_id": "chat_xyz",
    "title": "New Conversation",
    "created_at": "2025-10-19T18:30:00.000Z"
  },
  "metadata": {
    "version": "1.0",
    "environment": "production"
  }
}
```

**Headers:**
- `Content-Type`: `application/json`
- `User-Agent`: `Pulsai-Webhook/1.0`
- `X-Pulsai-Event`: `chat.created`
- `X-Pulsai-Event-Id`: `evt_abc123def456`
- `X-Pulsai-Timestamp`: `2025-10-19T18:30:00.000Z`
- `X-Pulsai-Signature`: `sha256=abc123...`

---

## Retry Logic

Failed webhook deliveries are automatically retried with exponential backoff:

- **Attempt 1**: Immediate
- **Attempt 2**: After 1 second
- **Attempt 3**: After 2 seconds
- **Attempt 4**: After 4 seconds
- **Attempt 5**: After 8 seconds
- ...up to `max_retries` (default: 3)

**Success Criteria:** HTTP status codes 200-299

**Failure Causes:**
- HTTP status codes outside 200-299
- Network errors
- Timeouts (default: 30 seconds)

---

## Troubleshooting

### Webhook Not Receiving Events

1. **Check subscription is enabled:**
   ```bash
   GET /api/v1/webhooks/{subscription_id}
   ```

2. **Verify event types match:**
   Ensure the events you want are in `event_types` array

3. **Check n8n webhook path:**
   Must match exactly (case-sensitive)

4. **Test webhook:**
   ```bash
   POST /api/v1/webhooks/test
   ```

### Signature Verification Failing

1. **Use correct secret:**
   Copy from webhook creation response

2. **Verify payload:**
   Use exact request body (no modifications)

3. **Check header format:**
   Should be `sha256=<hex_signature>`

### High Failure Rate

1. **Check endpoint availability:**
   Ensure n8n/service is accessible

2. **Increase timeout:**
   ```bash
   PATCH /api/v1/webhooks/{id}
   {"timeout": 60}
   ```

3. **Check logs:**
   ```bash
   docker logs pulsai-backend | grep webhook
   ```

---

## Best Practices

1. **Use Event Filtering**: Subscribe only to needed events
2. **Respond Quickly**: Return 200 within timeout (default: 30s)
3. **Verify Signatures**: Always validate `X-Pulsai-Signature`
4. **Handle Retries**: Implement idempotency using `event_id`
5. **Monitor Statistics**: Track success rates via `/statistics/overview`
6. **Test First**: Use `/webhooks/test` before production
7. **Secure Secrets**: Store webhook secrets securely (environment variables)

---

**Last Updated:** 19 octobre 2025  
**Version:** 1.0.0  
**Author:** Pulsai Team

