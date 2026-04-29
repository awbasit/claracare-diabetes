"""Filter raw JSONL to diabetes-focused instruction/output records — no LLM."""

from pathlib import Path

import jsonlines

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed" / "cleaned_real.jsonl"

KEYWORDS = [
    "diabetes", "blood sugar", "glucose", "insulin", "hba1c",
    "metformin", "type 2", "hyperglycemia", "hypoglycemia",
    "glycemic", "a1c", "diabetic",
]


def normalize(row):
    if not isinstance(row, dict):
        return None
    if "instruction" in row and "output" in row:
        instr, outp = row["instruction"], row["output"]
    elif "patient_message" in row and "doctor_response" in row:
        instr, outp = row["patient_message"], row["doctor_response"]
    elif "question" in row and "answer" in row:
        instr, outp = row["question"], row["answer"]
    else:
        return None
    if not isinstance(instr, str) or not isinstance(outp, str):
        return None
    instruct_input, output_text = instr.strip(), outp.strip()
    if not instruct_input or not output_text:
        return None
    return {"instruction": instruct_input, "output": output_text}


def main():
    mapped = []
    raw_n = 0
    skipped_map = 0
    paths = sorted(RAW.glob("*.jsonl"))
    assert paths, "No .jsonl in data/raw/"
    for p in paths:
        with jsonlines.open(p) as reader:
            for row in reader:
                raw_n += 1
                rec = normalize(row)
                if rec is None:
                    skipped_map += 1
                else:
                    mapped.append(rec)

    print(f"rows_read: {raw_n}")
    print(f"skipped_unmapped: {skipped_map}")
    print(f"after_normalize: {len(mapped)}")

    def kw_keep(r):
        blob = (r["instruction"] + " " + r["output"]).lower()
        return any(k in blob for k in KEYWORDS)

    kw_pass = [r for r in mapped if kw_keep(r)]
    print(f"after_keyword: {len(kw_pass)}")
    mapped = kw_pass

    len_pass = [
        r for r in mapped
        if len(r["output"].split()) >= 40
    ]
    print(f"after_length (output>=40 words): {len(len_pass)}")
    mapped = len_pass

    seen_instr = set()
    deduped = []
    for r in mapped:
        k = r["instruction"].strip().lower()
        if k in seen_instr:
            continue
        seen_instr.add(k)
        deduped.append(r)

    print(f"after_instruction_dedupe: {len(deduped)}")

    nfin = len(deduped)
    if nfin > 0:
        ilow = [r["instruction"].lower() for r in deduped]
        for kw in KEYWORDS:
            c = sum(1 for s in ilow if kw in s)
            if c / nfin > 0.30:
                print(f"WARNING: keyword {kw!r} in "
                      f"{100.0*c/nfin:.1f}% of instructions (>30%; manual review)")
    output_data = deduped
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with jsonlines.open(OUT, mode="w") as w:
        for r in output_data:
            w.write(r)

    assert all(
        "instruction" in r and "output" in r for r in output_data
    ), "Schema violation in output"
    assert len(output_data) > 0, "Clean output is empty — check filters"
    print(f"wrote {len(output_data)} -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
