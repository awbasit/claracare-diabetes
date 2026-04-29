"""Download HF datasets to data/raw/*.jsonl — download only."""

from pathlib import Path

import jsonlines
from datasets import DatasetDict, concatenate_datasets, load_dataset
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"


def ds_to_flat(d):
    if isinstance(d, DatasetDict):
        out = concatenate_datasets([d[k] for k in d.keys()])
    else:
        out = d
    assert len(out) > 0, "Downloaded dataset is empty"
    return out


def save_hf(name_prefix, ds):
    RAW.mkdir(parents=True, exist_ok=True)
    out = RAW / f"{name_prefix}.jsonl"
    n = len(ds)
    assert n > 0, "Downloaded dataset is empty"
    with jsonlines.open(out, mode="w") as f:
        for row in tqdm(ds, desc=out.name):
            f.write(dict(row))
    print(f"{name_prefix}: saved {n} rows -> {out.relative_to(ROOT)}")
    return n


def main():
    print("medical_dialog: Hugging Face OpenMed/MedDialog (train+validation)")
    dd_md = load_dataset("OpenMed/MedDialog")
    ds_md = ds_to_flat(dd_md)
    save_hf("medical_dialog", ds_md)

    second_ids = ["medalpaca/medical_meadow_mediqa", "MedSwin/iCliniq"]
    last_exc = None
    used_id = None
    dd2 = None
    for sid in second_ids:
        try:
            dd2 = load_dataset(sid)
            used_id = sid
            break
        except Exception as e:
            last_exc = e
    assert dd2 is not None, (
        "Could not load any secondary QA dataset "
        + f"(last error: {last_exc!r})"
    )

    ds2 = ds_to_flat(dd2)
    u = used_id.lower()
    if "medical_meadow_mediqa" in u:
        pref = "medical_meadow_mediqa"
    elif "icliniq" in u:
        pref = "medswin_icliniq"
    else:
        pref = used_id.replace("/", "_").replace("-", "_")
    save_hf(pref, ds2)


if __name__ == "__main__":
    main()
