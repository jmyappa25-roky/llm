from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check_ok():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["ok"] is True
    assert data["ai_mode"] == "mock"
    assert data["openai_enabled"] is False
