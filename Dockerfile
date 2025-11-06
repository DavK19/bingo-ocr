FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata

# Solo lo necesario para opencv-python-headless + Tesseract
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-spa \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Verificar instalación
RUN tesseract --version

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Respetar $PORT de Railway
CMD ["sh", "-c", "python -m uvicorn src.api:app --host 0.0.0.0 --port ${PORT:-8000}"]