from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from api.schemas import GenerateRequest, GenerateResponse, ErrorResponse
from api.ollama_client import generate

app = FastAPI(
    title="Local SLM Benchmark API",
    description="Run and benchmark local language models using Ollama",
    version="1.0.0"
)

# CORS - allows React frontend to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
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