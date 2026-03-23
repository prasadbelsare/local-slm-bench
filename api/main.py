from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from api.schemas import GenerateRequest, GenerateResponse, ErrorResponse
from api.schemas import StructuredGenerateRequest, StructuredGenerateResponse
from api.ollama_client import generate
from api.structured_client import structured_generate
from api.config import FRONTEND_URL
from api.constants import AVAILABLE_MODELS

app = FastAPI(
    title="Local SLM Benchmark API",
    description="Run and benchmark local language models using Ollama",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Local SLM API is running"}

@app.get("/models")
async def list_models():
    return {
        "models": [
            {"id": "tinyllama:1.1b",           "description": "Fastest - best for latency testing"},
            {"id": "phi3:mini",                 "description": "Balanced - efficient architecture"},
            {"id": "mistral:7b-instruct-q4_0",  "description": "Best quality - slowest on CPU"},
        ]
    }

@app.post("/generate", response_model=GenerateResponse)
async def generate_response(request: GenerateRequest):
    result = await generate(
        prompt=request.prompt,
        model=request.model
    )
    if isinstance(result, ErrorResponse):
        raise HTTPException(status_code=500, detail=result.error)
    return result

@app.post("/structured-generate", response_model=StructuredGenerateResponse)
async def structured_generate_response(request: StructuredGenerateRequest):
    result = await structured_generate(
        prompt=request.prompt,
        model=request.model,
        output_type=request.output_type,
        temperature=request.temperature
    )
    if isinstance(result, ErrorResponse):
        raise HTTPException(status_code=500, detail=result.error)
    return result