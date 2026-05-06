from pathlib import Path
import json
import random
from collections import Counter

from datasets import load_dataset

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REAL_PATH = PROJECT_ROOT / "data/processed/cleaned_real.jsonl"
SYNTHETIC_PATH = PROJECT_ROOT / "data/processed/synthetic.jsonl"
TRAIN_PATH = PROJECT_ROOT / "data/processed/claracare_train.jsonl"
EVAL_PATH = PROJECT_ROOT / "data/processed/claracare_eval.jsonl"

CORE_QUESTION_TERMS = [
    "diabetes",
    "diabetic",
    "type 2",
    "blood sugar",
    "glucose",
    "hba1c",
    "a1c",
    "metformin",
    "insulin",
    "hypoglycemia",
    "hyperglycemia",
]

BAD_TERMS = [
    "pregnancy",
    "pregnant",
    "gestational",
    "vaginal",
    "penis",
    "erection",
    "condom",
    "birth control",
    "pacemaker",
    "bypass",
    "aspirin",
    "heart surgery",
    "fungal",
    "discharge",
    "migraine",
    "vertigo",
]

OFF_TOPIC_MEDICAL_TERMS = [
    "stroke",
    "cancer",
    "tumor",
    "meningitis",
    "angioplasty",
    "liver",
    "gall bladder",
    "prostate",
    "hiv",
    "hepatitis",
    "thyroid",
    "circumcision",
]

SEED_REAL_TARGET = 129
RELAXED_REAL_TARGET = 200
SYNTHETIC_TARGET = 500


def first_question_line(text):
    return str(text).strip().split("\n", 1)[0].strip()


def is_diabetes_focused(record):
    instruction = str(record["instruction"]).lower()
    output = str(record["output"]).lower()
    full_text = instruction + " " + output

    question_is_diabetes_related = any(t in instruction for t in CORE_QUESTION_TERMS)
    has_bad_topic = any(t in full_text for t in BAD_TERMS)
    answer_long_enough = len(output.split()) >= 40

    return question_is_diabetes_related and not has_bad_topic and answer_long_enough


def is_diabetes_centered_question(record):
    first = first_question_line(record["instruction"]).lower()
    return first.endswith("?") and any(t in first for t in CORE_QUESTION_TERMS)


def score_real_record(record):
    first = first_question_line(record["instruction"]).lower()
    output = str(record["output"]).lower()
    score = 0
    score += sum(3 for t in CORE_QUESTION_TERMS if t in first)
    score += sum(1 for t in CORE_QUESTION_TERMS if t in output)
    score -= sum(3 for t in OFF_TOPIC_MEDICAL_TERMS if t in first)
    score -= max(0, (len(first.split()) - 16) // 3)
    return score


def dedupe_by_instruction(rows):
    seen = set()
    out = []
    for r in rows:
        key = first_question_line(r["instruction"]).strip().lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(dict(r))
    return out


def save_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(dict(r), ensure_ascii=False) + "\n")


def audit_preview(rows, n=50):
    print(f"\nAudit sample ({min(n, len(rows))} rows):")
    for i, r in enumerate(rows[:n]):
        print(f"\n--- {i}")
        print("Q:", first_question_line(r["instruction"])[:280])
        print("A:", str(r["output"])[:280])


def main():
    assert REAL_PATH.exists(), f"Missing real data file: {REAL_PATH}"
    assert SYNTHETIC_PATH.exists(), f"Missing synthetic data file: {SYNTHETIC_PATH}"
    assert EVAL_PATH.exists(), f"Missing eval data file: {EVAL_PATH}"

    real_ds = load_dataset("json", data_files=str(REAL_PATH), split="train")
    synthetic_ds = load_dataset("json", data_files=str(SYNTHETIC_PATH), split="train")
    eval_rows = [dict(r) for r in load_dataset("json", data_files=str(EVAL_PATH), split="train")]
    eval_instruction_set = {first_question_line(r["instruction"]).lower() for r in eval_rows}

    real_candidates = [
        dict(r)
        for r in real_ds
        if is_diabetes_focused(r) and is_diabetes_centered_question(r)
    ]
    real_candidates = dedupe_by_instruction(real_candidates)
    real_candidates = [
        r
        for r in real_candidates
        if first_question_line(r["instruction"]).lower() not in eval_instruction_set
    ]
    real_candidates.sort(
        key=lambda r: (
            -score_real_record(r),
            len(first_question_line(r["instruction"]).split()),
            first_question_line(r["instruction"]).lower(),
        )
    )

    seed_real = real_candidates[:SEED_REAL_TARGET]
    relaxed_real = real_candidates[SEED_REAL_TARGET : SEED_REAL_TARGET + RELAXED_REAL_TARGET]

    synthetic_candidates = [
        dict(r)
        for r in synthetic_ds
        if is_diabetes_focused(r) and is_diabetes_centered_question(r)
    ]
    synthetic_candidates = dedupe_by_instruction(synthetic_candidates)
    synthetic_candidates = [
        r
        for r in synthetic_candidates
        if first_question_line(r["instruction"]).lower() not in eval_instruction_set
    ]

    random.seed(42)
    random.shuffle(synthetic_candidates)
    synthetic_selected = synthetic_candidates[:SYNTHETIC_TARGET]

    assert len(seed_real) == SEED_REAL_TARGET, (
        f"Not enough seed real records: expected {SEED_REAL_TARGET}, got {len(seed_real)}"
    )
    assert len(synthetic_selected) == SYNTHETIC_TARGET, (
        f"Not enough synthetic records: expected {SYNTHETIC_TARGET}, got {len(synthetic_selected)}"
    )

    train_rows = seed_real + relaxed_real + synthetic_selected
    train_rows = dedupe_by_instruction(train_rows)
    train_rows = [
        r
        for r in train_rows
        if first_question_line(r["instruction"]).lower() not in eval_instruction_set
    ]
    random.shuffle(train_rows)

    TRAIN_PATH.parent.mkdir(parents=True, exist_ok=True)
    save_jsonl(TRAIN_PATH, train_rows)

    print("train_total:", len(train_rows))
    print("eval_total_kept:", len(eval_rows))
    print("seed_real:", len(seed_real))
    print("relaxed_real:", len(relaxed_real))
    print("synthetic_selected:", len(synthetic_selected))
    print("train_source_counts:", dict(Counter(r.get("source", "unknown") for r in train_rows)))

    audit_preview(train_rows, n=50)


if __name__ == "__main__":
    main()
