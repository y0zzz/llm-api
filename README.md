# llm-api
A production-grade LLM API built with Python and FastAPI that proxies prompts to multiple Cloudflare Workers AI models, with streaming, caching, authentication, persistent storage and real-time monitoring.

## Stack
· Python 
· FastAPI 
· PostgreSQL 
· Redis
· Docker Compose 
· Prometheus 
· Grafana 
· Terraform 
· GitHub Actions

## Endpoints
- `POST /generate` — Generate text (cached)
- `GET /conversations` — Conversation history
- `GET /models` — Available models
- `GET /health` — Health check

## Quickstart
```bash
cp .env.example .env
docker compose up
```

## Example
```bash
curl -X POST http://127.0.0.1:8080/generate \
-H "Content-Type: application/json" \
-H "X-API-Key: your-key" \
-d '{"prompt": "Hello!", "model": "llama-3.1-8b"}'
```

## GitHub Secrets
· `CLOUDFLARE_ACCOUNT_ID` 
· `CLOUDFLARE_API_TOKEN` 
· `API_KEY` 
· `DATABASE_URL`