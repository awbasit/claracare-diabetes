from datetime import UTC, datetime, timedelta

import pytest

from app.clinical_reasoning.services.glucose_regimen import determine_glucose_regimen
from app.clinical_reasoning.services.quality_utils import (
    consistency_score,
    consistency_score_from_stats,
    freshness,
    historical_stats,
)


class _FakeMedication:
    def __init__(self, name: str, is_active: bool = True, frequency: str | None = None) -> None:
        self.name = name
        self.is_active = is_active
        self.frequency = frequency


def test_freshness_full_at_zero_hours_since() -> None:
    now = datetime(2026, 1, 15, 12, tzinfo=UTC)
    assert freshness(now, staleness_threshold_hours=24, now=now) == 1.0


def test_freshness_decays_linearly_to_the_threshold() -> None:
    now = datetime(2026, 1, 15, 12, tzinfo=UTC)
    twelve_hours_ago = now - timedelta(hours=12)
    assert freshness(twelve_hours_ago, staleness_threshold_hours=24, now=now) == pytest.approx(0.5)


def test_freshness_zero_when_no_entry() -> None:
    assert freshness(None, staleness_threshold_hours=24) == 0.0


def test_freshness_floors_at_zero_past_the_threshold() -> None:
    now = datetime(2026, 1, 15, 12, tzinfo=UTC)
    two_days_ago = now - timedelta(days=2)
    assert freshness(two_days_ago, staleness_threshold_hours=24, now=now) == 0.0


def test_freshness_clamps_at_one_for_future_timestamps() -> None:
    now = datetime(2026, 1, 15, 12, tzinfo=UTC)
    one_hour_from_now = now + timedelta(hours=1)
    assert freshness(one_hour_from_now, staleness_threshold_hours=24, now=now) == 1.0


def test_historical_stats_none_with_fewer_than_two_points() -> None:
    assert historical_stats([]) is None
    assert historical_stats([100.0]) is None


def test_historical_stats_computes_mean_and_population_stdev() -> None:
    stats = historical_stats([90.0, 100.0, 110.0])
    assert stats is not None
    mean, stdev = stats
    assert mean == pytest.approx(100.0)
    assert stdev == pytest.approx(8.1650, abs=0.001)


def test_consistency_score_from_stats_zero_z_is_perfect() -> None:
    assert consistency_score_from_stats(100.0, mean=100.0, stdev=10.0) == 1.0


def test_consistency_score_from_stats_three_sigma_is_zero() -> None:
    assert consistency_score_from_stats(130.0, mean=100.0, stdev=10.0) == 0.0


def test_consistency_score_from_stats_far_outlier_floors_at_zero() -> None:
    assert consistency_score_from_stats(500.0, mean=100.0, stdev=10.0) == 0.0


def test_consistency_score_from_stats_one_sigma_is_two_thirds() -> None:
    assert consistency_score_from_stats(110.0, mean=100.0, stdev=10.0) == pytest.approx(2 / 3)


def test_consistency_score_from_stats_zero_stdev_exact_match_is_perfect() -> None:
    assert consistency_score_from_stats(100.0, mean=100.0, stdev=0.0) == 1.0


def test_consistency_score_from_stats_zero_stdev_any_deviation_is_zero() -> None:
    assert consistency_score_from_stats(100.1, mean=100.0, stdev=0.0) == 0.0


def test_consistency_score_insufficient_history_defaults_to_perfect() -> None:
    assert consistency_score(999.0, []) == 1.0
    assert consistency_score(999.0, [100.0]) == 1.0


def test_consistency_score_matches_consistency_score_from_stats() -> None:
    history = [90.0, 100.0, 110.0]
    mean, stdev = historical_stats(history)  # type: ignore[misc]
    expected = consistency_score_from_stats(150.0, mean, stdev)
    assert consistency_score(150.0, history) == pytest.approx(expected)


def test_glucose_regimen_no_medications_is_oral_or_none() -> None:
    regimen = determine_glucose_regimen([])
    assert regimen.label == "oral_or_none"
    assert regimen.expected_readings_per_day == 1
    assert regimen.staleness_hours == 24.0


def test_glucose_regimen_ignores_inactive_insulin() -> None:
    regimen = determine_glucose_regimen([_FakeMedication("Insulin Glargine", is_active=False)])
    assert regimen.label == "oral_or_none"


def test_glucose_regimen_oral_medications_only_is_oral_or_none() -> None:
    regimen = determine_glucose_regimen(
        [_FakeMedication("Metformin", frequency="twice daily"), _FakeMedication("Glipizide")]
    )
    assert regimen.label == "oral_or_none"
    assert regimen.expected_readings_per_day == 1


def test_glucose_regimen_single_insulin_moderate_frequency_is_non_intensive() -> None:
    regimen = determine_glucose_regimen(
        [_FakeMedication("Insulin Glargine", frequency="once daily")]
    )
    assert regimen.label == "insulin_non_intensive"
    assert regimen.expected_readings_per_day == 2
    assert regimen.staleness_hours == 12.0


def test_glucose_regimen_multiple_insulin_medications_is_basal_bolus() -> None:
    regimen = determine_glucose_regimen(
        [
            _FakeMedication("Insulin Glargine", frequency="once daily"),
            _FakeMedication("Insulin Lispro", frequency="before meals"),
        ]
    )
    assert regimen.label == "basal_bolus_insulin"
    assert regimen.expected_readings_per_day == 4
    assert regimen.staleness_hours == 6.0


def test_glucose_regimen_single_insulin_with_multi_dose_text_is_basal_bolus() -> None:
    regimen = determine_glucose_regimen(
        [_FakeMedication("Insulin Aspart", frequency="three times a day before meals")]
    )
    assert regimen.label == "basal_bolus_insulin"
