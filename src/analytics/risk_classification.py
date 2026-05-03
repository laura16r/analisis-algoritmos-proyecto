from typing import Any

def _calculate_percentiles(values: list[float]) -> tuple[float, float]:
    """
    Calcula percentiles 33 y 66 manualmente
    """

    if not values:
        return (0.0, 0.0)
    
    sorted_values = sorted(values)
    n = len(sorted_values)

    p33_index = int(n * 0.33)
    p66_index = int(n * 0.66)

    return (
        sorted_values[p33_index],
        sorted_values[p66_index],
    )

def classify_assets_by_risk(
    volatility_data: list[dict[str, Any]],
    volatility_field: str = "annual_volatility",
) -> list[dict[str, Any]]:
    """
    Calisifica activos en:
        - conservador
        - moderado
        - agresivo
    
    Basado en percentiles de volatilidad

    Args:
        volatility_data: Dataset con volatilidad por ticker.
        volatility_fields: campo de volatilidad.

    Returns:
        Dataset con clasificación de riesgo.
    """

    # Extraer volatilidades válidas
    vol_values = [
        row[volatility_field]
        for row in volatility_data
        if row.get(volatility_field) is not None
    ]

    if not vol_values:
        return volatility_data
    
    p33, p66 = _calculate_percentiles(vol_values)

    classified_data: list[dict[str, Any]] = []

    for row in volatility_data:
        new_row = row.copy()
        volatility = row.get(volatility_field)

        if volatility is None:
            risk = "unknown"

        elif volatility <= p33:
            risk = "conservador"

        elif volatility <= p66:
            risk = "moderado"

        else:
            risk = "agresivo"

        new_row["risk_level"] = risk
        classified_data.append(new_row)

    # Ordenar por riesgo
    risk_order = {
        "agresivo": 3,
        "moderado": 2,
        "conservador": 1,
        "unknown": 0,
    }

    classified_data.sort(
        key=lambda row: (
            risk_order.get(row["risk_level"], 0),
            row.get(volatility_field, 0),
        ),
        reverse=True
    )

    return classified_data