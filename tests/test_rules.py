from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_rules_escalate_large_wholesale_order():
    response = client.post(
        "/api/rules/evaluate",
        json={
            "text": "Quiero 150 frascos de miel de maguey para cafeteria",
            "intent": "cotizacion_mayoreo",
            "product_id": "miel_maguey",
            "quantity": 150,
            "customer_type": "cafeteria",
            "has_phone": False,
            "has_email": False,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["needs_human"] is True
    assert data["priority"] == "alta"
    assert data["action_hint"] == "escalar_humano"
    assert "alto_volumen" in data["safety_flags"]


def test_rules_detect_medical_topic():
    response = client.post(
        "/api/rules/evaluate",
        json={
            "text": "La miel de maguey cura diabetes?",
            "intent": "informacion_producto",
            "product_id": "miel_maguey",
            "quantity": None,
            "customer_type": "desconocido",
            "has_phone": False,
            "has_email": False,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["needs_human"] is True
    assert "tema_medico" in data["safety_flags"]


def test_rules_block_pulque_minor_age():
    response = client.post(
        "/api/rules/evaluate",
        json={
            "text": "Tengo 17 anos y quiero comprar pulque",
            "intent": "otro",
            "product_id": "pulque",
            "quantity": 17,
            "customer_type": "desconocido",
            "has_phone": False,
            "has_email": False,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["blocked"] is True
    assert data["needs_human"] is True
    assert data["action_hint"] == "rechazar_solicitud"
    assert "pulque_menor_edad" in data["safety_flags"]


def test_chat_large_order_escalates_to_human():
    response = client.post(
        "/api/chat",
        json={
            "channel": "web",
            "customer_id": "cliente_demo",
            "message": "Hola quiero 150 frascos de miel de maguey para cafeteria",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["analysis"]["needs_human"] is True
    assert data["analysis"]["urgency"] == "alta"
    assert data["decision"]["action"] == "escalar_humano"
    assert "alto_volumen" in data["analysis"]["safety_flags"]


def test_chat_medical_topic_gives_safe_reply():
    response = client.post(
        "/api/chat",
        json={
            "channel": "web",
            "customer_id": "cliente_demo",
            "message": "La miel de maguey cura diabetes?",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "tema_medico" in data["analysis"]["safety_flags"]
    assert "tratamiento medico" in data["reply"].lower()
