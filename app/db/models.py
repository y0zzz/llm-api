from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(String)
    response = Column(String)
    model = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)