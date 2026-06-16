# llm-api
A lightweight LLM API service built with FastAPI, proxying requests to Cloudflare Workers AI using Llama 3.1.

## Technical Stack
- **FastAPI & httpx**: Asynchronous text generation API.
- **Docker**: Production-hardened container running as a non-root `appuser`.
- **GitHub Actions**: Automated CI/CD container build pipeline.

## Local Quickstart
\```bash
# 1. Setup environment & install packages
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Run the server
uvicorn main:app --reload
\```
- **Health Check**: `http://127.0.0.1:8000/health`
- **Swagger Docs**: `http://127.0.0.1:8000/docs`

## Docker Build
\```bash
docker build -t llm-api:v1 .
docker run -d -p 8080:8080 -e CLOUDFLARE_ACCOUNT_ID="id" -e CLOUDFLARE_API_TOKEN="token" llm-api:v1
\```

## GitHub Secrets Required
- `CLOUDFLARE_ACCOUNT_ID`
- `CLOUDFLARE_API_TOKEN`
