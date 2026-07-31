import uuid
from datetime import UTC, datetime, timedelta

from app.clinical_reasoning.schemas.context import (
    AdherenceSummary,
    DemographicsSummary,
    DiabetesHistorySummary,
    GlucoseReading,
    LifestyleSummary,
    MedicationSummary,
    PatientContext,
    TimelineSummary,
)
from app.clinical_reasoning.services.rules import (
    ConsistencyRule,
    GlucoseRule,
    MealRule,
    MedicationAdherenceRule,
    RuleRegistry,
    SleepRule,
)
from app.health_events.models.enums import GlucoseReadingType, GlucoseUnit

_NOW = datetime(
    2026, 1, 15, 15, 0, tzinfo=UTC
)  # a fixed 3pm, past all 3 meal checkpoints (10/14/20 partially)


def _context(**overrides: object) -> PatientContext:
    defaults: dict[str, object] = dict(
        patient_id=uuid.uuid4(),
        version=1,
        generated_at=_NOW,
        demographics=DemographicsSummary(
            age=45,
            sex=None,
            height_cm=None,
            weight_kg=None,
            bmi=None,
            occupation=None,
            work_schedule=None,
        ),
        diabetes_history=DiabetesHistorySummary(
            diabetes_type=None,
            years_since_diagnosis=None,
            family_history=False,
            family_history_notes=None,
            latest_hba1c=None,
            latest_blood_pressure_systolic=None,
            latest_blood_pressure_diastolic=None,
            latest_cholesterol=None,
            has_kidney_disease=False,
            has_eye_disease=False,
            has_neuropathy=False,
            comorbidities=[],
        ),
        medications=[],
        latest_glucose=None,
        last_7_day_summary=TimelineSummary(
            period_days=7,
            total_events=0,
            glucose_reading_count=0,
            glucose_average_mg_dl=None,
            glucose_stdev_mg_dl=None,
            meals_logged_count=0,
            meals_logged_today=0,
            last_meal_at=None,
            exercise_total_minutes=0,
            exercise_session_count=0,
            sleep_average_hours=None,
            last_sleep_at=None,
            average_stress_level=None,
            symptoms_logged_count=0,
        ),
        adherence_summary=AdherenceSummary(
            doses_taken_7day=0, doses_missed_7day=0, adherence_pct_7day=None
        ),
        active_symptoms=[],
        lifestyle_summary=LifestyleSummary(
            sleep_hours_avg=None,
            exercise_frequency=None,
            exercise_type=None,
            smoking_status=None,
            alcohol_use=None,
            stress_level_baseline=None,
            meal_schedule_notes=None,
        ),
        goals=[],
        recent_patterns=[],
        known_barriers=[],
    )
    defaults.update(overrides)
    return PatientContext(**defaults)  # type: ignore[arg-type]


def _medication(
    name: str, *, is_active: bool = True, last_logged_at: datetime | None = None
) -> MedicationSummary:
    return MedicationSummary(
        id=uuid.uuid4(),
        name=name,
        dosage=None,
        frequency=None,
        time_of_day=None,
        purpose=None,
        is_active=is_active,
        last_logged_at=last_logged_at,
    )


# --- MedicationAdherenceRule --------------------------------------------------


def test_medication_adherence_flags_medication_never_logged() -> None:
    context = _context(medications=[_medication("Metformin", last_logged_at=None)])
    findings = MedicationAdherenceRule(now=_NOW).evaluate(context)
    assert len(findings) == 1
    assert findings[0].event_type == "medication"
    assert "Metformin" in findings[0].reason


def test_medication_adherence_flags_stale_log() -> None:
    stale = _NOW - timedelta(hours=25)
    context = _context(medications=[_medication("Metformin", last_logged_at=stale)])
    findings = MedicationAdherenceRule(now=_NOW).evaluate(context)
    assert len(findings) == 1


def test_medication_adherence_does_not_flag_recent_log() -> None:
    recent = _NOW - timedelta(hours=1)
    context = _context(medications=[_medication("Metformin", last_logged_at=recent)])
    findings = MedicationAdherenceRule(now=_NOW).evaluate(context)
    assert findings == []


