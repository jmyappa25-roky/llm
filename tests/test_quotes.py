from fastapi.testclient import TestClient

from app.main import app
from app.modules.ai.ai_log_store import ai_invocation_log_store
from app.modules.audit.audit_store import audit_event_store
from app.modules.tools.internal_store import internal_store


client = TestClient(app)


def reset_all():
    internal_store.reset()
    audit_event_store.reset_events()
    ai_invocation_log_store.reset_logs()


def create_quote_draft() -> str:
    response = client.post(
        "/api/chat",
        json={
            "channel": "web",
            "customer_id": "cliente_quote",
            "message": "Hola quiero 50 frascos de miel de maguey presentacion 500 ml para CDMX el lunes, necesito factura, mi telefono 5573896566",
        },
    )

    assert response.status_code == 200

    quote_drafts = client.get("/api/admin/quote-drafts").json()

    assert len(quote_drafts) == 1

    return quote_drafts[0]["id"]


def test_quote_preview_calculation():
    response = client.get("/api/quotes/preview/miel_maguey/50")

    assert response.status_code == 200

    data = response.json()

    assert data["product_id"] == "miel_maguey"
    assert data["quantity"] == 50
    assert data["unit_price_mxn"] == 145.0
    assert data["subtotal_mxn"] == 7250.0
    assert data["discount_percent"] == 10.0
    assert data["discount_mxn"] == 725.0
    assert data["shipping_mxn"] == 0.0
    assert data["total_mxn"] == 6525.0


def test_create_quote_from_draft():
    reset_all()

    quote_draft_id = create_quote_draft()

    response = client.post(f"/api/quotes/from-draft/{quote_draft_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["ok"] is True
    assert data["quote"]["quote_draft_id"] == quote_draft_id
    assert data["quote"]["product_id"] == "miel_maguey"
    assert data["quote"]["quantity"] == 50
    assert data["quote"]["status"] == "draft"
    assert data["quote"]["total_mxn"] == 6525.0

    quotes = client.get("/api/quotes").json()

    assert len(quotes) == 1


def test_create_quote_from_missing_draft_returns_404():
    reset_all()

    response = client.post("/api/quotes/from-draft/quote_draft_inexistente")

    assert response.status_code == 404

    data = response.json()

    assert data["ok"] is False
    assert data["error"]["code"] == "QUOTE_DRAFT_NOT_FOUND"


def test_approve_and_send_quote():
    reset_all()

    quote_draft_id = create_quote_draft()
    create_response = client.post(f"/api/quotes/from-draft/{quote_draft_id}")

    assert create_response.status_code == 200

    quote_id = create_response.json()["quote"]["id"]

    approve_response = client.patch(f"/api/quotes/{quote_id}/approve")
    assert approve_response.status_code == 200

    approved = approve_response.json()

    assert approved["old_status"] == "draft"
    assert approved["new_status"] == "approved"
    assert approved["quote"]["status"] == "approved"

    send_response = client.patch(f"/api/quotes/{quote_id}/send")
    assert send_response.status_code == 200

    sent = send_response.json()

    assert sent["old_status"] == "approved"
    assert sent["new_status"] == "sent"
    assert sent["quote"]["status"] == "sent"


def test_quote_creation_adds_metrics_and_audit():
    reset_all()

    quote_draft_id = create_quote_draft()
    response = client.post(f"/api/quotes/from-draft/{quote_draft_id}")

    assert response.status_code == 200

    metrics = client.get("/api/metrics/summary").json()

    assert metrics["operational"]["quotes"] == 1

    audit_events = client.get("/api/audit/events").json()
    event_types = [event["event_type"] for event in audit_events]

    assert "quote_created" in event_types
