from fastapi.testclient import TestClient
from fastapi import status
from api.main import app
client = TestClient(app=app)

def test_health():
    response = client.get("/api/health/live")
    assert response.status_code == status.HTTP_200_OK
