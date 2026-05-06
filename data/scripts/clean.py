from pathlib import Path
import jsonlines

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw"
OUT = ROOT / "data/processed/cleaned_real.jsonl"
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
KEYWORDS = CORE_QUESTION_TERMS + ["glycemic"]
JARGON = ["etiology", "pathophysiology", "comorbidity", "contraindicated", "titration", "pharmacokinetics", "endocrinologist recommends", "differential diagnosis", "serum creatinine"]
FAIL_PREFIX = ["patient presents", "patient is a", "case report", "chief complaint:", "history of present illness", "56-year-old", "55-year-old", "54-year-old", "53-year-old", "52-year-old", "51-year-old", "50-year-old", "45-year-old", "40-year-old", "35-year-old", "30-year-old", "65-year-old", "70-year-old", "60-year-old"]
PASS_PREFIX = ("how", "what", "why", "when", "can", "should", "is ", "are ", "do ", "does ", "will ", "my ", "i ")


def normalize(row):
    try:
        if not isinstance(row, dict):
            return None
        if "instruction" in row and "output" in row:
            i, o = row["instruction"], row["output"]
        elif "patient_message" in row and "doctor_response" in row:
            i, o = row["patient_message"], row["doctor_response"]
        elif "question" in row and "answer" in row:
            i, o = row["question"], row["answer"]
        else:
            return None
        if not isinstance(i, str) or not isinstance(o, str):
            return None
        i, o = i.strip(), o.strip()
        if not i or not o:
            return None
        return {"instruction": i, "output": o}
    except Exception:
        return None


def is_diabetes_focused(record):
    instruction = record["instruction"].lower()
    output = record["output"].lower()
    full_text = instruction + " " + output

    question_is_diabetes_related = any(t in instruction for t in CORE_QUESTION_TERMS)
    has_bad_topic = any(t in full_text for t in BAD_TERMS)
    answer_long_enough = len(output.split()) >= 40

    return question_is_diabetes_related and not has_bad_topic and answer_long_enough


def main():
    assert RAW.exists() and RAW.is_dir(), "data/raw directory not found"
    files = sorted(RAW.glob("*.jsonl"))
    assert files, "No .jsonl files in data/raw/"
    rows_read = 0
    skipped_unmapped = 0
    rows = []
    for p in files:
        with jsonlines.open(p) as r:
            for row in r:
                rows_read += 1
                rec = normalize(row)
                if rec is None:
                    skipped_unmapped += 1
                else:
                    rows.append(rec)
    after_normalize = len(rows)
    print("after_normalize:", after_normalize)
    rows = [x for x in rows if is_diabetes_focused(x)]
    after_strict_focus = len(rows)
    print("after_strict_focus:", after_strict_focus)
    rows = [x for x in rows if sum(1 for t in JARGON if t in x["output"].lower()) < 2]
    after_clinical_filter = len(rows)
    print("after_clinical_filter:", after_clinical_filter)
    keep = []
    for x in rows:
        s = x["instruction"].strip().lower()
        if any(s.startswith(p) for p in FAIL_PREFIX):
            continue
        if s.endswith("?") or s.startswith(PASS_PREFIX):
            keep.append(x)
    rows = keep
    after_patient_voice = len(rows)
    print("after_patient_voice:", after_patient_voice)
    seen = set()
    output_data = []
    for x in rows:
        k = x["instruction"].strip().lower()
        if k in seen:
            continue
        seen.add(k)
        x["input"] = ""
        x["topic"] = ""
        x["source"] = "real"
        output_data.append(x)
    after_dedupe = len(output_data)
    print("after_dedupe:", after_dedupe)
    total = len(output_data)
    if total > 0:
        texts = [x["instruction"].lower() for x in output_data]
        for kw in KEYWORDS:
            c = sum(1 for t in texts if kw in t)
            if c / total > 0.30:
                print(f"WARNING: {kw} {100*c/total:.1f}%")
    assert all("instruction" in r and "output" in r for r in output_data), "Schema violation in output"
    assert len(output_data) > 0, "Clean output is empty — check filters and raw data field names"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with jsonlines.open(OUT, mode="w") as w:
        for r in output_data:
            w.write(r)
    print(f"wrote {len(output_data)} records -> data/processed/cleaned_real.jsonl")
    print("rows_read:", rows_read)
    print("skipped_unmapped:", skipped_unmapped)
    print("after_normalize:", after_normalize)
    print("after_strict_focus:", after_strict_focus)
    print("after_clinical_filter:", after_clinical_filter)
    print("after_patient_voice:", after_patient_voice)
    print("after_dedupe:", after_dedupe)
    if len(output_data) < 400:
        print(
            f"WARNING: only {len(output_data)} clean records produced. Consider adjusting filters or\n"
            " increasing synthetic generation target before running format_dataset.py"
        )


if __name__ == "__main__":
    main()
