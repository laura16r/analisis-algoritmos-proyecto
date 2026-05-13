"""
dashboard/candlestick.py
=========================
Genera graficos de velas (candlestick) para un activo seleccionado,
incorporando medias moviles simples calculadas algoritmicamente.

Las medias moviles se calculan desde cero sin usar librerias de alto nivel.
Matplotlib solo se usa para la visualizacion final.

Complejidad media movil: O(n * w)
  n = numero de registros
  w = tamanio de la ventana
"""

from typing import Any
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


def _calculate_sma(
    values: list[float],
    window: int,
) -> list[float | None]:
    """
    Calcula la media movil simple (SMA) para una serie de valores.

    Para las primeras (window-1) posiciones retorna None porque
    no hay suficientes datos para la ventana completa.

    Complejidad: O(n * w)
    """
    sma: list[float | None] = []

    for index in range(len(values)):
        if index < window - 1:
            sma.append(None)
        else:
            window_values = values[index - window + 1 : index + 1]
            sma.append(sum(window_values) / window)

    return sma


def _get_ticker_ohlc(
    dataset: list[dict[str, Any]],
    ticker: str,
    last_n_days: int = 180,
) -> list[dict[str, Any]]:
    """
    Extrae y ordena las filas OHLC de un ticker.
    Limita a los ultimos N dias para legibilidad del grafico.
    """
    rows = [
        row for row in dataset
        if row["ticker"] == ticker
        and all(row.get(f) is not None for f in ["open", "high", "low", "close"])
    ]
    rows.sort(key=lambda r: r["date"])
    return rows[-last_n_days:]


def plot_candlestick(
    dataset: list[dict[str, Any]],
    ticker: str,
    output_path: str,
    last_n_days: int = 180,
    ma_windows: list[int] = [20, 50],
) -> str:
    """
    Genera un grafico de velas para el ticker indicado con medias moviles.

    Velas verdes: cierre >= apertura (dia alcista)
    Velas rojas:  cierre <  apertura (dia bajista)

    Args:
        dataset:     Dataset limpio con precios OHLC.
        ticker:      Activo a graficar.
        output_path: Ruta donde guardar la imagen PNG.
        last_n_days: Numero de dias recientes a mostrar.
        ma_windows:  Ventanas de medias moviles a graficar.

    Returns:
        Ruta del archivo generado.
    """
    rows = _get_ticker_ohlc(dataset, ticker, last_n_days)

    if not rows:
        print(f"  [AVISO] {ticker}: sin datos OHLC para graficar.")
        return ""

    dates  = [r["date"] for r in rows]
    opens  = [float(r["open"])  for r in rows]
    highs  = [float(r["high"])  for r in rows]
    lows   = [float(r["low"])   for r in rows]
    closes = [float(r["close"]) for r in rows]
    xs     = list(range(len(dates)))

    # Calcular medias moviles desde cero
    ma_series: dict[int, list[float | None]] = {}
    ma_colors = {20: "#ff8c00", 50: "#1e90ff", 100: "#9400d3"}

    for w in ma_windows:
        ma_series[w] = _calculate_sma(closes, w)

    fig, ax = plt.subplots(figsize=(16, 7))

    # Dibujar velas
    candle_width = 0.6
    for i, x in enumerate(xs):
        is_bullish = closes[i] >= opens[i]
        color      = "#26a69a" if is_bullish else "#ef5350"
        body_bottom = min(opens[i], closes[i])
        body_height = abs(closes[i] - opens[i])

        # Cuerpo de la vela
        rect = mpatches.Rectangle(
            (x - candle_width / 2, body_bottom),
            candle_width, body_height,
            linewidth=0.5,
            edgecolor=color,
            facecolor=color,
        )
        ax.add_patch(rect)

        # Mecha (sombra)
        ax.plot(
            [x, x], [lows[i], highs[i]],
            color=color, linewidth=0.8,
        )

    # Dibujar medias moviles
    for w, sma in ma_series.items():
        color  = ma_colors.get(w, "gray")
        xs_ma  = [x for x, v in zip(xs, sma) if v is not None]
        vals   = [v for v in sma if v is not None]
        ax.plot(xs_ma, vals, color=color, linewidth=1.5, label=f"MA{w}", zorder=3)

    # Eje X: mostrar solo algunas fechas para no saturar
    step = max(1, len(dates) // 10)
    ax.set_xticks(xs[::step])
    ax.set_xticklabels(dates[::step], rotation=45, ha="right", fontsize=8)

    ax.set_xlim(-1, len(xs))
    ax.set_ylim(min(lows) * 0.98, max(highs) * 1.02)
    ax.set_title(f"Candlestick — {ticker} (ultimos {len(rows)} dias)", fontsize=13)
    ax.set_ylabel("Precio (USD)")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.4)

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()

    print(f"  [OK] Candlestick {ticker} guardado: {output_path}")
    return output_path