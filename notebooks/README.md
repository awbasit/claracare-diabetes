# Notebooks Guide

## Available Notebook

- `claracare_sprint2_sft_dpo.ipynb`

This notebook runs the full Sprint 2 sequence in Colab:
1. Install dependencies
2. Auth + environment checks
3. Baseline inference
4. SFT config and training
5. SFT merge
6. Paired inference for preferences
7. Preference pair generation (GPT-4o-mini judge)
8. DPO config and training
9. DPO merge
10. Final inference comparison
11. OOM recovery reference
12. Final deliverables validation

## Prerequisites

- Colab runtime with T4 GPU (`fp16` only)
- `claracare_train.jsonl` and `claracare_eval.jsonl` uploaded into `/content`
- repository cloned in Colab (so `util/` is available to imports)
- API keys/tokens ready:
  - Weights & Biases
  - Hugging Face (write-access)
  - OpenAI

## How Utility Imports Work

Cell 2 auto-detects the repository root by looking for a `util/` folder and appends that path to `sys.path`.

This avoids hardcoding repo folder names and prevents path errors when the repo is cloned under a different directory.

If imports fail, verify the repo was cloned and that a top-level `util/` directory exists.

## Important Runtime Notes

- Keep prompt template identical across baseline, SFT, and DPO steps.
- DPO uses `ref_model=None` for QLoRA memory safety on T4.
- Run cells in order.
- Use the final validation cell to verify Sprint 2 artifacts and counts.
