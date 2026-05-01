"""
processors/market_processor.py
================================
Une todos los JSON de data/raw/ en un unico dataset maestro
ordenado por fecha y guardado en data/processed/.
"""

import os
from typing import Any

from config import RAW_DIR, MASTER_DATASET_PATH
from src.utils.io import load_json, save_json


def build_master_dataset() -> list[dict[str, Any]]:
    print("=" * 55)
    print("  CONSTRUCCION DEL DATASET MAESTRO")
    print("=" * 55)

    if not os.path.exists(RAW_DIR):
        print(f"  [ERROR] No existe la carpeta {RAW_DIR}.")
        print("  Ejecuta primero run_extraction().")
        return []

    files = sorted(f for f in os.listdir(RAW_DIR) if f.endswith(".json"))

    if not files:
        print(f"  [ERROR] No hay archivos JSON en {RAW_DIR}.")
        return []

    print(f"  Archivos encontrados: {len(files)}\n")

    master_dataset: list[dict[str, Any]] = []
    summary:        list[dict[str, Any]] = []

    for file_name in files:
        ticker = file_name.replace(".json", "").replace("_", ".")
        path   = os.path.join(RAW_DIR, file_name)

        try:
            rows = load_json(path)
        except Exception as e:
            print(f"  [ERROR] {ticker}: no se pudo leer el archivo — {e}")
            continue

        if not rows:
            print(f"  [AVISO] {ticker}: archivo vacio, se omite.")
            continue

        master_dataset.extend(rows)
        summary.append({"ticker": ticker, "registros": len(rows)})
        print(f"  {ticker}: {len(rows)} registros cargados")

    master_dataset.sort(
        key=lambda r: (
            r["date"],
            float(r["close"]) if r["close"] is not None else 0.0,
        )
    )

    save_json(MASTER_DATASET_PATH, master_dataset)

    print(f"\n  [OK] Dataset maestro: {MASTER_DATASET_PATH}")
    print(f"  [OK] Total registros : {len(master_dataset)}")
    print("\n  Resumen por activo:")
    print(f"  {'Ticker':<20} {'Registros':>10}")
    print(f"  {'-' * 32}")
    for s in summary:
        print(f"  {s['ticker']:<20} {s['registros']:>10}")
    print("=" * 55)

    return master_dataset


if __name__ == "__main__":
    build_master_dataset()