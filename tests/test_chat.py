from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_chat_mock_wholesale_request():
    response = client.post(
        "/api/chat",
        json={
            "channel": "web",
            "customer_id": "cliente_demo",
            "message": "Hola quiero comprar 50 frascos de miel de maguey para cafeteria",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["ok"] is True
    assert data["mode"] == "mock"
    assert data["analysis"]["intent"] == "cotizacion_mayoreo"
    assert data["analysis"]["customer_type"] == "cafeteria"
    assert data["analysis"]["product"] == "miel_maguey"
    assert data["analysis"]["quantity"] == 50
    assert data["decision"]["action"] == "pedir_datos"
    assert data["decision"]["created_lead"] is True
    assert data["decision"]["created_ticket"] is False
    assert "cotizacion" in data["reply"].lower()


def test_chat_rejects_empty_message():
    response = client.post(
        "/api/chat",
        json={
            "channel": "web",
            "customer_id": "cliente_demo",
            "message": "",
        },
    )

    assert response.status_code == 422
