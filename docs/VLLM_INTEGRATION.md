# vLLM Integration - Pulsai

## Overview

Pulsai now supports **vLLM** as an additional high-performance inference backend alongside Ollama. This integration provides:

- **Unified API**: Common interface for both Ollama and vLLM
- **Load Balancing**: Automatic distribution of requests
- **Failover**: Seamless switching between backends
- **Health Monitoring**: Real-time backend status tracking
- **Performance**: Optimized for production workloads

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│             Pulsai Inference Router                │
│  (Load Balancing + Failover + Health Monitoring)   │
└──────────────┬──────────────┬─────────────────────┘
               │              │
       ┌───────▼────┐  ┌──────▼────┐
       │  Ollama    │  │   vLLM    │
       │  Backend   │  │  Backend  │
       └────────────┘  └───────────┘
```

---

## Configuration

### Environment Variables

Add to your `.env` or `.env.production`:

```bash
# vLLM Configuration
VLLM_ENABLED=true
VLLM_BASE_URL=http://localhost:8000
VLLM_API_KEY=optional_api_key_if_required
VLLM_TIMEOUT=300  # seconds

# Inference Routing Strategy
# Options: round_robin, least_loaded, failover, priority
INFERENCE_STRATEGY=priority

# Backend Priority Order (comma-separated)
# Requests will prefer the first available backend
BACKEND_PRIORITIES=vllm,ollama
```

### Docker Compose

vLLM service is already configured in `docker-compose.production.yaml`:

```yaml
services:
  vllm:
    image: vllm/vllm-openai:latest
    ports:
      - "8000:8000"
    volumes:
      - vllm-models:/root/.cache/huggingface
    environment:
      - VLLM_API_KEY=${VLLM_API_KEY}
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    command: >
      --model meta-llama/Llama-2-7b-chat-hf
      --host 0.0.0.0
      --port 8000
```

---

## Running vLLM

### Option 1: Docker (Recommended)

```bash
# Start vLLM with Pulsai stack
docker-compose -f docker-compose.production.yaml up -d vllm

# View logs
docker-compose -f docker-compose.production.yaml logs -f vllm

# Check status
curl http://localhost:8000/v1/models
```

### Option 2: Standalone vLLM Server

```bash
# Install vLLM
pip install vllm

# Run server (requires GPU)
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Llama-2-7b-chat-hf \
  --host 0.0.0.0 \
  --port 8000 \
  --api-key your-optional-api-key

# Test connection
curl http://localhost:8000/v1/models
```

### Supported Models

vLLM supports many popular models:
- **Llama 2 / Llama 3**
- **Mistral / Mixtral**
- **Falcon**
- **MPT**
- **GPT-NeoX**
- **BLOOM**
- And many more...

---

## API Usage

### 1. Health Check

```bash
curl http://localhost:8080/api/v1/inference/backends/status

# Response:
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

### 2. List Models

```bash
curl http://localhost:8080/api/v1/inference/models

# Response:
{
  "ollama": [
    {"id": "llama2", "name": "llama2", "backend": "ollama", ...},
    {"id": "mistral", "name": "mistral", "backend": "ollama", ...}
  ],
  "vllm": [
    {"id": "meta-llama/Llama-2-7b-chat-hf", "name": "meta-llama/Llama-2-7b-chat-hf", "backend": "vllm", ...}
  ]
}
```

### 3. Generate Completion

```bash
curl -X POST http://localhost:8080/api/v1/inference/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta-llama/Llama-2-7b-chat-hf",
    "messages": [
      {"role": "user", "content": "Hello! How are you?"}
    ],
    "temperature": 0.7,
    "max_tokens": 512,
    "backend": "vllm"
  }'

# Response:
{
  "model": "meta-llama/Llama-2-7b-chat-hf",
  "content": "Hello! I'm doing well, thank you for asking...",
  "finish_reason": "stop",
  "backend": "vllm",
  "latency_ms": 1245.3,
  "usage": {
    "prompt_tokens": 12,
    "completion_tokens": 45,
    "total_tokens": 57
  }
}
```

### 4. Streaming Generation

```bash
curl -X POST http://localhost:8080/api/v1/inference/generate/stream \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta-llama/Llama-2-7b-chat-hf",
    "prompt": "Write a short poem about AI:",
    "stream": true,
    "backend": "vllm"
  }'

# Response (SSE stream):
data: In
data:  circuits
data:  deep
data:  and
data:  bright
...
data: [DONE]
```

