import uuid
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from firebase_admin import storage

from app.routes.auth import require_admin

router = APIRouter(prefix="/catalog", tags=["upload"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE_MB = 5
BUCKET_NAME = "catalogo-unifor-1629.firebasestorage.app"


@router.post("/products/upload-image", status_code=200)
async def upload_product_image(
    file: UploadFile = File(...),
    _admin: dict = Depends(require_admin),
):
    # Valida content type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Tipo inválido. Permitidos: jpeg, png, webp",
        )

    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > MAX_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"Arquivo excede {MAX_SIZE_MB}MB (recebido: {size_mb:.1f}MB)",
        )

    ext = (file.filename or "image").rsplit(".", 1)[-1]
    filename = f"products/{uuid.uuid4()}.{ext}"

    try:
        bucket = storage.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(contents, content_type=file.content_type)
        blob.make_public()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro no upload para Firebase Storage: {str(e)}",
        )

    return {"image_url": blob.public_url}
