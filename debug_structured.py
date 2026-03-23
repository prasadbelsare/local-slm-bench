import asyncio
import httpx
from api.config import OLLAMA_BASE_URL
from api.constants import SYSTEM_PROMPTS

async def debug():
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": "tinyllama:1.1b",
                "prompt": "Explain what machine learning is",
                "system": SYSTEM_PROMPTS["summary"],
                "stream": False,
                "options": {
                    "temperature": 0.7
                }
            }
        )
        data = response.json()
        print("=== RAW RESPONSE ===")
        print(repr(data["response"]))

asyncio.run(debug())