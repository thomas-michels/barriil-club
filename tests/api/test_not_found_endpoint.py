import os
from fastapi.testclient import TestClient

os.environ["DATABASE_HOST"] = "mongomock://localhost"

from app.application import app


def test_nonexistent_endpoint_returns_not_found_message():
    client = TestClient(app)
    response = client.get("/api/nonexistent")
    assert response.status_code == 404
    assert response.json() == {"message": "Não encontrado"}
