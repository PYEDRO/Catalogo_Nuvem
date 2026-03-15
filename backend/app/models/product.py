from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class CategoryEnum(str, Enum):
    eletronicos = "eletronicos"
    roupas = "roupas"
    alimentos = "alimentos"
    livros = "livros"
    outros = "outros"


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: str = Field(..., min_length=5)
    price: float = Field(..., gt=0)
    category: CategoryEnum
    tags: Optional[List[str]] = []
    in_stock: bool = True
    image_url: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    category: Optional[CategoryEnum] = None
    tags: Optional[List[str]] = None
    in_stock: Optional[bool] = None
    image_url: Optional[str] = None


class ProductResponse(BaseModel):
    id: str
    name: str
    description: str
    price: float
    category: str
    tags: List[str]
    in_stock: bool
    image_url: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]


class FilterParams(BaseModel):
    category: Optional[CategoryEnum] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    in_stock: Optional[bool] = None
    search: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=12, ge=1, le=50)


class PaginatedResponse(BaseModel):
    items: List[ProductResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
