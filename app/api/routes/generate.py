import logging
import httpx
from fastapi import APIRouter, Security, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.security import verify_api_key, check_rate_limit
from app.services.cache_service import get_cached_response, set_cached_response
from app.services.llm_service import call_cloudflare
from app.db.session import get_db
from app.db.models import Conversation
from app.schemas.request import PromptRequest
from app.core.config import CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_API_TOKEN, AVAILABLE_MODELS

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/generate")
async def generate_text(request: PromptRequest, key: str = Security(verify_api_key), db: Session = Depends(get_db), _: str = Depends(check_rate_limit)):
    logger.info(f"Received prompt using model: {request.model}")
    cached = get_cached_response(request.prompt, request.model)
    if cached:
        return {"status": "success", "response": cached, "cached": True}

    if request.stream:
        model_id = AVAILABLE_MODELS[request.model]
        url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/{model_id}"
        headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"}
        payload = {
            "messages": [{"role": "user", "content": request.prompt}],
            "stream": True
        }

        async def stream_response():
            async with httpx.AsyncClient() as client:
                async with client.stream("POST", url, headers=headers, json=payload, timeout=30.0) as response:
                    async for chunk in response.aiter_text():
                        yield chunk

        logger.info("Streaming response started")
        return StreamingResponse(stream_response(), media_type="text/event-stream")

    ai_response = await call_cloudflare(request.prompt, request.model, request.stream)
    set_cached_response(request.prompt, request.model, ai_response)

    # Saving conversation history is "best effort" -- if the database is
    # unavailable or expired, the user should still get their answer.
    try:
        conversation = Conversation(
            prompt=request.prompt,
            response=ai_response,
            model=request.model
        )
        db.add(conversation)
        db.commit()
        logger.info("Conversation saved to database")
    except Exception as exc:
        db.rollback()
        logger.warning(f"Could not save conversation to database: {exc}")

    return {"status": "success", "response": ai_response, "cached": False}
