from datetime import datetime

from pydantic import BaseModel

from app.clinical_reasoning.schemas.context import PatientContext
from app.clinical_reasoning.schemas.data_quality import DataQualityReport
from app.clinical_reasoning.schemas.findings import Contradiction, MissingInformation


class ClinicalAssessment(BaseModel):
    """Describes the patient's state (context + data quality + gaps) — it
    deliberately has NO `findings` field. Findings describe the AI's own
    reasoning about that state and live only in the Clinical Reasoning
    Ledger (Milestone 3.4), keeping "what's true about the patient" and
    "what the AI concluded" from bleeding into one object.
    """

    version: int
    context_version: int  # the PatientContext.version this was built from
    generated_at: datetime
    patient_context: PatientContext
    data_quality: DataQualityReport
    contradictions: list[Contradiction]
    missing_information: list[MissingInformation]
    uncertainties: list[str]
