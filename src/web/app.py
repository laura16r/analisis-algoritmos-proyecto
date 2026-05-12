"""
web/app.py
===========
Aplicacion web interactiva construida con Streamlit.

Para ejecutar localmente:
  streamlit run src/web/app.py

Para deploy en Streamlit Cloud:
  El archivo de entrada es app.py en la raiz del proyecto.
"""

import os
import sys
import io
import traceback
from contextlib import redirect_stdout

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
from main import main as run_main_pipeline

from config import (
    RISK_CLASSIFICATION_PATH,
    PATTERNS_PATH,
    HEATMAP_PATH,
    CHARTS_DIR,
    CLEAN_DATASET_PATH,
    DAILY_RETURNS_PATH,
    ASSETS,
)
from src.utils.io import FileUtils
from src.analytics.correlation import calculate_pearson_between_assets
from src.analytics.similarity import (
    calculate_euclidean_similarity_between_assets,
    calculate_dtw_similarity_between_assets,
    calculate_cosine_similarity_between_assets,
)
from src.analytics.visualization_preparer import prepare_asset_comparison
from src.dashboard.candlestick import plot_candlestick


# ─────────────────────────────────────────────────────────────
# Configuracion
# ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Dashboard Bursatil — BVC & ETFs",
    page_icon="📈",
    layout="wide",
)

st.title("📈 Dashboard Bursatil — BVC & ETFs Globales")
st.caption("Universidad del Quindio — Analisis de Algoritmos 2026-1")
st.divider()


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

@st.cache_data
def load_data(path: str):
    try:
        return FileUtils.load_json(path)
    except FileNotFoundError:
        return None


def check_data(data, path: str) -> bool:
    if data is None:
        st.error(f"Archivo no encontrado: `{path}`. Ejecuta primero `python main.py`.")
        return False
    return True


def execute_main_pipeline():
    output = io.StringIO()
    try:
        with redirect_stdout(output):
            run_main_pipeline()
        st.cache_data.clear()
        return True, output.getvalue()
    except Exception:
        return False, output.getvalue() + "\n" + traceback.format_exc()


# ─────────────────────────────────────────────────────────────
# Navegacion
# ─────────────────────────────────────────────────────────────

seccion = st.sidebar.radio(
    "Navegacion",
    [
        "🏠 Inicio",
        "📊 Clasificacion de Riesgo",
        "🔗 Similitud entre Activos",
        "🔍 Deteccion de Patrones",
        "🖼️ Visualizaciones",
        "⚙️ Ejecutar Pipeline",
    ],
)

st.sidebar.divider()
st.sidebar.caption("Datos: Yahoo Finance | Periodo: 5 años | 20 activos")


# ─────────────────────────────────────────────────────────────
# Inicio
# ─────────────────────────────────────────────────────────────

if seccion == "🏠 Inicio":
    st.subheader("Bienvenido al Dashboard de Analisis Financiero")
    st.markdown("""
    Esta aplicacion explora los resultados del pipeline de analisis
    financiero sobre **20 activos** del mercado colombiano (BVC) y global (ETFs).

    | Seccion | Descripcion |
    |---------|-------------|
    | 📊 Clasificacion de Riesgo | Volatilidad historica y nivel de riesgo por activo |
    | 🔗 Similitud entre Activos | Comparacion con 4 algoritmos desde cero |
    | 🔍 Deteccion de Patrones | Frecuencia de patrones en series de precios |
    | 🖼️ Visualizaciones | Heatmap de correlacion y graficos de velas |
    """)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Acciones colombianas (BVC)**")
        for t in ["EC", "CIB", "GGAL", "GEB.CL", "ISA.CL",
                  "CELSIA.CL", "NUTRESA.CL", "EXITO.CL", "CEMARGOS.CL", "CNEC.CL"]:
            st.markdown(f"- `{t}`")
    with col2:
        st.markdown("**ETFs y acciones globales**")
        for t in ["VOO", "SPY", "QQQ", "IVV", "VTI",
                  "EEM", "GLD", "AAPL", "MSFT", "AMZN"]:
            st.markdown(f"- `{t}`")


# ─────────────────────────────────────────────────────────────
# Clasificacion de Riesgo
# ─────────────────────────────────────────────────────────────

