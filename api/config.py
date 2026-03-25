from dotenv import load_dotenv
import os

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
API_HOST        = os.getenv("API_HOST", "0.0.0.0")
API_PORT        = int(os.getenv("API_PORT", "8000"))
FRONTEND_URL    = os.getenv("FRONTEND_URL", "http://localhost:5173")
STREAMLIT_API_URL = os.getenv("STREAMLIT_API_URL", "http://localhost:8000")