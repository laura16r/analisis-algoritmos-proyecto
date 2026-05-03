from datetime import datetime
from typing import Any

def calculate_daily_returns(
    dataset: list[dict[str, Any]],
    price_field: str = "close",
) -> list[dict[str, Any]]:
    """
    Calcula el retorno diario de cada activo usando un campo de precio.

    Fórmula:
        daily_return = (precio_actual - precio_anterior) / precio_anterior

    Args:
        dataset: Dataset limpio con registros financieros.
        price_field: Campo de precio a usar. Por defecto se usa "close".

    Returns:
        Nuevo dataset con el campo "daily_return".
    """

    grouped_by_ticker: dict[str, list[dict[str, Any]]] = {}

    for row in dataset:
        ticker = row["ticker"]
        grouped_by_ticker.setdefault(ticker, []).append(row)

    dataset_with_returns: list[dict[str, Any]] = []

    for ticker, rows in grouped_by_ticker.items():
        rows_sorted = sorted(
            rows,
            key=lambda row: datetime.strptime(row["date"], "%Y-%m-%d"),
        )

        previous_price: float | None = None

        for row in rows_sorted:
            new_row = row.copy()
            current_price = new_row.get(price_field)

            if current_price is None:
                new_row["daily_return"] = None

            elif previous_price is None:
                new_row["daily_return"] = None

            elif previous_price == 0:
                new_row["daily_return"] = None

            else:
                new_row["daily_return"] = round(
                    (current_price - previous_price) / previous_price,
                    8,
                )

            if current_price is not None:
                previous_price = current_price

            dataset_with_returns.append(new_row)

    dataset_with_returns.sort(
        key=lambda row: (
            row["date"],
            row["ticker"],
        )
    )

    return dataset_with_returns