def test_medication_adherence_ignores_inactive_medications() -> None:
    context = _context(medications=[_medication("Old Med", is_active=False, last_logged_at=None)])
    findings = MedicationAdherenceRule(now=_NOW).evaluate(context)
    assert findings == []


# --- GlucoseRule ---------------------------------------------------------------


def test_glucose_rule_flags_no_reading_ever() -> None:
    context = _context(latest_glucose=None)
    findings = GlucoseRule(now=_NOW).evaluate(context)
    assert len(findings) == 1
    assert findings[0].event_type == "glucose"
    assert findings[0].severity == "medium"  # oral_or_none regimen with no medications


def test_glucose_rule_flags_stale_reading_for_oral_regimen() -> None:
    stale = _NOW - timedelta(hours=25)
    context = _context(
        latest_glucose=GlucoseReading(
            value=100,
            unit=GlucoseUnit.mg_dl,
            reading_type=GlucoseReadingType.fasting,
            timestamp=stale,
        )
    )
    findings = GlucoseRule(now=_NOW).evaluate(context)
    assert len(findings) == 1


def test_glucose_rule_does_not_flag_recent_reading() -> None:
    recent = _NOW - timedelta(hours=1)
    context = _context(
        latest_glucose=GlucoseReading(
            value=100,
            unit=GlucoseUnit.mg_dl,
            reading_type=GlucoseReadingType.fasting,
            timestamp=recent,
        )
    )
    findings = GlucoseRule(now=_NOW).evaluate(context)
    assert findings == []


def test_glucose_rule_uses_tighter_window_and_higher_severity_for_basal_bolus() -> None:
    seven_hours_ago = _NOW - timedelta(hours=7)  # stale for basal-bolus (6h) but not for oral (24h)
    context = _context(
        medications=[
            _medication("Insulin Glargine"),
            _medication("Insulin Lispro"),
        ],
        latest_glucose=GlucoseReading(
            value=100,
            unit=GlucoseUnit.mg_dl,
            reading_type=GlucoseReadingType.fasting,
            timestamp=seven_hours_ago,
        ),
    )
    findings = GlucoseRule(now=_NOW).evaluate(context)
    assert len(findings) == 1
    assert findings[0].severity == "high"


# --- SleepRule -------------------------------------------------------------


def test_sleep_rule_flags_no_sleep_ever() -> None:
    findings = SleepRule(now=_NOW).evaluate(_context())
    assert len(findings) == 1
    assert findings[0].event_type == "sleep"


def test_sleep_rule_does_not_flag_entry_from_yesterday() -> None:
    yesterday = _NOW - timedelta(days=1)
    context = _context()
    context.last_7_day_summary.last_sleep_at = yesterday
    findings = SleepRule(now=_NOW).evaluate(context)
    assert findings == []


def test_sleep_rule_does_not_flag_entry_from_today() -> None:
    context = _context()
    context.last_7_day_summary.last_sleep_at = _NOW - timedelta(hours=2)
    findings = SleepRule(now=_NOW).evaluate(context)
    assert findings == []


def test_sleep_rule_flags_entry_older_than_yesterday() -> None:
    context = _context()
    context.last_7_day_summary.last_sleep_at = _NOW - timedelta(days=3)
    findings = SleepRule(now=_NOW).evaluate(context)
    assert len(findings) == 1


# --- MealRule ----------------------------------------------------------------


def test_meal_rule_does_not_flag_before_first_checkpoint() -> None:
    morning = datetime(2026, 1, 15, 8, 0, tzinfo=UTC)  # before the 10am checkpoint
    context = _context()
    findings = MealRule(now=morning).evaluate(context)
    assert findings == []


def test_meal_rule_flags_no_meals_by_early_afternoon() -> None:
    early_afternoon = datetime(2026, 1, 15, 15, 0, tzinfo=UTC)  # past 10am and 2pm checkpoints
    context = _context()
    findings = MealRule(now=early_afternoon).evaluate(context)
    assert len(findings) == 1
    assert "2 expected" in findings[0].reason


