from pathlib import Path
import json
import random

from datasets import load_dataset

from data.scripts.clean import is_diabetes_focused

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TRAIN_PATH = PROJECT_ROOT / "data/processed/claracare_train.jsonl"
EVAL_PATH = PROJECT_ROOT / "data/processed/claracare_eval.jsonl"
SYNTHETIC_PATH = PROJECT_ROOT / "data/processed/synthetic.jsonl"


def save_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(dict(r), ensure_ascii=False) + "\n")


def is_concise_diabetes_question(record):
    instruction = str(record["instruction"]).strip()
    return "\n" not in instruction and instruction.endswith("?") and len(instruction.split()) <= 22


def dedupe_by_instruction(rows):
    seen = set()
    deduped = []
    for r in rows:
        key = str(r["instruction"]).strip().lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(r)
    return deduped


def main():
    assert TRAIN_PATH.exists(), f"Missing train file: {TRAIN_PATH}"
    assert SYNTHETIC_PATH.exists(), f"Missing synthetic file: {SYNTHETIC_PATH}"

    raw_ds = load_dataset("json", data_files=str(TRAIN_PATH), split="train")
    synthetic_ds = load_dataset("json", data_files=str(SYNTHETIC_PATH), split="train")

    filtered = [r for r in raw_ds if is_diabetes_focused(r) and is_concise_diabetes_question(r)]
    synthetic_filtered = [r for r in synthetic_ds if is_diabetes_focused(r) and is_concise_diabetes_question(r)]
    filtered = filtered + synthetic_filtered
    print("Before:", len(raw_ds))
    print("After:", len(filtered))

    for i, r in enumerate(filtered[:20]):
        print(f"\n--- {i}")
        print("Q:", str(r["instruction"])[:300])
        print("A:", str(r["output"])[:300])

    random.seed(42)
    random.shuffle(filtered)
    eval_size = min(180, max(120, int(len(filtered) * 0.08), 1))
    eval_size = min(eval_size, max(1, len(filtered) - 1))

    eval_rows = filtered[:eval_size]
    train_rows = filtered[eval_size:]

    TRAIN_PATH.parent.mkdir(parents=True, exist_ok=True)
    save_jsonl(TRAIN_PATH, train_rows)
    save_jsonl(EVAL_PATH, eval_rows)

    print("Train:", len(train_rows))
    print("Eval:", len(eval_rows))


if __name__ == "__main__":
    main()
