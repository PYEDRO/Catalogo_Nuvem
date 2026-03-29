import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any

import firebase_admin
from firebase_admin import credentials, firestore

from app.config import settings

logger = logging.getLogger(__name__)


def init_firebase():
    if not firebase_admin._apps:
        if settings.FIREBASE_CREDENTIALS:
            cred_dict = json.loads(settings.FIREBASE_CREDENTIALS)
            cred = credentials.Certificate(cred_dict)
        else:
            cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred, {"projectId": settings.GCP_PROJECT_ID})


init_firebase()
db = firestore.client()


class FirestoreService:
    def __init__(self, collection: str):
        self.collection = db.collection(collection)

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            data["created_at"] = datetime.utcnow().isoformat()
            data["updated_at"] = datetime.utcnow().isoformat()
            doc_ref = self.collection.document()
            doc_ref.set(data)
            return {"id": doc_ref.id, **data}
        except Exception as e:
            logger.error(f"Erro ao criar documento: {e}")
            raise

    async def get_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        try:
            doc = self.collection.document(doc_id).get()
            if doc.exists:
                return {"id": doc.id, **doc.to_dict()}
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar documento {doc_id}: {e}")
            raise

    async def update(self, doc_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            data["updated_at"] = datetime.utcnow().isoformat()
            data_clean = {k: v for k, v in data.items() if v is not None}
            self.collection.document(doc_id).update(data_clean)
            return await self.get_by_id(doc_id)
        except Exception as e:
            logger.error(f"Erro ao atualizar documento {doc_id}: {e}")
            raise

    async def delete(self, doc_id: str) -> bool:
        try:
            self.collection.document(doc_id).delete()
            return True
        except Exception as e:
            logger.error(f"Erro ao deletar documento {doc_id}: {e}")
            raise

    async def query_with_filters(
        self,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        in_stock: Optional[bool] = None,
        page: int = 1,
        page_size: int = 12,
    ) -> Dict[str, Any]:
        try:
            query = self.collection

            if category:
                query = query.where("category", "==", category)
            if in_stock is not None:
                query = query.where("in_stock", "==", in_stock)
            if min_price is not None:
                query = query.where("price", ">=", min_price)
            if max_price is not None:
                query = query.where("price", "<=", max_price)

            docs = list(query.stream())
            total = len(docs)

            start = (page - 1) * page_size
            end = start + page_size
            paginated = docs[start:end]

            items = [{"id": doc.id, **doc.to_dict()} for doc in paginated]

            return {
                "items": items,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size,
            }
        except Exception as e:
            logger.error(f"Erro na query com filtros: {e}")
            raise


product_service = FirestoreService("products")
