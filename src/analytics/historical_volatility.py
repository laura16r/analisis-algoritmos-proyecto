from typing import Any
from src.statistics.descriptive_stats import (
    calculate_standard_deviation,
)
from src.utils.io import FileUtils
from config import TRADING_DAYS

def calculate_historical_volatility_by_ticker(
    dataset: list[dict[str, Any]],
    return_field: str = "daily_return",
    annualize: bool = True,
    sample: bool = True,
) -> list[dict[str, Any]]:
    """
    Calcula la volatilidad histórica por activo.

    Volatilidad = desviación estándar de retornos.

    Si annualize=True
        volatilidad = std * sqrt(252)

    Args:
        dataset: Dataset con retornos diarios.
        return_field: Campo de retornos.
        annualize: Si True, convierte a volatilidad anual.
        sample: Usa varianza muestral

    Returns:
        Lista con volatilidad por ticker
    """

    grouped_returns: dict[str, list[float]] = {}

    # Agrupar retornos por ticker
    for row in dataset:
        ticker = row["ticker"]
        daily_return = row.get(return_field)

        if daily_return is None:
            continue

        grouped_returns.setdefault(ticker, []).append(float(daily_return))

    results: list[dict[str, Any]] = []

    for ticker, returns in grouped_returns.items():
        std_dev = calculate_standard_deviation(
            returns,
            sample=sample,
        )

        if std_dev is None:
            volatility = None
        else:
            volatility = std_dev

            if annualize:
                volatility = volatility * (TRADING_DAYS ** 0.5)

        results.append(
            {
                "ticker": ticker,
                "records": len(returns),
                "daily_volatility": round(std_dev, 8) if std_dev else None,
                "annual_volatility": (
                    round(volatility, 8) if volatility else None
                )
            }
        )

    # Ordernar por riesgo (mayor volatilidad primero)
    results.sort(
        key=lambda row: (
            row["annual_volatility"]
            if row["annual_volatility"] is not None
            else -1
        ),
        reverse=True
    )

    return results