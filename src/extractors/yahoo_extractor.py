import datetime
import json
import os
import time
from typing import Any

import requests


RAW_DIR = "data/raw"

ASSETS = [
    # Acciones colombianas (BVC via Yahoo Finance)
    "EC",
    "CIB",
    "GGAL",
    "GEB.CL",
    "ISA.CL",
    "CELSIA.CL",
    "NUTRESA.CL",
    "EXITO.CL",
    "CEMARGOS.CL",
    "CNEC.CL",
    # ETFs y acciones globales
    "VOO",
    "SPY",
    "QQQ",
    "IVV",
    "VTI",
    "EEM",
    "GLD",
    "AAPL",
    "MSFT",
    "AMZN",
]

INTERVAL = "1d"
RANGE = "5y"

# User-Agent completo para evitar bloqueos de Yahoo Finance
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def build_url(ticker: str) -> str:
    base = "https://query1.finance.yahoo.com/v8/finance/chart/"
    return f"{base}{ticker}?interval={INTERVAL}&range={RANGE}"


def download_json(url: str, ticker: str) -> dict[str, Any] | None:
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)

        if response.status_code != 200:
            print(f"  [ERROR] {ticker}: servidor respondio con codigo {response.status_code}")
            return None

        return json.loads(response.text)

    except requests.exceptions.ConnectionError:
        print(f"  [ERROR] {ticker}: sin conexion a internet.")
        return None

    except requests.exceptions.Timeout:
        print(f"  [ERROR] {ticker}: tiempo de espera agotado (timeout).")
        return None

    except json.JSONDecodeError:
        print(f"  [ERROR] {ticker}: la respuesta no es un JSON valido.")
        return None


def parse_yahoo_response(data: dict[str, Any], ticker: str) -> list[dict[str, Any]]:
    try:
        result = data["chart"]["result"]

        if not result:
            print(f"  [AVISO] {ticker}: Yahoo no devolvio datos.")
            return []

        block = result[0]
        timestamps: list[int] = block["timestamp"]
        quote: dict[str, list] = block["indicators"]["quote"][0]

        opens   = quote.get("open",   [])
        highs   = quote.get("high",   [])
        lows    = quote.get("low",    [])
        closes  = quote.get("close",  [])
        volumes = quote.get("volume", [])

        rows: list[dict[str, Any]] = []

        for index, timestamp in enumerate(timestamps):
            date = datetime.datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d")

            rows.append({
                "ticker": ticker,
                "date":   date,
                "open":   opens[index]   if index < len(opens)   and opens[index]   is not None else None,
                "high":   highs[index]   if index < len(highs)   and highs[index]   is not None else None,
                "low":    lows[index]    if index < len(lows)    and lows[index]    is not None else None,
                "close":  closes[index]  if index < len(closes)  and closes[index]  is not None else None,
                "volume": volumes[index] if index < len(volumes) and volumes[index] is not None else None,
            })

        return rows

    except (KeyError, IndexError, TypeError) as error:
        print(f"  [ERROR] {ticker}: estructura del JSON inesperada — {error}")
        return []


def save_raw_json(ticker: str, rows: list[dict[str, Any]]) -> None:
    os.makedirs(RAW_DIR, exist_ok=True)

    file_name = ticker.replace(".", "_")
    path = os.path.join(RAW_DIR, f"{file_name}.json")

    with open(path, "w", encoding="utf-8") as file:
        json.dump(rows, file, indent=4, ensure_ascii=False)

    print(f"  [OK] {ticker}: {len(rows)} registros guardados en {path}")


def run_extraction() -> None:
    print("=" * 55)
    print("  EXTRACCION DE DATOS — Yahoo Finance")
    print("=" * 55)
    print(f"  Activos  : {len(ASSETS)}")
    print(f"  Intervalo: {INTERVAL}   Rango: {RANGE}")
    print(f"  Destino  : {RAW_DIR}/")
    print("=" * 55)

    ok: int = 0
    failed: list[str] = []

    for ticker in ASSETS:
        print(f"\nDescargando: {ticker}")

        url = build_url(ticker)
        data = download_json(url, ticker)

        if data is None:
            failed.append(ticker)
            continue

        rows = parse_yahoo_response(data, ticker)

        if not rows:
            failed.append(ticker)
            continue

        save_raw_json(ticker, rows)
        ok += 1
        time.sleep(1)

    print("\n" + "=" * 55)
    print(f"  Exitosos : {ok} / {len(ASSETS)}")
    if failed:
        print(f"  Fallidos : {', '.join(failed)}")
    print("=" * 55)


if __name__ == "__main__":
    run_extraction()
