from pathlib import Path
from collections import Counter
import json
import re

from datasets import Dataset, DatasetDict, concatenate_datasets, load_dataset

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUT_PATH = PROJECT_ROOT / "data/processed/hf_diabetes_clean.jsonl"
STATS_PATH = PROJECT_ROOT / "data/reports/hf_integration_stats.json"

HF_DATASET = "abdelhakimDZ/diabetes_QA_dataset"

ALLOWED_TOPICS = [
    "diabetes_basics",
    "blood_sugar_monitoring",
    "medication",
    "insulin",
    "diet_lifestyle",
    "exercise",
    "complications",
    "foot_care",
    "emergencies",
    "emotional_support",
    "healthcare_visit",
    "other_diabetes",
]

CORE_TERMS = [
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
    "neuropathy",
    "retinopathy",
    "kidney disease",
    "foot care",
]

BAD_TERMS = [
    "penis",
    "erection",
    "vaginal",
    "condom",
    "birth control",
    "pacemaker",
    "bypass",
    "aspirin daily",
    "surgery",
    "cancer",
    "covid",
    "malaria",
    "tuberculosis",
]

PREGNANCY_TERMS = ["pregnancy", "pregnant", "gestation", "gestational"]
GESTATIONAL_DIABETES_TERMS = ["gestational diabetes", "diabetes in pregnancy", "diabetes during pregnancy"]

CLINICIAN_JARGON_TERMS = [
    "etiology",
    "pathophysiology",
    "differential diagnosis",
    "comorbidity",
    "contraindicated",
    "titration",
    "serum creatinine",
    "patient presents",
    "chief complaint",
    "hpi",
]

UNSAFE_DOSAGE_PATTERNS = [
    re.compile(r"\b\d+(\.\d+)?\s?(mg|mcg|g|ml|units?)\b", re.IGNORECASE),
    re.compile(r"\b(once|twice|thrice)\s+(daily|a day)\b", re.IGNORECASE),
    re.compile(r"\bevery\s+\d+\s*(hours?|hrs?)\b", re.IGNORECASE),
    re.compile(r"\bbid\b|\btid\b|\bqid\b|\bqhs\b", re.IGNORECASE),
]


def collapse_spaces(text: str) -> str:
    return " ".join(text.split())


def normalize_instruction_key(text: str) -> str:
    cleaned = collapse_spaces(text.strip().lower())
    cleaned = re.sub(r"[.!?;:,\s]+$", "", cleaned)
    return cleaned


def word_count(text: str) -> int:
    return len(collapse_spaces(text).split())


def unsafe_term_hits(text: str) -> int:
    return sum(1 for t in BAD_TERMS if t in text.lower())


def jargon_hits(text: str) -> int:
    low = text.lower()
    return sum(1 for t in CLINICIAN_JARGON_TERMS if t in low)


def has_unsafe_dosage(text: str) -> bool:
    return any(p.search(text) for p in UNSAFE_DOSAGE_PATTERNS)


def is_diabetes_centered(question: str) -> bool:
    low = question.lower()
    return any(t in low for t in CORE_TERMS)


def is_patient_facing(output: str) -> bool:
    low = output.lower()
    if any(x in low for x in ["dear doctor", "fellow clinician", "for clinicians only"]):
        return False
    # Educational factual responses are acceptable if they are understandable.
    if jargon_hits(output) >= 4:
        return False
    return True


def is_allowed_pregnancy_context(text: str) -> bool:
    low = text.lower()
    has_pregnancy = any(t in low for t in PREGNANCY_TERMS)
    if not has_pregnancy:
        return True
    return any(t in low for t in GESTATIONAL_DIABETES_TERMS)


def infer_topic(question: str, answer: str) -> str:
    text = f"{question} {answer}".lower()
    if any(t in text for t in ["what is diabetes", "type 2", "prediabetes", "pre-diabetes"]):
        return "diabetes_basics"
    if any(t in text for t in ["blood sugar", "glucose", "hba1c", "a1c", "glucometer", "monitor"]):
        return "blood_sugar_monitoring"
    if any(t in text for t in ["metformin", "tablet", "medicine", "medication", "drug", "oral medicine"]):
        return "medication"
    if "insulin" in text:
        return "insulin"
    if any(t in text for t in ["diet", "food", "meal", "carb", "nutrition", "plate"]):
        return "diet_lifestyle"
    if any(t in text for t in ["exercise", "walk", "activity", "workout"]):
        return "exercise"
    if any(t in text for t in ["neuropathy", "retinopathy", "kidney", "complication", "heart"]):
        return "complications"
    if any(t in text for t in ["foot care", "foot ulcer", "feet", "toe"]):
        return "foot_care"
    if any(t in text for t in ["emergency", "hypoglycemia", "hyperglycemia", "very low", "very high"]):
        return "emergencies"
    if any(t in text for t in ["stress", "anxiety", "depression", "support", "family"]):
        return "emotional_support"
    if any(t in text for t in ["doctor", "clinic", "appointment", "follow up", "visit"]):
        return "healthcare_visit"
    return "other_diabetes"


