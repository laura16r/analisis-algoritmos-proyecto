"""
dashboard/heatmap.py
=====================
Genera la matriz de correlacion de Pearson entre todos los activos
y la representa como un mapa de calor (heatmap).

La correlacion se calcula desde cero usando los retornos diarios
del dataset. No se usa ninguna libreria de alto nivel para el calculo.
Matplotlib solo se usa para la visualizacion final.

Complejidad: O(n * m^2)
  n = numero de registros por activo
  m = numero de activos
"""

from typing import Any
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


def _get_returns_by_ticker(
    dataset: list[dict[str, Any]],
    field: str = "daily_return",
) -> dict[str, list[float]]:
    """Agrupa los retornos diarios por ticker, descartando None."""
    grouped: dict[str, list[float]] = {}

    for row in dataset:
        ticker = row["ticker"]
        value  = row.get(field)

        if value is None:
            continue

        grouped.setdefault(ticker, []).append(float(value))

    return grouped


def _align_two_series(
    series_a: list[float],
    series_b: list[float],
) -> tuple[list[float], list[float]]:
    """Recorta ambas series al mismo largo."""
    length = min(len(series_a), len(series_b))
    return series_a[:length], series_b[:length]


def _pearson(x: list[float], y: list[float]) -> float:
    """Calcula correlacion de Pearson desde cero. O(n)."""
    n = len(x)
    if n == 0:
        return 0.0

    mean_x = sum(x) / n
    mean_y = sum(y) / n

    num = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
    den_x = sum((x[i] - mean_x) ** 2 for i in range(n))
    den_y = sum((y[i] - mean_y) ** 2 for i in range(n))
    den   = (den_x * den_y) ** 0.5

    return round(num / den, 4) if den != 0 else 0.0


def build_correlation_matrix(
    dataset: list[dict[str, Any]],
    field: str = "daily_return",
) -> tuple[list[str], list[list[float]]]:
    """
    Calcula la matriz de correlacion de Pearson entre todos los activos.

    Retorna:
        tickers: lista ordenada de activos
        matrix:  matriz NxN de correlaciones
    """
    returns   = _get_returns_by_ticker(dataset, field)
    tickers   = sorted(returns.keys())
    n         = len(tickers)
    matrix    = [[0.0] * n for _ in range(n)]

    for i, ticker_a in enumerate(tickers):
        for j, ticker_b in enumerate(tickers):
            if i == j:
                matrix[i][j] = 1.0
            elif j > i:
                a, b = _align_two_series(returns[ticker_a], returns[ticker_b])
                corr = _pearson(a, b)
                matrix[i][j] = corr
                matrix[j][i] = corr

    return tickers, matrix


def plot_heatmap(
    dataset: list[dict[str, Any]],
    output_path: str,
    field: str = "daily_return",
) -> str:
    """
    Genera el heatmap de correlacion y lo guarda como imagen PNG.

    Args:
        dataset:     Dataset con retornos diarios.
        output_path: Ruta donde guardar la imagen.
        field:       Campo de retornos a usar.

    Returns:
        Ruta del archivo generado.
    """
    tickers, matrix = build_correlation_matrix(dataset, field)
    n = len(tickers)

    fig, ax = plt.subplots(figsize=(14, 12))

    # Dibujar celdas manualmente para control total
    for i in range(n):
        for j in range(n):
            value = matrix[i][j]

            # Color: rojo para correlacion negativa, azul para positiva
            if value >= 0:
                intensity = value
                color = (1 - intensity * 0.7, 1 - intensity * 0.7, 1.0)
            else:
                intensity = abs(value)
                color = (1.0, 1 - intensity * 0.7, 1 - intensity * 0.7)

            rect = mpatches.Rectangle(
                [j, n - i - 1], 1, 1,
                linewidth=0.5,
                edgecolor="white",
                facecolor=color,
            )
            ax.add_patch(rect)

            text_color = "black" if abs(value) < 0.7 else "white"
            ax.text(
                j + 0.5, n - i - 0.5,
                f"{value:.2f}",
                ha="center", va="center",
                fontsize=7, color=text_color,
            )

    ax.set_xlim(0, n)
    ax.set_ylim(0, n)
    ax.set_xticks([i + 0.5 for i in range(n)])
    ax.set_yticks([i + 0.5 for i in range(n)])
    ax.set_xticklabels(tickers, rotation=45, ha="right", fontsize=9)
    ax.set_yticklabels(reversed(tickers), fontsize=9)
    ax.set_title("Matriz de Correlacion de Pearson — Retornos Diarios", fontsize=13, pad=15)

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()

    print(f"  [OK] Heatmap guardado: {output_path}")
    return output_path