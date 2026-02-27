from fastapi.testclient import TestClient
from chatapp.main import app

client = TestClient(app)
def teste_health():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}