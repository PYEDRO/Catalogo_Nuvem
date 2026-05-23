"""
test_catalog.py — testes da API do catálogo.
O conftest.py já mockou o Firebase antes deste arquivo ser importado.
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    """Endpoint /health deve retornar 200."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_list_products_publico():
    """GET /catalog/products é rota pública — deve retornar 200."""
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
    """GET /catalog/products com paginação deve retornar 200."""
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
    """page_size até 200 é permitido."""
    response = client.get("/catalog/products?page_size=200")
    assert response.status_code == 200


def test_list_products_page_size_invalido():
    """page_size > 200 deve retornar 422 (validação do FastAPI)."""
    response = client.get("/catalog/products?page_size=201")
    assert response.status_code == 422


def test_get_product_nao_encontrado():
    """GET /catalog/products/{id} inexistente deve retornar 404."""
    response = client.get("/catalog/products/id-que-nao-existe")
    assert response.status_code == 404


def test_create_product_sem_token():
    """POST /catalog/products sem token deve ser negado com 401 ou 403."""
    response = client.post("/catalog/products", json={
        "name": "Produto Teste",
        "description": "Descrição de teste",
        "price": 99.9,
        "category": "eletronicos",
        "tags": [],
        "in_stock": True,
        "image_url": "",
    })
    assert response.status_code in (401, 403)


def test_create_product_payload_invalido():
    """POST com payload inválido deve retornar 401/403/422."""
    response = client.post("/catalog/products", json={"name": "", "price": -1})
    assert response.status_code in (401, 403, 422)


def test_update_product_sem_auth():
    """PUT sem auth deve retornar 401 ou 403."""
    response = client.put("/catalog/products/algum-id", json={"name": "Novo Nome"})
    assert response.status_code in (401, 403)


def test_delete_sem_auth():
    """DELETE sem auth deve retornar 401 ou 403."""
    response = client.delete("/catalog/products/qualquer-id")
    assert response.status_code in (401, 403)
