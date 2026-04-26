from fastapi.testclient import TestClient

from app.main import app
from app.modules.tools.internal_store import internal_store


client = TestClient(app)


def test_chat_complete_wholesale_creates_lead_and_quote_draft_records():
    internal_store.reset()

    response = client.post(
        "/api/chat",
        json={
            "channel": "web",
            "customer_id": "cliente_demo",
            "message": "Hola quiero 50 frascos de miel de maguey presentacion 500 ml para CDMX el lunes, necesito factura, mi telefono 5573896566",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["decision"]["action"] == "crear_borrador_cotizacion"

    operation_names = [operation["name"] for operation in data["operations"]]

    assert "save_conversation" in operation_names
    assert "save_user_message" in operation_names
    assert "save_assistant_message" in operation_names
    assert "create_lead" in operation_names
    assert "create_quote_draft" in operation_names

    leads_response = client.get("/api/internal/leads")
    quotes_response = client.get("/api/internal/quote-drafts")
    messages_response = client.get("/api/internal/messages")

    assert leads_response.status_code == 200
    assert quotes_response.status_code == 200
    assert messages_response.status_code == 200

    leads = leads_response.json()
    quotes = quotes_response.json()
    messages = messages_response.json()

    assert len(leads) == 1
    assert len(quotes) == 1
    assert len(messages) == 2

    assert leads[0]["product_id"] == "miel_maguey"
    assert leads[0]["quantity"] == 50
    assert leads[0]["status"] == "qualified"

    assert quotes[0]["product_id"] == "miel_maguey"
    assert quotes[0]["quantity"] == 50
    assert quotes[0]["status"] == "draft"


def test_chat_reclamo_creates_ticket_record():
    internal_store.reset()

    response = client.post(
        "/api/chat",
        json={
            "channel": "web",
            "customer_id": "cliente_reclamo",
            "message": "Estoy molesto porque mi pedido no llego",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["analysis"]["intent"] == "reclamo"
    assert data["decision"]["action"] == "escalar_humano"
    assert data["decision"]["created_ticket"] is True

    operation_names = [operation["name"] for operation in data["operations"]]

    assert "create_ticket" in operation_names

    tickets_response = client.get("/api/internal/tickets")

    assert tickets_response.status_code == 200

    tickets = tickets_response.json()

    assert len(tickets) == 1
    assert tickets[0]["reason"] == "reclamo"
    assert tickets[0]["status"] == "open"


def test_internal_reset_endpoint_clears_memory():
    internal_store.reset()

    client.post(
        "/api/chat",
        json={
            "channel": "web",
            "customer_id": "cliente_demo",
            "message": "Hola quiero 50 frascos de miel de maguey presentacion 500 ml para CDMX el lunes, necesito factura, mi telefono 5573896566",
        },
    )

    leads_before = client.get("/api/internal/leads").json()
    assert len(leads_before) == 1

    reset_response = client.post("/api/internal/reset")
    assert reset_response.status_code == 200

    leads_after = client.get("/api/internal/leads").json()
    messages_after = client.get("/api/internal/messages").json()
    quotes_after = client.get("/api/internal/quote-drafts").json()

    assert leads_after == []
    assert messages_after == []
    assert quotes_after == []
