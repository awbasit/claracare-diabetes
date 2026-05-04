"""Prompt helpers for ClaraCare Sprint 2."""

SYSTEM_INST = (
    "You are ClaraCare, a health assistant explaining Type 2 diabetes\n"
    "to patients in simple, clear language. Use short sentences. Avoid jargon.\n"
    "Be warm and accurate. Never give specific drug dosages. Always recommend\n"
    "seeing a doctor for personal decisions."
)


def build_prompt(instruction: str) -> str:
    """Build the exact [INST] prompt used in all sprint stages."""
    assert isinstance(instruction, str) and instruction.strip(), "instruction must be non-empty"
    return f"[INST] {SYSTEM_INST}\n\n{instruction} [/INST]"


def format_sft(sample: dict) -> str:
    """Format a training sample into a single SFT text sequence."""
    assert "instruction" in sample and "output" in sample, "sample needs instruction and output"
    instruction = str(sample["instruction"]).strip()
    output = str(sample["output"]).strip()
    assert instruction and output, "instruction/output cannot be empty"
    return f"{build_prompt(instruction)} {output}"