elif seccion == "📊 Clasificacion de Riesgo":
    st.subheader("📊 Clasificacion de Activos por Riesgo")
    st.markdown("""
    Volatilidad historica = desviacion estandar de retornos diarios × √252.
    Clasificacion por percentiles 33 y 66 de la distribucion de volatilidades.
    """)

    data = load_data(RISK_CLASSIFICATION_PATH)
    if check_data(data, RISK_CLASSIFICATION_PATH):

        niveles = ["Todos"] + sorted({r.get("risk_level", "").capitalize() for r in data})
        filtro  = st.selectbox("Filtrar por nivel de riesgo", niveles)

        rows = data if filtro == "Todos" else [
            r for r in data if r.get("risk_level", "").lower() == filtro.lower()
        ]

        color_map = {"agresivo": "🔴", "moderado": "🟡", "conservador": "🟢"}

        table_data = []
        for r in rows:
            daily  = f"{r.get('daily_volatility', 0) * 100:.4f}%" if r.get("daily_volatility") else "N/A"
            annual = f"{r.get('annual_volatility', 0) * 100:.2f}%" if r.get("annual_volatility") else "N/A"
            risk   = r.get("risk_level", "N/A")
            icon   = color_map.get(risk, "⚪")
            table_data.append({
                "Ticker":             r["ticker"],
                "Volatilidad Diaria": daily,
                "Volatilidad Anual":  annual,
                "Nivel de Riesgo":    f"{icon} {risk.capitalize()}",
            })

        st.dataframe(table_data, use_container_width=True, hide_index=True)
        st.divider()

        col1, col2, col3 = st.columns(3)
        col1.metric("🔴 Agresivos",     sum(1 for r in data if r.get("risk_level") == "agresivo"))
        col2.metric("🟡 Moderados",     sum(1 for r in data if r.get("risk_level") == "moderado"))
        col3.metric("🟢 Conservadores", sum(1 for r in data if r.get("risk_level") == "conservador"))


# ─────────────────────────────────────────────────────────────
# Similitud entre Activos
# ─────────────────────────────────────────────────────────────

elif seccion == "🔗 Similitud entre Activos":
    st.subheader("🔗 Similitud entre Activos")
    st.markdown("""
    Compara dos activos usando cuatro algoritmos implementados desde cero
    sobre sus **retornos diarios alineados por fecha**.
    """)

    col1, col2 = st.columns(2)
    ticker_a = col1.selectbox("Activo A", ASSETS, index=ASSETS.index("AAPL"))
    ticker_b = col2.selectbox("Activo B", ASSETS, index=ASSETS.index("MSFT"))

    if ticker_a == ticker_b:
        st.warning("Selecciona dos activos diferentes.")
    elif st.button("Calcular similitud", type="primary"):
        dataset = load_data(DAILY_RETURNS_PATH)
        if check_data(dataset, DAILY_RETURNS_PATH):
            with st.spinner("Calculando los 4 algoritmos..."):
                pearson   = calculate_pearson_between_assets(dataset, ticker_a, ticker_b)
                euclidean = calculate_euclidean_similarity_between_assets(dataset, ticker_a, ticker_b, field="daily_return")
                dtw       = calculate_dtw_similarity_between_assets(dataset, ticker_a, ticker_b, field="daily_return")
                cosine    = calculate_cosine_similarity_between_assets(dataset, ticker_a, ticker_b, field="daily_return")
                comparison = prepare_asset_comparison(pearson, euclidean, dtw, cosine)

            st.success(f"**{ticker_a}** vs **{ticker_b}** — {pearson['observations']} observaciones alineadas")
            st.divider()

            metrics = comparison["metrics"]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Pearson",    f"{metrics.get('pearson_correlation') or 0:.6f}")
            c2.metric("Euclidiana", f"{metrics.get('euclidean_distance') or 0:.6f}")
            c3.metric("DTW",        f"{metrics.get('dtw_distance') or 0:.6f}")
            c4.metric("Coseno",     f"{metrics.get('cosine_similarity') or 0:.6f}")

            st.divider()
            st.markdown("**Interpretacion de los resultados**")
            for key, desc in comparison["interpretation_reference"].items():
                st.markdown(f"- **{key}**: {desc}")


# ─────────────────────────────────────────────────────────────
# Deteccion de Patrones
# ─────────────────────────────────────────────────────────────

