from fastapi.testclient import TestClient

from app.main import app
from app.modules.ai.ai_log_store import ai_invocation_log_store


client = TestClient(app)


def test_ai_status_response_has_required_fields():
    response = client.get("/api/ai/status")

    assert response.status_code == 200

    data = response.json()

    assert data["ok"] is True
    assert "ai_mode" in data
    assert "openai_enabled" in data
    assert "model" in data
    assert "use_openai_analysis" in data
    assert "max_output_tokens" in data


def test_ai_analyze_uses_mock_provider_during_pytest_without_openai_cost():
    ai_invocation_log_store.reset_logs()

    response = client.post(
        "/api/ai/analyze",
        json={
            "message": "Hola quiero 50 frascos de miel de maguey para cafeteria",
            "channel": "web",
            "customer_id": "cliente_demo",
            "local_product": "miel_maguey",
            "local_quantity": 50,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["provider"] == "mock"
    assert data["intent"] == "cotizacion_mayoreo"
    assert data["product"] == "miel_maguey"
    assert data["quantity"] == 50


def test_ai_logs_are_created_for_analyze_calls():
    ai_invocation_log_store.reset_logs()

    response = client.post(
        "/api/ai/analyze",
        json={
            "message": "Hola quiero 50 frascos de miel de maguey para cafeteria",
            "channel": "web",
            "customer_id": "cliente_demo",
            "request_id": "req_test_ai_logs",
            "local_product": "miel_maguey",
            "local_quantity": 50,
        },
    )

    assert response.status_code == 200

    logs_response = client.get("/api/ai/logs")

    assert logs_response.status_code == 200

    logs = logs_response.json()

    assert len(logs) >= 1
    assert logs[0]["operation"] == "analysis"
    assert logs[0]["provider"] == "mock"
    assert logs[0]["success"] is True


def test_ai_logs_reset_endpoint():
    ai_invocation_log_store.reset_logs()

    client.post(
        "/api/ai/analyze",
        json={
            "message": "Hola quiero 50 frascos de miel de maguey para cafeteria",
            "channel": "web",
            "customer_id": "cliente_demo",
            "local_product": "miel_maguey",
            "local_quantity": 50,
        },
    )

    logs_before = client.get("/api/ai/logs").json()
    assert len(logs_before) >= 1

    reset_response = client.post("/api/ai/logs/reset")
    assert reset_response.status_code == 200

    logs_after = client.get("/api/ai/logs").json()
    assert logs_after == []


def test_ai_smoke_test_does_not_use_openai_during_pytest():
    ai_invocation_log_store.reset_logs()

    response = client.post("/api/ai/smoke-test")

    assert response.status_code == 200

    data = response.json()

    assert data["provider"] == "mock"
    assert data["intent"] == "cotizacion_mayoreo"

    logs = client.get("/api/ai/logs").json()

    assert len(logs) >= 1
    assert logs[0]["operation"] == "smoke_test"
