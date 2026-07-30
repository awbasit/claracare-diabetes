from datetime import date
from typing import Literal

from pydantic import BaseModel

from app.health_events.models.enums import GlucoseUnit

Period = Literal["week", "month"]


class DailyGlucoseTrendPoint(BaseModel):
    date: date
    average: float | None
    minimum: float | None
    maximum: float | None
    count: int


class GlucoseTrendResponse(BaseModel):
    period: Period
    unit: GlucoseUnit
    start_date: date
    end_date: date
    points: list[DailyGlucoseTrendPoint]
