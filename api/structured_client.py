# import httpx
# import json
# import time
# from api.schemas import StructuredGenerateResponse, ErrorResponse
# from api.schemas import SummaryOutput, ReasoningOutput, CodeOutput
# from api.config import OLLAMA_BASE_URL
# from api.constants import SYSTEM_PROMPTS, RETRY_SYSTEM_PROMPTS, OUTPUT_TYPES

# OUTPUT_SCHEMAS = {
#     "summary": SummaryOutput,
#     "reasoning": ReasoningOutput,
#     "code": CodeOutput
# }

# def clean_json_response(text: str) -> str:
#     text = text.strip()
#     if text.startswith("```json"):
#         text = text[7:]
#     if text.startswith("```"):
#         text = text[3:]
#     if text.endswith("```"):
#         text = text[:-3]
#     return text.strip()

# async def call_ollama(
#     prompt: str,
#     model: str,
#     system_prompt: str,
#     temperature: float
# ) -> str:
#     async with httpx.AsyncClient(timeout=120.0) as client:
#         response = await client.post(
#             f"{OLLAMA_BASE_URL}/api/generate",
#             json={
#                 "model": model,
#                 "prompt": prompt,
#                 "system": system_prompt,
#                 "stream": False,
#                 "options": {
#                     "temperature": temperature
#                 }
#             }
#         )
#         response.raise_for_status()
#         return response.json()["response"]

# async def structured_generate(
#     prompt: str,
#     model: str,
#     output_type: str,
#     temperature: float
# ) -> StructuredGenerateResponse | ErrorResponse:

#     if output_type not in OUTPUT_SCHEMAS:
#         return ErrorResponse(
#             error=f"Invalid output_type '{output_type}'. Choose from: {OUTPUT_TYPES}",
#             model=model
#         )

#     schema_class = OUTPUT_SCHEMAS[output_type]
#     start_time = time.time()
#     attempts = 0

#     # ── Attempt 1 ────────────────────────────────────────────────────
#     try:
#         attempts = 1
#         raw = await call_ollama(
#             prompt=prompt,
#             model=model,
#             system_prompt=SYSTEM_PROMPTS[output_type],
#             temperature=temperature
#         )
#         cleaned = clean_json_response(raw)
#         parsed = schema_class(**json.loads(cleaned))
#         duration = round(time.time() - start_time, 2)
#         return StructuredGenerateResponse(
#             result=parsed.model_dump(),
#             output_type=output_type,
#             model=model,
#             duration_seconds=duration,
#             attempts=attempts
#         )
#     except (json.JSONDecodeError, ValueError, KeyError):
#         pass

#     # ── Attempt 2 (retry with stronger prompt) ───────────────────────
#     try:
#         attempts = 2
#         raw = await call_ollama(
#             prompt=prompt,
#             model=model,
#             system_prompt=RETRY_SYSTEM_PROMPTS[output_type],
#             temperature=0.0
#         )
#         cleaned = clean_json_response(raw)
#         parsed = schema_class(**json.loads(cleaned))
#         duration = round(time.time() - start_time, 2)
#         return StructuredGenerateResponse(
#             result=parsed.model_dump(),
#             output_type=output_type,
#             model=model,
#             duration_seconds=duration,
#             attempts=attempts
#         )
#     except (json.JSONDecodeError, ValueError, KeyError) as e:
#         return ErrorResponse(
#             error=f"Model failed to return valid JSON after 2 attempts. Last error: {str(e)}",
#             model=model
#         )
#     except httpx.ConnectError:
#         return ErrorResponse(
#             error="Cannot connect to Ollama. Make sure Ollama is running.",
#             model=model
#         )
import httpx
import json
import time
from api.schemas import StructuredGenerateResponse, ErrorResponse
from api.schemas import SummaryOutput, ReasoningOutput, CodeOutput
from api.config import OLLAMA_BASE_URL
from api.constants import SYSTEM_PROMPTS, RETRY_SYSTEM_PROMPTS, OUTPUT_TYPES

OUTPUT_SCHEMAS = {
    "summary": SummaryOutput,
    "reasoning": ReasoningOutput,
    "code": CodeOutput
}

