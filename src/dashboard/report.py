"""
dashboard/report.py
====================
Genera un reporte tecnico en PDF que consolida todos los analisis
del proyecto: volatilidad, clasificacion de riesgo, similitud
entre activos y deteccion de patrones.

Usa reportlab para la construccion del PDF.
Las imagenes del heatmap y candlestick se incrustan en el reporte.
"""

from typing import Any
import os
import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
)


PAGE_W, PAGE_H = A4
MARGIN        = 2 * cm


def _styles() -> dict:
    base = getSampleStyleSheet()
    return {
        "title":    ParagraphStyle("title",    parent=base["Title"],   fontSize=18, spaceAfter=12),
        "h1":       ParagraphStyle("h1",        parent=base["Heading1"], fontSize=14, spaceAfter=8),
        "h2":       ParagraphStyle("h2",        parent=base["Heading2"], fontSize=11, spaceAfter=6),
        "body":     ParagraphStyle("body",      parent=base["Normal"],  fontSize=9,  spaceAfter=4),
        "small":    ParagraphStyle("small",     parent=base["Normal"],  fontSize=8,  spaceAfter=2),
        "centered": ParagraphStyle("centered",  parent=base["Normal"],  fontSize=9,  alignment=1),
    }


def _table_style_default() -> TableStyle:
    return TableStyle([
        ("BACKGROUND",  (0, 0), (-1, 0),  colors.HexColor("#1a237e")),
        ("TEXTCOLOR",   (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",    (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f5f5f5"), colors.white]),
        ("GRID",        (0, 0), (-1, -1), 0.3, colors.HexColor("#cccccc")),
        ("ALIGN",       (1, 1), (-1, -1), "CENTER"),
        ("TOPPADDING",  (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ])


def _section_volatility(
    volatility_data: list[dict[str, Any]],
    styles: dict,
) -> list:
    elements = []
    elements.append(Paragraph("1. Volatilidad Historica y Clasificacion de Riesgo", styles["h1"]))
    elements.append(Paragraph(
        "La volatilidad historica se calcula como la desviacion estandar de los retornos diarios, "
        "anualizada multiplicando por la raiz cuadrada de 252 dias bursatiles. "
        "Los activos se clasifican en tres categorias segun percentiles: "
        "conservador (percentil 33), moderado (percentil 66) y agresivo (por encima del 66).",
        styles["body"],
    ))
    elements.append(Spacer(1, 0.3 * cm))

    headers = [["Ticker", "Volatilidad Diaria", "Volatilidad Anual", "Nivel de Riesgo"]]
    rows = []

    for row in volatility_data:
        daily = f"{row.get('daily_volatility', 0) * 100:.4f}%" if row.get("daily_volatility") else "N/A"
        annual = f"{row.get('annual_volatility', 0) * 100:.2f}%" if row.get("annual_volatility") else "N/A"
        risk   = row.get("risk_level", "N/A").upper()
        rows.append([row["ticker"], daily, annual, risk])

    table = Table(headers + rows, colWidths=[3.5 * cm, 4 * cm, 4 * cm, 4 * cm])
    table.setStyle(_table_style_default())
    elements.append(table)
    elements.append(Spacer(1, 0.5 * cm))
    return elements


def _section_similarity(
    comparison_data: dict[str, Any],
    styles: dict,
) -> list:
    elements = []
    elements.append(Paragraph("2. Similitud entre Activos", styles["h1"]))

    asset_a = comparison_data.get("asset_a", "N/A")
    asset_b = comparison_data.get("asset_b", "N/A")
    obs     = comparison_data.get("observations", "N/A")
    metrics = comparison_data.get("metrics", {})

    elements.append(Paragraph(
        f"Comparacion entre <b>{asset_a}</b> y <b>{asset_b}</b> "
        f"usando {obs} observaciones de retornos diarios alineados por fecha.",
        styles["body"],
    ))
    elements.append(Spacer(1, 0.3 * cm))

    headers = [["Metrica", "Valor", "Interpretacion"]]
    interp  = comparison_data.get("interpretation_reference", {})

    rows = [
        ["Correlacion de Pearson",  str(round(metrics.get("pearson_correlation") or 0, 6)), interp.get("pearson_correlation", "")],
        ["Distancia Euclidiana",    str(round(metrics.get("euclidean_distance")  or 0, 6)), interp.get("euclidean_distance", "")],
        ["DTW Distance",            str(round(metrics.get("dtw_distance")        or 0, 6)), interp.get("dtw_distance", "")],
        ["Similitud Coseno",        str(round(metrics.get("cosine_similarity")   or 0, 6)), interp.get("cosine_similarity", "")],
    ]

    table = Table(headers + rows, colWidths=[4 * cm, 3 * cm, 8.5 * cm])
    table.setStyle(_table_style_default())
    elements.append(table)
    elements.append(Spacer(1, 0.5 * cm))
    return elements


def _section_patterns(
    patterns_data: list[dict[str, Any]],
    styles: dict,
) -> list:
    elements = []
    elements.append(Paragraph("3. Deteccion de Patrones (Sliding Window)", styles["h1"]))
    elements.append(Paragraph(
        "Se aplicaron dos patrones mediante ventana deslizante sobre el historial de precios: "
        "(1) N dias consecutivos al alza y "
        "(2) precio de cierre por encima de la media movil de 20 dias.",
        styles["body"],
    ))
    elements.append(Spacer(1, 0.3 * cm))

    headers = [["Ticker", "P1: Dias Alza (3d)", "Freq. P1", "P2: Precio > MA20", "Freq. P2"]]
    rows    = []

    for asset in patterns_data:
        ticker   = asset["ticker"]
        patterns = asset.get("patterns", [])
        p1 = next((p for p in patterns if "consecutive" in p["pattern"]), {})
        p2 = next((p for p in patterns if "ma" in p["pattern"]), {})

        rows.append([
            ticker,
            str(p1.get("occurrences", "N/A")),
            f"{p1.get('frequency_pct', 0):.2f}%",
            str(p2.get("occurrences", "N/A")),
            f"{p2.get('frequency_pct', 0):.2f}%",
        ])

    table = Table(headers + rows, colWidths=[3.5 * cm, 3.5 * cm, 2.5 * cm, 3.5 * cm, 2.5 * cm])
    table.setStyle(_table_style_default())
    elements.append(table)
    elements.append(Spacer(1, 0.5 * cm))
    return elements


def _section_charts(
    heatmap_path: str,
    candlestick_paths: list[str],
    styles: dict,
) -> list:
    elements = []
    elements.append(PageBreak())
    elements.append(Paragraph("4. Visualizaciones", styles["h1"]))

    if os.path.exists(heatmap_path):
        elements.append(Paragraph("4.1 Matriz de Correlacion (Heatmap)", styles["h2"]))
        elements.append(Image(heatmap_path, width=15 * cm, height=13 * cm))
        elements.append(Spacer(1, 0.5 * cm))

    for path in candlestick_paths:
        if os.path.exists(path):
            ticker = os.path.basename(path).replace("candlestick_", "").replace(".png", "")
            elements.append(Paragraph(f"4.2 Candlestick — {ticker}", styles["h2"]))
            elements.append(Image(path, width=15 * cm, height=6 * cm))
            elements.append(Spacer(1, 0.4 * cm))

    return elements


def generate_pdf_report(
    volatility_data:   list[dict[str, Any]],
    comparison_data:   dict[str, Any],
    patterns_data:     list[dict[str, Any]],
    heatmap_path:      str,
    candlestick_paths: list[str],
    output_path:       str,
) -> str:
    """
    Genera el reporte tecnico completo en PDF.

    Args:
        volatility_data:   Lista con volatilidad y clasificacion por ticker.
        comparison_data:   Diccionario con metricas de similitud entre dos activos.
        patterns_data:     Lista con resultados de deteccion de patrones.
        heatmap_path:      Ruta al PNG del heatmap de correlacion.
        candlestick_paths: Lista de rutas a PNGs de candlestick.
        output_path:       Ruta donde guardar el PDF.

    Returns:
        Ruta del PDF generado.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    doc     = SimpleDocTemplate(output_path, pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN,
                                topMargin=MARGIN, bottomMargin=MARGIN)
    styles  = _styles()
    today   = datetime.date.today().strftime("%d/%m/%Y")
    content = []

    # Portada
    content.append(Spacer(1, 2 * cm))
    content.append(Paragraph("Reporte Tecnico — Analisis de Activos Financieros", styles["title"]))
    content.append(Paragraph("Universidad del Quindio — Analisis de Algoritmos 2026-1", styles["centered"]))
    content.append(Paragraph(f"Generado: {today}", styles["centered"]))
    content.append(Spacer(1, 1 * cm))

    content += _section_volatility(volatility_data, styles)
    content += _section_similarity(comparison_data, styles)
    content += _section_patterns(patterns_data, styles)
    content += _section_charts(heatmap_path, candlestick_paths, styles)

    doc.build(content)
    print(f"  [OK] Reporte PDF generado: {output_path}")
    return output_path