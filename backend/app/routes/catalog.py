import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.models.product import (
    CategoryEnum,
    PaginatedResponse,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)
from app.routes.auth import require_admin
from app.services.firestore_service import product_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/products", response_model=PaginatedResponse)
async def list_products(
    category: Optional[CategoryEnum] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    in_stock: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=12, ge=1, le=50),
):
    result = await product_service.query_with_filters(
        category=category.value if category else None,
        min_price=min_price,
        max_price=max_price,
        in_stock=in_stock,
        page=page,
        page_size=page_size,
    )

    if search:
        search_lower = search.lower()
        result["items"] = [
            item
            for item in result["items"]
            if search_lower in item.get("name", "").lower()
            or search_lower in item.get("description", "").lower()
        ]
        result["total"] = len(result["items"])
        result["total_pages"] = (result["total"] + page_size - 1) // page_size

    return result


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str):
    product = await product_service.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return product


@router.post("/products", response_model=ProductResponse, status_code=201)
async def create_product(
    product: ProductCreate,
    admin: dict = Depends(require_admin),
):
    data = product.model_dump()
    data["category"] = data["category"].value
    created = await product_service.create(data)
    return created


@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    product: ProductUpdate,
    admin: dict = Depends(require_admin),
):
    existing = await product_service.get_by_id(product_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    data = product.model_dump(exclude_unset=True)
    if "category" in data and data["category"]:
        data["category"] = data["category"].value

    updated = await product_service.update(product_id, data)
    return updated


@router.delete("/products/{product_id}", status_code=204)
async def delete_product(
    product_id: str,
    admin: dict = Depends(require_admin),
):
    existing = await product_service.get_by_id(product_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    await product_service.delete(product_id)
