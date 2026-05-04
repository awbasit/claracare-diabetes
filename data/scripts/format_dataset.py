from pathlib import Path
from collections import Counter
import random
import jsonlines

ROOT = Path(__file__).resolve().parents[2]
REAL_P = ROOT / "data/processed/cleaned_real.jsonl"
SYN_P = ROOT / "data/processed/synthetic.jsonl"
OUT_TR = ROOT / "data/processed/claracare_train.jsonl"
OUT_EV = ROOT / "data/processed/claracare_eval.jsonl"


def norm_real(r):
    assert "instruction" in r and "output" in r
    return {"instruction": str(r["instruction"]).strip(), "input": "", "output": str(r["output"]).strip(), "topic": str(r.get("topic") or ""), "source": "real"}


def norm_syn(r):
    required = {"instruction", "input", "output", "topic", "source"}
    assert set(r.keys()) >= required
    assert r["source"] == "synthetic"
    assert r["input"] == ""
    return {"instruction": str(r["instruction"]).strip(), "input": "", "output": str(r["output"]).strip(), "topic": str(r["topic"]), "source": "synthetic"}


def dedupe_instr_ordered(rows):
    seen, out = set(), []
    for r in rows:
        k = r["instruction"].strip().lower()
        if k in seen:
            continue
        seen.add(k)
        out.append(r)
    return out


def split_vec(lst, frac_eval, rng):
    if not lst:
        return [], []
    if len(lst) == 1:
        return lst, []
    rng.shuffle(lst)
    n_ev = min(max(1, round(frac_eval * len(lst))), max(1, len(lst) - 1))
    return lst[n_ev:], lst[:n_ev]


def take_n(real_rows, syn_rows, n_target, rng):
    assert len(real_rows) + len(syn_rows) >= n_target
    if len(real_rows) + len(syn_rows) == n_target:
        return dedupe_instr_ordered(real_rows + syn_rows)
    if len(syn_rows) >= n_target:
        return rng.sample(syn_rows, n_target)
    need_real = n_target - len(syn_rows)
    assert len(real_rows) >= need_real
    picked_real = rng.sample(real_rows, need_real)
    return dedupe_instr_ordered(picked_real + syn_rows)


def main():
    assert REAL_P.exists(), f"Missing input file: {REAL_P}"
    assert SYN_P.exists(), f"Missing input file: {SYN_P}"
    with jsonlines.open(REAL_P) as fr:
        real_rows = dedupe_instr_ordered([norm_real(dict(r)) for r in fr])
    with jsonlines.open(SYN_P) as fs:
        syn_rows = dedupe_instr_ordered([norm_syn(dict(r)) for r in fs])
    print(f"loaded {len(real_rows)} real, {len(syn_rows)} synthetic")
    if len(real_rows) < 200:
        print(f"WARNING: only {len(real_rows)} real records loaded. Synthetic data will dominate the\n dataset. Verify clean.py filters are not too aggressive before continuing.")
    if len(syn_rows) < 50:
        print(f"WARNING: only {len(syn_rows)} synthetic records loaded. Dataset may lack Ghana-specific\n and edge-case coverage. Consider re-running generate_synthetic.py.")

    merged_full = dedupe_instr_ordered(real_rows + syn_rows)
    print("source counts after merge:", Counter(r["source"] for r in merged_full))
    minimum_pool = max(300, len(real_rows) + len(syn_rows) - 50)
    assert len(merged_full) >= minimum_pool, f"Merged pool too small: {len(merged_full)}. Check filter outputs."

    goal_n = min(3158, len(merged_full))
    rng = random.Random(42)
    merged = merged_full if len(merged_full) <= goal_n else take_n(real_rows, syn_rows, goal_n, rng)
    reals = [r for r in merged if r["source"] == "real"]
    syns = [r for r in merged if r["source"] == "synthetic"]
    tr_r, ev_r = split_vec(reals, 0.05, rng)
    tr_s, ev_s = split_vec(syns, 0.05, rng)
    train, eval_rows = tr_r + tr_s, ev_r + ev_s
    rng.shuffle(train)
    rng.shuffle(eval_rows)

    train_instructions = {r["instruction"].strip().lower() for r in train}
    leaks = [r for r in eval_rows if r["instruction"].strip().lower() in train_instructions]
    assert len(leaks) == 0, f"LEAKAGE: {len(leaks)} eval records found in train set"
    print("leakage_check: 0")

    OUT_TR.parent.mkdir(parents=True, exist_ok=True)
    with jsonlines.open(OUT_TR, mode="w") as wt:
        for r in train:
            wt.write(r)
    with jsonlines.open(OUT_EV, mode="w") as we:
        for r in eval_rows:
            we.write(r)

    print("merged_total_used:", len(merged))
    print("final train:", len(train))
    print("final eval:", len(eval_rows))
    print("train sources:", dict(Counter(r["source"] for r in train)))
    print("eval sources:", dict(Counter(r["source"] for r in eval_rows)))
    print("real_total:", len(reals))
    print("synthetic_total:", len(syns))
    expected_total = len(train) + len(eval_rows)
    expected_eval_min = max(20, round(0.04 * expected_total))
    expected_eval_max = max(50, round(0.08 * expected_total))
    expected_train_min = expected_total - expected_eval_max
    expected_train_max = expected_total - expected_eval_min
    assert expected_train_min <= len(train) <= expected_train_max, \
        f"Unexpected train size: {len(train)} (expected {expected_train_min}-{expected_train_max})"
    assert expected_eval_min <= len(eval_rows) <= expected_eval_max, \
        f"Unexpected eval size: {len(eval_rows)} (expected {expected_eval_min}-{expected_eval_max})"


if __name__ == "__main__":
    main()
