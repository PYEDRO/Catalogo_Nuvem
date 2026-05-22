# REFATORAÇÃO [REF-3]: list_products — eliminado código duplicado de busca e
#                        delegada a responsabilidade para o serviço correto.
#
# ANTES (bug crítico de lógica):
#   - O parâmetro `search` NÃO era passado para product_service.query_with_filters().
#   - A filtragem textual era feita aqui, APÓS a paginação, sobre apenas os `page_size`
#     itens retornados — tornando a busca completamente incorreta para dados paginados.
#   - Exemplo: page=1, page_size=12, busca "notebook" — se os 12 primeiros produtos do
#     Firestore não tivessem "notebook", o resultado era vazio mesmo havendo matches
#     nas páginas seguintes.
#
# DEPOIS:
#   - `search` é passado para query_with_filters(), que aplica o filtro antes de paginar.
#   - Violação do princípio DRY eliminada: lógica de busca existe apenas no serviço.
#   - Route handler reduzido a responsabilidade única: parsing de parâmetros HTTP.

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
    min_price: Optional[float] = Query(None, ge=0, description="Preço mínimo"),
    max_price: Optional[float] = Query(None, ge=0, description="Preço máximo"),
    in_stock: Optional[bool] = Query(None, description="Filtrar apenas produtos em estoque"),
    search: Optional[str] = Query(None, min_length=2, max_length=100, description="Busca por nome ou descrição"),
    page: int = Query(default=1, ge=1, description="Número da página"),
    page_size: int = Query(default=12, ge=1, le=50, description="Itens por página"),
) -> PaginatedResponse:
    """Lista produtos com filtros opcionais e paginação.

    A busca textual (search) é aplicada no servidor antes da paginação,
    garantindo consistência entre o total retornado e os itens da página.
    """
    return await product_service.query_with_filters(
        category=category.value if category else None,
        min_price=min_price,
        max_price=max_price,
        in_stock=in_stock,
        search=search,        # [REF-3] search delegado ao serviço — eliminada duplicação
        page=page,
        page_size=page_size,
    )


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str) -> ProductResponse:
    """Retorna um produto pelo ID."""
    product = await product_service.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return product


@router.post("/products", response_model=ProductResponse, status_code=201)
async def create_product(
    product: ProductCreate,
    admin: dict = Depends(require_admin),
) -> ProductResponse:
    """Cria um novo produto. Requer perfil admin."""
    data = product.model_dump()
    data["category"] = data["category"].value
    return await product_service.create(data)


@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    product: ProductUpdate,
    admin: dict = Depends(require_admin),
) -> ProductResponse:
    """Atualiza um produto existente. Requer perfil admin."""
    existing = await product_service.get_by_id(product_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    data = product.model_dump(exclude_unset=True)
    if "category" in data and data["category"]:
        data["category"] = data["category"].value

    return await product_service.update(product_id, data)


@router.delete("/products/{product_id}", status_code=204)
async def delete_product(
    product_id: str,
    admin: dict = Depends(require_admin),
) -> None:
    """Remove um produto. Requer perfil admin."""
    existing = await product_service.get_by_id(product_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    await product_service.delete(product_id)
