import asyncio
import json
import os
import psutil
import time
from datetime import datetime
from api.ollama_client import generate
from api.constants import AVAILABLE_MODELS, MEMORY_MEASUREMENT_PROMPTS

RESULTS_DIR = "experiments/results"

def get_ollama_ram_mb() -> float:
    total_mb = 0.0
    for proc in psutil.process_iter(['name', 'cmdline', 'memory_info']):
        try:
            name = proc.info['name'].lower()
            cmdline = ' '.join(proc.info['cmdline'] or []).lower()
            if 'ollama' in name or 'ollama' in cmdline:
                total_mb += proc.info['memory_info'].rss / 1024 / 1024
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return round(total_mb, 2)
def get_system_ram() -> dict:
    ram = psutil.virtual_memory()
    return {
        "total_gb": round(ram.total / 1024**3, 2),
        "available_gb": round(ram.available / 1024**3, 2),
        "used_percent": ram.percent
    }

async def measure_model_memory(model: str) -> dict:
    print(f"\nMeasuring: {model}")
    results = []

    for prompt in MEMORY_MEASUREMENT_PROMPTS:
        # Measure Ollama process before call
        ollama_before_mb = get_ollama_ram_mb()
        system_before = get_system_ram()

        start = time.time()
        result = await generate(prompt=prompt, model=model)
        duration = round(time.time() - start, 2)

        # Measure Ollama process after call
        ollama_after_mb = get_ollama_ram_mb()
        system_after = get_system_ram()

        ollama_delta_mb = round(ollama_after_mb - ollama_before_mb, 2)

        entry = {
            "model": model,
            "prompt": prompt[:50] + "...",
            "duration_seconds": duration,
            "ollama_ram_before_mb": ollama_before_mb,
            "ollama_ram_after_mb": ollama_after_mb,
            "ollama_ram_delta_mb": ollama_delta_mb,
            "system_ram_used_before_percent": system_before["used_percent"],
            "system_ram_used_after_percent": system_after["used_percent"],
        }

        results.append(entry)
        print(f"  prompt: {prompt[:40]}...")
        print(f"  duration: {duration}s")
        print(f"  ollama RAM: {ollama_before_mb}MB → {ollama_after_mb}MB (delta: {ollama_delta_mb}MB)")
        print(f"  system RAM: {system_before['used_percent']}% → {system_after['used_percent']}%")

    return results

async def run_memory_experiment():
    print("\n Memory Usage Experiment ")
    print(f"Models: {AVAILABLE_MODELS}")
    print(f"Prompts per model: {len(MEMORY_MEASUREMENT_PROMPTS)}")

    system_info = get_system_ram()
    print(f"\nSystem RAM: {system_info['total_gb']}GB total, "
          f"{system_info['available_gb']}GB available, "
          f"{system_info['used_percent']}% used\n")

    all_results = []

    for model in AVAILABLE_MODELS:
        model_results = await measure_model_memory(model)
        all_results.extend(model_results)

    print("\n Memory Summary ")
    for model in AVAILABLE_MODELS:
        model_data = [r for r in all_results if r["model"] == model]
        avg_ollama_mb = round(
            sum(r["ollama_ram_after_mb"] for r in model_data) / len(model_data), 2
        )
        avg_duration = round(
            sum(r["duration_seconds"] for r in model_data) / len(model_data), 2
        )
        print(f"{model}: ollama avg RAM={avg_ollama_mb}MB, avg duration={avg_duration}s")

    # Save results
    os.makedirs(RESULTS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{RESULTS_DIR}/memory_{timestamp}.json"

    summary = {
        "timestamp": timestamp,
        "system": get_system_ram(),
        "results": all_results
    }

    with open(filename, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nResults saved to: {filename}")

if __name__ == "__main__":
    asyncio.run(run_memory_experiment())