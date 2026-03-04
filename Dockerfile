# ============================================================
# Dockerfile — SDP Conventions API (VPS Production)
# ============================================================

# ────────────────────────────────────
# Stage 1 : API (léger, sans Chromium)
# ────────────────────────────────────
FROM python:3.11-slim AS api

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# sqlite3 en CLI (pour restaurer la BDD depuis le dump SQL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Rendre l'entrypoint exécutable
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

# Entrypoint : restaure la BDD si nécessaire, puis lance l'API
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]


# ────────────────────────────────────────────────────────────
# Stage 2 : Scraper (avec Chromium pour Selenium)
# ────────────────────────────────────────────────────────────
FROM python:3.11-slim AS scraper

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    sqlite3 \
    fonts-liberation \
    libnss3 \
    libatk-bridge2.0-0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "main.py", "--all"]
