from abc import ABC, abstractmethod
from datetime import UTC, datetime, timedelta

from app.clinical_reasoning.schemas.context import PatientContext
from app.clinical_reasoning.schemas.findings import Contradiction, MissingInformation
from app.clinical_reasoning.services.glucose_regimen import determine_glucose_regimen
from app.clinical_reasoning.services.quality_utils import consistency_score_from_stats
from app.health_events.glucose.service import mmol_l_to_mg_dl
from app.health_events.models.enums import GlucoseUnit

# Hour-of-day checkpoints past which a given number of meals should have
# been logged — a dumb, fixed schedule, not personalized. Keeps MealRule
# from flagging "no dinner logged" at 10am.
_MEAL_CHECKPOINTS_HOUR = (10, 14, 20)

# Below this consistency score, a reading is treated as enough of an
# outlier to surface — chosen so only genuinely unusual values (z >~ 1.5)
# trigger a flag, not ordinary day-to-day variance.
_CONSISTENCY_FLAG_THRESHOLD = 0.5


class Rule(ABC):
    @abstractmethod
    def evaluate(self, context: PatientContext) -> list[MissingInformation]: ...

    def check_contradiction(self, statement: str, context: PatientContext) -> Contradiction | None:
        # Stub for Milestone 3.2 — structured contradiction detection isn't
        # built yet. Must exist and be callable now so the interface is
        # already in place when 3.2 implements it.
        return None


class MedicationAdherenceRule(Rule):
    """Sprint 1's Medication model has free-text frequency, not a structured
    per-dose schedule, so "a scheduled dose" is approximated as "this
    actively-prescribed medication" — flags any active medication with no
    log at all in the last 24h.
    """

    def __init__(self, now: datetime | None = None) -> None:
        # Optional override for deterministic tests — production callers
        # never pass it, so evaluate(context) still matches the ABC exactly.
        self._now = now

    def evaluate(self, context: PatientContext) -> list[MissingInformation]:
        now = self._now or datetime.now(UTC)
        findings = []
        for medication in context.medications:
            if not medication.is_active:
                continue
            hours_since = (
                (now - medication.last_logged_at).total_seconds() / 3600
                if medication.last_logged_at is not None
                else None
            )
            if hours_since is None or hours_since > 24:
                findings.append(
                    MissingInformation(
                        event_type="medication",
                        reason=f"No log for {medication.name} in the last 24 hours",
                        severity="medium",
                    )
                )
        return findings


class GlucoseRule(Rule):
    """N depends on regimen — basal-bolus insulin expects a reading every
    ~6h, oral-only every ~24h — via the shared glucose_regimen lookup also
    used by GlucoseConfidenceCalculator.
    """

    def __init__(self, now: datetime | None = None) -> None:
        self._now = now

    def evaluate(self, context: PatientContext) -> list[MissingInformation]:
        regimen = determine_glucose_regimen(context.medications)
        now = self._now or datetime.now(UTC)

        if context.latest_glucose is None:
            hours_since: float | None = None
        else:
            hours_since = (now - context.latest_glucose.timestamp).total_seconds() / 3600

        if hours_since is None or hours_since > regimen.staleness_hours:
            severity = "high" if regimen.label == "basal_bolus_insulin" else "medium"
            return [
                MissingInformation(
                    event_type="glucose",
                    reason=f"No glucose reading in the last {regimen.staleness_hours:.0f} hours",
                    severity=severity,
                )
            ]
        return []


class SleepRule(Rule):
    """A sleep entry is typically logged the morning after waking, so "last
    night" is approximated as "an entry dated yesterday or today."
    """

    def __init__(self, now: datetime | None = None) -> None:
        self._now = now

    def evaluate(self, context: PatientContext) -> list[MissingInformation]:
        last_sleep_at = context.last_7_day_summary.last_sleep_at
        yesterday = (self._now or datetime.now(UTC)).date() - timedelta(days=1)
        logged_recently = last_sleep_at is not None and last_sleep_at.date() >= yesterday
        if not logged_recently:
            return [
                MissingInformation(
                    event_type="sleep", reason="No sleep logged for last night", severity="low"
                )
            ]
        return []


class MealRule(Rule):
    def __init__(self, now: datetime | None = None) -> None:
        self._now = now

    def evaluate(self, context: PatientContext) -> list[MissingInformation]:
        hour = (self._now or datetime.now(UTC)).hour
        expected_by_now = sum(1 for checkpoint in _MEAL_CHECKPOINTS_HOUR if hour >= checkpoint)
        if expected_by_now > 0 and context.last_7_day_summary.meals_logged_today < expected_by_now:
            return [
                MissingInformation(
                    event_type="meal",
                    reason=f"No meals logged today by {hour}:00 ({expected_by_now} expected)",
                    severity="low",
                )
            ]
        return []


class ConsistencyRule(Rule):
    """Glucose-only for this milestone — the clearest existing case of a
    numeric reading with an established personal baseline
    (TimelineSummary.glucose_average/stdev). Reuses the same
    consistency_score machinery as GlucoseConfidenceCalculator's consistency
    dimension (§7), just fed precomputed stats instead of a raw list, since
    Rule.evaluate only ever sees the already-built PatientContext.

    Routing an outlier flag through MissingInformation is a stopgap: it
    isn't really "missing" data, but Contradiction's "possible_inconsistency"
    category is reserved for Sprint 5/6 and Milestone 3.2 hasn't wired up
    check_contradiction yet.
    """

    def evaluate(self, context: PatientContext) -> list[MissingInformation]:
        latest = context.latest_glucose
        summary = context.last_7_day_summary
        if (
            latest is None
            or summary.glucose_average_mg_dl is None
            or summary.glucose_stdev_mg_dl is None
        ):
            return []

        value_mg_dl = (
            latest.value if latest.unit == GlucoseUnit.mg_dl else mmol_l_to_mg_dl(latest.value)
        )
        score = consistency_score_from_stats(
            value_mg_dl, summary.glucose_average_mg_dl, summary.glucose_stdev_mg_dl
        )
        if score < _CONSISTENCY_FLAG_THRESHOLD:
            return [
                MissingInformation(
                    event_type="glucose",
                    reason=(
                        f"Latest glucose reading of {latest.value} {latest.unit} is unusual "
                        f"compared to the recent average of {summary.glucose_average_mg_dl} mg/dL "
                        "— verify accuracy"
                    ),
                    severity="medium",
                )
            ]
        return []


class RuleRegistry:
    """Runs evaluate() across all active rules and combines the results.
    Adding a rule never touches existing rules — extend `_default_rules()`
    or pass a custom list in.
    """

    def __init__(self, rules: list[Rule] | None = None) -> None:
        self._rules = rules if rules is not None else _default_rules()

    def evaluate(self, context: PatientContext) -> list[MissingInformation]:
        findings: list[MissingInformation] = []
        for rule in self._rules:
            findings.extend(rule.evaluate(context))
        return findings


def _default_rules() -> list[Rule]:
    return [
        MedicationAdherenceRule(),
        GlucoseRule(),
        SleepRule(),
        MealRule(),
        ConsistencyRule(),
    ]
