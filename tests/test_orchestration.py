from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_decision_requests_missing_data():
    response = client.post(
        "/api/decisions/evaluate",
        json={
            "intent": "cotizacion_mayoreo",
            "customer_type": "cafeteria",
            "product": "miel_maguey",
            "quantity": 50,
            "urgency": "media",
            "needs_human": False,
            "blocked": False,
            "missing_data": ["presentacion", "zona_entrega"],
            "safety_flags": [],
            "rule_reasons": ["Faltan datos obligatorios para continuar."],
            "confidence": 0.9,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["action"] == "pedir_datos"
    assert data["created_lead"] is True
    assert data["created_ticket"] is False
    assert data["priority"] == "media"


def test_decision_rejects_blocked_request():
    response = client.post(
        "/api/decisions/evaluate",
        json={
            "intent": "otro",
            "customer_type": "desconocido",
            "product": "pulque",
            "quantity": 17,
            "urgency": "alta",
            "needs_human": True,
            "blocked": True,
            "missing_data": [],
            "safety_flags": ["pulque_menor_edad"],
            "rule_reasons": ["No se permite venta de pulque a menores de edad."],
            "confidence": 0.9,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["action"] == "rechazar_solicitud"
    assert data["created_lead"] is False
    assert data["created_ticket"] is False
    assert data["priority"] == "alta"


def test_decision_creates_quote_draft_when_wholesale_data_is_complete():
    response = client.post(
        "/api/decisions/evaluate",
        json={
            "intent": "cotizacion_mayoreo",
            "customer_type": "cafeteria",
            "product": "miel_maguey",
            "quantity": 50,
            "urgency": "media",
            "needs_human": False,
            "blocked": False,
            "missing_data": [],
            "safety_flags": [],
            "rule_reasons": [],
            "confidence": 0.9,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["action"] == "crear_borrador_cotizacion"
    assert data["created_lead"] is True
    assert data["created_ticket"] is False
    assert data["priority"] == "media"


def test_chat_complete_wholesale_data_creates_quote_draft():
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

    assert data["analysis"]["intent"] == "cotizacion_mayoreo"
    assert data["analysis"]["product"] == "miel_maguey"
    assert data["analysis"]["quantity"] == 50
    assert data["analysis"]["missing_data"] == []
    assert data["decision"]["action"] == "crear_borrador_cotizacion"
    assert data["decision"]["created_lead"] is True
    assert "borrador de cotizacion" in data["reply"].lower()
