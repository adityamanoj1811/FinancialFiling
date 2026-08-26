"""Offline structured extraction backed by a locally fine-tuned Seq2Seq model."""

import json
from functools import lru_cache
from pathlib import Path

import torch

from backend.config import FINANCIAL_METRICS


def detect_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


@lru_cache(maxsize=1)
def load_local_model(model_dir: str = "finetune/model"):
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
    path = Path(model_dir)
    if not path.is_dir():
        raise FileNotFoundError(f"Local model is not available at {path}. Train it first.")
    device = detect_device()
    tokenizer = AutoTokenizer.from_pretrained(path)
    model = AutoModelForSeq2SeqLM.from_pretrained(path).to(device).eval()
    return tokenizer, model, device


def extract_metrics_locally(vector_store, source_name: str, model_dir: str = "finetune/model") -> dict[str, str]:
    chunks = vector_store.search("revenue profit EBITDA EPS debt assets reporting period", top_k=8, source_filter=source_name)
    context = "\n---\n".join(chunk["text"] for chunk in chunks)
    prompt = "Extract the requested financial metrics as JSON only.\nFILING EXCERPTS:\n" + context
    tokenizer, model, device = load_local_model(model_dir)
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=256).to(device)
    with torch.inference_mode():
        generated = model.generate(**inputs, max_new_tokens=256, do_sample=False)
    raw = tokenizer.decode(generated[0], skip_special_tokens=True).strip()
    try:
        extracted = json.loads(raw)
    except json.JSONDecodeError:
        extracted = {}
    return {metric: str(extracted.get(metric) or "Not Found") for metric in FINANCIAL_METRICS}
