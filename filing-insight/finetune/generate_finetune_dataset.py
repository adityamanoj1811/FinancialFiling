"""Validate labelled examples and create a reproducible train/validation split."""

import argparse
import json
import random
from pathlib import Path


def read_jsonl(path: Path):
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number} is not valid JSON") from exc
            if not isinstance(row.get("input"), str) or not row["input"].strip():
                raise ValueError(f"{path}:{line_number} needs a non-empty string 'input'")
            target = row.get("target")
            if isinstance(target, dict):
                target = json.dumps(target, ensure_ascii=False, sort_keys=True)
            if not isinstance(target, str) or not target.strip():
                raise ValueError(f"{path}:{line_number} needs 'target' as a JSON object or string")
            try:
                json.loads(target)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number} target must be valid JSON") from exc
            rows.append({"input": row["input"].strip(), "target": target})
    return rows


def write_jsonl(path: Path, rows):
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default="finetune/data")
    parser.add_argument("--input-file", default="annotations.jsonl")
    parser.add_argument("--n-examples", "--n_examples", type=int, default=None)
    parser.add_argument("--validation-fraction", type=float, default=0.15)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if not 0 < args.validation_fraction < 1:
        parser.error("--validation-fraction must be between 0 and 1")
    data_dir = Path(args.data_dir)
    source_path = data_dir / args.input_file
    if not source_path.exists():
        parser.error(f"Missing {source_path}. Add human-reviewed labelled examples first; this tool will not manufacture financial values from filings.")
    rows = read_jsonl(source_path)
    if args.n_examples is not None:
        if args.n_examples < 2:
            parser.error("--n-examples must be at least 2")
        rows = rows[: args.n_examples]
    if len(rows) < 2:
        parser.error("At least two labelled examples are required")
    random.Random(args.seed).shuffle(rows)
    val_size = max(1, round(len(rows) * args.validation_fraction))
    val_rows, train_rows = rows[:val_size], rows[val_size:]
    if not train_rows:
        parser.error("Validation split left no training examples")
    write_jsonl(data_dir / "train.jsonl", train_rows)
    write_jsonl(data_dir / "val.jsonl", val_rows)
    print(f"Wrote {len(train_rows)} train and {len(val_rows)} validation examples to {data_dir}")


if __name__ == "__main__":
    main()
