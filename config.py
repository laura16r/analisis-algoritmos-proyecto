"""
config.py
=========
Rutas y constantes globales del proyecto.

Cualquier modulo que necesite una ruta la importa desde aqui.
Si en algun momento cambia la estructura de carpetas, solo se
modifica este archivo.
"""

import os

# ── Carpetas de datos ─────────────────────────────────────────
RAW_DIR         = "data/raw"
PROCESSED_DIR   = "data/processed"
RESULTS_DIR     = "data/results"

# ── Archivos del pipeline ─────────────────────────────────────
MASTER_DATASET_PATH         = os.path.join(PROCESSED_DIR, "master_dataset.json")
CLEAN_DATASET_PATH          = os.path.join(RESULTS_DIR,   "clean_dataset.json")
VALIDATION_LOG_PATH         = os.path.join(RESULTS_DIR,   "validation_report.json")
DAILY_RETURNS_PATH          = os.path.join(RESULTS_DIR,   "daily_returns_dataset.json")
HISTORICAL_VOLATILITY_PATH  = os.path.join(RESULTS_DIR,   "historical_volatility.json")
RISK_CLASSIFICATION_PATH    = os.path.join(RESULTS_DIR,   "risk_classification.json")
CORRELATION_PATH            = os.path.join(RESULTS_DIR,   "correlation_a_b.json")
SIMILARITY_PATH             = os.path.join(RESULTS_DIR,   "euclidean_similarity_a_b.json")
DTW_PATH                    = os.path.join(RESULTS_DIR,   "dtw_similarity_a_b.json")
COSINE_SIMILARITY_PATH      = os.path.join(RESULTS_DIR,   "cosine_similarity_a_b.json")
RISK_RANKING_PATH           = os.path.join(RESULTS_DIR,   "visual_risk_ranking.json")
PATTERNS_PATH               = os.path.join(RESULTS_DIR,   "patterns_detection.json")

# -- Imagenes y reporte PDF -------------------------------------------
CHARTS_DIR          = "data/results/charts"
HEATMAP_PATH        = "data/results/charts/heatmap_correlation.png"
REPORT_PDF_PATH     = "data/results/reporte_tecnico.pdf"
ASSET_COMPARISON_PATH       = os.path.join(RESULTS_DIR,   "visual_asset_comparison.json")

# ── Parametros de descarga ────────────────────────────────────
INTERVAL = "1d"
RANGE    = "5y"

# ── Lista de activos ──────────────────────────────────────────
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

# ── Validacion: minimo de registros esperados por activo ──────
# 5 años * ~252 dias bursatiles por año = ~1260 registros minimos
MIN_RECORDS_PER_ASSET = 1_000

# Estandar financiero para días de trading #
TRADING_DAYS = 252