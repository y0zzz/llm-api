from pydantic import BaseModel
from typing import Optional

class PromptRequest(BaseModel):
    prompt: str
    model: Optional[str] = "llama-3.1-8b"
    stream: Optional[bool] = False