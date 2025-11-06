
<div align="center">
 
  <h1>Bingo OCR API</h1>
  <p><strong>Servicio de extracción de números desde cartones de Bingo usando OCR y segmentación por cuadrícula.</strong></p>
  <p>Diseñado para integrarse fácilmente con frontends web o móviles y asistido por LLMs.</p>
  <p>
    <a href="#spec-api">Especificación API</a> ·
    <a href="#quickstart">Quickstart</a> ·
    <a href="#integracion-frontend">Integración Frontend</a> ·
    <a href="#debugging">Debugging</a> ·
    <a href="#errores">Errores</a> ·
    <a href="#llm-notes">Notas para LLM</a>
  </p>
</div>

---

## Objetivo

Tomar la imagen de un cartón de bingo, dividirla en una cuadrícula (por defecto 5x5) y devolver una matriz con el texto/números detectados en cada celda usando Tesseract OCR + preprocesamiento OpenCV.

## Arquitectura Resumida

- Framework backend: FastAPI (`src/api.py`)
- Motor OCR: Tesseract (instalado en sistema / paquete nixpacks)
- Preprocesamiento: OpenCV (`preproc.py`) + segmentación (`processor.py`)
- Formato de respuesta principal: JSON estructurado (ver más abajo)
- Despliegue: Railway (Nixpacks + uvicorn)

## Stack y Requisitos

| Componente          | Versión sugerida | Descripción |
|---------------------|------------------|-------------|
| Python              | 3.9+             | Runtime principal |
| FastAPI             | 0.104+           | Framework API |
| Uvicorn             | 0.24+            | ASGI server |
| OpenCV (headless)   | 4.8+             | Procesamiento de imagen |
| Pytesseract         | 0.3.10           | Wrapper de Tesseract |
| Tesseract OCR       | 5.x              | Motor OCR |

## Instalación Local

```bash
git clone https://github.com/<TU_USUARIO>/bingo-ocr.git
cd bingo-ocr
python -m venv venv
./venv/Scripts/activate  # Windows PowerShell
pip install -r requirements.txt
# Instala Tesseract (Windows: usar instalador UB Mannheim)
```

Ejecutar el servidor:
```bash
python -m uvicorn src.api:app --reload --port 8000
```

Visita: http://localhost:8000/docs

---

## <a id="spec-api"></a>Especificación de la API

### 1. GET `/health`
Health check simple.

Respuesta 200:
```json
{
  "status": "healthy",
  "service": "bingo-ocr-api",
  "version": "1.0.0"
}
```

### 2. GET `/`
Metadata y listado de endpoints.

### 3. POST `/process`
Procesa una imagen de cartón de bingo.

Content-Type: `multipart/form-data`

Campos:
| Nombre | Tipo | Obligatorio | Descripción |
|--------|------|-------------|-------------|
| file   | File | Sí          | Imagen del cartón (`.png .jpg .jpeg .bmp .tiff`) |
| rows   | int  | No (default 5) | Filas de la cuadrícula |
| cols   | int  | No (default 5) | Columnas de la cuadrícula |

Ejemplo cURL:
```bash
curl -X POST "http://localhost:8000/process" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@samples/carton_ejemplo.png" \
  -F "rows=5" \
  -F "cols=5"
```

Respuesta 200 (ejemplo):
```json
{
  "success": true,
  "filename": "carton_ejemplo.png",
  "grid": [
    ["14", "21", "32", "45", "57"],
    ["8", "17", "FREE", "49", "63"],
    ["3", "19", "27", "52", "70"],
    ["6", "24", "31", "59", "72"],
    ["10", "26", "33", "48", "75"]
  ],
  "dimensions": {"rows": 5, "cols": 5},
  "total_numbers": 25
}
```

