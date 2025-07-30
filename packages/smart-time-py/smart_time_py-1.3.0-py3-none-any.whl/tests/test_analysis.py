"""Testes para o módulo de análise temporal."""

from datetime import date, datetime

import pytest

from smart_time_py.analysis import (TimeGroup, analyze_seasonality,
                                    calculate_temporal_stats,
                                    detect_temporal_patterns, group_dates)


@pytest.fixture
def sample_dates():
    """Fixture com datas de exemplo para testes."""
    return [
        datetime(2025, 1, 1, 10, 0),
        datetime(2025, 1, 2, 10, 0),
        datetime(2025, 1, 3, 10, 0),
        datetime(2025, 1, 8, 10, 0),
        datetime(2025, 1, 9, 10, 0),
        datetime(2025, 1, 10, 10, 0),
        datetime(2025, 2, 1, 10, 0),
        datetime(2025, 2, 2, 10, 0),
        datetime(2025, 2, 3, 10, 0),
    ]


def test_group_dates_daily(sample_dates):
    """Testa agrupamento diário de datas."""
    groups = group_dates(sample_dates, TimeGroup.DAILY)
    assert len(groups) == 9
    assert "2025-01-01" in groups
    assert len(groups["2025-01-01"]) == 1


def test_group_dates_weekly(sample_dates):
    """Testa agrupamento semanal de datas."""
    groups = group_dates(sample_dates, TimeGroup.WEEKLY)
    assert len(groups) == 4
    assert "2025-W01" in groups
    assert "2025-W02" in groups
    assert "2025-W05" in groups
    assert "2025-W06" in groups
    assert len(groups["2025-W01"]) == 3
    assert len(groups["2025-W02"]) == 3
    assert len(groups["2025-W05"]) == 2
    assert len(groups["2025-W06"]) == 1


def test_group_dates_monthly(sample_dates):
    """Testa agrupamento mensal de datas."""
    groups = group_dates(sample_dates, TimeGroup.MONTHLY)
    assert len(groups) == 2
    assert "2025-01" in groups
    assert "2025-02" in groups


def test_group_dates_quarterly(sample_dates):
    """Testa agrupamento trimestral de datas."""
    groups = group_dates(sample_dates, TimeGroup.QUARTERLY)
    assert len(groups) == 1
    assert "2025-Q1" in groups


def test_group_dates_yearly(sample_dates):
    """Testa agrupamento anual de datas."""
    groups = group_dates(sample_dates, TimeGroup.YEARLY)
    assert len(groups) == 1
    assert "2025" in groups


def test_calculate_temporal_stats(sample_dates):
    """Testa cálculo de estatísticas temporais."""
    stats = calculate_temporal_stats(sample_dates, TimeGroup.DAILY)
    assert len(stats) == 9
    assert "2025-01-01" in stats
    assert "count" in stats["2025-01-01"]
    assert "mean" in stats["2025-01-01"]
    assert "median" in stats["2025-01-01"]
    assert "std_dev" in stats["2025-01-01"]


def test_detect_temporal_patterns():
    """Testa detecção de padrões temporais."""
    # Criar datas com padrão diário
    dates = [
        datetime(2025, 1, 1, 10, 0),
        datetime(2025, 1, 2, 10, 0),
        datetime(2025, 1, 3, 10, 0),
        datetime(2025, 1, 4, 10, 0),
    ]
    patterns = detect_temporal_patterns(dates)
    assert len(patterns) == 1
    assert patterns[0]["occurrences"] == 4
    assert abs(patterns[0]["interval"] - 86400) < 60  # 24 horas em segundos


def test_analyze_seasonality(sample_dates):
    """Testa análise de sazonalidade."""
    seasonality = analyze_seasonality(sample_dates)
    assert "monthly" in seasonality
    assert "weekly" in seasonality
    assert "daily" in seasonality
    assert len(seasonality["monthly"]) > 0
    assert len(seasonality["weekly"]) > 0
    assert len(seasonality["daily"]) > 0


def test_empty_dates():
    """Testa comportamento com lista vazia de datas."""
    empty_dates = []
    assert group_dates(empty_dates) == {}
    assert calculate_temporal_stats(empty_dates) == {}
    assert detect_temporal_patterns(empty_dates) == []
    assert analyze_seasonality(empty_dates) == {}


def test_single_date():
    """Testa comportamento com uma única data."""
    single_date = [datetime(2025, 1, 1)]
    assert len(group_dates(single_date)) == 1
    assert len(calculate_temporal_stats(single_date)) == 1
    assert detect_temporal_patterns(single_date) == []
    assert len(analyze_seasonality(single_date)) == 3


def test_mixed_date_types():
    """Testa comportamento com diferentes tipos de data."""
    mixed_dates = [
        datetime(2025, 1, 1),
        date(2025, 1, 2),
        datetime(2025, 1, 3)
    ]
    groups = group_dates(mixed_dates)
    assert len(groups) == 3
    assert "2025-01-01" in groups
    assert "2025-01-02" in groups
    assert "2025-01-03" in groups 