def choose_better_row(a: dict, b: dict) -> dict:
    def score(row: dict) -> tuple:
        out = row["output"]
        wc = word_count(out)
        preferred_band = 1 if 50 <= wc <= 160 else 0
        unsafe_hits = unsafe_term_hits(out)
        jargon = jargon_hits(out)
        return (
            preferred_band,
            -unsafe_hits,
            -jargon,
            -abs(105 - wc),
            min(wc, 220),
        )

    return a if score(a) >= score(b) else b


def validate_and_filter(row: dict) -> tuple[bool, str]:
    instruction = collapse_spaces(str(row["instruction"]).strip())
    output = collapse_spaces(str(row["output"]).strip())
    full_text = f"{instruction} {output}".lower()

    if not instruction:
        return False, "empty_instruction"
    if not output:
        return False, "empty_output"
    if word_count(instruction) < 5:
        return False, "short_instruction"
    if word_count(output) < 12:
        return False, "short_output"
    if word_count(output) > 220:
        return False, "long_output"
    if row.get("input", "") != "":
        return False, "non_empty_input"
    if not is_diabetes_centered(instruction):
        return False, "not_diabetes_centered"
    if any(t in full_text for t in BAD_TERMS):
        return False, "off_scope_term"
    if not is_allowed_pregnancy_context(full_text):
        return False, "pregnancy_non_diabetes_context"
    if not is_patient_facing(output):
        return False, "not_patient_facing"
    if has_unsafe_dosage(output):
        return False, "unsafe_dosage"
    if jargon_hits(output) >= 3:
        return False, "clinician_jargon_heavy"
    return True, "keep"


def save_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def to_dataset(raw: Dataset | DatasetDict) -> Dataset:
    if isinstance(raw, Dataset):
        return raw
    assert isinstance(raw, DatasetDict), f"Unsupported HF object type: {type(raw)}"
    split_names = list(raw.keys())
    assert split_names, "HF dataset has no splits"
    merged = concatenate_datasets([raw[s] for s in split_names])
    return merged


def resolve_columns(columns: list[str]) -> tuple[str, str]:
    question_candidates = ["question", "Question", "instruction", "prompt"]
    answer_candidates = ["answer", "Answer", "output", "response"]
    q_col = next((c for c in question_candidates if c in columns), None)
    a_col = next((c for c in answer_candidates if c in columns), None)
    assert q_col is not None, f"Missing question column in HF dataset. Columns found: {columns}"
    assert a_col is not None, f"Missing answer column in HF dataset. Columns found: {columns}"
    return q_col, a_col


def main() -> None:
    raw = load_dataset(HF_DATASET)
    ds = to_dataset(raw)

    columns = list(ds.column_names)
    print("HF dataset:", HF_DATASET)
    print("HF columns:", columns)

    q_col, a_col = resolve_columns(columns)
    print("Question column:", q_col)
    print("Answer column:", a_col)

    loaded_count = len(ds)
    kept_rows: list[dict] = []
    drop_reasons: Counter = Counter()

    for rec in ds:
        question = collapse_spaces(str(rec[q_col]).strip())
        answer = collapse_spaces(str(rec[a_col]).strip())
        answer = re.sub(r"^answer:\s*", "", answer, flags=re.IGNORECASE)
        row = {
            "instruction": question,
            "input": "",
            "output": answer,
            "topic": infer_topic(question, answer),
            "source": "hf_diabetes_qa",
        }
        assert row["topic"] in ALLOWED_TOPICS, f"Invalid topic inferred: {row['topic']}"
        ok, reason = validate_and_filter(row)
        if ok:
            kept_rows.append(row)
        else:
            drop_reasons[reason] += 1

    deduped: dict[str, dict] = {}
    duplicates_seen = 0
    for row in kept_rows:
        key = normalize_instruction_key(row["instruction"])
        if key in deduped:
            duplicates_seen += 1
            deduped[key] = choose_better_row(deduped[key], row)
        else:
            deduped[key] = row

    final_rows = list(deduped.values())
    final_rows.sort(key=lambda r: normalize_instruction_key(r["instruction"]))
    save_jsonl(OUT_PATH, final_rows)

    stats = {
        "hf_dataset": HF_DATASET,
        "loaded_count": loaded_count,
        "kept_before_dedupe": len(kept_rows),
        "kept_after_dedupe": len(final_rows),
        "dropped_count": loaded_count - len(kept_rows),
        "duplicates_collapsed": duplicates_seen,
        "drop_reasons": dict(drop_reasons.most_common()),
        "topic_distribution": dict(Counter(r["topic"] for r in final_rows)),
    }
    STATS_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATS_PATH.write_text(json.dumps(stats, indent=2), encoding="utf-8")

    print("HF loaded:", stats["loaded_count"])
    print("HF kept:", stats["kept_after_dedupe"])
    print("HF dropped:", stats["dropped_count"])
    print("HF duplicates collapsed:", stats["duplicates_collapsed"])
    print(f"Saved: {OUT_PATH}")
    print(f"Saved stats: {STATS_PATH}")


if __name__ == "__main__":
    main()
