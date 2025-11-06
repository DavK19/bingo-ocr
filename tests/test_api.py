from fastapi.testclient import TestClient
from src.api import app
import io
from PIL import Image

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_process_invalid_file():
    response = client.post(
        "/process",
        files={"file": ("test.txt", b"not an image", "text/plain")}
    )
    assert response.status_code == 400