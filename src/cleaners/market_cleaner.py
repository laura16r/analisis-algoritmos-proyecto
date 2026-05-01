import json
import os
from typing import Any


MASTER_DATASET_PATH = "data/processed/master_dataset.json"
CLEAN_DATASET_PATH  = "data/results/clean_master_dataset.json"


def load_json_file(path: str) -> list[dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json_file(path: str, data: list[dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def convert_types(row: dict[str, Any]) -> dict[str, Any] | None:
    """
    Convierte strings a float/int y descarta filas sin fecha o sin close.
    close es el campo critico: sin el no hay serie de tiempo valida.
    """
    if not row.get("date") or row.get("close") is None:
        return None

    try:
        return {
            "ticker": str(row["ticker"]),
            "date":   str(row["date"]),
            "open":   float(row["open"])        if row["open"]   is not None else None,
            "high":   float(row["high"])        if row["high"]   is not None else None,
            "low":    float(row["low"])         if row["low"]    is not None else None,
            "close":  float(row["close"]),
            "volume": int(row["volume"])        if row["volume"] is not None else None,
        }
    except (ValueError, TypeError):
        return None


def remove_anomalies(rows: list[dict[str, Any]], ticker: str) -> list[dict[str, Any]]:
    """
    Elimina filas con precios negativos o cero.
    Un precio <= 0 es fisicamente imposible en mercados reales.
    """
    clean: list[dict[str, Any]] = []
    removed = 0

    for row in rows:
        invalid = (
            row["close"] <= 0
            or (row["open"] is not None and row["open"] <= 0)
            or (row["high"] is not None and row["high"] <= 0)
            or (row["low"]  is not None and row["low"]  <= 0)
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
    Interpola linealmente open, high y low cuando son None.
    Se usa interpolacion (no eliminacion) porque estos campos son secundarios:
    eliminar la fila entera solo por un open faltante romperia innecesariamente
    la continuidad de la serie temporal. close nunca se interpola — la fila
    fue descartada en convert_types si close era None.
    """
    rows.sort(key=lambda r: r["date"])
    price_fields = ["open", "high", "low"]

    for field in price_fields:
        for index, row in enumerate(rows):
            if row[field] is not None:
                continue

            previous_value: float | None = None
            next_value:     float | None = None

            for prev_index in range(index - 1, -1, -1):
                if rows[prev_index][field] is not None:
                    previous_value = rows[prev_index][field]
                    break

            for next_index in range(index + 1, len(rows)):
                if rows[next_index][field] is not None:
                    next_value = rows[next_index][field]
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
    El volumen no sigue una tendencia tan predecible como el precio,
    por lo que el promedio es una estimacion razonable para dias sin dato.
    """
    valid_volumes = [r["volume"] for r in rows if r["volume"] is not None]
    average_volume = int(sum(valid_volumes) / len(valid_volumes)) if valid_volumes else 0

    imputed = 0
    for row in rows:
        if row["volume"] is None:
            row["volume"] = average_volume
            imputed += 1

    if imputed > 0:
        print(f"  [IMPUTACION] {imputed} valores de volumen reemplazados por promedio ({average_volume:,})")

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
        raw_rows = load_json_file(MASTER_DATASET_PATH)
    except FileNotFoundError:
        print(f"  [ERROR] No se encontro {MASTER_DATASET_PATH}.")
        print("  Ejecuta primero build_master_dataset().")
        return []

    # 1. Conversion de tipos
    typed: list[dict[str, Any]] = []
    discarded = 0

    for row in raw_rows:
        converted = convert_types(row)
        if converted is not None:
            typed.append(converted)
        else:
            discarded += 1

    if discarded > 0:
        print(f"  [INFO] {discarded} filas descartadas por close o fecha faltante\n")

    # 2. Limpiar cada ticker de forma independiente
    grouped = group_by_ticker(typed)
    final_rows: list[dict[str, Any]] = []
    summary: list[dict[str, Any]] = []

    for ticker, rows in grouped.items():
        original = len(rows)
        print(f"Procesando: {ticker}")

        rows = remove_anomalies(rows, ticker)
        rows = interpolate_missing_prices(rows)
        rows = impute_missing_volume(rows)

        final_rows.extend(rows)
        summary.append({"ticker": ticker, "original": original, "final": len(rows)})
        print(f"  [OK] {ticker}: {original} → {len(rows)} registros limpios\n")

    # 3. Ordenar final: fecha asc, close como desempate
    final_rows.sort(key=lambda r: (r["date"], r["close"]))

    save_json_file(CLEAN_DATASET_PATH, final_rows)

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
