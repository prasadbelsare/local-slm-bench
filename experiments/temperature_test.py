import asyncio
import json
import os
from datetime import datetime
from api.ollama_client import generate
from api.constants import AVAILABLE_MODELS, TEMPERATURE_PROMPTS, TEMPERATURES, RUNS_PER_TEMP

RESULTS_DIR = "experiments/results"

async def run_temperature_experiment():
    print("\n=== Temperature Experiment ===")
    print(f"Prompts: {len(TEMPERATURE_PROMPTS)}")
    print(f"Temperatures: {TEMPERATURES}")
    print(f"Runs per temp: {RUNS_PER_TEMP}")
    print(f"Models: {AVAILABLE_MODELS}\n")

    all_results = []

    for model in AVAILABLE_MODELS:
        print(f"\n--- Model: {model} ---")
        for temp in TEMPERATURES:
            print(f"\n  Temperature: {temp}")
            for prompt_obj in TEMPERATURE_PROMPTS:
                responses = []
                for run in range(RUNS_PER_TEMP):
                    result = await generate(
                        prompt=prompt_obj["prompt"],
                        model=model
                    )
                    if hasattr(result, "error"):
                        responses.append(None)
                    else:
                        responses.append(result.response.strip())

                unique_responses = list(set(r for r in responses if r))
                is_deterministic = len(unique_responses) == 1

                entry = {
                    "model": model,
                    "prompt_id": prompt_obj["id"],
                    "prompt": prompt_obj["prompt"],
                    "temperature": temp,
                    "responses": responses,
                    "unique_response_count": len(unique_responses),
                    "is_deterministic": is_deterministic
                }

                all_results.append(entry)
                det_label = "deterministic" if is_deterministic else f"{len(unique_responses)} unique responses"
                print(f"    [{prompt_obj['id']}] {det_label}")

    os.makedirs(RESULTS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{RESULTS_DIR}/temperature_{timestamp}.json"

    with open(filename, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n=== Experiment Complete ===")
    print(f"Results saved to: {filename}")

    print("\n=== Summary ===")
    for model in AVAILABLE_MODELS:
        print(f"\n{model}:")
        for temp in TEMPERATURES:
            model_temp_results = [
                r for r in all_results
                if r["model"] == model and r["temperature"] == temp
            ]
            det_count = sum(1 for r in model_temp_results if r["is_deterministic"])
            total = len(model_temp_results)
            print(f"  temp={temp}: {det_count}/{total} prompts deterministic")

if __name__ == "__main__":
    asyncio.run(run_temperature_experiment())