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


def create_complete_wholesale_chat(customer_id: str = "cliente_admin"):
    return client.post(
        "/api/chat",
        json={
            "channel": "web",
            "customer_id": customer_id,
            "message": "Hola quiero 50 frascos de miel de maguey presentacion 500 ml para CDMX el lunes, necesito factura, mi telefono 5573896566",
        },
    )


def test_admin_dashboard_and_lists():
    reset_all()

    response = create_complete_wholesale_chat()

    assert response.status_code == 200

    dashboard_response = client.get("/api/admin/dashboard")
    assert dashboard_response.status_code == 200

    dashboard = dashboard_response.json()

    assert dashboard["ok"] is True
    assert dashboard["metrics"]["operational"]["conversations"] == 1
    assert dashboard["metrics"]["operational"]["messages"] == 2
    assert dashboard["metrics"]["operational"]["leads"] == 1
    assert dashboard["metrics"]["operational"]["quote_drafts"] == 1

    conversations = client.get("/api/admin/conversations").json()
    leads = client.get("/api/admin/leads").json()
    quote_drafts = client.get("/api/admin/quote-drafts").json()
    messages = client.get("/api/admin/messages").json()

    assert len(conversations) == 1
    assert len(leads) == 1
    assert len(quote_drafts) == 1
    assert len(messages) == 2

    assert leads[0]["product_id"] == "miel_maguey"
    assert quote_drafts[0]["status"] == "draft"


def test_admin_customer_timeline():
    reset_all()

    response = create_complete_wholesale_chat("cliente_timeline")

    assert response.status_code == 200

    timeline_response = client.get("/api/admin/customers/cliente_timeline/timeline")

    assert timeline_response.status_code == 200

    timeline = timeline_response.json()
    types = [item["type"] for item in timeline]

    assert "message" in types
    assert "lead" in types
    assert "quote_draft" in types
    assert "audit_event" in types


def test_admin_update_ticket_status():
    reset_all()

    response = client.post(
        "/api/chat",
        json={
            "channel": "web",
            "customer_id": "cliente_ticket_admin",
            "message": "Estoy molesto porque mi pedido no llego",
        },
    )

    assert response.status_code == 200

    tickets = client.get("/api/admin/tickets").json()

    assert len(tickets) == 1
    assert tickets[0]["status"] == "open"

    ticket_id = tickets[0]["id"]

    update_response = client.patch(
        f"/api/admin/tickets/{ticket_id}/status",
        json={"status": "in_progress"},
    )

    assert update_response.status_code == 200

    updated = update_response.json()

    assert updated["ok"] is True
    assert updated["entity_type"] == "ticket"
    assert updated["old_status"] == "open"
    assert updated["new_status"] == "in_progress"

    tickets_after = client.get("/api/admin/tickets").json()

    assert tickets_after[0]["status"] == "in_progress"


def test_admin_update_lead_and_quote_status():
    reset_all()

    response = create_complete_wholesale_chat("cliente_status_admin")

    assert response.status_code == 200

    leads = client.get("/api/admin/leads").json()
    quote_drafts = client.get("/api/admin/quote-drafts").json()

    assert len(leads) == 1
    assert len(quote_drafts) == 1

    lead_id = leads[0]["id"]
    quote_id = quote_drafts[0]["id"]

    lead_update = client.patch(
        f"/api/admin/leads/{lead_id}/status",
        json={"status": "contacted"},
    )

    quote_update = client.patch(
        f"/api/admin/quote-drafts/{quote_id}/status",
        json={"status": "pending_review"},
    )

    assert lead_update.status_code == 200
    assert quote_update.status_code == 200

    assert lead_update.json()["new_status"] == "contacted"
    assert quote_update.json()["new_status"] == "pending_review"

    leads_after = client.get("/api/admin/leads").json()
    quote_drafts_after = client.get("/api/admin/quote-drafts").json()

    assert leads_after[0]["status"] == "contacted"
    assert quote_drafts_after[0]["status"] == "pending_review"