def test_meal_rule_does_not_flag_when_logged_meals_meet_checkpoint() -> None:
    early_afternoon = datetime(2026, 1, 15, 15, 0, tzinfo=UTC)
    context = _context()
    context.last_7_day_summary.meals_logged_today = 2
    findings = MealRule(now=early_afternoon).evaluate(context)
    assert findings == []


def test_meal_rule_does_not_flag_dinner_in_the_morning() -> None:
    # The whole point of the checkpoint schedule: don't flag "no dinner" at 10am.
    morning = datetime(2026, 1, 15, 9, 0, tzinfo=UTC)
    context = _context()
    findings = MealRule(now=morning).evaluate(context)
    assert findings == []


# --- ConsistencyRule -----------------------------------------------------------


def test_consistency_rule_no_findings_without_history() -> None:
    context = _context(
        latest_glucose=GlucoseReading(
            value=100,
            unit=GlucoseUnit.mg_dl,
            reading_type=GlucoseReadingType.fasting,
            timestamp=_NOW,
        )
    )
    findings = ConsistencyRule().evaluate(context)
    assert findings == []


def test_consistency_rule_flags_clear_outlier() -> None:
    context = _context(
        latest_glucose=GlucoseReading(
            value=350,
            unit=GlucoseUnit.mg_dl,
            reading_type=GlucoseReadingType.fasting,
            timestamp=_NOW,
        )
    )
    context.last_7_day_summary.glucose_average_mg_dl = 100.0
    context.last_7_day_summary.glucose_stdev_mg_dl = 10.0
    findings = ConsistencyRule().evaluate(context)
    assert len(findings) == 1
    assert findings[0].event_type == "glucose"
    assert findings[0].severity == "medium"


def test_consistency_rule_does_not_flag_typical_reading() -> None:
    context = _context(
        latest_glucose=GlucoseReading(
            value=102,
            unit=GlucoseUnit.mg_dl,
            reading_type=GlucoseReadingType.fasting,
            timestamp=_NOW,
        )
    )
    context.last_7_day_summary.glucose_average_mg_dl = 100.0
    context.last_7_day_summary.glucose_stdev_mg_dl = 10.0
    findings = ConsistencyRule().evaluate(context)
    assert findings == []


def test_consistency_rule_normalizes_mmol_l_before_comparing() -> None:
    # 10 mmol/L ~= 180.2 mg/dL — a clear outlier against a ~100 mg/dL baseline.
    context = _context(
        latest_glucose=GlucoseReading(
            value=10,
            unit=GlucoseUnit.mmol_l,
            reading_type=GlucoseReadingType.fasting,
            timestamp=_NOW,
        )
    )
    context.last_7_day_summary.glucose_average_mg_dl = 100.0
    context.last_7_day_summary.glucose_stdev_mg_dl = 10.0
    findings = ConsistencyRule().evaluate(context)
    assert len(findings) == 1


# --- RuleRegistry --------------------------------------------------------------


def test_rule_registry_combines_findings_from_all_rules() -> None:
    # An entirely empty context should trip MedicationAdherenceRule (no meds,
    # so nothing to flag), GlucoseRule (no reading), SleepRule (no sleep),
    # and MealRule (depends on real wall-clock hour) — use the default,
    # non-time-fixed registry just to prove it doesn't crash and returns a
    # list combining more than one rule's output.
    registry = RuleRegistry([GlucoseRule(now=_NOW), SleepRule(now=_NOW)])
    findings = registry.evaluate(_context())
    assert len(findings) == 2
    assert {f.event_type for f in findings} == {"glucose", "sleep"}


def test_check_contradiction_stub_is_callable_and_returns_none() -> None:
    context = _context()
    for rule in (
        MedicationAdherenceRule(),
        GlucoseRule(),
        SleepRule(),
        MealRule(),
        ConsistencyRule(),
    ):
        assert rule.check_contradiction("some statement", context) is None
