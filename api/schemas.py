from pydantic import BaseModel
from typing import Optional

class GenerateRequest(BaseModel):
    prompt: str
    model: str = "tinyllama:1.1b"

class GenerateResponse(BaseModel):
    response: str
    model: str
    duration_seconds: float
    time_to_first_token: Optional[float] = None
    prompt_used: str

class ErrorResponse(BaseModel):
    error: str
    model: Optional[str] = None

class SummaryOutput(BaseModel):
    summary: str
    key_points: list[str]
    word_count: int

class ReasoningOutput(BaseModel):
    answer: str
    reasoning_steps: list[str]
    confidence: str

class CodeOutput(BaseModel):
    code: str
    language: str
    explanation: str

class StructuredGenerateRequest(BaseModel):
    prompt: str
    model: str = "tinyllama:1.1b"
    output_type: str = "summary"
    temperature: float = 0.7

class StructuredGenerateResponse(BaseModel):
    result: dict
    output_type: str
    model: str
    duration_seconds: float
    attempts: int