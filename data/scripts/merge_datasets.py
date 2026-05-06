from pathlib import Path
from collections import Counter
import json
import random
import re

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CURRENT_TRAIN = PROJECT_ROOT / "data/processed/claracare_train.jsonl"
CURRENT_EVAL = PROJECT_ROOT / "data/processed/claracare_eval.jsonl"
REAL_CLEANED = PROJECT_ROOT / "data/processed/cleaned_real.jsonl"
HF_CLEAN = PROJECT_ROOT / "data/processed/hf_diabetes_clean.jsonl"
HF_STATS = PROJECT_ROOT / "data/reports/hf_integration_stats.json"

SYNTH_PATHS = [
    PROJECT_ROOT / "data/raw/synthetic/synthetic_diabetes.jsonl",
    PROJECT_ROOT / "data/processed/synthetic_clean.jsonl",
    PROJECT_ROOT / "data/processed/synthetic.jsonl",
]

FINAL_TRAIN = PROJECT_ROOT / "data/processed/claracare_train_final.jsonl"
FINAL_EVAL = PROJECT_ROOT / "data/processed/claracare_eval_final.jsonl"
MERGE_REPORT = PROJECT_ROOT / "data/reports/dataset_merge_report.md"

TARGET_EVAL_MIN = 120
TARGET_EVAL_MAX = 150
TARGET_TRAIN_MIN = 850
TARGET_TRAIN_MAX = 950
TARGET_TRAIN_DEFAULT = 900

REAL_CAP = 150
HF_CAP = 700
SYNTH_CAP = 50
MIN_EMERGENCY_FOOTCARE = 40

JARGON_TERMS = [
    "etiology",
    "pathophysiology",
    "differential diagnosis",
    "comorbidity",
    "contraindicated",
    "titration",
    "serum creatinine",
    "chief complaint",
]

UNSAFE_TERMS = ["aspirin daily", "bid", "tid", "qid", "qhs"]

DOSAGE_PATTERNS = [
    re.compile(r"\b\d+\s?mg\b", re.IGNORECASE),
    re.compile(r"\b\d+\s?units\b", re.IGNORECASE),
    re.compile(r"\b\d+\s?capsules?\b", re.IGNORECASE),
    re.compile(r"\b\d+\s?tablets?\b", re.IGNORECASE),
    re.compile(r"\b\d+\s?times?\s+a\s+day\b", re.IGNORECASE),
]

ALLOWED_TOPICS = {
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
}

STRONG_DIABETES_ANCHORS = [
    "diabetes",
    "diabetic",
    "type 2",
    "type ii",
    "blood sugar",
    "glucose",
    "hba1c",
    "a1c",
    "metformin",
    "insulin",
    "hypoglycemia",
    "hyperglycemia",
    "diabetic foot",
    "diabetic neuropathy",
    "diabetic kidney",
    "diabetic retinopathy",
]

REAL_DROP_TERMS = [
    "pregnant",
    "pregnancy",
    "period",
    "ovulation",
    "fertility",
    "penis",
    "foreskin",
    "vaginal",
    "intercourse",
    "pacemaker",
    "bypass",
    "appendix",
    "platelet",
    "wbc",
    "uric acid",
    "liver enzyme",
    "ast",
    "alt",
    "dog",
    "needle got stuck",
    "cholesterol",
]

CLARACARE_META_TERMS = [
    "booklet",
    "brochure",
    "ndep",
    "federally funded",
    "dppos",
    "study validation",
    "public health program",
    "chart promotes",
    "acknowledge",
    "primary goal",
]

ASPIRIN_TERMS = ["aspirin", "low-dose aspirin", "baby aspirin"]

ACUTE_NON_DIABETES_TERMS = [
    "blood in phlegm",
    "smoking meth",
    "cardiomegaly",
    "chest x-ray",
    "tb",
    "typhoid",
    "low grade fever",
    "appendicitis",
    "pneumonia",
]

