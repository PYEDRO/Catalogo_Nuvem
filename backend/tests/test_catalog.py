"""
test_catalog.py - testes da API do catalogo.
O conftest.py ja mockou o Firebase antes deste arquivo ser importado.
"""
from fastapi.testclient import TestClient
from app.main import app
from app.routes.auth import require_admin

client = TestClient(app)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _override_admin():
    """Dependency override que simula admin autenticado."""
    return {"uid": "test-uid", "email": "admin@test.com", "role": "admin"}


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

def test_health():
    """Endpoint /health deve retornar 200."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# ---------------------------------------------------------------------------
# GET /catalog/products
# ---------------------------------------------------------------------------

def test_list_products_publico():
    """GET /catalog/products e rota publica -- deve retornar 200."""
    response = client.get("/catalog/products")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "total_pages" in data
    assert data["items"] == []
    assert data["total"] == 0


def test_list_products_com_filtros():
    """GET /catalog/products com filtros opcionais deve retornar 200."""
    response = client.get("/catalog/products?category=eletronicos&min_price=10&max_price=500&in_stock=true")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data


def test_list_products_paginacao():
    """GET /catalog/products com paginacao deve retornar 200."""
    response = client.get("/catalog/products?page=1&page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 5


def test_list_products_busca():
    """GET /catalog/products com search deve retornar 200."""
    response = client.get("/catalog/products?search=notebook")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data


def test_list_products_page_size_maximo():
    """page_size ate 200 e permitido."""
    response = client.get("/catalog/products?page_size=200")
    assert response.status_code == 200


def test_list_products_page_size_invalido():
    """page_size > 200 deve retornar 422 (validacao do FastAPI)."""
    response = client.get("/catalog/products?page_size=201")
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# GET /catalog/products/{id}
# ---------------------------------------------------------------------------

def test_get_product_nao_encontrado():
    """GET /catalog/products/{id} inexistente deve retornar 404."""
    response = client.get("/catalog/products/id-que-nao-existe")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# POST /catalog/products (requer admin)
# ---------------------------------------------------------------------------

def test_create_product_sem_token():
    """POST /catalog/products sem token deve ser negado com 401 ou 403."""
    response = client.post("/catalog/products", json={
        "name": "Produto Teste",
        "description": "Descricao de teste",
        "price": 99.9,
        "category": "eletronicos",
        "tags": [],
        "in_stock": True,
        "image_url": "",
    })
    assert response.status_code in (401, 403)


def test_create_product_payload_invalido():
    """POST com payload invalido deve retornar 401/403/422."""
    response = client.post("/catalog/products", json={"name": "", "price": -1})
    assert response.status_code in (401, 403, 422)


def test_create_product_com_admin():
    """POST /catalog/products com admin autenticado deve retornar 201."""
    app.dependency_overrides[require_admin] = _override_admin
    try:
        response = client.post("/catalog/products", json={
            "name": "Produto Admin",
            "description": "Criado pelo admin",
            "price": 49.9,
            "category": "eletronicos",
            "tags": ["novo"],
            "in_stock": True,
            "image_url": "https://example.com/img.jpg",
        })
        assert response.status_code == 201
    finally:
        app.dependency_overrides.pop(require_admin, None)


# ---------------------------------------------------------------------------
# PUT /catalog/products/{id} (requer admin)
# ---------------------------------------------------------------------------

def test_update_product_sem_auth():
    """PUT sem auth deve retornar 401 ou 403."""
    response = client.put("/catalog/products/algum-id", json={"name": "Novo Nome"})
    assert response.status_code in (401, 403)


def test_update_product_nao_encontrado():
    """PUT /catalog/products/{id} inexistente com admin deve retornar 404."""
    app.dependency_overrides[require_admin] = _override_admin
    try:
        response = client.put("/catalog/products/id-inexistente", json={"name": "Novo Nome"})
        assert response.status_code == 404
    finally:
        app.dependency_overrides.pop(require_admin, None)


# ---------------------------------------------------------------------------
# DELETE /catalog/products/{id} (requer admin)
# ---------------------------------------------------------------------------

def test_delete_sem_auth():
    """DELETE sem auth deve retornar 401 ou 403."""
    response = client.delete("/catalog/products/qualquer-id")
    assert response.status_code in (401, 403)


def test_delete_product_nao_encontrado():
    """DELETE /catalog/products/{id} inexistente com admin deve retornar 404."""
    app.dependency_overrides[require_admin] = _override_admin
    try:
        response = client.delete("/catalog/products/id-inexistente")
        assert response.status_code == 404
    finally:
        app.dependency_overrides.pop(require_admin, None)