---

## Load Balancing Strategies

### 1. Round Robin (Default)

Distributes requests evenly across all healthy backends.

```bash
INFERENCE_STRATEGY=round_robin
```

### 2. Least Loaded

Routes to backend with fewest active requests.

```bash
INFERENCE_STRATEGY=least_loaded
```

### 3. Priority

Uses backends in specified priority order.

```bash
INFERENCE_STRATEGY=priority
BACKEND_PRIORITIES=vllm,ollama  # Prefer vLLM, fallback to Ollama
```

### 4. Failover

Attempts primary backend, switches on failure.

```bash
INFERENCE_STRATEGY=failover
BACKEND_PRIORITIES=vllm,ollama
```

---

## Performance Optimization

### vLLM Configuration

```bash
# Use PagedAttention for memory efficiency
--swap-space 16  # GB of CPU memory for swapping

# Enable continuous batching
--max-num-batched-tokens 8192

# Multi-GPU support
--tensor-parallel-size 2  # Number of GPUs

# Quantization for faster inference
--quantization awq  # Or 'gptq', 'sq'
```

### Production Tips

1. **GPU Memory**: vLLM requires significant VRAM
   - 7B model: ~14GB VRAM
   - 13B model: ~26GB VRAM
   - 70B model: 2x A100 (80GB each)

2. **Batching**: Enable continuous batching for throughput
   ```bash
   --max-num-seqs 256
   ```

3. **Caching**: Pre-download models
   ```bash
   huggingface-cli download meta-llama/Llama-2-7b-chat-hf
   ```

4. **Monitoring**: Track GPU utilization
   ```bash
   nvidia-smi -l 1
   ```

---

## Troubleshooting

### vLLM Won't Start

**Issue:** `CUDA out of memory`
**Solution:** Reduce model size or use quantization
```bash
--quantization awq --max-model-len 2048
```

**Issue:** `Model not found`
**Solution:** Download model first
```bash
huggingface-cli login
huggingface-cli download meta-llama/Llama-2-7b-chat-hf
```

### Connection Errors

**Issue:** `Connection refused to vLLM`
**Solution:** Check vLLM is running
```bash
docker ps | grep vllm
curl http://localhost:8000/v1/models
```

**Issue:** `Authentication failed`
**Solution:** Set correct API key
```bash
export VLLM_API_KEY=your-key
```

### Performance Issues

**Issue:** Slow inference
**Solutions:**
1. Enable GPU (check `nvidia-smi`)
2. Reduce `max_tokens`
3. Use smaller model
4. Enable continuous batching

**Issue:** High latency
**Solutions:**
1. Check network between services
2. Use `priority` strategy to prefer fastest backend
3. Monitor with `/api/v1/inference/backends/status`

---

##Monitoring & Metrics

### Health Dashboard

```bash
# Get real-time health
curl http://localhost:8080/api/v1/inference/backends/health

# Response:
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

### Prometheus Metrics

Add to `prometheus.yml`:
```yaml
scrape_configs:
  - job_name: 'pulsai-inference'
    static_configs:
      - targets: ['pulsai-backend:8080']
    metrics_path: '/metrics'
```

---

## Migration from Ollama-only

1. **Enable vLLM** in environment:
   ```bash
   VLLM_ENABLED=true
   VLLM_BASE_URL=http://vllm:8000
   ```

2. **Update models**: Models will appear in unified `/api/v1/inference/models`

3. **No code changes**: Existing chat endpoints remain compatible

4. **Gradual migration**: Use `priority` strategy to test vLLM:
   ```bash
   INFERENCE_STRATEGY=priority
   BACKEND_PRIORITIES=ollama,vllm  # Keep Ollama primary initially
   ```

---

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/inference/generate` | POST | Generate completion (non-streaming) |
| `/api/v1/inference/generate/stream` | POST | Generate completion (streaming SSE) |
| `/api/v1/inference/models` | GET | List all models from all backends |
| `/api/v1/inference/backends/status` | GET | Get backend status and metrics |
| `/api/v1/inference/backends/health` | GET | Get health monitoring data |
| `/api/v1/inference/backends/add` | POST | Add new backend dynamically |
| `/api/v1/inference/backends/{name}` | DELETE | Remove backend |

---

**Last Updated:** 19 octobre 2025  
**Version:** 1.0.0  
**Author:** Pulsai Team

