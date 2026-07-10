import logging
from fastapi import APIRouter, Security
from app.core.security import verify_api_key
from app.core.config import AVAILABLE_MODELS

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/models")
def list_models(key: str = Security(verify_api_key)):
    logger.info("Models list requested")
    return {"available_models": list(AVAILABLE_MODELS.keys())}