import httpx
import time
from api.schemas import GenerateResponse, ErrorResponse
from api.config import OLLAMA_BASE_URL
from api.constants import AVAILABLE_MODELS

async def generate(
    prompt: str,
    model: str
) -> GenerateResponse | ErrorResponse:

    if model not in AVAILABLE_MODELS:
        return ErrorResponse(
            error=f"Model '{model}' is not available. Choose from: {AVAILABLE_MODELS}",
            model=model
        )

    start_time = time.time()
    first_token_time = None
    full_response = ""

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": True
                }
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if not line.strip():
                        continue

                    import json
                    chunk = json.loads(line)

                    # Capture time when first token arrives
                    if first_token_time is None and chunk.get("response"):
                        first_token_time = time.time()

                    full_response += chunk.get("response", "")

                    # Stop when done
                    if chunk.get("done", False):
                        break

        end_time = time.time()
        total_duration = round(end_time - start_time, 2)
        ttft = round(first_token_time - start_time, 2) if first_token_time else None

        return GenerateResponse(
            response=full_response,
            model=model,
            duration_seconds=total_duration,
            time_to_first_token=ttft,
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