"""Sprint 2 deliverable checks."""

from pathlib import Path

from util.data_ops import count_jsonl


def validate_sprint2_outputs(
    baseline_out: Path,
    sft_ckpt: Path,
    sft_merged: Path,
    paired_out: Path,
    pref_path: Path,
    dpo_ckpt: Path,
    dpo_merged: Path,
    dpo_out: Path,
) -> None:
    """Validate required files and row counts for Sprint 2 completion."""
    checks = []

    checks.append(("baseline_outputs rows", count_jsonl(baseline_out) == 157))
    checks.append(("sft adapter exists", (sft_ckpt / "adapter_config.json").exists()))
    checks.append(("sft merged exists", sft_merged.exists() and any(sft_merged.iterdir())))
    checks.append(("sft paired rows", count_jsonl(paired_out) == 157))
    pref_count = count_jsonl(pref_path)
    checks.append(("preference pairs 60-130", 60 <= pref_count <= 130))
    checks.append(("dpo adapter exists", (dpo_ckpt / "adapter_config.json").exists()))
    checks.append(("dpo merged exists", dpo_merged.exists() and any(dpo_merged.iterdir())))
    checks.append(("dpo outputs rows", count_jsonl(dpo_out) == 157))

    for name, ok in checks:
        print(f"{name}: {'PASS' if ok else 'FAIL'}")
    print(f"preference_pairs count: {pref_count}")

    failed = [name for name, ok in checks if not ok]
    assert not failed, f"Validation failed: {failed}"
