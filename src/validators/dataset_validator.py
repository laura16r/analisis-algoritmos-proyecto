"""
validators/dataset_validator.py
================================
Valida el dataset limpio antes de pasarlo a los algoritmos:

  1. Verifica que cada activo tenga al menos MIN_RECORDS_PER_ASSET registros.
  2. Verifica que las fechas cubran al menos 5 años de historico.
  3. Detecta gaps (dias bursatiles sin datos) en cada serie.
  4. Genera un reporte JSON en data/results/validation_report.json.
"""

import datetime
from typing import Any

from config import CLEAN_DATASET_PATH, VALIDATION_LOG_PATH, MIN_RECORDS_PER_ASSET
from src.utils.io import FileUtils


# Maximo de dias naturales entre dos registros consecutivos considerado normal.
# Los fines de semana suman 2, mas algun festivo puede sumar 1 dia extra.
# Con 4 cubrimos lunes despues de un fin de semana largo sin falsa alarma.
MAX_NORMAL_GAP_DAYS = 4


def group_by_ticker(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(row["ticker"], []).append(row)
    return grouped


def detect_gaps(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Recorre la serie ordenada por fecha y detecta saltos mayores a
    MAX_NORMAL_GAP_DAYS dias entre registros consecutivos.
    Devuelve lista de diccionarios con informacion de cada gap encontrado.
    """
    sorted_rows = sorted(rows, key=lambda r: r["date"])
    gaps: list[dict[str, Any]] = []

    for index in range(1, len(sorted_rows)):
        date_a = datetime.date.fromisoformat(sorted_rows[index - 1]["date"])
        date_b = datetime.date.fromisoformat(sorted_rows[index]["date"])
        delta  = (date_b - date_a).days

        if delta > MAX_NORMAL_GAP_DAYS:
            gaps.append({
                "from":      str(date_a),
                "to":        str(date_b),
                "days_missing": delta - 1,
            })

    return gaps


def validate_ticker(ticker: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Valida un activo individual y devuelve su reporte de validacion.
    """
    sorted_rows = sorted(rows, key=lambda r: r["date"])
    total       = len(sorted_rows)

    date_min = sorted_rows[0]["date"]  if sorted_rows else None
    date_max = sorted_rows[-1]["date"] if sorted_rows else None

    # Calcular cobertura en anios
    coverage_years: float = 0.0
    if date_min and date_max:
        d_min = datetime.date.fromisoformat(date_min)
        d_max = datetime.date.fromisoformat(date_max)
        coverage_years = round((d_max - d_min).days / 365.25, 2)

    gaps           = detect_gaps(sorted_rows)
    enough_records = total >= MIN_RECORDS_PER_ASSET
    enough_history = coverage_years >= 5.0
    passed         = enough_records and enough_history

    status = "OK" if passed else "ADVERTENCIA"

    issues: list[str] = []
    if not enough_records:
        issues.append(
            f"Solo {total} registros (minimo esperado: {MIN_RECORDS_PER_ASSET})"
        )
    if not enough_history:
        issues.append(
            f"Cobertura de {coverage_years} anios (minimo esperado: 5.0)"
        )
    if gaps:
        issues.append(f"{len(gaps)} gaps detectados en la serie")

    return {
        "ticker":         ticker,
        "status":         status,
        "total_records":  total,
        "date_min":       date_min,
        "date_max":       date_max,
        "coverage_years": coverage_years,
        "gaps_count":     len(gaps),
        "gaps":           gaps,
        "issues":         issues,
    }


def validate_dataset() -> list[dict[str, Any]]:
    print("=" * 55)
    print("  VALIDACION DEL DATASET LIMPIO")
    print("=" * 55)

    try:
        rows = FileUtils.load_json(CLEAN_DATASET_PATH)
    except FileNotFoundError:
        print(f"  [ERROR] No se encontro {CLEAN_DATASET_PATH}.")
        print("  Ejecuta primero clean_dataset().")
        return []

    grouped = group_by_ticker(rows)
    reports: list[dict[str, Any]] = []

    ok_count:   int = 0
    warn_count: int = 0

    for ticker, ticker_rows in grouped.items():
        report = validate_ticker(ticker, ticker_rows)
        reports.append(report)

        if report["status"] == "OK":
            ok_count += 1
            print(f"  [OK]          {ticker:<15} {report['total_records']:>5} registros  "
                  f"{report['coverage_years']} años  gaps: {report['gaps_count']}")
        else:
            warn_count += 1
            print(f"  [ADVERTENCIA] {ticker:<15} {report['total_records']:>5} registros  "
                  f"{report['coverage_years']} años  gaps: {report['gaps_count']}")
            for issue in report["issues"]:
                print(f"               → {issue}")

    FileUtils.save_json(VALIDATION_LOG_PATH, reports)

    print("\n" + "=" * 55)
    print(f"  Activos OK         : {ok_count}")
    print(f"  Activos con aviso  : {warn_count}")
    print(f"  Reporte guardado   : {VALIDATION_LOG_PATH}")
    print("=" * 55)

    return reports


if __name__ == "__main__":
    validate_dataset()