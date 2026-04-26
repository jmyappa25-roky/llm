from fastapi.testclient import TestClient

from app.main import app
from app.modules.ai.ai_log_store import ai_invocation_log_store
from app.modules.audit.audit_store import audit_event_store
from app.modules.tools.internal_store import internal_store


client = TestClient(app)


def test_audit_events_are_created_after_chat_operations():
    internal_store.reset()
    audit_event_store.reset_events()
    ai_invocation_log_store.reset_logs()

    response = client.post(
        "/api/chat",
        json={
            "channel": "web",
            "customer_id": "cliente_metricas",
            "message": "Hola quiero 50 frascos de miel de maguey presentacion 500 ml para CDMX el lunes, necesito factura, mi telefono 5573896566",
        },
    )

    assert response.status_code == 200

    audit_response = client.get("/api/audit/events")

    assert audit_response.status_code == 200

    events = audit_response.json()
    event_types = [event["event_type"] for event in events]

    assert "conversation_saved" in event_types
    assert "message_saved" in event_types
    assert "lead_created" in event_types
    assert "quote_draft_created" in event_types


def test_metrics_summary_counts_operational_records():
    internal_store.reset()
    audit_event_store.reset_events()
    ai_invocation_log_store.reset_logs()

    client.post(
        "/api/chat",
        json={
            "channel": "web",
            "customer_id": "cliente_metricas",
            "message": "Hola quiero 50 frascos de miel de maguey presentacion 500 ml para CDMX el lunes, necesito factura, mi telefono 5573896566",
        },
    )

    response = client.get("/api/metrics/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["ok"] is True
    assert data["operational"]["conversations"] == 1
    assert data["operational"]["messages"] == 2
    assert data["operational"]["leads"] == 1
    assert data["operational"]["quote_drafts"] == 1
    assert data["operational"]["audit_events"] >= 4


def test_metrics_summary_counts_ai_logs():
    internal_store.reset()
    audit_event_store.reset_events()
    ai_invocation_log_store.reset_logs()

    response = client.post(
        "/api/ai/analyze",
        json={
            "message": "Hola quiero 50 frascos de miel de maguey para cafeteria",
            "channel": "web",
            "customer_id": "cliente_metricas_ai",
            "request_id": "req_metricas_ai",
            "local_product": "miel_maguey",
            "local_quantity": 50,
        },
    )

    assert response.status_code == 200

    metrics_response = client.get("/api/metrics/summary")

    assert metrics_response.status_code == 200

    data = metrics_response.json()

    assert data["ai"]["total_invocations"] == 1
    assert data["ai"]["successful_invocations"] == 1
    assert data["ai"]["failed_invocations"] == 0
    assert data["ai"]["provider_counts"]["mock"] == 1
    assert data["ai"]["operation_counts"]["analysis"] == 1
