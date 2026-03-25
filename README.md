# Local SLM Benchmarking App

Run and benchmark small language models entirely offline using Ollama.
No cloud APIs. No data leaving your machine. No per-token costs.

This project was built to understand the real-world tradeoffs of local
inference on CPU-only hardware — speed, memory, output quality, and
reliability across three models and 40 real-world prompts.

---

## Models Tested

| Model | Disk size | RAM loaded | Quantization |
|---|---|---|---|
| tinyllama:1.1b | 600MB | 730MB | Q4 |
| phi3:mini | 2.3GB | 4.4GB | Q4 |
| mistral:7b-instruct-q4_0 | 4.1GB | 4.5GB | Q4_0 |

---

## Hardware

- CPU only — no GPU
- 16GB RAM
- Windows
- Ollama v0.18.0

---

## What This Project Does

**Local inference** — all three models run entirely offline via Ollama.
No prompt data, no response data, nothing leaves the machine.

**FastAPI wrapper** — a REST API with `/generate` and `/structured-generate`
endpoints. Structured outputs enforce Pydantic schemas on model responses
with a retry mechanism that catches invalid JSON and reprompts before
failing gracefully.

**Benchmarking suite** — 120 runs across 3 models and 40 prompts covering
healthcare, legal, finance, code, education, marketing, HR, and customer
support. Records tokens per second, time to first token, total latency,
and response length per run.

**Experiments** — temperature experiment (0.0 vs 0.7 across 90 runs),
memory measurement tracking Ollama process RSS, and structured output
reliability testing across all three models.

**Streamlit frontend** — three-page UI with a live chat interface,
benchmark result charts, and model comparison tables driven by real
benchmark data.

---

## Key Findings

**Speed**
Tinyllama averages 19.4 tok/s with a 1.1s time to first token.
Mistral averages 3.4 tok/s with a 5.2s time to first token.
On CPU, none of these models are suitable for real-time chat interfaces.
They are viable for batch processing, document pipelines, and async
workflows where latency is acceptable.

**Memory**
Only one large model fits in memory at a time on 16GB RAM. Loading phi3
pushes system RAM from 68% to 88%. Ollama evicts the previous model
before loading the next, creating a 20-60 second cold-start penalty
when switching models.

**Structured outputs**
Tinyllama failed JSON schema compliance on every first attempt and
required the retry mechanism each time. Even after retrying, it copied
the example JSON template rather than filling in real content — a
pattern-matching failure rather than a comprehension failure.
Phi3 and mistral both succeeded on first attempt across all structured
output tests.

**Temperature**
Temperature 0 did not produce identical outputs on CPU hardware due to
floating point non-determinism in matrix operations. Only factual
single-answer prompts (capital of France) were consistently identical
across 3 runs. Creative prompts varied every time regardless of
temperature setting.

**Real-world prompts**
Phi3 generated a 35,476 character response on a healthcare prompt
taking 37 minutes — a critical production risk without output length
limits. Tinyllama invented a fictional AI called "PythaGoreaN" when
asked to explain the Pythagorean theorem. Mistral was the most
consistent model across all 8 categories.

**Privacy**
All inference runs locally. This stack is viable for medical, legal,
or proprietary business data where sending prompts to an external API
is not acceptable.

**Cost**
Zero inference cost per token after hardware setup. At scale this
matters — GPT-4o runs roughly $0.01-0.03 per 1K tokens. For high-volume
internal document processing, local inference pays for itself quickly.

---

## Project Structure
```
local-slm-bench/
├── api/
│   ├── main.py                  # FastAPI app
│   ├── schemas.py               # Pydantic request/response models
│   ├── ollama_client.py         # Async streaming client with TTFT
│   ├── structured_client.py     # JSON schema enforcement + retry
│   ├── config.py                # Environment variable loading
│   └── constants.py             # Models, prompts, system prompts
│
├── benchmarks/
│   ├── runner.py                # Benchmark orchestrator
│   ├── prompts.py               # Imports 40 prompts from constants
│   └── results/                 # JSON output files per run
│
├── experiments/
│   ├── temperature_test.py      # Temperature 0 vs 0.7 experiment
│   ├── memory_test.py           # Ollama process RAM measurement
│   └── results/                 # Experiment output files
│
├── streamlit_app.py             # Frontend — chat, charts, comparison
├── FINDINGS.md                  # Full benchmark analysis
├── .env                         # Environment variables
└── requirements.txt
```

---

## Setup

**Prerequisites**
- Python 3.10+
- [Ollama](https://ollama.com) installed and running

**Install dependencies**
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
```

**Pull models**
```bash
ollama pull tinyllama:1.1b
ollama pull phi3:mini
ollama pull mistral:7b-instruct-q4_0
```

**Configure environment**
```bash
cp .env.example .env
```

---

## Running the Project

**Start the API**
```bash
uvicorn api.main:app --reload
```

**Start the frontend**
```bash
streamlit run streamlit_app.py
```

**Run the full benchmark** (120 runs, expect 3-5 hours on CPU)
```bash
python -m benchmarks.runner
```

**Run experiments**
```bash
python -m experiments.temperature_test
python -m experiments.memory_test
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| GET | `/models` | List available models |
| POST | `/generate` | Generate a response |
| POST | `/structured-generate` | Generate with JSON schema enforcement |

---

## Stack

- [Ollama](https://ollama.com) — local model runtime
- [FastAPI](https://fastapi.tiangolo.com) — REST API framework
- [Pydantic](https://docs.pydantic.dev) — data validation
- [httpx](https://www.python-httpx.org) — async HTTP client
- [Streamlit](https://streamlit.io) — frontend UI
- [Plotly](https://plotly.com) — benchmark charts
- [psutil](https://psutil.readthedocs.io) — memory measurement

---

## Full Findings

See [FINDINGS.md](./FINDINGS.md) for the complete benchmark analysis
including per-category breakdowns, quality observations, and
recommendations for model selection.