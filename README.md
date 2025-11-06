
# Bingo OCR API

API para extraer números de cartones de bingo usando OCR (Optical Character Recognition).

## 🚀 Características

- Extracción automática de números de cartones de bingo
- API REST con FastAPI
- Documentación automática con Swagger
- Soporte para múltiples formatos de imagen
- Desplegable en Railway

## 📋 Requisitos

- Python 3.9+
- Tesseract OCR

## 🛠️ Instalación Local

1. Clonar el repositorio:

```bash
git clone <tu-repo>
cd bingo-ocr
```

2. Crear entorno virtual:

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

4. Instalar Tesseract:
   - **Windows**: Descargar de [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - **Linux**: `sudo apt-get install tesseract-ocr`
   - **macOS**: `brew install tesseract`

## 🚀 Uso

### Ejecutar localmente:

```bash
uvicorn src.api:app --reload --port 8000
```

Visita `http://localhost:8000/docs` para la documentación interactiva.

### Ejemplo de request:

```bash
curl -X POST "http://localhost:8000/process" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@carton.png" \
  -F "rows=5" \
  -F "cols=5"
```

## 📦 Deploy en Railway

1. Conecta tu repositorio a Railway
2. Railway detectará automáticamente el `nixpacks.toml`
3. El servicio se desplegará automáticamente

## 📚 Endpoints

- `GET /` - Información de la API
- `GET /health` - Estado del servicio
- `POST /process` - Procesar imagen de cartón
- `GET /docs` - Documentación Swagger
- `GET /redoc` - Documentación ReDoc

## 🧪 Testing

```bash
pytest tests/
```

## 📄 Licencia

MIT
