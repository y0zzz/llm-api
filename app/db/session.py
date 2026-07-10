import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Base

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://llmuser:llmpassword@localhost/llmapi")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()