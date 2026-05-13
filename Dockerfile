# ── Imagen base ───────────────────────────────────────────────
FROM python:3.11-slim

# Metadatos
LABEL description="Analisis de Algoritmos - Dashboard financiero con Streamlit"

# ── Variables de entorno ───────────────────────────────────────
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# ── Directorio de trabajo ──────────────────────────────────────
WORKDIR /app

# ── Dependencias del sistema ───────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ── Dependencias de Python ─────────────────────────────────────
# Se copia primero solo el requirements para aprovechar el cache de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Código fuente del proyecto ─────────────────────────────────
COPY . .

# ── Puerto que expone Streamlit ────────────────────────────────
EXPOSE 8501

# ── Healthcheck ────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" || exit 1

# ── Comando de inicio ──────────────────────────────────────────
# Usa app.py en la raíz (igual que Streamlit Cloud)
CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
