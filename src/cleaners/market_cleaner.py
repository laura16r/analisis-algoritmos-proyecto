"""
cleaners/market_cleaner.py
===========================
Limpia el dataset maestro ticker por ticker:
  1. Convierte tipos y descarta filas sin close.
  2. Elimina anomalias (precios <= 0).
  3. Interpola linealmente open, high, low y adjclose faltantes.
  4. Imputa volumen faltante con el promedio historico del ticker.
"""

from typing import Any

from config import MASTER_DATASET_PATH, CLEAN_DATASET_PATH
from src.utils.io import FileUtils


def convert_types(row: dict[str, Any]) -> dict[str, Any] | None:
    """
    Convierte strings a float/int.
    Descarta la fila si falta fecha o close (campos criticos).
    """
    if not row.get("date") or row.get("close") is None:
        return None

    try:
        return {
            "ticker":   str(row["ticker"]),
            "date":     str(row["date"]),
            "open":     float(row["open"])     if row["open"]     is not None else None,
            "high":     float(row["high"])     if row["high"]     is not None else None,
            "low":      float(row["low"])      if row["low"]      is not None else None,
            "close":    float(row["close"]),
            "adjclose": float(row["adjclose"]) if row.get("adjclose") is not None else None,
            "volume":   int(row["volume"])     if row["volume"]   is not None else None,
        }
    except (ValueError, TypeError):
        return None


def remove_anomalies(rows: list[dict[str, Any]], ticker: str) -> list[dict[str, Any]]:
    """
    Elimina filas con cualquier precio <= 0.
    Un precio negativo o cero es fisicamente imposible en mercados reales.
    """
    clean:   list[dict[str, Any]] = []
    removed: int = 0

    for row in rows:
        invalid = (
            row["close"] <= 0
            or (row["open"]     is not None and row["open"]     <= 0)
            or (row["high"]     is not None and row["high"]     <= 0)
            or (row["low"]      is not None and row["low"]      <= 0)
            or (row["adjclose"] is not None and row["adjclose"] <= 0)
        )
        if invalid:
            removed += 1
        else:
            clean.append(row)

    if removed > 0:
        print(f"  [ANOMALIA] {ticker}: {removed} filas con precio <= 0 eliminadas")

    return clean


def interpolate_missing_prices(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Interpola linealmente open, high, low y adjclose cuando son None.

    Se prefiere interpolacion sobre eliminacion porque estos campos son
    secundarios: eliminar la fila entera por un open faltante romperia
    la continuidad de la serie temporal sin justificacion suficiente.
    close nunca se interpola — la fila se descarta en convert_types si
    close es None, ya que es el campo principal de la serie.
    """
    rows.sort(key=lambda r: r["date"])
    fields_to_interpolate = ["open", "high", "low", "adjclose"]

    for field in fields_to_interpolate:
        for index, row in enumerate(rows):
            if row[field] is not None:
                continue

            previous_value: float | None = None
            next_value:     float | None = None

            for prev in range(index - 1, -1, -1):
                if rows[prev][field] is not None:
                    previous_value = rows[prev][field]
                    break

            for nxt in range(index + 1, len(rows)):
                if rows[nxt][field] is not None:
                    next_value = rows[nxt][field]
                    break

            if previous_value is not None and next_value is not None:
                row[field] = round((previous_value + next_value) / 2.0, 4)
            elif previous_value is not None:
                row[field] = previous_value
            elif next_value is not None:
                row[field] = next_value

    return rows


def impute_missing_volume(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Imputa el volumen faltante con el promedio historico del ticker.
    El volumen no sigue tendencia predecible, por lo que el promedio
    es una estimacion razonable para dias sin dato.
    """
    valid_volumes  = [r["volume"] for r in rows if r["volume"] is not None]
    average_volume = int(sum(valid_volumes) / len(valid_volumes)) if valid_volumes else 0

    imputed: int = 0
    for row in rows:
        if row["volume"] is None:
            row["volume"] = average_volume
            imputed += 1

    if imputed > 0:
        print(f"  [IMPUTACION] {imputed} valores de volumen → promedio ({average_volume:,})")

    return rows


def group_by_ticker(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(row["ticker"], []).append(row)
    return grouped


def clean_dataset() -> list[dict[str, Any]]:
    print("=" * 55)
    print("  LIMPIEZA Y TRANSFORMACION DEL DATASET")
    print("=" * 55)

    try:
        raw_rows = FileUtils.load_json(MASTER_DATASET_PATH)
    except FileNotFoundError:
        print(f"  [ERROR] No se encontro {MASTER_DATASET_PATH}.")
        print("  Ejecuta primero build_master_dataset().")
        return []

    typed:     list[dict[str, Any]] = []
    discarded: int = 0

    for row in raw_rows:
        converted = convert_types(row)
        if converted is not None:
            typed.append(converted)
        else:
            discarded += 1

    if discarded > 0:
        print(f"  [INFO] {discarded} filas descartadas por close o fecha faltante\n")

    grouped    = group_by_ticker(typed)
    final_rows: list[dict[str, Any]] = []
    summary:    list[dict[str, Any]] = []

    for ticker, rows in grouped.items():
        original = len(rows)
        print(f"Procesando: {ticker}")

        rows = remove_anomalies(rows, ticker)
        rows = interpolate_missing_prices(rows)
        rows = impute_missing_volume(rows)

        final_rows.extend(rows)
        summary.append({"ticker": ticker, "original": original, "final": len(rows)})
        print(f"  [OK] {ticker}: {original} → {len(rows)} registros limpios\n")

    final_rows.sort(key=lambda r: (r["date"], r["close"]))

    FileUtils.save_json(CLEAN_DATASET_PATH, final_rows)

    print("=" * 55)
    print("  RESUMEN POR ACTIVO")
    print("=" * 55)
    print(f"  {'Ticker':<20} {'Original':>10} {'Final':>10}")
    print(f"  {'-' * 42}")
    for s in summary:
        print(f"  {s['ticker']:<20} {s['original']:>10} {s['final']:>10}")
    print("=" * 55)
    print(f"\n  [OK] Dataset limpio: {CLEAN_DATASET_PATH}")
    print(f"  [OK] Total registros: {len(final_rows)}")
    print("=" * 55)

    return final_rows


if __name__ == "__main__":
    clean_dataset()