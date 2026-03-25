import streamlit as st
import httpx
import json
import os
import glob
import pandas as pd
import plotly.express as px
from api.config import STREAMLIT_API_URL
st.set_page_config(
    page_title="Local SLM Bench",
    page_icon="🖥️",
    layout="wide"
)


API_BASE = STREAMLIT_API_URL

MODELS = {
    "tinyllama:1.1b": {
        "label": "TinyLlama 1.1B",
        "size": "600MB",
        "speed": "Fast",
        "best_for": "Speed, simple tasks",
        "ram": "730MB loaded",
        "color": "#5DCAA5"
    },
    "phi3:mini": {
        "label": "Phi3 Mini 3.8B",
        "size": "2.3GB",
        "speed": "Medium",
        "best_for": "Structured output, accuracy",
        "ram": "4.4GB loaded",
        "color": "#7F77DD"
    },
    "mistral:7b-instruct-q4_0": {
        "label": "Mistral 7B",
        "size": "4.1GB",
        "speed": "Slow",
        "best_for": "Quality, clean code",
        "ram": "4.5GB loaded",
        "color": "#D85A30"
    }
}

def call_api(prompt: str, model: str) -> dict:
    try:
        response = httpx.post(
            f"{API_BASE}/generate",
            json={"prompt": prompt, "model": model},
            timeout=180.0
        )
        return response.json()
    except httpx.ConnectError:
        return {"error": "Cannot connect to API. Make sure uvicorn is running."}
    except Exception as e:
        return {"error": str(e)}

def load_latest_benchmark() -> dict | None:
    files = glob.glob("benchmarks/results/benchmark_*.json")
    if not files:
        return None
    latest = max(files, key=os.path.getctime)
    with open(latest) as f:
        return json.load(f)

def compute_model_stats(data: dict) -> dict:
    results = data["results"]
    stats = {}

    for model_id in MODELS.keys():
        model_results = [
            r for r in results
            if r["model"] == model_id and r["status"] == "success"
        ]

        if not model_results:
            continue

        tps_values = [r["tokens_per_second"] for r in model_results if r["tokens_per_second"]]
        dur_values = [r["duration_seconds"] for r in model_results if r["duration_seconds"]]
        ttft_values = [r["time_to_first_token"] for r in model_results if r["time_to_first_token"]]
        len_values = [r["response_length"] for r in model_results if r["response_length"]]

        stats[model_id] = {
            "avg_tps": round(sum(tps_values) / len(tps_values), 1) if tps_values else None,
            "avg_duration": round(sum(dur_values) / len(dur_values), 1) if dur_values else None,
            "avg_ttft": round(sum(ttft_values) / len(ttft_values), 2) if ttft_values else None,
            "avg_response_length": round(sum(len_values) / len(len_values)) if len_values else None,
            "total_runs": len(model_results),
        }

    return stats

