from app.clinical_reasoning.schemas.findings import EvidenceRef
from app.health_events.models.enums import EventType
from app.health_events.models.health_event import HealthEvent


def build_evidence_ref(health_event: HealthEvent) -> EvidenceRef:
    """Turns a raw HealthEvent (+ its type-specific detail row) into a
    human-readable EvidenceRef — e.g. "Missed Metformin, Wednesday" rather
    than "medication_logs row id=...". Sync and DB-free: the caller must
    have already eagerly loaded the relevant detail relationship (and, for
    medication, MedicationLog.medication) before calling this — nothing in
    Milestone 3.1 calls it yet, so there's no orchestration point that does
    that loading for you.
    """
    weekday = health_event.event_timestamp.strftime("%A")
    summary = f"{_summarize_detail(health_event)}, {weekday}"
    return EvidenceRef(source_type="timeline_event", source_id=health_event.id, summary=summary)


def _summarize_detail(health_event: HealthEvent) -> str:
    event_type = health_event.event_type

    if event_type == EventType.glucose and health_event.glucose_log is not None:
        glucose = health_event.glucose_log
        unit_label = "mg/dL" if glucose.unit.value == "mg_dl" else "mmol/L"
        return (
            f"Glucose {glucose.value} {unit_label} ({glucose.reading_type.value.replace('_', ' ')})"
        )

    if event_type == EventType.meal and health_event.meal_log is not None:
        meal = health_event.meal_log
        return f"{meal.meal_type.value.capitalize()} logged: {meal.food_items}"

    if event_type == EventType.medication and health_event.medication_log is not None:
        medication_log = health_event.medication_log
        verb = "Took" if medication_log.taken else "Missed"
        return f"{verb} {medication_log.medication.name}"

    if event_type == EventType.exercise and health_event.exercise_log is not None:
        exercise = health_event.exercise_log
        return (
            f"{exercise.duration_minutes} min {exercise.exercise_type} ({exercise.intensity.value})"
        )

    if event_type == EventType.sleep and health_event.sleep_log is not None:
        sleep = health_event.sleep_log
        return f"{sleep.hours_slept}h sleep ({sleep.quality.value})"

    if event_type == EventType.stress and health_event.stress_log is not None:
        stress = health_event.stress_log
        return f"Stress level {stress.stress_level} ({stress.mood.value} mood)"

    if event_type == EventType.symptom and health_event.symptom_log is not None:
        symptom = health_event.symptom_log
        label = symptom.symptom_type.value.replace("_", " ").capitalize()
        return f"{label} ({symptom.severity.value})"

    if event_type == EventType.vitals and health_event.vitals_log is not None:
        vitals = health_event.vitals_log
        parts = []
        if vitals.weight_kg is not None:
            parts.append(f"Weight {vitals.weight_kg} kg")
        if (
            vitals.blood_pressure_systolic is not None
            and vitals.blood_pressure_diastolic is not None
        ):
            parts.append(f"BP {vitals.blood_pressure_systolic}/{vitals.blood_pressure_diastolic}")
        if vitals.heart_rate is not None:
            parts.append(f"HR {vitals.heart_rate}")
        return ", ".join(parts) if parts else "Vitals logged"

    return f"{event_type.value.capitalize()} event"
