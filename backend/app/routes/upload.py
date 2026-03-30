import uuid
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from firebase_admin import storage

from app.routes.auth import require_admin  # ✅ mesmo padrão do catalog.py

router = APIRouter(prefix="/catalog", tags=["upload"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE_MB = 5


@router.post("/products/upload-image", status_code=200)
async def upload_product_image(
    file: UploadFile = File(...),
    _admin: dict = Depends(require_admin),  # ✅ unificado com o restante da API
):
    # Valida content type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo inválido. Permitidos: jpeg, png, webp",
        )

    # Lê e valida tamanho
    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > MAX_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"Arquivo excede {MAX_SIZE_MB}MB (recebido: {size_mb:.1f}MB)",
        )

    # Gera path único no Storage
    ext = (file.filename or "image").rsplit(".", 1)[-1]
    filename = f"products/{uuid.uuid4()}.{ext}"

    # Upload para Firebase Storage
    try:
        bucket = storage.bucket()
        blob = bucket.blob(filename)
        blob.upload_from_string(contents, content_type=file.content_type)
        blob.make_public()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro no upload para Firebase Storage: {str(e)}",
        )

    return {"image_url": blob.public_url}
