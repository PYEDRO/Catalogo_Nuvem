from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

MOCK_PRODUCTS = {
    "items": [
        {
            "id": "abc123",
            "name": "Produto Teste",
            "description": "Descrição do produto",
            "price": 99.90,
            "category": "eletronicos",
            "tags": ["novo"],
            "in_stock": True,
            "image_url": None,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        }
    ],
    "total": 1,
    "page": 1,
    "page_size": 12,
    "total_pages": 1,
}


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@patch("app.routes.catalog.product_service.query_with_filters", new_callable=AsyncMock)
def test_list_products(mock_query):
    mock_query.return_value = MOCK_PRODUCTS
    response = client.get("/catalog/products")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data


@patch("app.routes.catalog.product_service.query_with_filters", new_callable=AsyncMock)
def test_list_products_with_category_filter(mock_query):
    mock_query.return_value = MOCK_PRODUCTS
    response = client.get("/catalog/products?category=eletronicos")
    assert response.status_code == 200


@patch("app.routes.catalog.product_service.query_with_filters", new_callable=AsyncMock)
def test_list_products_with_price_filter(mock_query):
    mock_query.return_value = MOCK_PRODUCTS
    response = client.get("/catalog/products?min_price=50&max_price=200")
    assert response.status_code == 200


@patch("app.routes.catalog.product_service.get_by_id", new_callable=AsyncMock)
def test_get_product_not_found(mock_get):
    mock_get.return_value = None
    response = client.get("/catalog/products/id-inexistente")
    assert response.status_code == 404


@patch("app.routes.catalog.product_service.query_with_filters", new_callable=AsyncMock)
def test_search_filter(mock_query):
    mock_query.return_value = MOCK_PRODUCTS
    response = client.get("/catalog/products?search=Produto")
    assert response.status_code == 200
