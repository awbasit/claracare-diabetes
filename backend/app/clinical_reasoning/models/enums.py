from enum import Enum


class PatientGoalStatus(str, Enum):
    active = "active"
    achieved = "achieved"
    abandoned = "abandoned"


class PatientGoalSource(str, Enum):
    patient_stated = "patient_stated"
    ai_suggested = "ai_suggested"
