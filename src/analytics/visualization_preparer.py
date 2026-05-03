from typing import Any

def prepare_risk_ranking(
    risk_data: list[dict[str, Any]],
    volatility_field: str = "annual_volatility",
) -> list[dict[str, Any]]:
    """
    Prepara datos para ranking de riesgo.

    Ordena los activos desde el más riesgoso hasta el más conservador.
    """

    ranking = []

    for row in risk_data:
        ranking.append(
            {
                "ticker": row["ticker"],
                "risk_level": row.get("risk_level"),
                "daily_volatility": row.get("daily_volatility"),
                "annual_volatility": row.get(volatility_field),
            }
        )
    
    ranking.sort(
        key=lambda row: (
            row["annual_volatility"]
            if row["annual_volatility"] is not None
            else -1
        ),
        reverse=True,
    )

    return ranking

def prepare_heatmap_matrix(
        correlation_results: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Prepara datos para heatmap de correlaciones.

    Entrada esperada:
        [
            {
                "asset_a": "AAPL",
                "asset_b": "MSFT",
                "correlation": 0.87
            }
        ]

    Salida:
        {
            "ticker": [...],
            "matrix": [...]
        }
    """

    ticker_set = set()

    for row in correlation_results:
        ticker_set.add(row["asset_a"])
        ticker_set.add(row["asset_b"])

        tickers = sorted(ticker_set)

        correlation_map = {}

    for row in correlation_results:
        asset_a = row["asset_a"]
        asset_b = row["asset_b"]
        correlation = row.get("correlation")

        correlation_map[(asset_a, asset_b)] = correlation
        correlation_map[(asset_b, asset_a)] = correlation

    matrix = []

    for ticker_a in tickers:
        row_values = []

        for ticker_b in tickers:
            if ticker_a == ticker_b:
                row.values.append(1.0)
            else:
                row.values.append(
                    correlation_map.get((ticker_a, ticker_b))
                )

        matrix.append(
            {
                "ticker": ticker_a,
                "values": row_values,
            }
        )
    
    return {
        "tickers": tickers,
        "matrix": matrix,
    }

def prepare_asset_comparison(
    pearson_result: dict[str, Any],
    euclidean_result: dict[str, Any],
    dtw_result: dict[str, Any],
    cosine_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Prepara una comparación consolidada entre dos activos.

    Une:
    - Pearson
    - Distancia euclidiana
    - DTW
    - Similitud por coseno
    """

    return {
        "asset_a": pearson_result["asset_a"],
        "asset_b": pearson_result["asset_b"],
        "observations": pearson_result.get("observations"),
        "metrics": {
            "pearson_correlation": pearson_result.get("correlation"),
            "euclidean_distance": euclidean_result.get("euclidean_distance"),
            "dtw_distance": dtw_result.get("dtw_distance"),
            "cosine_similitary": cosine_result.get("cosine_similitary"),
        },
        "interpretation_reference": {
            "pearson_correlation": "Cerca de 1 indica relación positiva fuerte.",
            "euclidean_distance": "Menor distancia indica mayor similitud.",
            "dtw_distance": "Menor distancia indica patrones temporales más similares.",
            "cosine_similitary": "Cerca de 1 indica dirección similar de los retornos.",
        },
    }