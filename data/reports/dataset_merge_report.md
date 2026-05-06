# Dataset Merge Report

## Input Summary
- HF loaded rows: 1075
- HF kept rows: 933
- HF dropped rows: 125
- Current train rows: 129
- Current eval rows: 120
- Real cleaned rows: 8988
- Synthetic rows included: 30
- Synthetic path used: `C:\Users\dell\Desktop\LLM\claracare-diabetes\data\processed\synthetic_clean.jsonl`
- Real rows after strict filter: 1792
- HF rows after filter: 823
- Synthetic rows after targeted filter: 30
- Source caps used: real=150, hf=700, synthetic=50

## Processing Summary
- Duplicate rows removed: 40
- Leakage rows removed from train: 0
- Post-merge safety rows removed: 21
- Final train count: 862
- Final eval count: 117

## HF Top Drop Reasons

| Drop Reason | Count |
|---|---:|
| not_diabetes_centered | 77 |
| pregnancy_non_diabetes_context | 23 |
| short_output | 13 |
| unsafe_dosage | 11 |
| off_scope_term | 1 |

## Topic Distribution (Final Train)

| Topic | Count |
|---|---:|
| blood_sugar_monitoring | 306 |
| diet_lifestyle | 97 |
| complications | 89 |
| other_diabetes | 83 |
| medication | 64 |
| exercise | 45 |
| insulin | 43 |
| emotional_support | 37 |
| diabetes_basics | 36 |
| emergencies | 26 |
| foot_care | 18 |
| healthcare_visit | 18 |

## Source Distribution (Final Train)

| Source | Count |
|---|---:|
| hf_diabetes_qa | 684 |
| real | 148 |
| synthetic | 30 |
