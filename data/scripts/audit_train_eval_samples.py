from pathlib import Path
import json
import random
import re

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TRAIN_PATH = PROJECT_ROOT / "data/processed/claracare_train_final.jsonl"
EVAL_PATH = PROJECT_ROOT / "data/processed/claracare_eval_final.jsonl"
OUT_PATH = PROJECT_ROOT / "data/reports/audit_train_eval_50.md"

TRAIN_N = 30
EVAL_N = 20


def load_jsonl(path: Path) -> list[dict]:
    assert path.exists(), f"Missing file: {path}"
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def normalize_key(text: str) -> str:
    cleaned = " ".join(str(text).strip().lower().split())
    return re.sub(r"[.!?;:,\s]+$", "", cleaned)


def dedupe(rows: list[dict]) -> list[dict]:
    seen = set()
    out = []
    for r in rows:
        key = normalize_key(r["instruction"])
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def sample_rows(rows: list[dict], n: int, rng: random.Random) -> list[dict]:
    assert len(rows) >= n, f"Need at least {n} rows, got {len(rows)}"
    return rng.sample(rows, n)


def render_sample(idx: int, split: str, row: dict) -> list[str]:
    return [
        f"## Sample {idx}",
        f"- Split: {split}",
        f"- Source: {row.get('source', 'unknown')}",
        f"- Topic: {row.get('topic', 'TODO')}",
        f"- Instruction: {str(row['instruction']).strip()}",
        f"- Output: {str(row['output']).strip()}",
        "- Checklist:",
        "  - Readable and simple? [TODO]",
        "  - Diabetes-centered? [TODO]",
        "  - Tone consistent with ClaraCare? [TODO]",
        "  - Unsafe advice or dosage? [TODO]",
        "  - Duplicative/near-duplicate? [TODO]",
        "  - Keep? [TODO]",
        "- Reviewer note: TODO",
        "",
    ]


def main() -> None:
    train_rows = dedupe(load_jsonl(TRAIN_PATH))
    eval_rows = dedupe(load_jsonl(EVAL_PATH))

    rng = random.Random(42)
    sampled_train = sample_rows(train_rows, TRAIN_N, rng)
    sampled_eval = sample_rows(eval_rows, EVAL_N, rng)

    lines = [
        "# Train/Eval Manual Audit (50 Samples)",
        "",
        "Review this before any SFT run.",
        "",
        f"- Train samples: {len(sampled_train)}",
        f"- Eval samples: {len(sampled_eval)}",
        "",
    ]

    all_rows = [("train", r) for r in sampled_train] + [("eval", r) for r in sampled_eval]
    rng.shuffle(all_rows)
    for i, (split, row) in enumerate(all_rows, start=1):
        lines.extend(render_sample(i, split, row))

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved: {OUT_PATH}")


if __name__ == "__main__":
    main()
