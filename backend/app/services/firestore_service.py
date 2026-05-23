# REFATORACAO [REF-2]: query_with_filters -- paginacao e busca corrigidas
#
# PROBLEMA ORIGINAL:
#   - query.stream() carregava TODOS os documentos para memoria (O(n) por request).
#   - A paginacao era feita por slice de lista Python.
#   - O filtro `search` era aplicado no catalog.py APOS a paginacao (bug critico).
#
# SOLUCAO IMPLEMENTADA:
#   - Cursor-based pagination via Firestore .offset() + .limit().
#   - COUNT aggregation query para total.
#   - Busca por `search` aplicada ANTES de paginar.
#   - asyncio.to_thread() para operacoes blocking (SOLID: SRP + DIP).

import json
import logging
import math
from asyncio import to_thread
from datetime import datetime, timezone
from typing import Optional, Dict, Any

import firebase_admin
from firebase_admin import credentials, firestore

from app.config import settings

logger = logging.getLogger(__name__)


def _init_firebase() -> None:
    """Inicializa o Firebase Admin SDK uma unica vez (idempotente)."""
    if not firebase_admin._apps:
        if settings.FIREBASE_CREDENTIALS:
            cred_dict = json.loads(settings.FIREBASE_CREDENTIALS)
            cred = credentials.Certificate(cred_dict)
        else:
            cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred, {"projectId": settings.GCP_PROJECT_ID})


_init_firebase()
db = firestore.client()


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _doc_to_dict(doc) -> Dict[str, Any]:
    return {"id": doc.id, **doc.to_dict()}


class FirestoreService:
    def __init__(self, collection: str) -> None:
        self._col = db.collection(collection)

    # ------------------------------------------------------------------
    # CRUD basico
    # ------------------------------------------------------------------

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        now = _now_iso()
        data = {**data, "created_at": now, "updated_at": now}
        try:
            doc_ref = await to_thread(lambda: self._col.document())
            await to_thread(doc_ref.set, data)
            return {"id": doc_ref.id, **data}
        except Exception as exc:
            logger.error("Erro ao criar documento: %s", exc)
            raise

    async def get_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        try:
            doc = await to_thread(self._col.document(doc_id).get)
            return _doc_to_dict(doc) if doc.exists else None
        except Exception as exc:
            logger.error("Erro ao buscar documento %s: %s", doc_id, exc)
            raise

    async def update(self, doc_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        data_clean = {k: v for k, v in data.items() if v is not None}
        data_clean["updated_at"] = _now_iso()
        try:
            await to_thread(self._col.document(doc_id).update, data_clean)
            return await self.get_by_id(doc_id)
        except Exception as exc:
            logger.error("Erro ao atualizar documento %s: %s", doc_id, exc)
            raise

    async def delete(self, doc_id: str) -> bool:
        try:
            await to_thread(self._col.document(doc_id).delete)
            return True
        except Exception as exc:
            logger.error("Erro ao deletar documento %s: %s", doc_id, exc)
            raise

    # ------------------------------------------------------------------
    # Query com filtros + paginacao cursor-based + COUNT aggregation
    # ------------------------------------------------------------------

    async def query_with_filters(
        self,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        in_stock: Optional[bool] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 12,
    ) -> Dict[str, Any]:
        """
        Retorna pagina de documentos com total via COUNT aggregation.
        Filtros Firestore: category, min_price, max_price, in_stock.
        Busca textual (search) em memoria, aplicada antes da paginacao.
        """
        try:
            query = self._col

            if category is not None:
                query = query.where("category", "==", category)
            if in_stock is not None:
                query = query.where("in_stock", "==", in_stock)
            if min_price is not None:
                query = query.where("price", ">=", min_price)
            if max_price is not None:
                query = query.where("price", "<=", max_price)

            if search:
                # Busca em memoria: carrega documentos filtrados e filtra por nome/descricao
                def _stream_search():
                    docs = list(query.stream())
                    term = search.lower()
                    matched = [
                        _doc_to_dict(d) for d in docs
                        if term in (d.to_dict().get("name") or "").lower()
                        or term in (d.to_dict().get("description") or "").lower()
                    ]
                    total = len(matched)
                    offset = (page - 1) * page_size
                    items = matched[offset: offset + page_size]
                    return items, total

                items, total = await to_thread(_stream_search)
            else:
                # COUNT aggregation -- evita carregar documentos so para contar
                def _count():
                    count_result = query.count().get()
                    return count_result[0][0].value

                total = await to_thread(_count)

                # Cursor-based pagination
                def _paginate():
                    offset = (page - 1) * page_size
                    return list(query.offset(offset).limit(page_size).stream())

                raw_docs = await to_thread(_paginate)
                items = [_doc_to_dict(d) for d in raw_docs]

            total_pages = math.ceil(total / page_size) if page_size > 0 else 0

            return {
                "items": items,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
            }

        except Exception as exc:
            logger.error("Erro ao consultar colecao: %s", exc)
            raise


# Singleton para uso nas rotas
product_service = FirestoreService("products")
