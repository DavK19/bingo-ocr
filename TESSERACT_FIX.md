# 🔧 Solución: Tesseract no encontrado en Railway

## El Problema

```
Error OCR (500): {"detail":"Tesseract no encontrado: asegúrate de que esté instalado y en PATH"}
```

Esto significa que Railway no está instalando Tesseract correctamente.

---

## ✅ Solución Rápida

### Paso 1: Verificar archivos de configuración

Asegúrate de que estos archivos existen y están correctos:

**`nixpacks.toml`**
```toml
[phases.setup]
nixPkgs = ["tesseract", "python39"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[start]
cmd = "python -m uvicorn src.api:app --host 0.0.0.0 --port $PORT"
```

**`Procfile`** (alternativo si nixpacks no funciona)
```
web: python -m uvicorn src.api:app --host 0.0.0.0 --port $PORT
```

### Paso 2: Desplegar cambios

```bash
git add .
git commit -m "Fix tesseract configuration"
git push
```

### Paso 3: Verificar deployment en Railway

Una vez desplegado, revisa los logs:

```bash
railway logs --follow
```

Deberías ver al inicio:

```
🚀 BINGO OCR API STARTING
  Tesseract: ✅ Available
  Path: /usr/bin/tesseract
✅ API READY TO ACCEPT REQUESTS
```

### Paso 4: Probar el endpoint de health

```bash
curl https://tu-api.railway.app/health
```

Respuesta esperada:
```json
{
  "status": "healthy",
  "tesseract": {
    "status": "available",
    "path": "/usr/bin/tesseract"
  }
}
```

---

## 🔍 Si el problema persiste

### Opción A: Usar Dockerfile en lugar de Nixpacks

Crea `Dockerfile` en la raíz:

```dockerfile
FROM python:3.9-slim

# Instalar Tesseract y dependencias
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-spa \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["python", "-m", "uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

Luego en Railway:
1. Settings → Deploy → Builder
2. Cambiar de "Nixpacks" a "Dockerfile"
3. Redeploy

### Opción B: Forzar rebuild completo

En Railway Dashboard:
1. Deployments → Botón de 3 puntos
2. "Redeploy" o "Restart"
3. Espera a que termine el build completo

### Opción C: Verificar Railway Service

Algunas veces Railway usa un builder antiguo. Intenta:

```bash
railway service
```

Y verifica que el servicio esté usando la configuración correcta.

---

## 🧪 Testing Local

Para verificar que el código funciona localmente:

```bash
# Windows (asumiendo Tesseract instalado)
python -m uvicorn src.api:app --reload --port 8000

# Probar health
curl http://localhost:8000/health
```

Deberías ver:
```json
{
  "status": "healthy",
  "tesseract": {
    "status": "available",
    "path": "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
  }
}
```

---

## 📊 Cómo Verificar que Tesseract está Instalado en Railway

En los logs de startup, busca:

**✅ Correcto:**
```
✅ Tesseract encontrado en PATH
  Version: 5.3.0

🚀 BINGO OCR API STARTING
  Tesseract: ✅ Available
    Path: /usr/bin/tesseract
✅ API READY TO ACCEPT REQUESTS
```

**❌ Incorrecto:**
```
❌ Tesseract no encontrado en ninguna ruta común
  Rutas buscadas:
    - /usr/bin/tesseract
    - /usr/local/bin/tesseract
    ...

⚠️ API STARTED BUT TESSERACT NOT AVAILABLE
   OCR requests will fail until Tesseract is installed
```

---

## 🚨 Errores Comunes

### Error 1: "nixPkgs not found"
**Solución**: Usar Dockerfile en lugar de nixpacks.toml

### Error 2: "Command not found: uvicorn"
**Solución**: Usar `python -m uvicorn` en lugar de solo `uvicorn`

### Error 3: Build exitoso pero Tesseract no funciona
**Solución**: Verificar que el start command incluye `python -m`

---

## 📞 Soporte

Si después de estos pasos sigue sin funcionar:

1. **Copia los logs de startup completos**
   ```bash
   railway logs -n 100 > logs.txt
   ```

2. **Verifica la respuesta del health check**
   ```bash
   curl https://tu-api.railway.app/health | jq
   ```

3. **Comparte ambos outputs** para diagnóstico más profundo

---

## ✅ Checklist Final

- [ ] `nixpacks.toml` tiene `nixPkgs = ["tesseract", "python39"]`
- [ ] Start command usa `python -m uvicorn`
- [ ] Código actualizado con detección automática de Tesseract
- [ ] Deployment completo (no solo restart)
- [ ] Logs muestran "✅ Tesseract: Available"
- [ ] `/health` endpoint muestra `tesseract.status: "available"`
- [ ] Test de procesamiento funciona

---

_Última actualización: 2025-11-06_
