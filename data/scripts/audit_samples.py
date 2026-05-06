from pathlib import Path
import json
import random
import re

PROJECT_ROOT = Path(__file__).resolve().parents[2]

HF_CLEAN = PROJECT_ROOT / "data/processed/hf_diabetes_clean.jsonl"
CURRENT_REAL = PROJECT_ROOT / "data/processed/cleaned_real.jsonl"

AUDIT_REPORT = PROJECT_ROOT / "data/reports/audit_50_samples.md"

TOTAL_SAMPLES = 50
TARGET_HF = 30
TARGET_REAL = 20


def load_jsonl(path: Path) -> list[dict]:
    assert path.exists(), f"Missing required file: {path}"
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def normalize_key(text: str) -> str:
    cleaned = " ".join(str(text).strip().lower().split())
    cleaned = re.sub(r"[.!?;:,\s]+$", "", cleaned)
    return cleaned


def dedupe_by_instruction(rows: list[dict]) -> list[dict]:
    seen = set()
    out = []
    for row in rows:
        key = normalize_key(row["instruction"])
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    return out


def sample_n(rows: list[dict], n: int, rng: random.Random) -> list[dict]:
    if n <= 0 or not rows:
        return []
    if len(rows) <= n:
        out = list(rows)
        rng.shuffle(out)
        return out
    return rng.sample(rows, n)


def allocate_counts(available: dict[str, int]) -> dict[str, int]:
    targets = {"hf": TARGET_HF, "real": TARGET_REAL}
    alloc = {k: min(targets[k], available.get(k, 0)) for k in targets}
    total = sum(alloc.values())
    if total == TOTAL_SAMPLES:
        return alloc

    remaining = TOTAL_SAMPLES - total
    pools = ["hf", "real"]
    while remaining > 0:
        progressed = False
        for key in pools:
            if alloc[key] < available.get(key, 0):
                alloc[key] += 1
                remaining -= 1
                progressed = True
                if remaining == 0:
                    break
        if not progressed:
            break
    return alloc


def row_topic(row: dict) -> str:
    topic = str(row.get("topic", "")).strip()
    return topic if topic else "TODO"


def write_sample_block(lines: list[str], sample_id: int, source_name: str, row: dict) -> None:
    lines.extend(
        [
            f"## Sample {sample_id}",
            f"- Sample ID: {sample_id}",
            f"- Source: {source_name}",
            f"- Topic: {row_topic(row)}",
            f"- Instruction: {str(row['instruction']).strip()}",
            f"- Output: {str(row['output']).strip()}",
            "- Checklist:",
            "  - Diabetes-centered? [TODO]",
            "  - Patient-facing? [TODO]",
            "  - Simple language? [TODO]",
            "  - Unsafe dosage advice? [TODO]",
            "  - Too much jargon? [TODO]",
            "  - Keep? [TODO]",
            "- Reviewer note: TODO",
            "",
        ]
    )


def main() -> None:
    hf_rows = dedupe_by_instruction(load_jsonl(HF_CLEAN))
    current_rows = dedupe_by_instruction(load_jsonl(CURRENT_REAL))
    current_real_rows = current_rows

    available = {"hf": len(hf_rows), "real": len(current_real_rows)}
    alloc = allocate_counts(available)

    rng = random.Random(42)
    sampled_hf = sample_n(hf_rows, alloc["hf"], rng)
    sampled_real = sample_n(current_real_rows, alloc["real"], rng)

    all_samples = [("hf_diabetes_qa", r) for r in sampled_hf]
    all_samples += [("current_real_cleaned", r) for r in sampled_real]
    rng.shuffle(all_samples)

    lines = [
        "# Audit 50 Samples",
        "",
        "Manual review checklist for dataset quality before SFT.",
        "",
        "## Audit Allocation",
        f"- HF samples: {len(sampled_hf)}",
        f"- Current real samples: {len(sampled_real)}",
        "- Synthetic samples: 0 (intentionally excluded)",
        f"- Total samples: {len(all_samples)}",
        "",
    ]

    for idx, (source, row) in enumerate(all_samples, start=1):
        write_sample_block(lines, idx, source, row)

    AUDIT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved: {AUDIT_REPORT}")
    print("Next action: manually review data/reports/audit_50_samples.md before SFT")


if __name__ == "__main__":
    main()
