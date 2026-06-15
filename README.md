# AI-Ops Pipeline

A secure, production-grade LLMOps pipeline that containers a FastAPI service using Cloudflare Workers AI.

## Technical Stack
- **FastAPI & httpx**: Asynchronous AI API text generation.
- **Docker**: Production-hardened container running as a non-root `appuser`.
- **GitHub Actions**: Automated CI/CD container build pipeline.

## Local Quickstart

```bash
# 1. Setup environment & install packages
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Run the server
uvicorn app:app --reload
```
- **Health Check**: `http://127.0.0`
- **Swagger Docs**: `http://127.0.0`

## Docker Build

```bash
docker build -t ai-ops:v1 .
docker run -d -p 8080:8080 -e CLOUDFLARE_ACCOUNT_ID="id" -e CLOUDFLARE_API_TOKEN="token" ai-ops:v1
```

## GitHub Secrets Required
- `CLOUDFLARE_ACCOUNT_ID`
- `CLOUDFLARE_API_TOKEN`
 # llm-api
# llm-api
