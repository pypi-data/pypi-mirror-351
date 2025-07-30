"""
Módulo para análise temporal de datas e identificação de padrões.
"""

import statistics
from collections import defaultdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Union


class TimeGroup(Enum):
    """Enumeração para tipos de agrupamento temporal."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


def _format_group_key(date: datetime, group_type: TimeGroup) -> str:
    """Formata a chave do grupo de acordo com o tipo de agrupamento."""
    if group_type == TimeGroup.DAILY:
        return date.strftime("%Y-%m-%d")
    elif group_type == TimeGroup.WEEKLY:
        # Usar apenas o número da semana e o ano para agrupar
        year, week, _ = date.isocalendar()
        return f"{year}-W{week:02d}"
    elif group_type == TimeGroup.MONTHLY:
        return date.strftime("%Y-%m")
    elif group_type == TimeGroup.QUARTERLY:
        quarter = (date.month - 1) // 3 + 1
        return f"{date.year}-Q{quarter}"
    else:  # YEARLY
        return str(date.year)


def group_dates(
    dates: List[Union[datetime, str]],
    group_type: TimeGroup = TimeGroup.DAILY,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict[str, List[datetime]]:
    """
    Agrupa datas de acordo com o período especificado.

    Args:
        dates: Lista de datas para agrupar
        group_type: Tipo de agrupamento (diário, semanal, mensal, etc.)
        start_date: Data inicial para filtrar (opcional)
        end_date: Data final para filtrar (opcional)

    Returns:
        Dicionário com as datas agrupadas por período
    """
    if not dates:
        return {}

    # Converter strings para datetime se necessário
    processed_dates = []
    for dt in dates:
        if isinstance(dt, str):
            try:
                dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
            except ValueError:
                continue
        processed_dates.append(dt)

    # Filtrar por intervalo de datas se especificado
    if start_date:
        processed_dates = [d for d in processed_dates if d >= start_date]
    if end_date:
        processed_dates = [d for d in processed_dates if d <= end_date]

    # Agrupar datas
    groups = defaultdict(list)
    for dt in processed_dates:
        key = _format_group_key(dt, group_type)
        groups[key].append(dt)

    return dict(groups)


def calculate_temporal_stats(
    dates: List[Union[datetime, str]],
    group_type: TimeGroup = TimeGroup.DAILY
) -> Dict[str, Dict[str, float]]:
    """
    Calcula estatísticas temporais para um conjunto de datas.

    Args:
        dates: Lista de datas para análise
        group_type: Tipo de agrupamento temporal

    Returns:
        Dicionário com estatísticas por grupo temporal
    """
    date_groups = group_dates(dates, group_type)
    stats = {}

    for group_key, dt_group in date_groups.items():
        if not dt_group:
            continue

        # Converter datas para timestamps para cálculos
        timestamps = [d.timestamp() for d in dt_group]

        # Calcular estatísticas básicas
        std_dev = statistics.stdev(timestamps) if len(timestamps) > 1 else 0

        group_stats = {
            "count": len(timestamps),
            "mean": statistics.mean(timestamps),
            "median": statistics.median(timestamps),
            "std_dev": std_dev,
            "min": min(timestamps),
            "max": max(timestamps)
        }

        # Converter timestamps de volta para datetime para melhor legibilidade
        stats[group_key] = {
            "count": group_stats["count"],
            "mean": datetime.fromtimestamp(group_stats["mean"]),
            "median": datetime.fromtimestamp(group_stats["median"]),
            "std_dev": timedelta(seconds=group_stats["std_dev"]),
            "min": datetime.fromtimestamp(group_stats["min"]),
            "max": datetime.fromtimestamp(group_stats["max"])
        }

    return stats


def detect_temporal_patterns(
    dates: List[Union[datetime, str]],
    min_occurrences: int = 3,
    max_interval: Optional[timedelta] = None
) -> List[Dict]:
    """
    Detecta padrões temporais em uma sequência de datas.

    Args:
        dates: Lista de datas para análise
        min_occurrences: Número mínimo de ocorrências para considerar um padrão
        max_interval: Intervalo máximo entre ocorrências (opcional)

    Returns:
        Lista de padrões encontrados com suas características
    """
    if not dates or len(dates) < min_occurrences:
        return []

    # Processar e ordenar datas
    processed_dates = []
    for dt in dates:
        if isinstance(dt, str):
            try:
                dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
            except ValueError:
                continue
        processed_dates.append(dt)

    processed_dates.sort()

    # Calcular intervalos entre datas consecutivas
    intervals = []
    for i in range(len(processed_dates) - 1):
        interval = processed_dates[i + 1] - processed_dates[i]
        if max_interval and interval > max_interval:
            continue
        intervals.append(interval.total_seconds())

    if not intervals:
        return []

    # Identificar padrões
    patterns = []
    current_pattern = {"interval": intervals[0], "occurrences": 2}
    tolerance = 60  # 1 minuto de tolerância

    for interval in intervals[1:]:
        if abs(interval - current_pattern["interval"]) <= tolerance:
            current_pattern["occurrences"] += 1
        else:
            if current_pattern["occurrences"] >= min_occurrences:
                patterns.append(current_pattern.copy())
            current_pattern = {"interval": interval, "occurrences": 2}

    if current_pattern["occurrences"] >= min_occurrences:
        patterns.append(current_pattern)

    return patterns


def analyze_seasonality(
    dates: List[Union[datetime, str]]
) -> Dict[str, Dict[str, int]]:
    """
    Analisa padrões sazonais em uma série temporal.

    Args:
        dates: Lista de datas para análise

    Returns:
        Dicionário com análise de sazonalidade por diferentes períodos
    """
    if not dates:
        return {}

    # Processar datas
    processed_dates = []
    for dt in dates:
        if isinstance(dt, str):
            try:
                dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
            except ValueError:
                continue
        processed_dates.append(dt)

    if not processed_dates:
        return {}

    # Inicializar contadores
    monthly_counts = defaultdict(int)
    weekly_counts = defaultdict(int)
    daily_counts = defaultdict(int)

    # Analisar padrões
    for dt in processed_dates:
        # Padrão mensal
        month_key = dt.strftime("%B")  # Nome do mês
        monthly_counts[month_key] += 1

        # Padrão semanal
        week_key = dt.strftime("%A")  # Nome do dia da semana
        weekly_counts[week_key] += 1

        # Padrão diário
        hour_key = dt.strftime("%H:00")  # Hora do dia
        daily_counts[hour_key] += 1

    return {
        "monthly": dict(monthly_counts),
        "weekly": dict(weekly_counts),
        "daily": dict(daily_counts)
    } 