Errores comunes:
| Código | Motivo | Ejemplo `detail` |
|--------|--------|------------------|
| 400 | Extensión inválida | `Formato de archivo no permitido. Use: .png, .jpg, ...` |
| 400 | Grid fuera de rango | `Las dimensiones del grid deben estar entre 1 y 10` |
| 404 | Imagen no encontrada | `Imagen no encontrada: path` |
| 500 | Fallo interno OCR | `Error procesando imagen: ...` |

### OpenAPI
El esquema completo se expone automáticamente en: `/openapi.json`. Úsalo para generar clientes (por ejemplo, con `openapi-generator` o directamente en tu frontend).

---

## Ejemplos de Consumo

### JavaScript (fetch)
```js
async function uploadBingoCard(file, rows = 5, cols = 5) {
  const form = new FormData();
  form.append('file', file);
  form.append('rows', rows);
  form.append('cols', cols);

  const res = await fetch('/process', { method: 'POST', body: form });
  if (!res.ok) throw new Error('Error OCR: ' + res.status);
  return res.json();
}
```

### TypeScript interfaz sugerida
```ts
export interface BingoOCRResponse {
  success: boolean;
  filename: string;
  grid: string[][];
  dimensions: { rows: number; cols: number };
  total_numbers: number;
}
```

### Python (requests)
```python
import requests

def process_card(path):
    with open(path, 'rb') as f:
        files = {'file': (path, f, 'image/png')}
        data = {'rows': 5, 'cols': 5}
        r = requests.post('http://localhost:8000/process', files=files, data=data)
        r.raise_for_status()
        return r.json()

print(process_card('samples/carton_ejemplo.png'))
```

### Bash (cURL mínimo)
```bash
curl -F "file=@samples/carton_ejemplo.png" http://localhost:8000/process
```

---

## Integración Frontend

### Flujo típico
1. Usuario selecciona imagen (input file / drag & drop)
2. Mostrar preview
3. Enviar FormData a `/process`
4. Recibir `grid` y renderizar tabla interactiva
5. Permitir exportación (CSV / JSON) o validación de patrón de bingo

### Renderizado de la matriz (React)
```jsx
function BingoGrid({ grid }) {
  return (
    <table className="bingo-grid">
      <tbody>
        {grid.map((row, i) => (
          <tr key={i}>
            {row.map((cell, j) => <td key={j}>{cell || ''}</td>)}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

### Validación rápida de Bingo (ejemplo lógica)
```ts
function hasBingo(grid: string[][]): boolean {
  const n = grid.length;
  const checkLine = (cells: string[]) => cells.every(c => c && c.toUpperCase() !== 'FREE');
  // Filas
  if (grid.some(row => checkLine(row))) return true;
  // Columnas
  for (let c = 0; c < n; c++) {
    const col = grid.map(row => row[c]);
    if (checkLine(col)) return true;
  }
  // Diagonales
  const d1 = grid.map((r, i) => r[i]);
  const d2 = grid.map((r, i) => r[n - 1 - i]);
  return checkLine(d1) || checkLine(d2);
}
```

---

## Manejo de Errores

Patrón sugerido frontend:
```js
try {
  const data = await uploadBingoCard(file);
  // usar data.grid
} catch (e) {
  // e.message o inspeccionar status
}
```

Respuesta de error FastAPI (formato estándar):
```json
{
  "detail": "Mensaje de error" 
}
```

Reintentar solo si el error es 500 y la imagen podría estar corrupta temporalmente.

---

## Seguridad y Límites

- Tamaño máximo de imagen: dependerá del límite por defecto de Uvicorn/Server (se recomienda < 5MB para rendimiento).
- Sanitización: Se valida la extensión; podrías agregar validación MIME y límite de dimensiones.
- CORS: Abierto a `*` por defecto. Ajustar en producción para dominios específicos.

---

## Despliegue en Railway (Resumen)

Archivos clave:
```
requirements.txt
nixpacks.toml
Procfile (opcional)
```
Start command:
```
python -m uvicorn src.api:app --host 0.0.0.0 --port $PORT
```

Variables entorno sugeridas:
```
ENVIRONMENT=production
PORT=<auto>
```

---

## <a id="debugging"></a>Debugging y Logs

### Sistema de Logging Detallado

La API incluye logging extensivo para facilitar el debugging:

- 📨 **Request logs**: Método, URL, origin, headers
- 🎯 **Processing logs**: Pasos de procesamiento OCR
- 📤 **Response logs**: Status codes, headers
- ❌ **Error logs**: Excepciones con traceback completo

### Ver Logs en Railway

**Opción 1: Dashboard Web**
1. Ve a [railway.app](https://railway.app)
2. Selecciona tu proyecto
3. Click en "Deployments" → Deployment activo → "Logs"

**Opción 2: Railway CLI (Recomendado)**
```bash
# Instalar CLI
npm i -g @railway/cli

