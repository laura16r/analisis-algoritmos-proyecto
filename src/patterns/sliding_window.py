"""
patterns/sliding_window.py
===========================
Deteccion de patrones en series de tiempo financieras
mediante ventana deslizante (sliding window).

Patrones implementados:
  1. N dias consecutivos al alza
  2. Precio de cierre por encima de la media movil de 20 dias

Complejidad de la ventana deslizante: O(n * w)
  n = numero de registros de la serie
  w = tamaño de la ventana
"""

from typing import Any


# ─────────────────────────────────────────────────────────────
# Utilidades internas
# ─────────────────────────────────────────────────────────────

def _get_sorted_series(
    dataset: list[dict[str, Any]],
    ticker: str,
    field: str,
) -> list[dict[str, Any]]:
    """
    Filtra y ordena por fecha las filas de un ticker especifico.
    Descarta filas donde el campo requerido sea None.
    """
    rows = [
        row for row in dataset
        if row["ticker"] == ticker and row.get(field) is not None
    ]
    return sorted(rows, key=lambda r: r["date"])


def _calculate_moving_average(
    values: list[float],
    window: int,
    index: int,
) -> float | None:
    """
    Calcula la media movil simple para la posicion `index`
    usando los ultimos `window` valores (incluyendo el actual).

    Complejidad: O(w) por llamada, donde w es el tamanio de la ventana.
    """
    if index < window - 1:
        return None

    window_values = values[index - window + 1 : index + 1]
    return sum(window_values) / window


# ─────────────────────────────────────────────────────────────
# Patron 1: N dias consecutivos al alza
# ─────────────────────────────────────────────────────────────

def detect_consecutive_up_days(
    dataset: list[dict[str, Any]],
    ticker: str,
    consecutive_days: int = 3,
    price_field: str = "close",
) -> dict[str, Any]:
    """
    Detecta ocurrencias de N dias consecutivos donde el precio
    de cierre sube respecto al dia anterior.

    Algoritmo (sliding window):
      - Ventana de tamanio `consecutive_days`
      - Avanza un dia a la vez sobre la serie ordenada
      - Registra cada vez que todos los dias de la ventana son al alza

    Complejidad: O(n) — un recorrido lineal sobre la serie.

    Args:
        dataset:          Dataset con retornos diarios.
        ticker:           Activo a analizar.
        consecutive_days: Tamanio de la ventana (dias al alza requeridos).
        price_field:      Campo de precio a usar.

    Returns:
        Diccionario con el conteo y detalle de cada ocurrencia.
    """
    rows = _get_sorted_series(dataset, ticker, price_field)

    if len(rows) < consecutive_days + 1:
        return {
            "ticker":           ticker,
            "pattern":          f"{consecutive_days}_consecutive_up_days",
            "window_size":      consecutive_days,
            "total_records":    len(rows),
            "occurrences":      0,
            "frequency_pct":    0.0,
            "details":          [],
        }

    prices = [float(r[price_field]) for r in rows]
    dates  = [r["date"] for r in rows]

    occurrences: list[dict[str, Any]] = []
    consecutive_count = 0

    for index in range(1, len(prices)):
        if prices[index] > prices[index - 1]:
            consecutive_count += 1

            if consecutive_count >= consecutive_days:
                occurrences.append({
                    "end_date":   dates[index],
                    "start_date": dates[index - consecutive_days + 1],
                    "days":       consecutive_days,
                    "price_start": round(prices[index - consecutive_days + 1], 4),
                    "price_end":   round(prices[index], 4),
                    "change_pct":  round(
                        (prices[index] - prices[index - consecutive_days + 1])
                        / prices[index - consecutive_days + 1] * 100,
                        4,
                    ),
                })
        else:
            consecutive_count = 0

    total_windows  = len(prices) - consecutive_days
    frequency_pct  = round(len(occurrences) / total_windows * 100, 4) if total_windows > 0 else 0.0

    return {
        "ticker":        ticker,
        "pattern":       f"{consecutive_days}_consecutive_up_days",
        "window_size":   consecutive_days,
        "total_records": len(rows),
        "occurrences":   len(occurrences),
        "frequency_pct": frequency_pct,
        "details":       occurrences,
    }