PROMPT_TEMPLATES = {
    "summary": """{prompt}

Respond with ONLY this JSON, no other text, no markdown backticks:
{{
  "summary": "one paragraph summary here",
  "key_points": ["point 1", "point 2", "point 3"],
  "word_count": 42
}}""",

    "reasoning": """{prompt}

Respond with ONLY this JSON, no other text, no markdown backticks:
{{
  "answer": "final answer here",
  "reasoning_steps": ["step 1", "step 2", "step 3"],
  "confidence": "high"
}}
confidence must be exactly one of: high, medium, low""",

    "code": """{prompt}

Respond with ONLY this JSON, no other text, no markdown backticks:
{{
  "code": "def your_function():\\n    pass",
  "language": "python",
  "explanation": "brief explanation here"
}}"""
}

RETRY_PROMPT_TEMPLATES = {
    "summary": """IMPORTANT: You must respond with ONLY valid JSON, nothing else.
No explanations, no markdown, no backticks. Just the raw JSON object.

Task: {prompt}

Required JSON format:
{{
  "summary": "your summary here",
  "key_points": ["point 1", "point 2"],
  "word_count": 10
}}""",

    "reasoning": """IMPORTANT: You must respond with ONLY valid JSON, nothing else.
No explanations, no markdown, no backticks. Just the raw JSON object.

Task: {prompt}

Required JSON format:
{{
  "answer": "your answer here",
  "reasoning_steps": ["step 1", "step 2"],
  "confidence": "high"
}}""",

    "code": """IMPORTANT: You must respond with ONLY valid JSON, nothing else.
No explanations, no markdown, no backticks. Just the raw JSON object.

Task: {prompt}

Required JSON format:
{{
  "code": "your code here",
  "language": "python",
  "explanation": "your explanation here"
}}"""
}

def clean_json_response(text: str) -> str:
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    # Extract JSON object if surrounded by extra text
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end > start:
        text = text[start:end]
    return text.strip()

async def call_ollama(
    prompt: str,
    model: str,
    system_prompt: str,
    temperature: float
) -> str:
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False,
                "options": {
                    "temperature": temperature
                }
            }
        )
        response.raise_for_status()
        return response.json()["response"]

async def structured_generate(
    prompt: str,
    model: str,
    output_type: str,
    temperature: float
) -> StructuredGenerateResponse | ErrorResponse:

    if output_type not in OUTPUT_SCHEMAS:
        return ErrorResponse(
            error=f"Invalid output_type '{output_type}'. Choose from: {OUTPUT_TYPES}",
            model=model
        )

    schema_class = OUTPUT_SCHEMAS[output_type]
    start_time = time.time()
    attempts = 0

    # Inject JSON instructions directly into the prompt
    injected_prompt = PROMPT_TEMPLATES[output_type].format(prompt=prompt)

    # ── Attempt 1 ────────────────────────────────────────────────────
    try:
        attempts = 1
        raw = await call_ollama(
            prompt=injected_prompt,
            model=model,
            system_prompt=SYSTEM_PROMPTS[output_type],
            temperature=temperature
        )
        cleaned = clean_json_response(raw)
        parsed = schema_class(**json.loads(cleaned))
        duration = round(time.time() - start_time, 2)
        return StructuredGenerateResponse(
            result=parsed.model_dump(),
            output_type=output_type,
            model=model,
            duration_seconds=duration,
            attempts=attempts
        )
    except (json.JSONDecodeError, ValueError, KeyError):
        pass

    # ── Attempt 2 (retry with stronger injected prompt) ──────────────
    try:
        attempts = 2
        retry_prompt = RETRY_PROMPT_TEMPLATES[output_type].format(prompt=prompt)
        raw = await call_ollama(
            prompt=retry_prompt,
            model=model,
            system_prompt=RETRY_SYSTEM_PROMPTS[output_type],
            temperature=0.0
        )
        cleaned = clean_json_response(raw)
        parsed = schema_class(**json.loads(cleaned))
        duration = round(time.time() - start_time, 2)
        return StructuredGenerateResponse(
            result=parsed.model_dump(),
            output_type=output_type,
            model=model,
            duration_seconds=duration,
            attempts=attempts
        )
    except (json.JSONDecodeError, ValueError, KeyError) as e:
        return ErrorResponse(
            error=f"Model failed to return valid JSON after 2 attempts. Last error: {str(e)}",
            model=model
        )
    except httpx.ConnectError:
        return ErrorResponse(
            error="Cannot connect to Ollama. Make sure Ollama is running.",
            model=model
        )