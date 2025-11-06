from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
from .processor import process_image
import tempfile
import logging
from datetime import datetime
import traceback
import sys
import pytesseract
import subprocess

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configurar Tesseract automáticamente
def configure_tesseract():
    """Detecta y configura Tesseract en diferentes entornos"""
    tesseract_paths = [
        '/usr/bin/tesseract',  # Linux/Railway
        '/usr/local/bin/tesseract',  # Linux alternativo
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',  # Windows
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',  # Windows 32-bit
        '/opt/homebrew/bin/tesseract',  # macOS M1
        '/usr/local/Cellar/tesseract',  # macOS Intel
    ]
    
    # Intentar encontrar tesseract en PATH primero
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        if result.returncode == 0:
            logger.info(f"✅ Tesseract encontrado en PATH")
            logger.info(f"  Version: {result.stdout.split()[1] if result.stdout else 'unknown'}")
            return True
    except Exception as e:
        logger.warning(f"Tesseract no encontrado en PATH: {e}")
    
    # Buscar en rutas comunes
    for path in tesseract_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            logger.info(f"✅ Tesseract configurado en: {path}")
            try:
                result = subprocess.run([path, '--version'], 
                                      capture_output=True, 
                                      text=True, 
                                      timeout=5)
                logger.info(f"  Version: {result.stdout.split()[1] if result.stdout else 'unknown'}")
            except:
                pass
            return True
    
    logger.error("❌ Tesseract no encontrado en ninguna ruta común")
    logger.error("  Rutas buscadas:")
    for path in tesseract_paths:
        logger.error(f"    - {path}")
    return False

# Configurar Tesseract al iniciar
tesseract_available = configure_tesseract()

app = FastAPI(
    title="Bingo OCR API",
    description="API para extraer números de cartones de bingo usando OCR",
    version="1.0.0"
)

# Configuración de CORS mejorada
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
]

# Agregar dominio de producción si existe
if os.getenv("FRONTEND_URL"):
    frontend_url = os.getenv("FRONTEND_URL")
    origins.append(frontend_url)
    logger.info(f"✅ Added FRONTEND_URL to CORS: {frontend_url}")

# En desarrollo, permitir todo
if os.getenv("ENVIRONMENT") != "production":
    origins.append("*")
    logger.info("⚠️ CORS permitiendo todos los orígenes (desarrollo)")

