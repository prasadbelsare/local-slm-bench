AVAILABLE_MODELS = [
    "tinyllama:1.1b",
    "phi3:mini",
    "mistral:7b-instruct-q4_0"
]

OUTPUT_TYPES = ["summary", "reasoning", "code"]

SYSTEM_PROMPTS = {
    "summary": """You are a summarization assistant.
You must respond with ONLY valid JSON matching this exact structure, no other text:
{
  "summary": "one paragraph summary here",
  "key_points": ["point 1", "point 2", "point 3"],
  "word_count": 42
}""",

    "reasoning": """You are a reasoning assistant.
You must respond with ONLY valid JSON matching this exact structure, no other text:
{
  "answer": "final answer here",
  "reasoning_steps": ["step 1", "step 2", "step 3"],
  "confidence": "high"
}
confidence must be exactly one of: high, medium, low""",

    "code": """You are a coding assistant.
You must respond with ONLY valid JSON matching this exact structure, no other text:
{
  "code": "def your_function():\\n    pass",
  "language": "python",
  "explanation": "brief explanation here"
}"""
}

RETRY_SYSTEM_PROMPTS = {
    "summary": """IMPORTANT: Your previous response was not valid JSON.
You must respond with ONLY this JSON structure, nothing else, no markdown, no backticks:
{
  "summary": "your summary here",
  "key_points": ["point 1", "point 2"],
  "word_count": 10
}""",

    "reasoning": """IMPORTANT: Your previous response was not valid JSON.
You must respond with ONLY this JSON structure, nothing else, no markdown, no backticks:
{
  "answer": "your answer here",
  "reasoning_steps": ["step 1", "step 2"],
  "confidence": "high"
}
confidence must be exactly one of: high, medium, low""",

    "code": """IMPORTANT: Your previous response was not valid JSON.
You must respond with ONLY this JSON structure, nothing else, no markdown, no backticks:
{
  "code": "your code here",
  "language": "python",
  "explanation": "your explanation here"
}"""
}