FROM python:3.9-slim

# Instalar Tesseract y dependencias del sistema
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-spa \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Verificar instalación de Tesseract
RUN tesseract --version

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements primero (para aprovechar cache de Docker)
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código
COPY . .

# Exponer puerto (Railway usa variable $PORT)
EXPOSE 8000

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production

# Comando de inicio
CMD python -m uvicorn src.api:app --host 0.0.0.0 --port ${PORT:-8000}
