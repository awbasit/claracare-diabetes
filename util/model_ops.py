"""Model and inference helpers for ClaraCare Sprint 2."""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

from util.prompting import build_prompt


def make_4bit_config() -> BitsAndBytesConfig:
    """Return the required 4-bit NF4 config for T4."""
    return BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )


def load_tokenizer(model_name_or_path: str):
    """Load tokenizer with right padding and EOS as pad token."""
    tok = AutoTokenizer.from_pretrained(model_name_or_path, use_fast=True)
    tok.padding_side = "right"
    tok.pad_token = tok.eos_token
    return tok


def load_model_4bit(model_name_or_path: str, bnb_config: BitsAndBytesConfig):
    """Load model in 4-bit quantized mode."""
    return AutoModelForCausalLM.from_pretrained(
        model_name_or_path, quantization_config=bnb_config, device_map="auto"
    )


def generate_one(model, tokenizer, prompt: str, temperature: float, max_new_tokens: int = 300) -> str:
    """Generate one completion for a prompt."""
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )
    answer_ids = out[0][inputs["input_ids"].shape[1] :]
    return tokenizer.decode(answer_ids, skip_special_tokens=True).strip()


def run_eval_single(eval_rows: list[dict], model, tokenizer, temperature: float) -> list[dict]:
    """Run eval generation once per record."""
    out_rows = []
    for row in eval_rows:
        prompt = build_prompt(row["instruction"])
        text = generate_one(model, tokenizer, prompt, temperature)
        out_rows.append(
            {
                "instruction": row["instruction"],
                "reference_output": row["output"],
                "model_output": text,
                "source": row.get("source", ""),
            }
        )
    return out_rows


def run_eval_paired(eval_rows: list[dict], model, tokenizer, cold: float = 0.3, warm: float = 0.9) -> list[dict]:
    """Run paired eval generation with two temperatures."""
    paired = []
    for row in eval_rows:
        prompt = build_prompt(row["instruction"])
        a = generate_one(model, tokenizer, prompt, cold)
        b = generate_one(model, tokenizer, prompt, warm)
        paired.append(
            {
                "instruction": row["instruction"],
                "reference_output": row["output"],
                "model_output_a": a,
                "model_output_b": b,
                "source": row.get("source", ""),
            }
        )
    return paired
