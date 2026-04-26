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


def create_sent_quote() -> str:
    chat_response = client.post(
        "/api/chat",
        json={
            "channel": "web",
            "customer_id": "cliente_inventory",
            "message": "Hola quiero 50 frascos de miel de maguey presentacion 500 ml para CDMX el lunes, necesito factura, mi telefono 5573896566",
        },
    )
    assert chat_response.status_code == 200

    drafts = client.get("/api/admin/quote-drafts").json()
    assert len(drafts) == 1

    draft_id = drafts[0]["id"]

    quote_response = client.post(f"/api/quotes/from-draft/{draft_id}")
    assert quote_response.status_code == 200

    quote_id = quote_response.json()["quote"]["id"]

    approve_response = client.patch(f"/api/quotes/{quote_id}/approve")
    assert approve_response.status_code == 200

    send_response = client.patch(f"/api/quotes/{quote_id}/send")
    assert send_response.status_code == 200

    return quote_id


def test_inventory_adjustment_creates_item_and_movement():
    reset_all()

    response = client.post(
        "/api/inventory/adjust",
        json={
            "product_id": "miel_maguey",
            "quantity_delta": 100,
            "unit": "frasco",
            "notes": "Carga inicial de inventario.",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["ok"] is True
    assert data["item"]["product_id"] == "miel_maguey"
    assert data["item"]["available_quantity"] == 100
    assert data["item"]["reserved_quantity"] == 0
    assert data["movement"]["movement_type"] == "adjustment"
    assert data["movement"]["quantity"] == 100

    item_response = client.get("/api/inventory/miel_maguey")
    assert item_response.status_code == 200
    assert item_response.json()["available_quantity"] == 100


def test_inventory_reserve_from_quote_reduces_available_and_increases_reserved():
    reset_all()

    adjust_response = client.post(
        "/api/inventory/adjust",
        json={
            "product_id": "miel_maguey",
            "quantity_delta": 100,
            "unit": "frasco",
            "notes": "Stock inicial.",
        },
    )
    assert adjust_response.status_code == 200

    quote_id = create_sent_quote()

    reserve_response = client.post(f"/api/inventory/reserve-from-quote/{quote_id}")
    assert reserve_response.status_code == 200

    data = reserve_response.json()

    assert data["ok"] is True
    assert data["item"]["available_quantity"] == 50
    assert data["item"]["reserved_quantity"] == 50
    assert data["movement"]["movement_type"] == "reservation"
    assert data["movement"]["quantity"] == 50
    assert data["quote_id"] == quote_id


def test_inventory_reserve_from_quote_fails_when_stock_is_insufficient():
    reset_all()

    adjust_response = client.post(
        "/api/inventory/adjust",
        json={
            "product_id": "miel_maguey",
            "quantity_delta": 10,
            "unit": "frasco",
            "notes": "Stock insuficiente.",
        },
    )
    assert adjust_response.status_code == 200

    quote_id = create_sent_quote()

    reserve_response = client.post(f"/api/inventory/reserve-from-quote/{quote_id}")

    assert reserve_response.status_code == 409

    data = reserve_response.json()

    assert data["ok"] is False
    assert data["error"]["code"] == "INSUFFICIENT_INVENTORY"


def test_inventory_reservation_is_idempotent_for_same_quote():
    reset_all()

    client.post(
        "/api/inventory/adjust",
        json={
            "product_id": "miel_maguey",
            "quantity_delta": 100,
            "unit": "frasco",
            "notes": "Stock inicial.",
        },
    )

    quote_id = create_sent_quote()

    first_response = client.post(f"/api/inventory/reserve-from-quote/{quote_id}")
    second_response = client.post(f"/api/inventory/reserve-from-quote/{quote_id}")

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    first_data = first_response.json()
    second_data = second_response.json()

    assert first_data["item"]["available_quantity"] == 50
    assert first_data["item"]["reserved_quantity"] == 50

    assert second_data["item"]["available_quantity"] == 50
    assert second_data["item"]["reserved_quantity"] == 50
    assert "ya tenia inventario reservado" in second_data["message"]


def test_inventory_metrics_and_audit_events():
    reset_all()

    client.post(
        "/api/inventory/adjust",
        json={
            "product_id": "miel_maguey",
            "quantity_delta": 100,
            "unit": "frasco",
            "notes": "Stock inicial.",
        },
    )

    quote_id = create_sent_quote()
    client.post(f"/api/inventory/reserve-from-quote/{quote_id}")

    metrics = client.get("/api/metrics/summary").json()

    assert metrics["operational"]["inventory_items"] == 1
    assert metrics["operational"]["inventory_movements"] == 2

    audit_events = client.get("/api/audit/events").json()
    event_types = [event["event_type"] for event in audit_events]

    assert "inventory_adjusted" in event_types
    assert "inventory_reserved" in event_types
