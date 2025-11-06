from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
from .processor import process_image
import tempfile

app = FastAPI(
    title="Bingo OCR API",
    description="API para extraer números de cartones de bingo usando OCR",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js local
        "http://localhost:3001",  # Alternativo
        "https://tu-frontend.vercel.app",  # Tu dominio de producción
        "*"  # ⚠️ Solo para desarrollo, en producción especifica dominios
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Permite GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],  # Permite todos los headers
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Bingo OCR API",
        "version": "1.0.0",
        "endpoints": {
            "/process": "POST - Procesar imagen de cartón de bingo",
            "/health": "GET - Verificar estado del servicio"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/process")
async def process_bingo_card(
    file: UploadFile = File(...),
    save_grid: bool = False
):
    """
    Procesa una imagen de cartón de bingo y extrae los números.
    
    Args:
        file: Archivo de imagen del cartón de bingo
        save_grid: Si es True, devuelve también las imágenes con cuadrícula
    
    Returns:
        JSON con los números detectados y opcionalmente las URLs de las imágenes
    """
    # Validar tipo de archivo
    allowed_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Formato de archivo no permitido. Use: {', '.join(allowed_extensions)}"
        )
    
    # Crear directorio temporal para procesar la imagen
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Guardar archivo subido temporalmente
        temp_input_path = os.path.join(tmp_dir, f"input{file_ext}")
        
        try:
            with open(temp_input_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error guardando archivo: {str(e)}")
        
        # Procesar imagen
        try:
            save_grid_path = None
            if save_grid:
                save_grid_path = os.path.join(tmp_dir, "grid.png")
            
            numeros = process_image(
                temp_input_path,
                grid=(5, 5),
                save_grid_path=save_grid_path
            )
            
            response = {
                "success": True,
                "grid": numeros,
                "dimensions": {
                    "rows": len(numeros),
                    "cols": len(numeros[0]) if numeros else 0
                }
            }
            
            # Si se solicitó guardar la cuadrícula, incluir información de los archivos
            if save_grid and save_grid_path and os.path.exists(save_grid_path):
                base, ext = os.path.splitext(save_grid_path)
                bw_path = f"{base}_bw{ext}"
                
                response["images"] = {
                    "grid_available": os.path.exists(save_grid_path),
                    "bw_available": os.path.exists(bw_path)
                }
            
            return JSONResponse(content=response)
            
        except FileNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error procesando imagen: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("api:app", host="0.0.0.0", port=port, reload=False)