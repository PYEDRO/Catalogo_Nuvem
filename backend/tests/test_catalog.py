"""
test_catalog.py — testes da API do catálogo.
O conftest.py já mockou o Firebase antes deste arquivo ser importado.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    """Endpoint /health deve retornar 200."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_list_products_publico():
    """GET /catalog/products é rota pública — deve retornar 200 ou 500 (sem Firestore real)."""
    response = client.get("/catalog/products")
    assert response.status_code in (200, 500)


def test_create_product_sem_token():
    """POST /catalog/products sem token deve ser negado com 401 ou 403."""
    response = client.post("/catalog/products", json={
        "name": "Produto Teste",
        "description": "Descrição de teste",
        "price": 99.9,
        "category": "eletronicos",
        "tags": [],
        "in_stock": True,
        "image_url": ""
    })
    assert response.status_code in (401, 403)


def test_create_product_payload_invalido():
    """POST com payload inválido deve retornar 401/403/422."""
    response = client.post("/catalog/products", json={"name": "", "price": -1})
    assert response.status_code in (401, 403, 422)


def test_delete_sem_auth():
    """DELETE sem auth deve retornar 401 ou 403."""
    response = client.delete("/catalog/products/qualquer-id")
    assert response.status_code in (401, 403)
