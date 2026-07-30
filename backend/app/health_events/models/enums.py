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
