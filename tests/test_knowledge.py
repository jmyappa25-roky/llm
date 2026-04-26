from fastapi.testclient import TestClient

from app.main import app
from app.modules.knowledge.knowledge_service import knowledge_service


client = TestClient(app)


def test_get_products_endpoint():
    response = client.get("/api/products")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 4
    assert any(product["id"] == "miel_maguey" for product in data)


def test_get_product_by_id_endpoint():
    response = client.get("/api/products/miel_maguey")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == "miel_maguey"
    assert data["name"] == "Miel de maguey"
    assert len(data["presentations"]) >= 1


def test_knowledge_search_endpoint():
    response = client.get(
        "/api/knowledge/search",
        params={"query": "quiero precio de mayoreo de miel de maguey para cafeteria"},
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["products"]) >= 1
    assert data["products"][0]["id"] == "miel_maguey"
    assert len(data["faqs"]) >= 1
    assert len(data["policies"]) >= 1


def test_knowledge_service_detects_pulque():
    product = knowledge_service.detect_product("Necesito 20 litros de pulque para un evento")

    assert product is not None
    assert product.id == "pulque"
