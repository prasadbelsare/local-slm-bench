import httpx
import time
from api.schemas import GenerateResponse, ErrorResponse
from api.config import OLLAMA_BASE_URL
from api.constants import AVAILABLE_MODELS

async def generate(prompt: str, model: str) -> GenerateResponse | ErrorResponse:
    if model not in AVAILABLE_MODELS:
        return ErrorResponse(
            error=f"Model '{model}' is not available. Choose from: {AVAILABLE_MODELS}",
            model=model
        )

    start_time = time.time()

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            data = response.json()

        duration = round(time.time() - start_time, 2)

        return GenerateResponse(
            response=data["response"],
            model=model,
            duration_seconds=duration,
            prompt_used=prompt
        )

    except httpx.ConnectError:
        return ErrorResponse(
            error="Cannot connect to Ollama. Make sure Ollama is running.",
            model=model
        )
    except httpx.TimeoutException:
        return ErrorResponse(
            error=f"Model '{model}' timed out after 120 seconds.",
            model=model
        )
    except Exception as e:
        return ErrorResponse(
            error=f"Unexpected error: {str(e)}",
            model=model
        )