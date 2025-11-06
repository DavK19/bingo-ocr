"""
Script para verificar que Tesseract está correctamente configurado
"""
import sys
import os
import subprocess

def check_tesseract():
    print("=" * 60)
    print("🔍 VERIFICANDO TESSERACT")
    print("=" * 60)
    
    # Rutas comunes
    tesseract_paths = [
        '/usr/bin/tesseract',
        '/usr/local/bin/tesseract',
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        '/opt/homebrew/bin/tesseract',
    ]
    
    print("\n1️⃣ Buscando Tesseract en PATH...")
    try:
        result = subprocess.run(
            ['tesseract', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("   ✅ Tesseract encontrado en PATH")
            print(f"   📍 Versión: {result.stdout.split()[1] if result.stdout else 'unknown'}")
            return True
        else:
            print("   ❌ Tesseract no responde correctamente")
    except FileNotFoundError:
        print("   ❌ Tesseract no encontrado en PATH")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n2️⃣ Buscando en rutas comunes...")
    for path in tesseract_paths:
        print(f"   Verificando: {path}")
        if os.path.exists(path):
            print(f"   ✅ Encontrado: {path}")
            try:
                result = subprocess.run(
                    [path, '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                print(f"   📍 Versión: {result.stdout.split()[1] if result.stdout else 'unknown'}")
                return True
            except Exception as e:
                print(f"   ⚠️ Archivo existe pero no responde: {e}")
        else:
            print(f"   ❌ No encontrado")
    
    return False

def test_pytesseract():
    print("\n3️⃣ Probando pytesseract...")
    try:
        import pytesseract
        from PIL import Image
        import numpy as np
        
        # Crear imagen de prueba simple con texto
        print("   Creando imagen de prueba...")
        img = Image.new('RGB', (200, 100), color='white')
        
        # Intentar OCR
        print("   Ejecutando OCR...")
        text = pytesseract.image_to_string(img)
        print("   ✅ pytesseract funciona correctamente")
        return True
    except pytesseract.pytesseract.TesseractNotFoundError as e:
        print(f"   ❌ pytesseract no puede encontrar Tesseract: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error en pytesseract: {e}")
        return False

def check_dependencies():
    print("\n4️⃣ Verificando dependencias Python...")
    required = ['pytesseract', 'opencv-python', 'PIL', 'numpy']
    
    for package in required:
        try:
            if package == 'opencv-python':
                import cv2
                print(f"   ✅ opencv-python: {cv2.__version__}")
            elif package == 'PIL':
                from PIL import Image
                print(f"   ✅ Pillow: {Image.__version__}")
            elif package == 'pytesseract':
                import pytesseract
                print(f"   ✅ pytesseract instalado")
            elif package == 'numpy':
                import numpy as np
                print(f"   ✅ numpy: {np.__version__}")
        except ImportError:
            print(f"   ❌ {package} no instalado")
            return False
    
    return True

def main():
    print("\n")
    print("🚀 DIAGNÓSTICO DE TESSERACT PARA BINGO OCR")
    print("=" * 60)
    
    tesseract_ok = check_tesseract()
    deps_ok = check_dependencies()
    
    if tesseract_ok and deps_ok:
        pytesseract_ok = test_pytesseract()
    else:
        pytesseract_ok = False
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN")
    print("=" * 60)
    print(f"  Tesseract instalado: {'✅' if tesseract_ok else '❌'}")
    print(f"  Dependencias Python: {'✅' if deps_ok else '❌'}")
    print(f"  pytesseract funcional: {'✅' if pytesseract_ok else '❌'}")
    print("=" * 60)
    
    if tesseract_ok and deps_ok and pytesseract_ok:
        print("\n✅ TODO ESTÁ LISTO PARA USAR BINGO OCR API")
        print("\nPuedes iniciar el servidor con:")
        print("  python -m uvicorn src.api:app --reload --port 8000")
    else:
        print("\n❌ CONFIGURACIÓN INCOMPLETA")
        if not tesseract_ok:
            print("\n🔧 Instalar Tesseract:")
            print("  Windows: https://github.com/UB-Mannheim/tesseract/wiki")
            print("  Linux: sudo apt-get install tesseract-ocr")
            print("  macOS: brew install tesseract")
        
        if not deps_ok:
            print("\n🔧 Instalar dependencias Python:")
            print("  pip install -r requirements.txt")
    
    print("\n")

if __name__ == "__main__":
    main()
