import os
import logging
import redis
import json
import hashlib
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from prometheus_fastapi_instrumentator import Instrumentator
import httpx
from database import init_db, get_db, Conversation

load_dotenv()

redis_client = redis.Redis(host="redis", port=6379, decode_responses=True)
CACHE_TTL = 300  # 5 minuter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Cloudflare AI-Service")

Instrumentator().instrument(app).expose(app)

@app.on_event("startup")
def startup():
    init_db()
    logger.info("Database initialized")

CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
API_KEY = os.getenv("API_KEY")

AVAILABLE_MODELS = {
    "llama-3.1-8b": "@cf/meta/llama-3.1-8b-instruct-fast",
    "llama-3.1-70b": "@cf/meta/llama-3.1-70b-instruct",
    "mistral-7b": "@cf/mistral/mistral-7b-instruct-v0.1",
}

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(key: str = Security(api_key_header)):
    if key != API_KEY:
        logger.warning("Invalid API key attempt")
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return key

async def check_rate_limit(key: str = Security(api_key_header)):
    rate_limit_key = f"rate_limit:{key}"
    try:
        requests = redis_client.incr(rate_limit_key)
        if requests == 1:
            redis_client.expire(rate_limit_key, 60)  # 60 sekunder window
        if requests > 10:  # Max 10 requests per minut
            logger.warning(f"Rate limit exceeded for key: {key}")
            raise HTTPException(status_code=429, detail="Rate limit exceeded. Max 10 requests per minute.")
    except HTTPException:
        raise
    except Exception:
        logger.warning("Redis unavailable, skipping rate limit check")
    return key

class PromptRequest(BaseModel):
    prompt: str
    model: Optional[str] = "llama-3.1-8b"
    stream: Optional[bool] = False

@app.post("/generate")
async def generate_text(request: PromptRequest, key: str = Security(verify_api_key), db: Session = Depends(get_db), _: str = Depends(check_rate_limit)):
    logger.info(f"Received prompt using model: {request.model}")

    if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
        logger.error("Cloudflare keys missing")
        raise HTTPException(status_code=500, detail="Cloudflare keys missing. Configure environment variables.")

    if request.model not in AVAILABLE_MODELS:
        logger.error(f"Invalid model: {request.model}")
        raise HTTPException(status_code=400, detail=f"Invalid model. Choose from: {list(AVAILABLE_MODELS.keys())}")

    # Check cache
    cache_key = hashlib.md5(f"{request.prompt}{request.model}".encode()).hexdigest()
    try:
        cached = redis_client.get(cache_key)
        if cached:
            logger.info("Cache hit!")
            return {"status": "success", "response": cached, "cached": True}
    except Exception:
        logger.warning("Redis unavailable, skipping cache")

    model = AVAILABLE_MODELS[request.model]
    url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/{model}"
    headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"}
    payload = {
        "messages": [{"role": "user", "content": request.prompt}],
        "stream": request.stream
    }

    try:
        if request.stream:
            async def stream_response():
                async with httpx.AsyncClient() as client:
                    async with client.stream("POST", url, headers=headers, json=payload, timeout=30.0) as response:
                        async for chunk in response.aiter_text():
                            yield chunk

            logger.info("Streaming response started")
            return StreamingResponse(stream_response(), media_type="text/event-stream")

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload, timeout=30.0)

        if response.status_code != 200:
            logger.error(f"Cloudflare error: {response.status_code}")
            raise HTTPException(status_code=response.status_code, detail=f"Cloudflare Error: {response.text}")

        result = response.json()
        ai_response = result.get("result", {}).get("response")

        # Save to cache
        try:
            redis_client.setex(cache_key, CACHE_TTL, ai_response)
            logger.info("Response cached")
        except Exception:
            logger.warning("Redis unavailable, response not cached")

        # Save to database
        conversation = Conversation(
            prompt=request.prompt,
            response=ai_response,
            model=request.model
        )
        db.add(conversation)
        db.commit()
        logger.info("Conversation saved to database")

        return {"status": "success", "response": ai_response, "cached": False}

    except Exception as e:
        logger.error(f"Exception occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversations")
def get_conversations(key: str = Security(verify_api_key), db: Session = Depends(get_db)):
    conversations = db.query(Conversation).all()
    logger.info(f"Retrieved {len(conversations)} conversations")
    return {"conversations": [{"id": c.id, "prompt": c.prompt, "response": c.response, "model": c.model, "created_at": c.created_at} for c in conversations]}

@app.get("/models")
def list_models(key: str = Security(verify_api_key)):
    logger.info("Models list requested")
    return {"available_models": list(AVAILABLE_MODELS.keys())}

@app.get("/health")
def health_check():
    return {"status": "healthy"}