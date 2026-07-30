import uuid
from datetime import datetime
from typing import Self

from pydantic import BaseModel

from app.health_events.models.enums import EventSource, MealType
from app.health_events.models.health_event import HealthEvent
from app.health_events.models.meal_log import MealLog


class MealLogCreate(BaseModel):
    event_timestamp: datetime
    meal_type: MealType
    food_items: str
    estimated_carbs_g: float | None = None
    estimated_calories: int | None = None
    portion_size: str | None = None
    drink: str | None = None
    notes: str | None = None


class MealLogUpdate(BaseModel):
    event_timestamp: datetime | None = None
    meal_type: MealType | None = None
    food_items: str | None = None
    estimated_carbs_g: float | None = None
    estimated_calories: int | None = None
    portion_size: str | None = None
    drink: str | None = None
    notes: str | None = None


class MealLogRead(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    event_timestamp: datetime
    notes: str | None
    source: EventSource
    created_at: datetime
    updated_at: datetime

    meal_type: MealType
    food_items: str
    estimated_carbs_g: float | None
    estimated_calories: int | None
    portion_size: str | None
    drink: str | None

    @classmethod
    def from_event_and_detail(cls, event: HealthEvent, detail: MealLog) -> Self:
        return cls(
            id=event.id,
            patient_id=event.patient_id,
            event_timestamp=event.event_timestamp,
            notes=event.notes,
            source=event.source,
            created_at=event.created_at,
            updated_at=event.updated_at,
            meal_type=detail.meal_type,
            food_items=detail.food_items,
            estimated_carbs_g=detail.estimated_carbs_g,
            estimated_calories=detail.estimated_calories,
            portion_size=detail.portion_size,
            drink=detail.drink,
        )
