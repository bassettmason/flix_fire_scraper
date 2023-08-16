from fastapi.testclient import TestClient
from fastapi import status
from api.main import app
client = TestClient(app=app)

def test_scrape_flixlist_route():
    response = client.get("/api/scrape/flixlist/")
    assert response.status_code == status.HTTP_200_OK
