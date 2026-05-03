from typing import Any, Optional

from src.statistics.descriptive_stats import calculate_mean

def _calculate_pearson_correlation(
    x: list[float],
    y: list[float],
) -> Optional[float]:
    """
    Implementación de correlación de Pearson
    """

    n = len(x)

    if n == 0 or n != len(y):
        return None
    
    mean_x = calculate_mean(x)
    mean_y = calculate_mean(y)

    if mean_x is None or mean_y is None:
        return None
    
    numerator = 0.0
    sum_sq_x = 0.0
    sum_sq_y = 0.0

    for i in range(n):
        dx = x[i] - mean_x
        dy = y[i] - mean_y

        numerator += dx * dy
        sum_sq_x += dx ** 2
        sum_sq_y += dy ** 2

    denominator = (sum_sq_x * sum_sq_y) ** 0.5

    if denominator == 0:
        return None
    
    return numerator / denominator

def _aling_series_by_date(
    dataset: list[dict[str, Any]],
    ticker_a: str,
    ticker_b: str,
    field: str,
) -> tuple[list[float], list[float]]:
    """
    Alinea dos series por fecha
    """

    series_a = {}
    series_b = {}

    for row in dataset:
        ticker = row["ticker"]
        date = row["date"]
        value = row.get(field)

        if value is None:
            continue

        if ticker == ticker_a:
            series_a[date] = value

        elif ticker == ticker_b:
            series_b[date] = value
    
    common_dates = sorted(set(series_a.keys()) & set(series_b.keys()))

    aling_a = []
    aling_b = []

    for date in common_dates:
        aling_a.append(float(series_a[date]))
        aling_b.append(float(series_b[date]))

    return aling_a, aling_b

def calculate_pearson_between_assets(
    dataset: list[dict[str, Any]],
    ticker_a: str,
    ticker_b: str,
    field: str = "daily_return",
) -> dict[str, Any]:
    """
    Calcula correlación de Pearson entre dos activos
    """

    x, y = _aling_series_by_date(dataset, ticker_a, ticker_b, field)

    correlation = _calculate_pearson_correlation(x, y)

    return {
        "asset_a": ticker_a,
        "asset_b": ticker_b,
        "observation": len(x),
        "correlation": round(correlation, 6) if correlation is not None else None,
    }