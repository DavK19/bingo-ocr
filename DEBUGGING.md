# 🔍 Guía de Debugging - Bingo OCR API

## Cómo Ver los Logs

### Opción 1: Railway Dashboard (Más Fácil)

1. Ve a [railway.app](https://railway.app)
2. Selecciona tu proyecto "bingo-ocr"
3. Click en el servicio
4. Pestaña **"Deployments"**
5. Click en el deployment activo (verde)
6. Pestaña **"Logs"** (se actualizan en tiempo real)

### Opción 2: Railway CLI (Recomendado para debugging)

```bash
# Instalar Railway CLI (solo primera vez)
npm i -g @railway/cli

# Login
railway login

# Link a tu proyecto
railway link

# Ver logs en tiempo real
railway logs --follow

# Ver últimas 100 líneas
railway logs -n 100

# Buscar errores específicos
railway logs | grep "ERROR"
railway logs | grep "CORS"
railway logs | grep "❌"
```

---

## Tipos de Logs que Verás

### ✅ Logs de Startup
```
🚀 BINGO OCR API STARTING
  Environment: production
  Port: 8000
  CORS Origins: ['http://localhost:3000', ...]
✅ API READY TO ACCEPT REQUESTS
```

### 📨 Logs de Request Entrante
```
📨 [20251106123045000] ===== INCOMING REQUEST =====
  Method: POST
  URL: https://tu-api.railway.app/process
  Origin: https://tu-frontend.vercel.app
  Content-Type: multipart/form-data
  All Headers: {...}
```

### 🎯 Logs de Procesamiento
```
🎯 [20251106123045000] ===== PROCESSING REQUEST =====
  Filename: carton.png
  Content-Type: image/png
  Grid size: 5x5
💾 [20251106123045000] File saved successfully. Size: 245678 bytes
🔄 [20251106123045000] Starting OCR processing...
✅ [20251106123045000] OCR processing completed successfully
```

### 📤 Logs de Response
```
📤 [20251106123045000] ===== RESPONSE =====
  Status: 200
  Headers: {...}
```

### ❌ Logs de Error
```
❌ [20251106123045000] ===== ERROR =====
  Exception: No module named 'tesseract'
  Type: ModuleNotFoundError
  Traceback: ...
```

---

## Problemas Comunes y Cómo Detectarlos

### 1. Error de CORS

**Síntomas en logs:**
```
📨 Origin: https://tu-frontend-no-autorizado.com
❌ CORS error: Origin not allowed
```

**Solución:**
Agregar variable de entorno en Railway:
```
FRONTEND_URL=https://tu-frontend.vercel.app
```

O actualizar el código en `api.py`:
```python
origins = [
    "https://tu-frontend.vercel.app",
    "http://localhost:3000"
]
```

---

### 2. Tesseract No Encontrado

**Síntomas en logs:**
```
❌ RuntimeError: Tesseract no encontrado
```

**Solución:**
Verificar que `nixpacks.toml` tiene:
```toml
[phases.setup]
nixPkgs = ["tesseract", "python39"]
```

Redeploy en Railway.

---

### 3. Error de Timeout

**Síntomas en logs:**
```
❌ Timeout processing image
⏱️ Processing time: >30s
```

**Solución:**
- Imagen muy grande, pedir al usuario que reduzca tamaño
- Optimizar preprocesamiento
- Aumentar timeout en Railway settings

---

### 4. Archivo No Válido

**Síntomas en logs:**
```
⚠️ Invalid file extension: .txt
```

**Solución:**
Usuario debe enviar imagen válida (.png, .jpg, etc.)

---

### 5. Conexión Rechazada desde Frontend

**Cómo detectar:**

**En logs verás:**
- ✅ Si hay requests: `📨 INCOMING REQUEST`
- ❌ Si NO hay requests: el frontend no está llegando

**Si NO ves requests:**
1. Frontend tiene la URL incorrecta
2. CORS está bloqueando antes de llegar al servidor
3. Red/firewall bloqueando

**Si VES requests pero fallan:**
Revisar el status code en logs:
```
📤 Status: 400  → Bad request (validación)
📤 Status: 500  → Error interno (OCR falló)
📤 Status: 404  → Endpoint no existe
```

---

## Variables de Entorno en Railway

Configurar en Railway Dashboard → Settings → Variables:

```env
# Obligatorio para CORS
FRONTEND_URL=https://tu-frontend.vercel.app

# Opcional
ENVIRONMENT=production
LOG_LEVEL=INFO
```

---

## Testing Directo desde Terminal

### Test Health Check
```bash
curl https://tu-api.railway.app/health
```

Deberías ver:
```json
{
  "status": "healthy",
  "service": "bingo-ocr-api",
  "version": "1.0.0"
}
```

### Test Process (con imagen)
```bash
curl -X POST "https://tu-api.railway.app/process" \
  -F "file=@samples/carton_ejemplo.png" \
  -F "rows=5" \
  -F "cols=5"
```

---

## Habilitar Logs Más Detallados

Si necesitas más información, actualiza en Railway:

```env
LOG_LEVEL=DEBUG
```

Redeploy y verás logs adicionales.

---

## Logs desde el Frontend

Agrega esto en tu código Next.js para correlacionar:

```typescript
const handleSubmit = async () => {
  const requestId = Date.now()
  console.log(`🚀 [${requestId}] Sending request to API`)
  console.log(`  URL: ${API_URL}/process`)
  console.log(`  File:`, file.name)
  
  try {
    const response = await fetch(`${API_URL}/process`, {
      method: 'POST',
      body: formData
    })
    
    console.log(`✅ [${requestId}] Response received:`, response.status)
    const data = await response.json()
    console.log(`  Data:`, data)
    
  } catch (error) {
    console.error(`❌ [${requestId}] Error:`, error)
  }
}
```

---

## Comando Rápido de Debugging

```bash
# Ver logs en tiempo real filtrando solo errores
railway logs --follow | grep -E "(❌|ERROR|Exception)"

# Ver requests POST
railway logs | grep "POST"

# Ver CORS issues
railway logs | grep "Origin"

# Ver últimos 50 logs
railway logs -n 50
```

---

## Checklist de Debugging

- [ ] API está corriendo (railway status)
- [ ] Health check responde: `curl https://tu-api.railway.app/health`
- [ ] Logs muestran startup exitoso
- [ ] FRONTEND_URL está configurado en Railway
- [ ] Frontend usa la URL correcta (`NEXT_PUBLIC_API_URL`)
- [ ] No hay errores de Tesseract en logs
- [ ] Requests aparecen en logs con `📨 INCOMING REQUEST`
- [ ] Response codes son 200 (no 400/500)

---

## Contacto para Soporte

Si los logs muestran algo inesperado, abre un issue con:
1. Copia de los logs (últimas 50 líneas)
2. Código del frontend que hace la llamada
3. Variables de entorno (sin secretos)
