from pathlib import Path
import json

from transformers import AutoTokenizer

from util.prompting import format_sft

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TRAIN_PATH = PROJECT_ROOT / "data/processed/claracare_train_final.jsonl"
TOKEN_STATS_PATH = PROJECT_ROOT / "data/reports/token_length_stats.json"
TOKENIZER_NAME = "mistralai/Mistral-7B-Instruct-v0.3"


def load_jsonl(path: Path) -> list[dict]:
    assert path.exists(), f"Missing file: {path}"
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def percentile(sorted_vals: list[int], p: float) -> int:
    assert sorted_vals, "Cannot compute percentile on empty list"
    idx = min(len(sorted_vals) - 1, int(p * len(sorted_vals)))
    return sorted_vals[idx]


def main() -> None:
    rows = load_jsonl(TRAIN_PATH)
    assert rows, "Train dataset is empty"
    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_NAME, use_fast=True)

    lengths = [len(tokenizer(format_sft(r))["input_ids"]) for r in rows]
    lengths_sorted = sorted(lengths)
    total = len(lengths_sorted)

    stats = {
        "tokenizer": TOKENIZER_NAME,
        "num_samples": total,
        "mean": sum(lengths_sorted) / total,
        "p50": percentile(lengths_sorted, 0.50),
        "p90": percentile(lengths_sorted, 0.90),
        "p95": percentile(lengths_sorted, 0.95),
        "p99": percentile(lengths_sorted, 0.99),
        "max": max(lengths_sorted),
        "count_gt_512": sum(1 for x in lengths_sorted if x > 512),
        "count_gt_768": sum(1 for x in lengths_sorted if x > 768),
        "count_gt_1024": sum(1 for x in lengths_sorted if x > 1024),
    }

    TOKEN_STATS_PATH.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_STATS_PATH.write_text(json.dumps(stats, indent=2), encoding="utf-8")

    print("Samples:", stats["num_samples"])
    print("Mean:", round(stats["mean"], 2))
    print("P95:", stats["p95"])
    print("Max:", stats["max"])
    print(">512:", stats["count_gt_512"])
    print(">768:", stats["count_gt_768"])
    print(">1024:", stats["count_gt_1024"])
    print(f"Saved: {TOKEN_STATS_PATH}")


if __name__ == "__main__":
    main()
