from pydantic import BaseModel
from typing import Optional

# What the frontend sends TO your API
class GenerateRequest(BaseModel):
    prompt: str
    model: str = "tinyllama:1.1b"  # default model if none specified

# What your API sends BACK to the frontend
class GenerateResponse(BaseModel):
    response: str
    model: str
    duration_seconds: float
    prompt_used: str

# What your API sends back if something goes wrong
class ErrorResponse(BaseModel):
    error: str
    model: Optional[str] = None