POST_MERGE_DROP_TERMS = [
    "aspirin",
    "clinical trial",
    "clinical trials",
    "ndep",
    "booklet",
    "professional organizations",
    "research study",
    "historical evolution",
    "tooth extraction",
    "hip pain",
    "empty sella",
    "brain ct",
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


def save_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def collapse_spaces(text: str) -> str:
    return " ".join(text.split())


def normalize_instruction_key(text: str) -> str:
    cleaned = collapse_spaces(str(text).strip().lower())
    cleaned = re.sub(r"[.!?;:,\s]+$", "", cleaned)
    return cleaned


def word_count(text: str) -> int:
    return len(collapse_spaces(text).split())


def jargon_hits(text: str) -> int:
    low = text.lower()
    return sum(1 for t in JARGON_TERMS if t in low)


def unsafe_hits(text: str) -> int:
    low = text.lower()
    return sum(1 for t in UNSAFE_TERMS if t in low)


def has_direct_dosage(text: str) -> bool:
    return any(p.search(text) for p in DOSAGE_PATTERNS)


def validate_schema(row: dict, context: str) -> None:
    required = {"instruction", "input", "output"}
    assert required.issubset(row.keys()), f"{context}: missing required keys in row: {row.keys()}"
    assert row["input"] == "", f"{context}: input must be empty string"
    assert str(row["instruction"]).strip(), f"{context}: empty instruction"
    assert str(row["output"]).strip(), f"{context}: empty output"


def infer_topic(question: str, answer: str) -> str:
    text = f"{question} {answer}".lower()
    topic_map = {
        "exercise": "exercise",
        "walk": "exercise",
        "workout": "exercise",
        "food": "diet_lifestyle",
        "diet": "diet_lifestyle",
        "meal": "diet_lifestyle",
        "eat": "diet_lifestyle",
        "metformin": "medication",
        "medication": "medication",
        "medicine": "medication",
        "tablet": "medication",
        "insulin": "insulin",
        "blood sugar": "blood_sugar_monitoring",
        "glucose": "blood_sugar_monitoring",
        "hba1c": "blood_sugar_monitoring",
        "a1c": "blood_sugar_monitoring",
        "monitor": "blood_sugar_monitoring",
        "neuropathy": "complications",
        "retinopathy": "complications",
        "kidney": "complications",
        "foot care": "foot_care",
        "feet": "foot_care",
        "hypoglycemia": "emergencies",
        "hyperglycemia": "emergencies",
        "emergency": "emergencies",
        "stress": "emotional_support",
        "depression": "emotional_support",
        "anxiety": "emotional_support",
        "doctor": "healthcare_visit",
        "clinic": "healthcare_visit",
        "appointment": "healthcare_visit",
        "type 2": "diabetes_basics",
        "prediabetes": "diabetes_basics",
        "what is diabetes": "diabetes_basics",
    }
    for key, topic in topic_map.items():
        if key in text:
            return topic
    return "other_diabetes"


def is_diabetes_centered(question: str) -> bool:
    low = question.lower()
    return any(t in low for t in STRONG_DIABETES_ANCHORS)


def sanitize_row(row: dict, default_source: str) -> dict:
    instruction = collapse_spaces(str(row["instruction"]).strip())
    output = collapse_spaces(str(row["output"]).strip())
    source = str(row.get("source") or default_source).strip().lower()
    topic = str(row.get("topic") or "").strip()
    if topic not in ALLOWED_TOPICS:
        topic = infer_topic(instruction, output)
    return {
        "instruction": instruction,
        "input": "",
        "output": output,
        "topic": topic,
        "source": source,
    }


def keep_row_common(row: dict) -> bool:
    instruction = row["instruction"]
    output = row["output"]
    full_text = f"{instruction} {output}".lower()
    if word_count(instruction) < 5:
        return False
    if word_count(output) < 12 or word_count(output) > 220:
        return False
    if any(t in full_text for t in BAD_TERMS):
        return False
    if unsafe_hits(output) > 0:
        return False
    if jargon_hits(output) >= 4:
        return False
    return True


def keep_real_row(row: dict) -> bool:
    if not keep_row_common(row):
        return False
    instruction = row["instruction"].lower()
    output = row["output"]
    full_text = f"{instruction} {output.lower()}"
    if not is_diabetes_centered(instruction):
        return False
    if any(t in full_text for t in ASPIRIN_TERMS):
        return False
    if any(t in full_text for t in CLARACARE_META_TERMS):
        return False
    drop_hits = sum(1 for t in REAL_DROP_TERMS if t in instruction)
    anchor_hits = sum(1 for t in STRONG_DIABETES_ANCHORS if t in instruction)
    if drop_hits > 0 and anchor_hits < 2:
        return False
    acute_hits = sum(1 for t in ACUTE_NON_DIABETES_TERMS if t in instruction)
    if acute_hits > 0 and anchor_hits < 2:
        return False
    if has_direct_dosage(output):
        return False
    return True


def keep_hf_row(row: dict) -> bool:
    instruction = row["instruction"].lower()
    output = row["output"].lower()
    full_text = f"{instruction} {output}"
    if not (keep_row_common(row) and is_diabetes_centered(row["instruction"])):
        return False
    if any(t in full_text for t in ASPIRIN_TERMS):
        return False
    if any(t in full_text for t in CLARACARE_META_TERMS):
        return False
    return True


def is_targeted_synth(row: dict) -> bool:
    topic = str(row.get("topic", "")).lower()
    text = f"{row['instruction']} {row['output']}".lower()
    return (
        topic in {"emergencies", "foot_care"}
        or any(x in text for x in ["hypoglycemia", "hyperglycemia", "emergency", "foot care", "ulcer", "feet"])
    )


def should_drop_post_merge(row: dict) -> bool:
    text = f"{row.get('instruction', '')} {row.get('output', '')}".lower()
    return any(term in text for term in POST_MERGE_DROP_TERMS)


def choose_better_row(a: dict, b: dict) -> dict:
    def score(row: dict) -> tuple:
        wc = word_count(str(row["output"]))
        preferred_band = 1 if 50 <= wc <= 160 else 0
        return (
            preferred_band,
            -unsafe_hits(str(row["output"])),
            -jargon_hits(str(row["output"])),
            min(wc, 220),
        )

    return a if score(a) >= score(b) else b


def dedupe_rows(rows: list[dict]) -> tuple[list[dict], int]:
    deduped: dict[str, dict] = {}
    replaced = 0
    for row in rows:
        key = normalize_instruction_key(row["instruction"])
        if key in deduped:
            replaced += 1
            deduped[key] = choose_better_row(deduped[key], row)
        else:
            deduped[key] = row
    out = list(deduped.values())
    out.sort(key=lambda r: normalize_instruction_key(r["instruction"]))
    return out, replaced


def markdown_table_from_counter(counter: Counter, headers: tuple[str, str]) -> str:
    lines = [f"| {headers[0]} | {headers[1]} |", "|---|---:|"]
    for key, value in sorted(counter.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"| {key} | {value} |")
    return "\n".join(lines)


def main() -> None:
    current_train = load_jsonl(CURRENT_TRAIN)
    current_eval = load_jsonl(CURRENT_EVAL)
    real_cleaned = load_jsonl(REAL_CLEANED)
    hf_rows = load_jsonl(HF_CLEAN)

    for idx, row in enumerate(current_train):
        validate_schema(row, f"current_train[{idx}]")
    for idx, row in enumerate(current_eval):
        validate_schema(row, f"current_eval[{idx}]")
    for idx, row in enumerate(real_cleaned):
        validate_schema(row, f"real_cleaned[{idx}]")
    for idx, row in enumerate(hf_rows):
        validate_schema(row, f"hf_rows[{idx}]")

    synth_rows = []
    synth_path_used = None
    for p in SYNTH_PATHS:
        if p.exists():
            synth_rows = load_jsonl(p)
            synth_path_used = p
            break

    eval_rows, eval_dupe_removed = dedupe_rows(current_eval)
    eval_keys = {normalize_instruction_key(r["instruction"]) for r in eval_rows}

    # Source-aware filtering and caps.
    current_real_train = [r for r in current_train if str(r.get("source", "")).lower() != "synthetic"]
    sanitized_real = [sanitize_row(r, "real") for r in (current_real_train + real_cleaned)]
    sanitized_hf = [sanitize_row(r, "hf_diabetes_qa") for r in hf_rows]
    sanitized_synth = [sanitize_row(r, "synthetic") for r in synth_rows]

    filtered_real = [r for r in sanitized_real if keep_real_row(r)]
    filtered_hf = [r for r in sanitized_hf if keep_hf_row(r)]
    filtered_synth = [r for r in sanitized_synth if keep_row_common(r) and is_targeted_synth(r)]

    filtered_real, real_dupes = dedupe_rows(filtered_real)
    filtered_hf, hf_dupes = dedupe_rows(filtered_hf)
    filtered_synth, synth_dupes = dedupe_rows(filtered_synth)
    train_dupe_removed = real_dupes + hf_dupes + synth_dupes

    leakage_removed = 0
    filtered_real_no_leak = []
    filtered_hf_no_leak = []
    filtered_synth_no_leak = []
    for row in filtered_real:
        key = normalize_instruction_key(row["instruction"])
        if key in eval_keys:
            leakage_removed += 1
        else:
            filtered_real_no_leak.append(row)
    for row in filtered_hf:
        key = normalize_instruction_key(row["instruction"])
        if key in eval_keys:
            leakage_removed += 1
        else:
            filtered_hf_no_leak.append(row)
    for row in filtered_synth:
        key = normalize_instruction_key(row["instruction"])
        if key in eval_keys:
            leakage_removed += 1
        else:
            filtered_synth_no_leak.append(row)

    random.seed(42)
    random.shuffle(filtered_real_no_leak)
    random.shuffle(filtered_hf_no_leak)
    random.shuffle(filtered_synth_no_leak)

    if len(eval_rows) < TARGET_EVAL_MIN:
        needed = TARGET_EVAL_MIN - len(eval_rows)
        pool_for_eval = filtered_hf_no_leak + filtered_real_no_leak
        assert len(pool_for_eval) >= needed, (
            f"Not enough rows to expand eval to {TARGET_EVAL_MIN}. Available pool: {len(pool_for_eval)}"
        )
        eval_extras = pool_for_eval[:needed]
        eval_rows = eval_rows + eval_extras
        eval_extra_keys = {normalize_instruction_key(r["instruction"]) for r in eval_extras}
        filtered_real_no_leak = [r for r in filtered_real_no_leak if normalize_instruction_key(r["instruction"]) not in eval_extra_keys]
        filtered_hf_no_leak = [r for r in filtered_hf_no_leak if normalize_instruction_key(r["instruction"]) not in eval_extra_keys]
    elif len(eval_rows) > TARGET_EVAL_MAX:
        print(
            f"WARNING: existing eval has {len(eval_rows)} rows (> {TARGET_EVAL_MAX}). Keeping it unchanged."
        )

    eval_rows, eval_dupe_removed_after_expand = dedupe_rows(eval_rows)
    eval_dupe_removed += eval_dupe_removed_after_expand
    eval_keys = {normalize_instruction_key(r["instruction"]) for r in eval_rows}

    filtered_real_no_leak = [r for r in filtered_real_no_leak if normalize_instruction_key(r["instruction"]) not in eval_keys]
    filtered_hf_no_leak = [r for r in filtered_hf_no_leak if normalize_instruction_key(r["instruction"]) not in eval_keys]
    filtered_synth_no_leak = [r for r in filtered_synth_no_leak if normalize_instruction_key(r["instruction"]) not in eval_keys]

    selected_real = filtered_real_no_leak[:REAL_CAP]
    selected_hf = filtered_hf_no_leak[:HF_CAP]
    selected_synth = filtered_synth_no_leak[:SYNTH_CAP]

    # Ensure enough emergency/foot-care coverage.
    selected = selected_real + selected_hf + selected_synth
    emergency_foot = [r for r in selected if r.get("topic") in {"emergencies", "foot_care"}]
    if len(emergency_foot) < MIN_EMERGENCY_FOOTCARE:
        candidates = [r for r in (filtered_hf_no_leak + filtered_synth_no_leak) if r.get("topic") in {"emergencies", "foot_care"}]
        existing_keys = {normalize_instruction_key(r["instruction"]) for r in selected}
        for c in candidates:
            key = normalize_instruction_key(c["instruction"])
            if key in existing_keys:
                continue
            selected.append(c)
            existing_keys.add(key)
            emergency_foot.append(c)
            if len(emergency_foot) >= MIN_EMERGENCY_FOOTCARE:
                break

    final_train = selected
    final_train, train_dupe_removed_after_expand = dedupe_rows(final_train)
    train_dupe_removed += train_dupe_removed_after_expand
    random.shuffle(final_train)

    if len(final_train) > TARGET_TRAIN_MAX:
        final_train = final_train[:TARGET_TRAIN_DEFAULT]

    # Final post-merge safety scan requested by reviewer guidance.
    pre_scan_train = len(final_train)
    pre_scan_eval = len(eval_rows)
    final_train = [r for r in final_train if not should_drop_post_merge(r)]
    eval_rows = [r for r in eval_rows if not should_drop_post_merge(r)]
    post_merge_removed = (pre_scan_train - len(final_train)) + (pre_scan_eval - len(eval_rows))
    eval_rows, eval_dupe_removed_post_scan = dedupe_rows(eval_rows)
    final_train, train_dupe_removed_post_scan = dedupe_rows(final_train)
    eval_dupe_removed += eval_dupe_removed_post_scan
    train_dupe_removed += train_dupe_removed_post_scan

    save_jsonl(FINAL_TRAIN, final_train)
    save_jsonl(FINAL_EVAL, eval_rows)

    final_source_counts = Counter(r.get("source", "unknown") for r in final_train)
    final_topic_counts = Counter(r.get("topic", "unknown") for r in final_train)

    hf_loaded = "unknown"
    hf_kept = len(hf_rows)
    hf_dropped = "unknown"
    hf_drop_reasons = {}
    if HF_STATS.exists():
        stats = json.loads(HF_STATS.read_text(encoding="utf-8"))
        hf_loaded = stats.get("loaded_count", "unknown")
        hf_kept = stats.get("kept_after_dedupe", len(hf_rows))
        hf_dropped = stats.get("dropped_count", "unknown")
        hf_drop_reasons = stats.get("drop_reasons", {})

    report_lines = [
        "# Dataset Merge Report",
        "",
        "## Input Summary",
        f"- HF loaded rows: {hf_loaded}",
        f"- HF kept rows: {hf_kept}",
        f"- HF dropped rows: {hf_dropped}",
        f"- Current train rows: {len(current_train)}",
        f"- Current eval rows: {len(current_eval)}",
        f"- Real cleaned rows: {len(real_cleaned)}",
        f"- Synthetic rows included: {len(selected_synth)}",
        f"- Synthetic path used: `{synth_path_used}`" if synth_path_used else "- Synthetic path used: none",
        f"- Real rows after strict filter: {len(filtered_real_no_leak)}",
        f"- HF rows after filter: {len(filtered_hf_no_leak)}",
        f"- Synthetic rows after targeted filter: {len(filtered_synth_no_leak)}",
        f"- Source caps used: real={REAL_CAP}, hf={HF_CAP}, synthetic={SYNTH_CAP}",
        "",
        "## Processing Summary",
        f"- Duplicate rows removed: {train_dupe_removed + eval_dupe_removed}",
        f"- Leakage rows removed from train: {leakage_removed}",
        f"- Post-merge safety rows removed: {post_merge_removed}",
        f"- Final train count: {len(final_train)}",
        f"- Final eval count: {len(eval_rows)}",
        "",
    ]

    if hf_drop_reasons:
        report_lines.extend(
            [
                "## HF Top Drop Reasons",
                "",
                markdown_table_from_counter(Counter(hf_drop_reasons), ("Drop Reason", "Count")),
                "",
            ]
        )

    report_lines.extend(
        [
            "## Topic Distribution (Final Train)",
            "",
            markdown_table_from_counter(final_topic_counts, ("Topic", "Count")),
            "",
            "## Source Distribution (Final Train)",
            "",
            markdown_table_from_counter(final_source_counts, ("Source", "Count")),
            "",
        ]
    )

    MERGE_REPORT.parent.mkdir(parents=True, exist_ok=True)
    MERGE_REPORT.write_text("\n".join(report_lines), encoding="utf-8")

    if len(final_train) < TARGET_TRAIN_MIN:
        print(
            f"WARNING: final train set is below target ({len(final_train)} < {TARGET_TRAIN_MIN}). "
            "Do not train yet; add more clean data."
        )
    if len(final_train) > TARGET_TRAIN_MAX:
        print(
            f"WARNING: final train set is above target ({len(final_train)} > {TARGET_TRAIN_MAX}). "
            "Consider downsampling for cost-efficient SFT."
        )

    print("HF loaded:", hf_loaded)
    print("HF kept:", hf_kept)
    print("Final train:", len(final_train))
    print("Final eval:", len(eval_rows))
    print("Duplicate removed:", train_dupe_removed + eval_dupe_removed)
    print("Leakage removed:", leakage_removed)
    print("Post-merge safety removed:", post_merge_removed)
    print("Reports saved:", MERGE_REPORT)
    print("Next action: manually review data/reports/audit_train_eval_50.md before SFT")


if __name__ == "__main__":
    main()
