import logging
from fastapi import APIRouter, Security, Depends
from sqlalchemy.orm import Session
from app.core.security import verify_api_key
from app.db.session import get_db
from app.db.models import Conversation

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/conversations")
def get_conversations(key: str = Security(verify_api_key), db: Session = Depends(get_db)):
    conversations = db.query(Conversation).all()
    logger.info(f"Retrieved {len(conversations)} conversations")
    return {"conversations": [
        {
            "id": c.id,
            "prompt": c.prompt,
            "response": c.response,
            "model": c.model,
            "created_at": c.created_at
        } for c in conversations
    ]}