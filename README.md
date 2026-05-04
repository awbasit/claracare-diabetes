# ClaraCare Diabetes Dataset + Training Pipeline

ClaraCare is a diabetes health-literacy project focused on simple, safe explanations for patients in Ghana.

This repository contains:
- data collection and curation scripts
- synthetic data generation scripts
- dataset formatting scripts for train/eval splits
- a Colab notebook for Sprint 2 (`SFT -> DPO`) fine-tuning
- reusable utility functions used by the notebook
- a minimal CLI entrypoint for pipeline steps

## Repository Structure

```text
claracare-diabetes/
├─ run.py
├─ src/
│  └─ claracare/
│     ├─ __init__.py
│     └─ cli.py
├─ data/
│  ├─ __init__.py
│  └─ scripts/
│     ├─ __init__.py
│     ├─ collect.py
│     ├─ clean.py
│     ├─ generate_synthetic.py
│     └─ format_dataset.py
├─ notebooks/
│  ├─ claracare_sprint2_sft_dpo.ipynb
│  └─ README.md
├─ util/
│  ├─ __init__.py
│  ├─ prompting.py
│  ├─ data_ops.py
│  ├─ model_ops.py
│  └─ validation.py
└─ .gitignore
```

## Data Pipeline (Sprint 1)

Run from the repository root using the new CLI launcher:

1) Collect raw public datasets
```bash
python run.py collect
```

2) Clean and normalize to patient-friendly rows
```bash
python run.py clean
```

3) Generate synthetic Ghana-focused rows
```bash
python run.py synthetic
```

4) Build train/eval files
```bash
python run.py format
```

Run all steps in order:
```bash
python run.py all
```

Expected outputs:
- `data/processed/cleaned_real.jsonl`
- `data/processed/synthetic.jsonl`
- `data/processed/claracare_train.jsonl`
- `data/processed/claracare_eval.jsonl`

## Training Pipeline (Sprint 2)

Use:
- `notebooks/claracare_sprint2_sft_dpo.ipynb`

The notebook performs:
- baseline inference with base Mistral
- SFT with QLoRA
- SFT adapter merge
- paired generations for preference data
- preference pair creation via GPT-4o-mini judging
- DPO training on top of SFT model
- DPO adapter merge
- final qualitative comparison
- final deliverables validation cell

Notebook details are documented in `notebooks/README.md`.

## Path and Import Assumptions

- Script output paths in `data/scripts/*.py` are rooted via:
  - `ROOT = Path(__file__).resolve().parents[2]`
- `run.py` injects `src/` into `sys.path`, then dispatches to `claracare.cli`
- `claracare.cli` imports `data.scripts.*` via package markers in `data/` and `data/scripts/`
- Notebook utility imports resolve by searching upward for a `util/` folder in Cell 2.
- Colab checkpoint root is fixed to:
  - `/content/drive/MyDrive/claracare-checkpoints`

## Restructure Applied

The repo now has a lightweight package/CLI layer without rewriting working scripts:
- keeps existing script logic unchanged
- adds a stable command surface (`python run.py <step>`)
- preserves path behavior for local and Colab execution
