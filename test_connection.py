import httpx

response = httpx.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "tinyllama:1.1b",
        "prompt": "Say hello in one sentence.",
        "stream": False
    }
)

print(response.status_code)
print(response.json()["response"])