"""Evaluate a fine-tuned local extractor using a device detected at runtime."""

import argparse
import json
from pathlib import Path

import numpy as np
import torch
from train_flan_t5 import detect_device, load_jsonl, metric_scores
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-dir", default="finetune/model")
    parser.add_argument("--data-file", default="finetune/data/val.jsonl")
    parser.add_argument("--max-input-len", type=int, default=256)
    parser.add_argument("--max-target-len", type=int, default=256)
    args = parser.parse_args()
    device = torch.device(detect_device())
    print(f"Detected device: {device.type}")
    tokenizer = AutoTokenizer.from_pretrained(args.model_dir)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.model_dir).to(device).eval()
    dataset = load_jsonl(Path(args.data_file))
    predictions, labels = [], []
    with torch.inference_mode():
        for row in dataset:
            inputs = tokenizer(row["input"], return_tensors="pt", truncation=True, max_length=args.max_input_len).to(device)
            output = model.generate(**inputs, max_new_tokens=args.max_target_len)
            predictions.append(output.cpu().numpy()[0])
            labels.append(tokenizer(row["target"], truncation=True, max_length=args.max_target_len)["input_ids"])
    width = max(max(map(len, predictions)), max(map(len, labels)))
    pad = tokenizer.pad_token_id
    padded_predictions = np.array([np.pad(row, (0, width - len(row)), constant_values=pad) for row in predictions])
    padded_labels = np.array([np.pad(row, (0, width - len(row)), constant_values=-100) for row in labels])
    print(json.dumps(metric_scores((padded_predictions, padded_labels), tokenizer), indent=2))


if __name__ == "__main__":
    main()
