import statistics
from datetime import UTC, datetime


def freshness(
    last_entry_time: datetime | None,
    staleness_threshold_hours: float,
    *,
    now: datetime | None = None,
) -> float:
    """`max(0, 1 - hours_since_last_entry / staleness_threshold)` per §7.
    Also clamped to <=1 as a safety bound beyond the literal formula (a
    last_entry_time in the future — e.g. clock skew — shouldn't produce a
    freshness above "perfectly fresh"). `now` defaults to the real current
    time; callers pass it explicitly for deterministic tests.
    """
    if last_entry_time is None:
        return 0.0
    now = now or datetime.now(UTC)
    hours_since = (now - last_entry_time).total_seconds() / 3600
    return max(0.0, min(1.0, 1 - hours_since / staleness_threshold_hours))


def historical_stats(values: list[float]) -> tuple[float, float] | None:
    """Mean and population stdev of a patient's own historical values for a
    type. None when there's too little history to establish a distribution
    (<2 points) — callers should treat that as "can't judge, assume fine."
    """
    if len(values) < 2:
        return None
    return statistics.mean(values), statistics.pstdev(values)


def consistency_score_from_stats(value: float, mean: float, stdev: float) -> float:
    """1.0 minus a normalized outlier score (§7): z=0 -> 1.0, z>=3 (the
    conventional 3-standard-deviation outlier cutoff) -> 0.0. A zero-stdev
    history (every past value identical) treats any deviation as a full
    outlier rather than dividing by zero.
    """
    if stdev == 0:
        return 1.0 if value == mean else 0.0
    z = abs(value - mean) / stdev
    return max(0.0, 1 - z / 3)


def consistency_score(value: float, historical_values: list[float]) -> float:
    """Convenience wrapper over consistency_score_from_stats for callers that
    hold the raw historical values rather than precomputed (mean, stdev) —
    e.g. GlucoseConfidenceCalculator, which has the full list on hand, vs.
    ConsistencyRule, which only has TimelineSummary's precomputed stats
    (Rule.evaluate is sync and context-only, see services/rules.py).
    """
    stats = historical_stats(historical_values)
    if stats is None:
        return 1.0
    return consistency_score_from_stats(value, *stats)
