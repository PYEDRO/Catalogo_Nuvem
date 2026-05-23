# REFATORACAO [REF-3]: list_products -- eliminado codigo duplicado de busca e
#                       delegada a responsabilidade para o servico correto.
#
# ANTES (bug critico de logica):
#   - O parametro `search` NAO era passado para product_service.query_with_filters().
#   - A filtragem textual era feita aqui, APOS a paginacao, sobre apenas os `page_size`
#     itens retornados -- tornando a busca completamente incorreta para dados paginados.
#
# DEPOIS:
#   - `search` e passado para query_with_filters(), que aplica o filtro antes de paginar.
#   - Violacao do principio DRY eliminada: logica de busca existe apenas no servico.
#   - Route handler reduzido a responsabilidade unica: parsing de parametros HTTP.

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
    category: Optional[CategoryEnum] = Query(None, description="Filtrar por categoria"),
    min_price: Optional[float] = Query(None, ge=0, description="Preco minimo"),
    max_price: Optional[float] = Query(None, ge=0, description="Preco maximo"),
    in_stock: Optional[bool] = Query(None, description="Filtrar apenas produtos em estoque"),
    search: Optional[str] = Query(None, min_length=2, max_length=100, description="Busca por nome ou descricao"),
    page: int = Query(default=1, ge=1, description="Numero da pagina"),
    page_size: int = Query(default=12, ge=1, le=200, description="Itens por pagina"),
) -> PaginatedResponse:
    """Lista produtos com filtros opcionais e paginacao."""
    return await product_service.query_with_filters(
        category=category.value if category else None,
        min_price=min_price,
        max_price=max_price,
        in_stock=in_stock,
        search=search,
        page=page,
        page_size=page_size,
    )


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str) -> ProductResponse:
    """Retorna um produto pelo ID."""
    product = await product_service.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produto nao encontrado")
    return product


@router.post("/products", response_model=ProductResponse, status_code=201)
async def create_product(
    payload: ProductCreate,
    _admin: dict = Depends(require_admin),
) -> ProductResponse:
    """Cria um novo produto (admin)."""
    data = payload.model_dump()
    return await product_service.create(data)


@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    payload: ProductUpdate,
    _admin: dict = Depends(require_admin),
) -> ProductResponse:
    """Atualiza um produto existente (admin)."""
    existing = await product_service.get_by_id(product_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Produto nao encontrado")
    data = payload.model_dump(exclude_unset=True)
    updated = await product_service.update(product_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Produto nao encontrado")
    return updated


@router.delete("/products/{product_id}", status_code=204)
async def delete_product(
    product_id: str,
    _admin: dict = Depends(require_admin),
):
    """Remove um produto (admin)."""
    existing = await product_service.get_by_id(product_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Produto nao encontrado")
    await product_service.delete(product_id)
