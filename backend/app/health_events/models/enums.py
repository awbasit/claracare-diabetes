from enum import Enum


class EventType(str, Enum):
    glucose = "glucose"
    meal = "meal"
    medication = "medication"
    exercise = "exercise"
    sleep = "sleep"
    stress = "stress"
    symptom = "symptom"
    vitals = "vitals"


class EventSource(str, Enum):
    manual = "manual"
    imported = "imported"


class GlucoseUnit(str, Enum):
    mg_dl = "mg_dl"
    mmol_l = "mmol_l"


class GlucoseReadingType(str, Enum):
    fasting = "fasting"
    before_breakfast = "before_breakfast"
    after_breakfast = "after_breakfast"
    before_lunch = "before_lunch"
    after_lunch = "after_lunch"
    before_dinner = "before_dinner"
    after_dinner = "after_dinner"
    bedtime = "bedtime"
    random = "random"


class MealType(str, Enum):
    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"
    snack = "snack"


class ExerciseIntensity(str, Enum):
    light = "light"
    moderate = "moderate"
    vigorous = "vigorous"


class SleepQuality(str, Enum):
    poor = "poor"
    fair = "fair"
    good = "good"
    excellent = "excellent"


class Mood(str, Enum):
    low = "low"
    neutral = "neutral"
    good = "good"
    high = "high"


class SymptomType(str, Enum):
    excessive_thirst = "excessive_thirst"
    frequent_urination = "frequent_urination"
    blurred_vision = "blurred_vision"
    fatigue = "fatigue"
    dizziness = "dizziness"
    sweating = "sweating"
    confusion = "confusion"
    foot_pain = "foot_pain"
    chest_pain = "chest_pain"
    breathing_difficulty = "breathing_difficulty"
    nausea = "nausea"
    vomiting = "vomiting"
    other = "other"


class SymptomSeverity(str, Enum):
    mild = "mild"
    moderate = "moderate"
    severe = "severe"
