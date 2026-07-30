import uuid
from collections import defaultdict
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.health_events.analytics.schemas import DailyGlucoseTrendPoint, GlucoseTrendResponse, Period
from app.health_events.glucose.service import mg_dl_to_mmol_l, mmol_l_to_mg_dl
from app.health_events.models.enums import GlucoseUnit
from app.health_events.models.glucose_log import GlucoseLog
from app.health_events.models.health_event import HealthEvent

_PERIOD_DAYS: dict[Period, int] = {"week": 7, "month": 30}


def _normalize(value: float, from_unit: GlucoseUnit, to_unit: GlucoseUnit) -> float:
    if from_unit == to_unit:
        return value
    return mmol_l_to_mg_dl(value) if to_unit == GlucoseUnit.mg_dl else mg_dl_to_mmol_l(value)


async def get_glucose_trend(
    db: AsyncSession, patient_id: uuid.UUID, period: Period, unit: GlucoseUnit
) -> GlucoseTrendResponse:
    """Daily average/min/max/count of glucose readings over the trailing
    week or month, normalized to a single unit. Deliberately dumb: no
    smoothing, no outlier handling — just per-day arithmetic. Days with no
    readings still appear (nulls, count=0) so a chart's x-axis stays
    continuous instead of skipping gaps.
    """
    days = _PERIOD_DAYS[period]
    today = datetime.now(UTC).date()
    start_date = today - timedelta(days=days - 1)
    range_start = datetime(start_date.year, start_date.month, start_date.day, tzinfo=UTC)
    range_end = datetime(today.year, today.month, today.day, tzinfo=UTC) + timedelta(days=1)

    result = await db.execute(
        select(HealthEvent.event_timestamp, GlucoseLog.value, GlucoseLog.unit)
        .join(GlucoseLog, GlucoseLog.health_event_id == HealthEvent.id)
        .where(
            HealthEvent.patient_id == patient_id,
            HealthEvent.event_timestamp >= range_start,
            HealthEvent.event_timestamp < range_end,
        )
    )

    values_by_day: dict[date, list[float]] = defaultdict(list)
    for event_timestamp, value, row_unit in result.all():
        values_by_day[event_timestamp.date()].append(_normalize(value, row_unit, unit))

    points: list[DailyGlucoseTrendPoint] = []
    for offset in range(days):
        day = start_date + timedelta(days=offset)
        day_values = values_by_day.get(day, [])
        if day_values:
            points.append(
                DailyGlucoseTrendPoint(
                    date=day,
                    average=round(sum(day_values) / len(day_values), 1),
                    minimum=round(min(day_values), 1),
                    maximum=round(max(day_values), 1),
                    count=len(day_values),
                )
            )
        else:
            points.append(
                DailyGlucoseTrendPoint(date=day, average=None, minimum=None, maximum=None, count=0)
            )

    return GlucoseTrendResponse(
        period=period, unit=unit, start_date=start_date, end_date=today, points=points
    )
