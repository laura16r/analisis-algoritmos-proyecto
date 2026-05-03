from typing import Any

from src.analytics.time_series import aling_series_by_date

def calculate_cosine_similarity(
    values_a: list[float],
    values_b: list[float],
) -> float | None:
    """
    Calcular la similitud por coseno entre dos vectores.

    Formula:
        coseno = (A . B) / (||A|| * ||B||)

    Interpretación:
        1 -> misma dirección
        0 -> sin similitud direccional
       -1 -> dirección opuesta
    """

    if not values_a or not values_b:
        return None
    
    if len(values_a) != len(values_b):
        return None
    
    dot_product = 0.0
    magnitude_a = 0.0
    magnitude_b = 0.0

    for index in range(len(values_a)):
        value_a = values_a[index]
        value_b = values_b[index]

        dot_product += value_a * value_b
        magnitude_a += value_a ** 2
        magnitude_b += value_b ** 2

    magnitude_a = magnitude_a ** 0.5
    magnitude_b = magnitude_b ** 0.5

    if magnitude_a == 0 or magnitude_b == 0:
        return None
    
    return dot_product / (magnitude_a * magnitude_b)

def calculate_cosine_similarity_between_assets(
    dataset: list[dict[str, Any]],
    ticker_a: str,
    ticker_b: str,
    field: str = "daily_return",
) -> dict[str, Any]:
    """
    Calcula similitud por coseno entre dos activos usando rendimientos diarios.
    """

    values_a, values_b = aling_series_by_date(
        dataset=dataset,
        ticker_a=ticker_a,
        ticker_b=ticker_b,
        field=field,
    )

    similarity = calculate_cosine_similarity(
        values_a=values_a,
        values_b=values_b,
    )

    return {
        "asset_a": ticker_a,
        "asset_b": ticker_b,
        "field": field,
        "observations": len(values_a),
        "cosine_similitary": (
            round(similarity, 8)
            if similarity is not None
            else None
        )
    }

def calculate_dtw_distance(
    values_a: list[float],
    values_b: list[float],
) -> float | None:
    """
    Calcula Dynamic Time Warping.

    DWT permite comparar dos secuencias aunque tengan pequeñnas diferencias
    de ritmo, desfase o velocidad

    Args:
        values_a: Primera serie numérica.
        values_b: Segunda serie numérica.
    
    Returns:
        Distancia DWT entre ambas series.
    """

    if not values_a or not values_b:
        return None
    
    n = len(values_a)
    m = len(values_b)

    dtw_matrix = []

    for i in range(n + 1):
        row = []

        for j in range(m + 1):
            row.append(float("inf"))

        dtw_matrix.append(row)

    dtw_matrix[0][0] = 0.0

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = abs(values_a[i - 1] - values_b[j - 1])

            previous_minimum = min(
                dtw_matrix[i - 1][j],       # inserción
                dtw_matrix[i][j - 1],       # eliminiación
                dtw_matrix[i - 1][j - 1],   # coincidencia
            )

            dtw_matrix[i][j] = cost + previous_minimum
        
    return dtw_matrix[n][m]

def calculate_dtw_similarity_between_assets(
    dataset: list[dict[str, Any]],
    ticker_a: str,
    ticker_b: str,
    field: str = "daily_return",
) -> dict[str, Any]:
    """
    Calcula distancia DTY entre dos activos usando series alineadas por fecha.

    Mientras menor sea la distancia DTW, más similares son las secuencias.
    """

    values_a, values_b = aling_series_by_date(
        dataset=dataset,
        ticker_a=ticker_a,
        ticker_b=ticker_b,
        field=field,
    )

    distance = calculate_dtw_distance(
        values_a=values_a,
        values_b=values_b,
    )

    return {
        "asset_a": ticker_a,
        "asset_b": ticker_b,
        "field": field,
        "observation_a": len(values_a),
        "observation_b": len(values_b),
        "dtw_distance": round(distance, 8) if distance is not None else None,
    }

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