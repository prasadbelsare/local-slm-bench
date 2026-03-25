import asyncio
import json
import os
import time
from datetime import datetime
from api.ollama_client import generate, AVAILABLE_MODELS
from benchmarks.prompts import PROMPTS

RESULTS_DIR = "benchmarks/results"

def calculate_tokens_per_second(response_text: str, duration_seconds: float) -> float:
    estimated_tokens = len(response_text) / 4
    if duration_seconds == 0:
        return 0.0
    return round(estimated_tokens / duration_seconds, 2)

async def run_single(model: str, prompt_obj: dict) -> dict:
    print(f"  running [{prompt_obj['id']}] on {model}...")

    result = await generate(
        prompt=prompt_obj["prompt"],
        model=model
    )

    if hasattr(result, "error"):
        return {
            "model": model,
            "prompt_id": prompt_obj["id"],
            "category": prompt_obj["category"],
            "prompt": prompt_obj["prompt"],
            "response": None,
            "duration_seconds": None,
            "time_to_first_token": None,
            "tokens_per_second": None,
            "response_length": None,
            "status": "error",
            "error": result.error
        }

    tokens_per_sec = calculate_tokens_per_second(
        result.response,
        result.duration_seconds
    )

    return {
        "model": model,
        "prompt_id": prompt_obj["id"],
        "category": prompt_obj["category"],
        "prompt": prompt_obj["prompt"],
        "response": result.response,
        "duration_seconds": result.duration_seconds,
        "time_to_first_token": result.time_to_first_token,
        "tokens_per_second": tokens_per_sec,
        "response_length": len(result.response),
        "status": "success",
        "error": None
    }

async def run_benchmark():
    print(f"\nStarting benchmark...")
    print(f"Models: {AVAILABLE_MODELS}")
    print(f"Prompts: {len(PROMPTS)}")
    print(f"Total runs: {len(AVAILABLE_MODELS) * len(PROMPTS)}\n")

    all_results = []
    total = len(AVAILABLE_MODELS) * len(PROMPTS)
    completed = 0

    for model in AVAILABLE_MODELS:
        print(f"\nRunning {model}...")
        for prompt_obj in PROMPTS:
            result = await run_single(model, prompt_obj)
            all_results.append(result)
            completed += 1

            status = "ok" if result["status"] == "success" else "err"
            duration = result["duration_seconds"] or "N/A"
            tps = result["tokens_per_second"] or "N/A"
            ttft = result.get("time_to_first_token") or "N/A"

            print(f"  {status} [{prompt_obj['id']}] {duration}s | ttft={ttft}s | {tps} tok/s")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{RESULTS_DIR}/benchmark_{timestamp}.json"

    os.makedirs(RESULTS_DIR, exist_ok=True)

    summary = {
        "timestamp": timestamp,
        "total_runs": total,
        "successful_runs": sum(1 for r in all_results if r["status"] == "success"),
        "models": AVAILABLE_MODELS,
        "prompt_count": len(PROMPTS),
        "results": all_results
    }

    with open(filename, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nBenchmark done.")
    print(f"Results saved to: {filename}")
    print(f"Successful runs: {summary['successful_runs']}/{total}")

    return summary

if __name__ == "__main__":
    asyncio.run(run_benchmark())