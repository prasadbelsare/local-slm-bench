# Local SLM Benchmarking App

Three small language models running entirely offline on a CPU-only laptop.
No cloud APIs, no data leaving the machine, no per-token costs.

Built to answer a practical question: what does local inference actually
look like on consumer hardware, and which model holds up under real
workloads?

---

## Models

| Model | Disk | RAM loaded | Quant |
|---|---|---|---|
| tinyllama:1.1b | 600MB | 730MB | Q4 |
| phi3:mini | 2.3GB | 4.4GB | Q4 |
| mistral:7b-instruct-q4_0 | 4.1GB | 4.5GB | Q4_0 |

---

## Hardware

- CPU only, no GPU
- 16GB RAM, Windows
- Ollama v0.18.0

---

## What is built

**Ollama + FastAPI backend**
Two endpoints: `/generate` for raw text responses and
`/structured-generate` for enforced JSON schema outputs.
Structured outputs use Pydantic models and a retry mechanism that
catches invalid JSON and reprompts at temperature 0 before failing.

**Benchmarking suite**
120 runs across 3 models and 40 prompts. Prompt categories cover
healthcare, legal, finance, code, education, marketing, HR, and
customer support. Each run records tokens per second, time to first
token, total latency, and response length.

**Experiments**
- Temperature: same 5 prompts at 0.0 and 0.7, run 3 times each (90 calls)
- Memory: Ollama process RSS tracked before and after each model load
- Structured output: JSON schema compliance tested across all three models

**Streamlit frontend**
Three pages: live chat with latency metrics, benchmark charts pulled
from the latest results JSON, and a model comparison table with stats
computed from real benchmark data.

---

## Key findings

Tinyllama is 5x faster than mistral in tokens per second but failed
every reasoning test and hallucinated on basic education prompts.
It also ignored system prompt instructions entirely, requiring JSON
format to be injected directly into the user prompt.

Phi3 generated a 35,476 character response on a single healthcare
prompt taking 37 minutes. Open-ended clinical prompts need output
length limits or phi3 will not stop.

Mistral produced the most consistent outputs across all 8 categories.
It stops when the task is done without padding or inventing follow-up
questions.

Temperature 0 did not produce identical outputs. CPU floating point
non-determinism means the same prompt can generate different outputs
across runs even at temperature 0. Only factual single-answer prompts
were consistently identical.

Loading phi3 pushes system RAM from 68% to 88% on 16GB. Only one
large model fits in memory at a time. Switching models incurs a
20-60 second cold-start penalty while Ollama evicts and reloads.

Full analysis with per-category breakdowns is in FINDINGS.md.

---

## Project structure
```
local-slm-bench/
├── api/
│   ├── main.py               # FastAPI app, CORS, endpoints
│   ├── schemas.py            # Pydantic request and response models
│   ├── ollama_client.py      # Async streaming client, TTFT measurement
│   ├── structured_client.py  # JSON enforcement, retry logic
│   ├── config.py             # Loads from .env
│   └── constants.py          # Model list, prompts, system prompts
├── benchmarks/
│   ├── runner.py             # Runs all models against all prompts
│   ├── prompts.py            # Imports prompt suite from constants
│   └── results/              # Benchmark output JSON files
├── experiments/
│   ├── temperature_test.py   # 0.0 vs 0.7 variance experiment
│   ├── memory_test.py        # Ollama process RAM tracking
│   └── results/              # Experiment output JSON files
├── streamlit_app.py          # Frontend
├── FINDINGS.md               # Full written analysis
├── .env.example              # Environment variable template
└── requirements.txt
```

---

## Setup

Requires Python 3.10+ and Ollama installed from https://ollama.com
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Pull the models:
```bash
ollama pull tinyllama:1.1b
ollama pull phi3:mini
ollama pull mistral:7b-instruct-q4_0
```

Copy the environment file:
```bash
cp .env.example .env
```

---

## Running

Start the API:
```bash
uvicorn api.main:app --reload
```

Start the frontend:
```bash
streamlit run streamlit_app.py
```

Run the full benchmark (3-5 hours on CPU):
```bash
python -m benchmarks.runner
```

Run experiments:
```bash
python -m experiments.temperature_test
python -m experiments.memory_test
```

---

## API

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| GET | `/models` | Available models |
| POST | `/generate` | Text generation |
| POST | `/structured-generate` | JSON schema enforced generation |

---

## Stack

- Ollama - local model runtime
- FastAPI - REST API
- Pydantic - data validation and schema enforcement
- httpx - async HTTP client
- Streamlit - frontend
- Plotly - benchmark charts
- psutil - memory measurement