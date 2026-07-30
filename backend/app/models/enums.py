from enum import Enum


class UserRole(str, Enum):
    patient = "patient"
    clinician = "clinician"
    admin = "admin"


class Sex(str, Enum):
    male = "male"
    female = "female"
    other = "other"


class DiabetesType(str, Enum):
    type1 = "type1"
    type2 = "type2"
    gestational = "gestational"
    prediabetes = "prediabetes"
    other = "other"
