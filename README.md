# Local SLM Benchmarking App

Run and benchmark small language models entirely offline using Ollama.

## Models
- tinyllama:1.1b
- phi3:mini
- mistral:7b-instruct-q4_0

## Stack
- Ollama — local model inference
- FastAPI — REST API wrapper
- React — frontend UI
- Jupyter — benchmark analysis

## Setup
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Run the API
```bash
uvicorn api.main:app --reload
```