elif seccion == "🔍 Deteccion de Patrones":
    st.subheader("🔍 Deteccion de Patrones (Sliding Window)")
    st.markdown("""
    - **Patron 1**: 3 dias consecutivos al alza
    - **Patron 2**: Precio de cierre por encima de la media movil de 20 dias (MA20)
    """)

    data = load_data(PATTERNS_PATH)
    if check_data(data, PATTERNS_PATH):

        table_data = []
        for asset in data:
            ticker   = asset["ticker"]
            patterns = asset.get("patterns", [])
            p1 = next((p for p in patterns if "consecutive" in p["pattern"]), {})
            p2 = next((p for p in patterns if "ma" in p["pattern"]), {})

            table_data.append({
                "Ticker":              ticker,
                "P1 — Dias alza (3d)": p1.get("occurrences", "N/A"),
                "Frecuencia P1":       f"{p1.get('frequency_pct', 0):.2f}%",
                "P2 — Precio > MA20":  p2.get("occurrences", "N/A"),
                "Frecuencia P2":       f"{p2.get('frequency_pct', 0):.2f}%",
            })

        st.dataframe(table_data, use_container_width=True, hide_index=True)

        st.divider()
        st.markdown("**Detalle de un activo especifico**")
        ticker_sel = st.selectbox("Selecciona un activo", [a["ticker"] for a in data])
        asset_sel  = next((a for a in data if a["ticker"] == ticker_sel), None)

        if asset_sel:
            for pattern in asset_sel["patterns"]:
                with st.expander(f"Patron: {pattern['pattern']} — {pattern['occurrences']} ocurrencias ({pattern['frequency_pct']}%)"):
                    if pattern["details"]:
                        st.dataframe(pattern["details"][:50], use_container_width=True, hide_index=True)
                    else:
                        st.info("Sin ocurrencias detectadas.")


# ─────────────────────────────────────────────────────────────
# Visualizaciones
# ─────────────────────────────────────────────────────────────

elif seccion == "🖼️ Visualizaciones":
    st.subheader("🖼️ Visualizaciones")

    tab1, tab2 = st.tabs(["Heatmap de Correlacion", "Candlestick + Medias Moviles"])

    with tab1:
        st.markdown("**Matriz de Correlacion de Pearson** entre todos los activos (retornos diarios)")
        if os.path.exists(HEATMAP_PATH):
            st.image(HEATMAP_PATH, use_container_width=True)
        else:
            st.error("Heatmap no encontrado. Ejecuta primero `python main.py`.")

    with tab2:
        st.markdown("**Grafico de velas** con medias moviles simples (MA20 y MA50)")

        ticker_sel = st.selectbox("Selecciona un activo", ASSETS)
        days_sel   = st.slider("Dias a mostrar", min_value=60, max_value=365, value=180, step=30)

        if st.button("Generar grafico", type="primary"):
            clean_data = load_data(CLEAN_DATASET_PATH)
            if check_data(clean_data, CLEAN_DATASET_PATH):
                with st.spinner("Generando candlestick..."):
                    os.makedirs(CHARTS_DIR, exist_ok=True)
                    tmp_path = os.path.join(CHARTS_DIR, f"candlestick_{ticker_sel}_tmp.png")
                    plot_candlestick(
                        dataset=clean_data,
                        ticker=ticker_sel,
                        output_path=tmp_path,
                        last_n_days=days_sel,
                        ma_windows=[20, 50],
                    )
                st.image(tmp_path, use_container_width=True)


# ─────────────────────────────────────────────────────────────
# Ejecutar Pipeline
# ─────────────────────────────────────────────────────────────

elif seccion == "⚙️ Ejecutar Pipeline":
    st.subheader("⚙️ Ejecutar Pipeline de Analisis")
    st.markdown("""
    Desde esta seccion puedes invocar el archivo `main.py` para regenerar
    los archivos de resultados que usa el dashboard.
    """)

    st.warning(
        "Este proceso puede tardar y sobrescribira los archivos generados en `data/results/`."
    )

    if st.button("Ejecutar main.py", type="primary"):
        with st.spinner("Ejecutando pipeline completo..."):
            success, output = execute_main_pipeline()

        if success:
            st.success("Pipeline completado correctamente.")
        else:
            st.error("El pipeline fallo durante la ejecucion.")

        with st.expander("Ver salida de main.py", expanded=not success):
            st.code(output or "main.py no produjo salida en consola.", language="text")
