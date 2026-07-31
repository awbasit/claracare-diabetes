from typing import Literal

from pydantic import BaseModel

CoverageLabel = Literal["high", "moderate", "low", "unknown"]


class DataQuality(BaseModel):
    completeness: float  # 0-1, calculator-specific meaning (§6)
    freshness: float  # 0-1, decays with time since last entry
    consistency: float  # 0-1, variance/plausibility check
    reliability: float  # 0-1, manual vs imported, calculator-specific
    # Populated instead of leaning on `completeness` for event types where
    # "expected frequency" isn't meaningful (exercise, symptoms) — see
    # ExerciseConfidenceCalculator / SymptomConfidenceCalculator.
    coverage_label: CoverageLabel | None


class DataQualityReport(BaseModel):
    by_type: dict[str, DataQuality]
    overall: DataQuality