# ─────────────────────────────────────────────────────────────
# Patron 2: Cierre por encima de la media movil de 20 dias
# ─────────────────────────────────────────────────────────────

def detect_price_above_moving_average(
    dataset: list[dict[str, Any]],
    ticker: str,
    window: int = 20,
    price_field: str = "close",
) -> dict[str, Any]:
    """
    Detecta dias donde el precio de cierre supera la media movil
    simple de los ultimos `window` dias.

    Este patron indica momentum alcista: el precio actual esta por
    encima de su promedio reciente, senial tipica de tendencia positiva
    en analisis tecnico financiero.

    Algoritmo (sliding window):
      - Ventana de tamanio `window` que avanza un dia a la vez
      - Para cada posicion calcula la media movil de la ventana
      - Registra si el precio actual supera esa media

    Complejidad: O(n * w) — para cada posicion se calcula la media
    de la ventana. Podria optimizarse a O(n) con suma acumulada,
    pero se mantiene explicito para transparencia algorítmica.

    Args:
        dataset:     Dataset con precios.
        ticker:      Activo a analizar.
        window:      Tamanio de la ventana para la media movil.
        price_field: Campo de precio a usar.

    Returns:
        Diccionario con el conteo y detalle de cada ocurrencia.
    """
    rows = _get_sorted_series(dataset, ticker, price_field)

    if len(rows) < window + 1:
        return {
            "ticker":        ticker,
            "pattern":       f"price_above_ma{window}",
            "window_size":   window,
            "total_records": len(rows),
            "occurrences":   0,
            "frequency_pct": 0.0,
            "details":       [],
        }

    prices = [float(r[price_field]) for r in rows]
    dates  = [r["date"] for r in rows]

    occurrences: list[dict[str, Any]] = []

    for index in range(len(prices)):
        moving_avg = _calculate_moving_average(prices, window, index)

        if moving_avg is None:
            continue

        if prices[index] > moving_avg:
            occurrences.append({
                "date":          dates[index],
                "price":         round(prices[index], 4),
                "moving_avg":    round(moving_avg, 4),
                "diff_pct":      round(
                    (prices[index] - moving_avg) / moving_avg * 100,
                    4,
                ),
            })

    eligible_days  = len(prices) - window + 1
    frequency_pct  = round(len(occurrences) / eligible_days * 100, 4) if eligible_days > 0 else 0.0

    return {
        "ticker":        ticker,
        "pattern":       f"price_above_ma{window}",
        "window_size":   window,
        "total_records": len(rows),
        "occurrences":   len(occurrences),
        "frequency_pct": frequency_pct,
        "details":       occurrences,
    }


# ─────────────────────────────────────────────────────────────
# Funcion principal: analiza todos los activos
# ─────────────────────────────────────────────────────────────

def run_pattern_detection(
    dataset: list[dict[str, Any]],
    tickers: list[str],
    consecutive_days: int = 3,
    ma_window: int = 20,
    price_field: str = "close",
) -> list[dict[str, Any]]:
    """
    Ejecuta los dos detectores de patrones sobre todos los activos
    y consolida los resultados en una sola lista.

    Args:
        dataset:          Dataset limpio con precios.
        tickers:          Lista de activos a analizar.
        consecutive_days: Dias consecutivos al alza para patron 1.
        ma_window:        Ventana de media movil para patron 2.
        price_field:      Campo de precio a usar.

    Returns:
        Lista con resultados de ambos patrones por cada activo.
    """
    results: list[dict[str, Any]] = []

    for ticker in tickers:
        print(f"  Analizando patrones: {ticker}")

        pattern_1 = detect_consecutive_up_days(
            dataset=dataset,
            ticker=ticker,
            consecutive_days=consecutive_days,
            price_field=price_field,
        )

        pattern_2 = detect_price_above_moving_average(
            dataset=dataset,
            ticker=ticker,
            window=ma_window,
            price_field=price_field,
        )

        results.append({
            "ticker":   ticker,
            "patterns": [pattern_1, pattern_2],
        })

        print(f"    Patron 1 ({consecutive_days} dias alza): {pattern_1['occurrences']} ocurrencias ({pattern_1['frequency_pct']}%)")
        print(f"    Patron 2 (precio > MA{ma_window}):       {pattern_2['occurrences']} ocurrencias ({pattern_2['frequency_pct']}%)")

    return results