# Login y link
railway login
railway link

# Ver logs en tiempo real
railway logs --follow

# Buscar errores
railway logs | grep "❌"
railway logs | grep "CORS"
```

### Ejemplo de Logs

Cuando tu frontend hace una request, verás:

```
🚀 BINGO OCR API STARTING
  CORS Origins: ['http://localhost:3000', 'https://tu-frontend.vercel.app']
✅ API READY TO ACCEPT REQUESTS

📨 [20251106123045] ===== INCOMING REQUEST =====
  Method: POST
  URL: /process
  Origin: https://tu-frontend.vercel.app
  Content-Type: multipart/form-data

🎯 [20251106123045] ===== PROCESSING REQUEST =====
  Filename: carton.png
  Grid size: 5x5
💾 File saved successfully. Size: 245678 bytes
🔄 Starting OCR processing...
✅ OCR processing completed successfully

📤 [20251106123045] ===== RESPONSE =====
  Status: 200
```

### Variables de Entorno para Debugging

Configura en Railway Dashboard → Variables:

```env
# Requerido para CORS
FRONTEND_URL=https://tu-frontend.vercel.app

# Opcional
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### Test Local con Logs

```bash
# Ejecutar API
python -m uvicorn src.api:app --reload --port 8000

# En otra terminal, ejecutar tests
python test_logs.py
```

### Problemas Comunes

| Síntoma | Log que verás | Solución |
|---------|---------------|----------|
| CORS error | `Origin: NO ORIGIN` | Agregar `FRONTEND_URL` en Railway |
| Tesseract error | `❌ Tesseract no encontrado` | Verificar `nixpacks.toml` |
| Conexión rechazada | No aparece `📨 INCOMING REQUEST` | Verificar URL en frontend |
| 500 error | `❌ Unexpected error` + traceback | Revisar logs completos |

📖 **Guía completa**: Ver [`DEBUGGING.md`](DEBUGGING.md) para instrucciones detalladas.

---

## Testing

```bash
pytest -q
```

Test mínimo incluido en `tests/test_api.py` para endpoints básicos.

---

## Roadmap / Ideas Futuras

- Detección automática de tamaño de cuadrícula.
- Highlight de celdas dudosas (baja confianza OCR).
- Endpoint `/process/base64` para enviar imágenes codificadas.
- Cache de resultados.
- Internacionalización (nombres de campos, mensajes).

---

## <a id="llm-notes"></a>Notas para LLM

Objetivo: Este README está estructurado para que un LLM pueda:
1. Generar automáticamente componentes de subida de imagen.
2. Crear un cliente API tipado (TypeScript interface incluida).
3. Implementar lógica de validación de Bingo.
4. Extender endpoints manteniendo formato JSON existente.

Reglas de la respuesta `/process` a respetar si se añaden campos:
- Mantener `success: boolean`
- Mantener `grid: string[][]`
- Nuevos metadatos deben ir en la raíz y ser camelCase.
- Evitar mutar semántica de `dimensions`.

---

## Licencia

MIT

---

## Contacto / Contribuir

PRs y issues bienvenidos. Para cambios mayores, abrir issue primero.

---

_Última actualización: 2025-11-06_
