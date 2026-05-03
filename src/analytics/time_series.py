from typing import Any


def aling_series_by_date(
    dataset: list[dict[str, Any]],
    ticker_a: str,
    ticker_b: str,
    field: str,
) -> tuple[list[float], list[float]]:
    """
    Alinea dos series por fecha usando fechas comunes.

    Se usa para:
    - Correlación
    - Distancia euclidiana
    - Similitud coseno
    - DWT
    """

    series_a: dict[str, float] = {}
    series_b: dict[str, float] = {}

    for row in dataset:
        ticker = row["ticker"]
        date = row["date"]
        value = row.get(field)

        if value is None:
            continue

        if ticker == ticker_a:
            series_a[date] = float(value)

        elif ticker == ticker_b:
            series_b[date] = float(value)
    
    common_dates = sorted(set(series_a.keys()) & set(series_b.keys()))

    aling_a: list[float] = []
    aling_b: list[float] = []

    for date in common_dates:
        aling_a.append(series_a[date])
        aling_b.append(series_b[date])

    return aling_a, aling_b