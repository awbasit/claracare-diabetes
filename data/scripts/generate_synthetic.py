import json
import os
import time
from dotenv import load_dotenv
from pathlib import Path

from openai import OpenAI
import jsonlines

load_dotenv()

ROOT = Path(__file__).resolve().parents[2]
SYN = ROOT / "data" / "processed" / "synthetic.jsonl"
MODEL = "gpt-4o-mini"

SYSTEM = (
    "You are generating training data for a health literacy assistant that\n"
    "helps Type 2 diabetes patients in Ghana understand their condition.\n"
    "Generate ONE patient question and a clear, simple answer.\n"
    "Rules for the answer:\n"
    "- Maximum grade 7 reading level\n"
    "- Short sentences (under 15 words each)\n"
    "- No jargon without plain-language explanation\n"
    "- Warm, direct tone\n"
    "- Never give specific drug dosages\n"
    "- Always recommend seeing a doctor for personal medical decisions\n"
    "Return ONLY valid JSON. No preamble. No markdown fences.\n"
    "Schema: {instruction: str, input: str, output: str, topic: str, source: str}\n"
    'Set input to empty string. Set source to "synthetic".'
)

TOPICS = [
    "what type 2 diabetes means in simple terms",
    "difference between type 1 and type 2 diabetes",
    "why blood sugar rises after eating",
    "what HbA1c means and what a good number looks like",
    "what fasting blood sugar means",
    "what a normal blood sugar range is",
    "common symptoms of high blood sugar",
    "common symptoms of low blood sugar",
    "what happens when blood sugar stays high for too long",
    "how often to check blood sugar at home",
    "how to use a glucometer step by step",
    "what time of day is best to check blood sugar",
    "what to eat for breakfast when you have diabetes",
    "foods that raise blood sugar quickly to avoid",
    "foods that are safe to eat regularly with diabetes",
    "how portion size affects blood sugar levels",
    "why exercise helps control blood sugar",
    "safe exercises for someone newly diagnosed with diabetes",
    "how alcohol affects blood sugar levels",
    "what to eat before and after exercise with diabetes",
    "how metformin works explained simply",
    "what to do if you forget your diabetes medication",
    "common side effects of metformin in simple language",
    "when insulin becomes necessary for type 2 diabetes",
    "how to store insulin properly at home",
    "what to do when blood sugar is very low at home",
    "symptoms of a diabetic emergency and when to call for help",
    "how diabetes affects the kidneys over time",
    "how diabetes affects the eyes and vision",
    "how diabetes affects the feet and why foot care matters",
    "what diabetic neuropathy means and how it feels",
    "why sleeping well matters for blood sugar control",
    "how stress raises blood sugar and what to do about it",
    "how to explain your diabetes diagnosis to your family",
    "managing diabetes when you cannot afford a glucometer in Ghana",
    "local Ghanaian foods that are safe for diabetics",
    "local Ghanaian foods that can raise blood sugar quickly",
    "managing diabetes during hot weather in West Africa",
    "how to stay hydrated safely with diabetes",
    "what to do if you cannot afford diabetes medication",
    "how to talk to your doctor when you do not understand something",
    "how to keep a simple diabetes diary at home",
    "why regular clinic visits matter for diabetes management",
    "what questions to ask at your next diabetes appointment",
    "how weight loss helps control type 2 diabetes",
    "what happens if diabetes is left untreated for years",
    "how diabetes and high blood pressure are connected",
    "what a diabetes-friendly meal plate looks like",
    "how to read a food label when you have diabetes",
    "what sugar-free products mean and are they always safe",
    "how to manage diabetes during a religious fast",
    "travelling with diabetes — what to pack and check",
    "how to handle low blood sugar at school or work",
    "what is pre-diabetes and can it be reversed",
    "can type 2 diabetes be reversed with lifestyle changes",
    "how to set a simple daily routine for diabetes management",
    "how to get support from family when living with diabetes",
    "what community health workers can help with for diabetes in Ghana",
    "how to manage diabetes on a low income in West Africa",
    "what to eat during a diabetes-friendly Ghanaian celebration meal",
]


def chk(row, topic_expected):
    need = {"instruction", "input", "output", "topic", "source"}
    assert isinstance(row, dict) and set(row.keys()) >= need
    assert row["source"] == "synthetic"
    assert row["input"] == ""
    assert row["topic"] == topic_expected
    assert len(row["output"].split()) >= 30


def dump(path, mode, rows):
    with jsonlines.open(path, mode=mode) as wf:
        for r in rows:
            wf.write(r)


def main():
    api_key = os.getenv("OPENAI_API_KEY")
    assert api_key, "Set OPENAI_API_KEY"
    assert len(TOPICS) == 60, "Must be 60 sprint topics"
    assert len(TOPICS) <= 150

    SYN.parent.mkdir(parents=True, exist_ok=True)
    SYN.unlink(missing_ok=True)
    buf = []
    did_write = False
    for topic in TOPICS:
        try:
            cli = OpenAI(api_key=api_key)

            response = cli.chat.completions.create(
                model=MODEL,
                temperature=0.9,
                max_tokens=500,
                messages=[
                    {"role": "system", "content": SYSTEM},
                    {
                        "role": "user",
                        "content": (
                            'Return one JSON object with keys "instruction", '
                            '"input", "output", "topic", "source". Topic must '
                            "exactly match: "
                            + json.dumps(topic)
                        ),
                    },
                ],
            )

            blk = response.choices[0].message.content
            row = json.loads(blk.strip())
            chk(row, topic)
            buf.append(row)
            if len(buf) >= 10:
                dump(SYN, "a" if did_write else "w", buf)
                did_write = True
                buf.clear()
        except Exception as e:
            print(f"skipped {topic[:48]!r}... {e!r}")
        time.sleep(0.5)
    if buf:
        dump(SYN, "a" if did_write else "w", buf)


if __name__ == "__main__":
    main()