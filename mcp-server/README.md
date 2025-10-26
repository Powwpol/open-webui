# Pulsai Custom MCP Server

Custom Model Context Protocol (MCP) server for Pulsai with specialized tools for recursive chat workflows, model introspection, and context summarization.

## Features

- **Recursive Chat**: Execute complex recursive chat workflows with different strategies
- **Model Info**: Get detailed information about available AI models
- **Context Summary**: Summarize long conversation contexts

## Installation

### Using Poetry

```bash
cd mcp-server
poetry install
```

### Using pip

```bash
cd mcp-server
pip install -e .
```

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Key configuration options:

- `PULSAI_MCP_HOST`: Server host (default: 0.0.0.0)
- `PULSAI_MCP_PORT`: Server port (default: 8400)
- `PULSAI_BACKEND_URL`: Pulsai backend URL
- `PULSAI_MCP_AUTH_ENABLED`: Enable authentication (default: true)
- `PULSAI_MCP_TOKEN`: Authentication token

## Running the Server

### Development

```bash
poetry run pulsai-mcp
```

Or:

```bash
python -m pulsai_mcp.server
```

### Docker

Build and run with Docker:

```bash
docker build -t pulsai-mcp:latest .
docker run -p 8400:8400 --env-file .env pulsai-mcp:latest
```

## Available Tools

### 1. recursive_chat

Execute a recursive chat workflow for complex problem-solving.

**Parameters:**
- `prompt` (string, required): Initial prompt for the recursive chat
- `strategy` (string, optional): Recursion strategy (breadth_first, depth_first, adaptive)
- `max_depth` (integer, optional): Maximum recursion depth (1-10)

**Example:**
```json
{
  "name": "recursive_chat",
  "arguments": {
    "prompt": "Solve this problem step by step",
    "strategy": "breadth_first",
    "max_depth": 3
  }
}
```

### 2. model_info

Get information about available AI models.

**Parameters:**
- `model_name` (string, optional): Specific model to query

**Example:**
```json
{
  "name": "model_info",
  "arguments": {
    "model_name": "gpt-4"
  }
}
```

### 3. context_summary

Summarize a conversation context.

**Parameters:**
- `messages` (array, required): List of message objects with role and content
- `max_length` (integer, optional): Maximum summary length

**Example:**
```json
{
  "name": "context_summary",
  "arguments": {
    "messages": [
      {"role": "user", "content": "Hello"},
      {"role": "assistant", "content": "Hi there!"}
    ],
    "max_length": 500
  }
}
```

## API Endpoints

- `GET /health` - Health check
- `GET /v1/tools` - List available tools
- `POST /v1/tools/execute` - Execute a tool
- `POST /v1/tools/stream` - Stream tool execution (coming soon)

## Authentication

When authentication is enabled, include a Bearer token in requests:

```bash
curl -H "Authorization: Bearer your-token" http://localhost:8400/v1/tools
```

## Integration with Pulsai

Add this server to your Pulsai MCP configuration (`config/mcp-servers.yaml`):

```yaml
mcp_servers:
  - id: "pulsai-custom"
    name: "Pulsai Custom MCP"
    description: "Custom Pulsai MCP server"
    protocol: "http"
    enabled: true
    config:
      url: "http://localhost:8400"
      auth_type: "bearer"
      token: "${PULSAI_MCP_TOKEN}"
      timeout: 60
    tags: ["pulsai", "custom", "recursive"]
```

## Development

### Running Tests

```bash
poetry run pytest
```

### Code Formatting

```bash
poetry run black pulsai_mcp/
poetry run isort pulsai_mcp/
```

## License

Same as Pulsai main project.