page = st.sidebar.selectbox(
    "Navigation",
    ["Chat", "Benchmark Results", "Model Comparison"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Stack**")
st.sidebar.markdown("Ollama · FastAPI · Streamlit")
st.sidebar.markdown("CPU only · 16GB RAM")

# Page 1: Chat
if page == "Chat":
    st.title("Local AI Chat")
    

    col1, col2 = st.columns([3, 1])

    with col2:
        selected_model = st.selectbox(
            "Model",
            options=list(MODELS.keys()),
            format_func=lambda x: MODELS[x]["label"]
        )
        st.caption(f"Size: {MODELS[selected_model]['size']}")
        st.caption(f"RAM: {MODELS[selected_model]['ram']}")
        st.caption(f"Best for: {MODELS[selected_model]['best_for']}")

    with col1:
        prompt = st.text_area(
            "Your prompt",
            placeholder="Ask anything...",
            height=120
        )

        if st.button("Generate", type="primary"):
            if not prompt.strip():
                st.warning("Please enter a prompt.")
            else:
                with st.spinner(f"Waiting for {MODELS[selected_model]['label']}..."):
                    result = call_api(prompt, selected_model)

                if "error" in result:
                    st.error(result["error"])
                else:
                    st.markdown("### Response")
                    st.write(result["response"])

                    st.markdown("---")
                    m1, m2, m3 = st.columns(3)
                    with m1:
                        st.metric("Total time", f"{result['duration_seconds']}s")
                    with m2:
                        ttft = result.get("time_to_first_token")
                        st.metric("Time to first token", f"{ttft}s" if ttft else "N/A")
                    with m3:
                        chars = len(result["response"])
                        st.metric("Response length", f"{chars} chars")

# Page 2: Benchmark Results 
elif page == "Benchmark Results":
    st.title("Benchmark Results")
    st.caption("120 runs across 3 models and 40 real-world prompts")

    data = load_latest_benchmark()

    if not data:
        st.warning("No benchmark results found. Run python -m benchmarks.runner first.")
    else:
        results = data["results"]
        df = pd.DataFrame(results)
        df = df[df["status"] == "success"]

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Total runs", data["total_runs"])
        with c2:
            st.metric("Successful", data["successful_runs"])
        with c3:
            tiny_avg = df[df["model"] == "tinyllama:1.1b"]["tokens_per_second"].mean()
            st.metric("TinyLlama avg tok/s", f"{tiny_avg:.1f}")
        with c4:
            mist_avg = df[df["model"] == "mistral:7b-instruct-q4_0"]["tokens_per_second"].mean()
            st.metric("Mistral avg tok/s", f"{mist_avg:.1f}")

        st.markdown("---")

        st.subheader("Tokens per second by category")
        tps_df = df.groupby(["model", "category"])["tokens_per_second"].mean().reset_index()
        tps_df["model_label"] = tps_df["model"].map({
            "tinyllama:1.1b": "TinyLlama",
            "phi3:mini": "Phi3 Mini",
            "mistral:7b-instruct-q4_0": "Mistral 7B"
        })
        fig1 = px.bar(
            tps_df,
            x="category",
            y="tokens_per_second",
            color="model_label",
            barmode="group",
            color_discrete_map={
                "TinyLlama": "#5DCAA5",
                "Phi3 Mini": "#7F77DD",
                "Mistral 7B": "#D85A30"
            },
            labels={"tokens_per_second": "tokens/sec", "category": ""}
        )
        fig1.update_layout(
            legend_title="Model",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("Average response time by category (seconds)")
        dur_df = df.groupby(["model", "category"])["duration_seconds"].mean().reset_index()
        dur_df["model_label"] = dur_df["model"].map({
            "tinyllama:1.1b": "TinyLlama",
            "phi3:mini": "Phi3 Mini",
            "mistral:7b-instruct-q4_0": "Mistral 7B"
        })
        fig2 = px.bar(
            dur_df,
            x="category",
            y="duration_seconds",
            color="model_label",
            barmode="group",
            color_discrete_map={
                "TinyLlama": "#5DCAA5",
                "Phi3 Mini": "#7F77DD",
                "Mistral 7B": "#D85A30"
            },
            labels={"duration_seconds": "seconds", "category": ""}
        )
        fig2.update_layout(
            legend_title="Model",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Time to first token by model (seconds)")
        ttft_df = df.dropna(subset=["time_to_first_token"])
        ttft_avg = ttft_df.groupby("model")["time_to_first_token"].mean().reset_index()
        ttft_avg["model_label"] = ttft_avg["model"].map({
            "tinyllama:1.1b": "TinyLlama",
            "phi3:mini": "Phi3 Mini",
            "mistral:7b-instruct-q4_0": "Mistral 7B"
        })
        fig3 = px.bar(
            ttft_avg,
            x="model_label",
            y="time_to_first_token",
            color="model_label",
            color_discrete_map={
                "TinyLlama": "#5DCAA5",
                "Phi3 Mini": "#7F77DD",
                "Mistral 7B": "#D85A30"
            },
            labels={"time_to_first_token": "seconds", "model_label": ""}
        )
        fig3.update_layout(
            showlegend=False,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig3, use_container_width=True)

        st.subheader("Raw results")
        display_df = df[[
            "model", "category", "prompt_id",
            "duration_seconds", "time_to_first_token", "tokens_per_second"
        ]].copy()
        display_df["model"] = display_df["model"].map({
            "tinyllama:1.1b": "TinyLlama",
            "phi3:mini": "Phi3 Mini",
            "mistral:7b-instruct-q4_0": "Mistral 7B"
        })
        st.dataframe(display_df, use_container_width=True)

# Page 3: Model Comparison
elif page == "Model Comparison":
    st.title("Model Comparison")
    st.caption("Based on 120 benchmark runs on CPU-only hardware")

    col1, col2, col3 = st.columns(3)

    for col, (model_id, info) in zip([col1, col2, col3], MODELS.items()):
        with col:
            st.markdown(
                f"""
                <div style="
                    border: 1px solid {info['color']};
                    border-radius: 8px;
                    padding: 1.2rem;
                    margin-bottom: 1rem;
                ">
                    <h3 style="color: {info['color']}; margin-top: 0;">
                        {info['label']}
                    </h3>
                    <p style="font-size: 13px; color: #888; margin: 0 0 12px;">
                        {model_id}
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.metric("Disk size", info["size"])
            st.metric("RAM when loaded", info["ram"])
            st.markdown(f"**Best for:** {info['best_for']}")

    st.markdown("---")
    st.subheader("Performance metrics from benchmark")

    data = load_latest_benchmark()

    if not data:
        st.warning("No benchmark data found. Run the benchmark first.")
    else:
        stats = compute_model_stats(data)

        comparison_data = {
            "Metric": [
                "Avg tokens per second",
                "Avg time to first token",
                "Avg total duration",
                "Avg response length",
                "Total runs"
            ]
        }

        for model_id, info in MODELS.items():
            s = stats.get(model_id, {})
            comparison_data[info["label"]] = [
                f"{s.get('avg_tps', 'N/A')} tok/s",
                f"{s.get('avg_ttft', 'N/A')}s",
                f"{s.get('avg_duration', 'N/A')}s",
                f"{s.get('avg_response_length', 'N/A')} chars",
                str(s.get('total_runs', 'N/A'))
            ]

        st.dataframe(
            pd.DataFrame(comparison_data).set_index("Metric"),
            use_container_width=True
        )

    st.markdown("---")
    st.subheader("Qualitative findings from benchmark")

    comparison_quality = {
        "Criteria": [
            "Follows system prompts",
            "JSON schema compliance",
            "Reasoning accuracy",
            "Code quality",
            "Instruction following",
            "Language consistency",
        ],
        "TinyLlama": [
            "No", "Needs retry", "Poor", "Verbose", "Inconsistent", "Unreliable"
        ],
        "Phi3 Mini": [
            "Yes", "First attempt", "Good", "Good", "Good", "Reliable"
        ],
        "Mistral 7B": [
            "Yes", "First attempt", "Good", "Best", "Best", "Reliable"
        ]
    }

    st.dataframe(
        pd.DataFrame(comparison_quality).set_index("Criteria"),
        use_container_width=True
    )

    st.markdown("---")
    st.subheader("When to use each model")

    u1, u2, u3 = st.columns(3)
    with u1:
        st.markdown("**TinyLlama** is the right choice when speed is the only priority and output quality is less critical. Good for draft generation or tasks where a human reviews the output. The only viable option on hardware with less than 8GB RAM.")
    with u2:
        st.markdown("**Phi3 Mini** is the best balance for most production use cases on CPU. Reliable JSON schema compliance on first attempt, good reasoning, and 2x faster than Mistral. Best for structured output pipelines and privacy-sensitive internal tools.")
    with u3:
        st.markdown("**Mistral 7B** produces the cleanest outputs across code, customer support, and HR tasks. Best instruction following — it stops when the task is done. Right choice for batch processing where latency is acceptable and quality matters most.")