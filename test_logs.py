"""
Script para probar los logs de la API localmente
"""
import requests
import time

API_URL = "http://localhost:8000"

def test_health():
    print("=" * 50)
    print("🧪 Testing /health endpoint")
    print("=" * 50)
    try:
        response = requests.get(f"{API_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print("✅ Health check passed!\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")

def test_root():
    print("=" * 50)
    print("🧪 Testing / endpoint")
    print("=" * 50)
    try:
        response = requests.get(f"{API_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print("✅ Root endpoint passed!\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")

def test_process_no_file():
    print("=" * 50)
    print("🧪 Testing /process without file (should fail)")
    print("=" * 50)
    try:
        response = requests.post(f"{API_URL}/process")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Expected error: {e}\n")

def test_cors():
    print("=" * 50)
    print("🧪 Testing CORS headers")
    print("=" * 50)
    try:
        headers = {
            "Origin": "http://localhost:3000"
        }
        response = requests.get(f"{API_URL}/health", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Access-Control-Allow-Origin: {response.headers.get('access-control-allow-origin')}")
        print(f"Access-Control-Allow-Methods: {response.headers.get('access-control-allow-methods')}")
        print("✅ CORS test passed!\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")

if __name__ == "__main__":
    print("\n")
    print("🚀 INICIANDO TESTS DE LA API")
    print("=" * 50)
    print("Asegúrate de que la API esté corriendo en http://localhost:8000")
    print("Ejecuta: python -m uvicorn src.api:app --reload --port 8000")
    print("=" * 50)
    
    input("\nPresiona ENTER para continuar...")
    
    test_health()
    time.sleep(1)
    
    test_root()
    time.sleep(1)
    
    test_cors()
    time.sleep(1)
    
    test_process_no_file()
    
    print("\n" + "=" * 50)
    print("✅ TESTS COMPLETADOS")
    print("=" * 50)
    print("\nRevisa la terminal donde corre la API para ver los logs detallados.")
    print("Deberías ver:")
    print("  - 📨 Logs de requests entrantes")
    print("  - ✅ Logs de endpoints")
    print("  - 📤 Logs de responses")
    print("=" * 50)
