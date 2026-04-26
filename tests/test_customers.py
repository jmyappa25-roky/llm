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


def create_customer_chat(customer_id: str = "cliente_crm"):
    return client.post(
        "/api/chat",
        json={
            "channel": "web",
            "customer_id": customer_id,
            "message": "Hola quiero 50 frascos de miel de maguey presentacion 500 ml para CDMX el lunes, necesito factura, mi telefono 5573896566 y correo ventas@cafeteria.com",
        },
    )


def test_customer_is_created_from_chat():
    reset_all()

    response = create_customer_chat()

    assert response.status_code == 200

    data = response.json()
    operation_names = [operation["name"] for operation in data["operations"]]

    assert "upsert_customer" in operation_names

    customers_response = client.get("/api/customers")
    assert customers_response.status_code == 200

    customers = customers_response.json()

    assert len(customers) == 1
    assert customers[0]["id"] == "cliente_crm"
    assert customers[0]["phone"] == "5573896566"
    assert customers[0]["email"] == "ventas@cafeteria.com"
    assert customers[0]["last_intent"] == "cotizacion_mayoreo"
    assert customers[0]["last_product_id"] == "miel_maguey"
    assert customers[0]["last_quantity"] == 50


def test_customer_can_be_updated_manually():
    reset_all()

    create_customer_chat()

    update_response = client.patch(
        "/api/customers/cliente_crm",
        json={
            "name": "Cafeteria Demo",
            "customer_type": "cafeteria",
            "status": "active",
            "notes": "Cliente interesado en mayoreo.",
        },
    )

    assert update_response.status_code == 200

    data = update_response.json()

    assert data["ok"] is True
    assert data["customer"]["name"] == "Cafeteria Demo"
    assert data["customer"]["customer_type"] == "cafeteria"
    assert data["customer"]["notes"] == "Cliente interesado en mayoreo."

    get_response = client.get("/api/customers/cliente_crm")
    assert get_response.status_code == 200

    customer = get_response.json()
    assert customer["name"] == "Cafeteria Demo"


def test_customer_commercial_summary():
    reset_all()

    create_customer_chat("cliente_summary")

    drafts = client.get("/api/admin/quote-drafts").json()
    assert len(drafts) == 1

    quote_response = client.post(f"/api/quotes/from-draft/{drafts[0]['id']}")
    assert quote_response.status_code == 200

    quote_id = quote_response.json()["quote"]["id"]

    client.patch(f"/api/quotes/{quote_id}/approve")
    client.patch(f"/api/quotes/{quote_id}/send")

    summary_response = client.get("/api/customers/cliente_summary/commercial-summary")

    assert summary_response.status_code == 200

    summary = summary_response.json()

    assert summary["customer_id"] == "cliente_summary"
    assert summary["conversations_count"] == 1
    assert summary["messages_count"] == 2
    assert summary["leads_count"] == 1
    assert summary["quotes_count"] == 1
    assert summary["sent_quotes_count"] == 1
    assert summary["total_quoted_mxn"] == 6525.0


def test_customers_metrics_count():
    reset_all()

    create_customer_chat("cliente_metric_crm")

    metrics_response = client.get("/api/metrics/summary")

    assert metrics_response.status_code == 200

    metrics = metrics_response.json()

    assert metrics["operational"]["customers"] == 1
    assert metrics["operational"]["conversations"] == 1
    assert metrics["operational"]["messages"] == 2


def test_customer_not_found_returns_404():
    reset_all()

    response = client.get("/api/customers/no_existe")

    assert response.status_code == 404

    data = response.json()

    assert data["ok"] is False
    assert data["error"]["code"] == "CUSTOMER_NOT_FOUND"
