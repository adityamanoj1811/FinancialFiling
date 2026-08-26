"""Fine-tune a Flan-T5 model locally for structured financial metric extraction."""

import argparse
import inspect
import json
from pathlib import Path

import numpy as np
import torch
from datasets import Dataset
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, DataCollatorForSeq2Seq, Seq2SeqTrainer, Seq2SeqTrainingArguments


def detect_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def load_jsonl(path: Path) -> Dataset:
    with path.open(encoding="utf-8") as handle:
        rows = [json.loads(line) for line in handle if line.strip()]
    if not rows:
        raise ValueError(f"No examples found in {path}")
    return Dataset.from_list(rows)


def metric_scores(eval_predictions, tokenizer):
    predictions, labels = eval_predictions
    if isinstance(predictions, tuple):
        predictions = predictions[0]
    predictions = np.where(predictions != -100, predictions, tokenizer.pad_token_id)
    labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
    predicted_text = tokenizer.batch_decode(predictions, skip_special_tokens=True)
    label_text = tokenizer.batch_decode(labels, skip_special_tokens=True)
    exact_matches = sum(p.strip() == y.strip() for p, y in zip(predicted_text, label_text))
    correct_fields = total_fields = 0
    for predicted, expected in zip(predicted_text, label_text):
        try:
            predicted_json, expected_json = json.loads(predicted), json.loads(expected)
        except json.JSONDecodeError:
            continue
        for key, value in expected_json.items():
            total_fields += 1
            correct_fields += predicted_json.get(key) == value
    return {"exact_match": exact_matches / max(1, len(label_text)), "field_accuracy": correct_fields / max(1, total_fields)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-name", default="google/flan-t5-small")
    parser.add_argument("--data-dir", default="finetune/data")
    parser.add_argument("--output-dir", default="finetune/model")
    parser.add_argument("--epochs", type=int, default=4)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--lr", type=float, default=3e-4)
    parser.add_argument("--max-input-len", type=int, default=256)
    parser.add_argument("--max-target-len", type=int, default=256)
    args = parser.parse_args()
    device = detect_device()
    print(f"Detected device: {device}")
    if device == "cpu":
        print("CPU training enabled. For a quicker first run, use 400–600 examples and 2–3 epochs.")
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.model_name)
    data_dir = Path(args.data_dir)
    train_ds, val_ds = load_jsonl(data_dir / "train.jsonl"), load_jsonl(data_dir / "val.jsonl")
    print(f"Train examples: {len(train_ds)} | Validation examples: {len(val_ds)}")

    def preprocess(batch):
        encoded = tokenizer(batch["input"], max_length=args.max_input_len, truncation=True)
        encoded["labels"] = tokenizer(text_target=batch["target"], max_length=args.max_target_len, truncation=True)["input_ids"]
        return encoded

    train_tok = train_ds.map(preprocess, batched=True, remove_columns=train_ds.column_names)
    val_tok = val_ds.map(preprocess, batched=True, remove_columns=val_ds.column_names)
    argument_names = inspect.signature(Seq2SeqTrainingArguments).parameters
    evaluation_key = "eval_strategy" if "eval_strategy" in argument_names else "evaluation_strategy"
    training_kwargs = {"output_dir": args.output_dir + "_checkpoints", "num_train_epochs": args.epochs, "per_device_train_batch_size": args.batch_size, "per_device_eval_batch_size": args.batch_size, "learning_rate": args.lr, "weight_decay": 0.01, "predict_with_generate": True, "generation_max_length": args.max_target_len, evaluation_key: "epoch", "save_strategy": "epoch", "save_total_limit": 2, "load_best_model_at_end": True, "metric_for_best_model": "field_accuracy", "logging_steps": 25, "report_to": "none", "fp16": device == "cuda"}
    if "use_cpu" in argument_names:
        training_kwargs["use_cpu"] = device == "cpu"
    trainer_kwargs = {"model": model, "args": Seq2SeqTrainingArguments(**training_kwargs), "train_dataset": train_tok, "eval_dataset": val_tok, "data_collator": DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model), "compute_metrics": lambda predictions: metric_scores(predictions, tokenizer)}
    trainer_parameters = inspect.signature(Seq2SeqTrainer).parameters
    if "processing_class" in trainer_parameters:
        trainer_kwargs["processing_class"] = tokenizer
    elif "tokenizer" in trainer_parameters:
        trainer_kwargs["tokenizer"] = tokenizer
    trainer = Seq2SeqTrainer(**trainer_kwargs)
    trainer.train()
    trainer.save_model(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    metrics = trainer.evaluate()
    with (Path(args.output_dir) / "eval_metrics.json").open("w", encoding="utf-8") as handle:
        json.dump(metrics, handle, indent=2)
    print("Final validation metrics:", metrics)


if __name__ == "__main__":
    main()
