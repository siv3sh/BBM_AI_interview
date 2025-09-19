import re
import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from datetime import datetime
from rouge_score import rouge_scorer
from sentence_transformers import SentenceTransformer, util

# ---------------- Embedding Model ----------------
_embedder = SentenceTransformer("all-MiniLM-L6-v2")

# ---------------- Text Normalization ----------------
def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return " ".join(text.split())

# ---------------- Metrics ----------------
def exact_match(pred: str, gold: str) -> float:
    return float(normalize_text(pred) == normalize_text(gold))

def f1_metric(pred: str, gold: str) -> float:
    pred_tokens = normalize_text(pred).split()
    gold_tokens = normalize_text(gold).split()
    common = set(pred_tokens) & set(gold_tokens)
    if not pred_tokens or not gold_tokens or not common:
        return 0.0
    precision = len(common) / len(pred_tokens)
    recall = len(common) / len(gold_tokens)
    if precision + recall == 0:
        return 0.0
    return 2 * (precision * recall) / (precision + recall)

def rouge_scores(pred: str, gold: str):
    scorer = rouge_scorer.RougeScorer(["rouge1", "rougeL"], use_stemmer=True)
    scores = scorer.score(gold, pred)
    return {
        "rouge1": scores["rouge1"].fmeasure,
        "rougeL": scores["rougeL"].fmeasure,
    }

def semantic_similarity(pred: str, gold: str) -> float:
    emb_pred = _embedder.encode(pred, convert_to_tensor=True)
    emb_gold = _embedder.encode(gold, convert_to_tensor=True)
    return float(util.cos_sim(emb_pred, emb_gold).item())

# ---------------- Combined Evaluation ----------------
def evaluate(pred: str, gold: str) -> dict:
    results = {
        "Exact Match": exact_match(pred, gold),
        "F1 Score": f1_metric(pred, gold),
        "ROUGE-1": rouge_scores(pred, gold)["rouge1"],
        "ROUGE-L": rouge_scores(pred, gold)["rougeL"],
        "Semantic Similarity": semantic_similarity(pred, gold),
    }
    return results

# ---------------- CSV Logging ----------------
def log_results(app_name: str, pred: str, gold: str, results: dict, file_path="evaluation_log.csv"):
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "app": app_name,
        "prediction": pred,
        "ground_truth": gold,
        **results
    }
    df_entry = pd.DataFrame([log_entry])
    if os.path.exists(file_path):
        df_entry.to_csv(file_path, mode="a", header=False, index=False)
    else:
        df_entry.to_csv(file_path, index=False)
    return log_entry

# ---------------- Visualization ----------------
def plot_metrics(results: dict, title="Evaluation Metrics"):
    df = pd.DataFrame(list(results.items()), columns=["Metric", "Score"])
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.barplot(x="Metric", y="Score", hue="Metric", data=df,
                palette="viridis", legend=False, ax=ax)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_ylim(0, 1)
    ax.set_ylabel("Score")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha="right")
    plt.tight_layout()
    return fig

def radar_plot(results: dict, title="Metric Radar Chart"):
    metrics = list(results.keys())
    values = list(results.values())
    values += values[:1]
    angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
    angles += angles[:1]
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.plot(angles, values, "o-", linewidth=2, label="LLM")
    ax.fill(angles, values, alpha=0.25)
    ax.set_thetagrids(np.degrees(angles[:-1]), metrics)
    ax.set_title(title, size=14, fontweight="bold")
    ax.set_ylim(0, 1)
    return fig

# ---------------- Example Evaluations ----------------
def run_examples():
    examples = {
        "agenticATS.py": (
            "Python, SQL, Machine Learning",
            "Python, SQL, Machine Learning, AWS"
        ),
        "Chat.py": (
            "The capital of France is Paris.",
            "Paris is the capital of France."
        ),
        "dashboard.py": (
            "Placement rate is 80%, Google hired the most students.",
            "80% students placed, majority hired by Google."
        ),
        "interview.py": (
            "Candidate mentioned Python, SQL but missed ML pipelines.",
            "Candidate knows Python and SQL, but lacked ML pipeline details."
        ),
    }
    return examples

# ---------------- Streamlit Dashboard ----------------
def main():
    st.set_page_config(page_title="LLM Evaluation Dashboard", page_icon="📊", layout="wide")

    st.markdown("""
    <style>
    .main {background-color: #f9f9f9;}
    h1 {color: #4CAF50;}
    h2 {color: #333;}
    .stButton>button {background-color: #4CAF50; color: white; font-weight: bold;}
    .stButton>button:hover {background-color: #45a049;}
    </style>
    """, unsafe_allow_html=True)

    st.title("📊 Unified LLM Evaluation Dashboard")
    st.write("Automatically evaluating predictions from **agenticATS**, **Chat**, **Dashboard**, and **Interview Assistant** apps.")

    examples = run_examples()

    for app_name, (pred, gold) in examples.items():
        st.header(f"📌 {app_name}")
        results = evaluate(pred, gold)
        log_results(app_name, pred, gold, results)

        col1, col2 = st.columns([1,1])
        with col1:
            st.subheader("📋 Metrics")
            st.json(results)
        with col2:
            st.pyplot(plot_metrics(results, title=f"{app_name} - Bar Chart"))

        st.pyplot(radar_plot(results, title=f"{app_name} - Radar Chart"))

    st.header("📑 Evaluation Logs")
    if os.path.exists("evaluation_log.csv"):
        df_logs = pd.read_csv("evaluation_log.csv")
        st.dataframe(df_logs.tail(20))
    else:
        st.info("No logs yet. Run evaluations to generate logs.")

if __name__ == "__main__":
    main()
