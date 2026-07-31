from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

from app.clinical_reasoning.schemas.context import MedicationSummary
from app.models.medication import Medication

RegimenLabel = Literal["basal_bolus_insulin", "insulin_non_intensive", "oral_or_none"]

# A plain Union rather than a structural Protocol: mypy's structural
# matching against SQLAlchemy's `Mapped[T]` class-body annotations is
# unreliable without the sqlalchemy2 mypy plugin (not installed here), so
# this names the two concrete callers instead — GlucoseConfidenceCalculator
# (loaded `patient.medications`, SQLAlchemy Medication rows) and GlucoseRule
# (PatientContext.medications, MedicationSummary) — without either depending
# on the other's module.
MedicationLike = Medication | MedicationSummary


@dataclass(frozen=True)
class GlucoseRegimenExpectation:
    label: RegimenLabel
    expected_readings_per_day: int
    staleness_hours: float


# Sprint 1's Medication model has no structured regimen/insulin-type field —
# just free-text name/frequency. This infers regimen from those free-text
# fields; it's a documented heuristic for expectation-setting, not a
# clinical classification, and is intentionally conservative (defaults to
# the lower-intensity tier when the frequency text is ambiguous).
_MULTI_DOSE_KEYWORDS = (
    "times a day",
    "times daily",
    "times/day",
    "before each meal",
    "before meals",
    "qid",
    "tid",
    "4x",
    "3x",
)


def determine_glucose_regimen(medications: Sequence[MedicationLike]) -> GlucoseRegimenExpectation:
    """Shared by GlucoseConfidenceCalculator (§6) and GlucoseRule (rules
    engine) so the insulin-vs-oral expectation is computed exactly once.
    """
    active_insulin = [m for m in medications if m.is_active and "insulin" in m.name.lower()]

    if not active_insulin:
        return GlucoseRegimenExpectation(
            "oral_or_none", expected_readings_per_day=1, staleness_hours=24.0
        )

    combined_frequency_text = " ".join((m.frequency or "").lower() for m in active_insulin)
    is_intensive = len(active_insulin) >= 2 or any(
        keyword in combined_frequency_text for keyword in _MULTI_DOSE_KEYWORDS
    )
    if is_intensive:
        return GlucoseRegimenExpectation(
            "basal_bolus_insulin", expected_readings_per_day=4, staleness_hours=6.0
        )
    return GlucoseRegimenExpectation(
        "insulin_non_intensive", expected_readings_per_day=2, staleness_hours=12.0
    )
