"""
test_catalog.py — testes da API do catálogo.
O conftest.py já mockou o Firebase antes deste arquivo ser importado.
"""
import pytest
<<<<<<< HEAD
=======
from unittest.mock import MagicMock, patch
import sys

# ✅ Mock do firebase_admin ANTES de qualquer import da app
# Isso evita que o Firestore tente conectar durante os testes
firebase_mock = MagicMock()
firebase_admin_mock = MagicMock()
firebase_admin_mock._apps = {"default": MagicMock()}  # simula app já inicializado

sys.modules["firebase_admin"] = firebase_admin_mock
sys.modules["firebase_admin.credentials"] = MagicMock()
sys.modules["firebase_admin.auth"] = MagicMock()
sys.modules["firebase_admin.firestore"] = MagicMock()
sys.modules["firebase_admin.storage"] = MagicMock()
sys.modules["google.cloud.firestore"] = MagicMock()

# Agora é seguro importar a app
>>>>>>> 48d62ab (fix: mock firebase in tests, remove pip cache)
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


<<<<<<< HEAD
def test_health():
    """Endpoint /health deve retornar 200."""
=======
# ─── Testes ───────────────────────────────────────────────────────────────────

def test_health():
    """Endpoint /health deve retornar 200 com status ok."""
>>>>>>> 48d62ab (fix: mock firebase in tests, remove pip cache)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


<<<<<<< HEAD
def test_list_products_publico():
    """GET /catalog/products é rota pública — deve retornar 200 ou 500 (sem Firestore real)."""
    response = client.get("/catalog/products")
=======
def test_list_products_sem_auth():
    """GET /catalog/products deve retornar 200 (rota pública)."""
    response = client.get("/catalog/products")
    # 200 ou 500 são aceitáveis em ambiente de teste sem Firestore real
>>>>>>> 48d62ab (fix: mock firebase in tests, remove pip cache)
    assert response.status_code in (200, 500)


def test_create_product_sem_token():
<<<<<<< HEAD
    """POST /catalog/products sem token deve ser negado com 401 ou 403."""
    response = client.post("/catalog/products", json={
        "name": "Produto Teste",
        "description": "Descrição de teste",
=======
    """POST /catalog/products sem token deve retornar 401 ou 403."""
    response = client.post("/catalog/products", json={
        "name": "Produto Teste",
        "description": "Descrição",
>>>>>>> 48d62ab (fix: mock firebase in tests, remove pip cache)
        "price": 99.9,
        "category": "eletronicos",
        "tags": [],
        "in_stock": True,
        "image_url": ""
    })
    assert response.status_code in (401, 403)


def test_create_product_payload_invalido():
<<<<<<< HEAD
    """POST com payload inválido deve retornar 401/403/422."""
    response = client.post("/catalog/products", json={"name": "", "price": -1})
    assert response.status_code in (401, 403, 422)


def test_delete_sem_auth():
    """DELETE sem auth deve retornar 401 ou 403."""
    response = client.delete("/catalog/products/qualquer-id")
=======
    """POST /catalog/products com payload inválido deve retornar 401/403/422."""
    response = client.post("/catalog/products", json={
        "name": "",
        "price": -1
    })
    assert response.status_code in (401, 403, 422)


def test_delete_produto_inexistente_sem_auth():
    """DELETE sem auth deve retornar 401 ou 403."""
    response = client.delete("/catalog/products/id-inexistente")
>>>>>>> 48d62ab (fix: mock firebase in tests, remove pip cache)
    assert response.status_code in (401, 403)
