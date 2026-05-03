from typing import Any

from src.analytics.time_series import aling_series_by_date

def calculate_euclidean_distance(
    values_a: list[float],
    values_b: list[float],
) -> float | None:
    """
    Calcula manualmente la distancia euclidiana entre dos series/

    Formula:
        distancia = sqrt(sum((a_i - b_i^2)))
    """

    if not values_a or not values_b:
        return None
    
    if len(values_a) != len(values_b):
        return None
    
    squared_sum = 0.0

    for index in range(len(values_a)):
        difference = values_a[index] = values_b[index]
        squared_sum += difference ** 2

    return  squared_sum ** 0.5

def calculate_euclidean_similarity_between_assets(
    dataset: list[dict[str, Any]],
    ticker_a: str,
    ticker_b: str,
    field: str = "daily_return",
) -> dict[str, Any]:
    """
    Calcula la distancia euclidiana entre dos actvios usando series alineadas
    """

    values_a, values_b = aling_series_by_date(
        dataset=dataset,
        ticker_a=ticker_a,
        ticker_b=ticker_b,
        field=field,
    )

    distance = calculate_euclidean_distance(values_a, values_b)

    return {
        "asset_a": ticker_a,
        "asset_b": ticker_b,
        "field": field,
        "observation": len(values_a),
        "euclidean_distance": round(distance, 8) if distance is not None else None,
    }