logger.info(f"🌐 CORS configurado para: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Middleware para logging de todas las requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
    
    # Log detallado del request entrante
    logger.info(f"📨 [{request_id}] ===== INCOMING REQUEST =====")
    logger.info(f"  Method: {request.method}")
    logger.info(f"  URL: {request.url}")
    logger.info(f"  Path: {request.url.path}")
    logger.info(f"  Client: {request.client.host if request.client else 'Unknown'}:{request.client.port if request.client else 'Unknown'}")
    logger.info(f"  Origin: {request.headers.get('origin', 'NO ORIGIN HEADER')}")
    logger.info(f"  Referer: {request.headers.get('referer', 'NO REFERER')}")
    logger.info(f"  User-Agent: {request.headers.get('user-agent', 'NO USER-AGENT')}")
    logger.info(f"  Content-Type: {request.headers.get('content-type', 'NO CONTENT-TYPE')}")
    logger.info(f"  All Headers: {dict(request.headers)}")
    
    try:
        response = await call_next(request)
        
        # Log del response
        logger.info(f"📤 [{request_id}] ===== RESPONSE =====")
        logger.info(f"  Status: {response.status_code}")
        logger.info(f"  Headers: {dict(response.headers)}")
        
        return response
    except Exception as e:
        logger.error(f"❌ [{request_id}] ===== ERROR =====")
        logger.error(f"  Exception: {str(e)}")
        logger.error(f"  Type: {type(e).__name__}")
        logger.error(f"  Traceback:\n{traceback.format_exc()}")
        raise

# Log de startup
@app.on_event("startup")
async def startup_event():
    logger.info("=" * 50)
    logger.info("🚀 BINGO OCR API STARTING")
    logger.info("=" * 50)
    logger.info(f"  Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"  Port: {os.getenv('PORT', '8000')}")
    logger.info(f"  CORS Origins: {origins}")
    logger.info(f"  Python: {sys.version}")
    logger.info(f"  Tesseract: {'✅ Available' if tesseract_available else '❌ NOT FOUND'}")
    if tesseract_available:
        logger.info(f"    Path: {pytesseract.pytesseract.tesseract_cmd}")
    logger.info("=" * 50)
    if tesseract_available:
        logger.info("✅ API READY TO ACCEPT REQUESTS")
    else:
        logger.warning("⚠️ API STARTED BUT TESSERACT NOT AVAILABLE")
        logger.warning("   OCR requests will fail until Tesseract is installed")
    logger.info("=" * 50)

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Bingo OCR API shutting down...")

@app.get("/")
async def root(request: Request):
    logger.info("✅ Root endpoint accessed")
    logger.info(f"  Origin: {request.headers.get('origin', 'NO ORIGIN')}")
    return {
        "message": "Bingo OCR API",
        "version": "1.0.0",
        "status": "running",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "endpoints": {
            "/": "GET - Información de la API",
            "/health": "GET - Verificar estado del servicio",
            "/process": "POST - Procesar imagen de cartón de bingo",
            "/docs": "GET - Documentación interactiva",
            "/redoc": "GET - Documentación alternativa"
        }
    }

@app.get("/health")
async def health_check(request: Request):
    logger.info("❤️ Health check endpoint accessed")
    logger.info(f"  Origin: {request.headers.get('origin', 'NO ORIGIN')}")
    
    # Verificar estado de Tesseract
    tesseract_status = "available" if tesseract_available else "not_found"
    tesseract_path = pytesseract.pytesseract.tesseract_cmd if tesseract_available else None
    
    health_data = {
        "status": "healthy" if tesseract_available else "degraded",
        "service": "bingo-ocr-api",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "tesseract": {
            "status": tesseract_status,
            "path": tesseract_path
        }
    }
    logger.info(f"  Response: {health_data}")
    return health_data

@app.post("/process")
async def process_bingo_card(
    request: Request,
    file: UploadFile = File(...),
    rows: int = 5,
    cols: int = 5,
    save_grid: bool = False
):
    """
    Procesa una imagen de cartón de bingo y extrae los números.
    
    Args:
        file: Archivo de imagen del cartón de bingo
        rows: Número de filas (default: 5)
        cols: Número de columnas (default: 5)
        save_grid: Si es True, devuelve también las imágenes con cuadrícula
    
    Returns:
        JSON con los números detectados
    """
    start_time = datetime.now()
    request_id = start_time.strftime("%Y%m%d%H%M%S%f")
    
    logger.info(f"🎯 [{request_id}] ===== PROCESSING REQUEST =====")
    logger.info(f"  Filename: {file.filename}")
    logger.info(f"  Content-Type: {file.content_type}")
    logger.info(f"  Grid size: {rows}x{cols}")
    logger.info(f"  Save grid: {save_grid}")
    logger.info(f"  Origin: {request.headers.get('origin', 'NO ORIGIN')}")
    logger.info(f"  Tesseract available: {tesseract_available}")
    
    # Verificar que Tesseract está disponible
    if not tesseract_available:
        logger.error(f"❌ [{request_id}] Tesseract not available")
        raise HTTPException(
            status_code=503,
            detail="Tesseract OCR no está disponible. Contacta al administrador del sistema."
        )
    
    # Validar tipo de archivo
    allowed_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        logger.warning(f"⚠️ [{request_id}] Invalid file extension: {file_ext}")
        raise HTTPException(
            status_code=400,
            detail=f"Formato de archivo no permitido. Use: {', '.join(allowed_extensions)}"
        )
    
    logger.info(f"✅ [{request_id}] File extension valid: {file_ext}")
    
    # Validar dimensiones
    if rows < 1 or rows > 10 or cols < 1 or cols > 10:
        logger.warning(f"⚠️ [{request_id}] Invalid grid dimensions: {rows}x{cols}")
        raise HTTPException(
            status_code=400,
            detail="Las dimensiones del grid deben estar entre 1 y 10"
        )
    
    # Crear directorio temporal para procesar la imagen
    with tempfile.TemporaryDirectory() as tmp_dir:
        temp_input_path = os.path.join(tmp_dir, f"input{file_ext}")
        
        try:
            # Guardar archivo subido temporalmente
            logger.info(f"💾 [{request_id}] Saving uploaded file to: {temp_input_path}")
            with open(temp_input_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            file_size = os.path.getsize(temp_input_path)
            logger.info(f"✅ [{request_id}] File saved successfully. Size: {file_size} bytes")
            
        except Exception as e:
            logger.error(f"❌ [{request_id}] Error saving file: {str(e)}")
            logger.error(f"  Traceback:\n{traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Error guardando archivo: {str(e)}")
        
        # Procesar imagen
        try:
            logger.info(f"🔄 [{request_id}] Starting OCR processing...")
            
            save_grid_path = None
            if save_grid:
                save_grid_path = os.path.join(tmp_dir, "grid.png")
                logger.info(f"  Grid will be saved to: {save_grid_path}")
            
            numeros = process_image(
                temp_input_path,
                grid=(rows, cols),
                save_grid_path=save_grid_path
            )
            
            logger.info(f"✅ [{request_id}] OCR processing completed successfully")
            logger.info(f"  Detected grid:\n{numeros}")
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            response = {
                "success": True,
                "filename": file.filename,
                "grid": numeros,
                "dimensions": {
                    "rows": len(numeros),
                    "cols": len(numeros[0]) if numeros else 0
                },
                "processing_time_seconds": processing_time,
                "request_id": request_id
            }
            
            # Si se solicitó guardar la cuadrícula
            if save_grid and save_grid_path and os.path.exists(save_grid_path):
                base, ext = os.path.splitext(save_grid_path)
                bw_path = f"{base}_bw{ext}"
                
                response["images"] = {
                    "grid_available": os.path.exists(save_grid_path),
                    "bw_available": os.path.exists(bw_path)
                }
            
            logger.info(f"📊 [{request_id}] Response prepared. Processing time: {processing_time:.2f}s")
            return JSONResponse(content=response)
            
        except FileNotFoundError as e:
            logger.error(f"❌ [{request_id}] File not found: {str(e)}")
            raise HTTPException(status_code=404, detail=str(e))
        except RuntimeError as e:
            logger.error(f"❌ [{request_id}] Runtime error: {str(e)}")
            logger.error(f"  Traceback:\n{traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            logger.error(f"❌ [{request_id}] Unexpected error: {str(e)}")
            logger.error(f"  Type: {type(e).__name__}")
            logger.error(f"  Traceback:\n{traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Error procesando imagen: {str(e)}")

# Handler global de excepciones
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("=" * 50)
    logger.error("🔥 GLOBAL EXCEPTION HANDLER")
    logger.error("=" * 50)
    logger.error(f"  Exception: {str(exc)}")
    logger.error(f"  Type: {type(exc).__name__}")
    logger.error(f"  Request: {request.method} {request.url}")
    logger.error(f"  Origin: {request.headers.get('origin', 'NO ORIGIN')}")
    logger.error(f"  Traceback:\n{traceback.format_exc()}")
    logger.error("=" * 50)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": str(exc),
            "type": type(exc).__name__,
            "path": str(request.url),
            "method": request.method
        }
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"🚀 Starting uvicorn on port {port}")
    uvicorn.run(
        "src.api:app", 
        host="0.0.0.0", 
        port=port, 
        reload=False,
        log_level="info"
    )