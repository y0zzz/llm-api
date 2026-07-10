import httpx
import logging
from fastapi import HTTPException
from app.core.config import CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_API_TOKEN, AVAILABLE_MODELS

logger = logging.getLogger(__name__)

async def call_cloudflare(prompt: str, model: str, stream: bool = False):
    if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
        logger.error("Cloudflare keys missing")
        raise HTTPException(status_code=500, detail="Cloudflare keys missing. Configure environment variables.")

    if model not in AVAILABLE_MODELS:
        logger.error(f"Invalid model: {model}")
        raise HTTPException(status_code=400, detail=f"Invalid model. Choose from: {list(AVAILABLE_MODELS.keys())}")

    model_id = AVAILABLE_MODELS[model]
    url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/{model_id}"
    headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"}
    payload = {
        "messages": [{"role": "user", "content": prompt}],
        "stream": stream
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload, timeout=30.0)

    if response.status_code != 200:
        logger.error(f"Cloudflare error: {response.status_code}")
        raise HTTPException(status_code=response.status_code, detail=f"Cloudflare Error: {response.text}")

    result = response.json()
    return result.get("result", {}).get("response")