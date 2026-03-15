from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from app.services.auth_service import verify_token, get_user_role

router = APIRouter()
security = HTTPBearer()


class TokenRequest(BaseModel):
    token: str


@router.post("/verify")
async def verify_user_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials
    decoded = await verify_token(token)
    role = await get_user_role(decoded["uid"])
    return {
        "uid": decoded["uid"],
        "email": decoded.get("email"),
        "role": role,
    }


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials
    decoded = await verify_token(token)
    decoded["role"] = await get_user_role(decoded["uid"])
    return decoded


async def require_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Acesso restrito a administradores")
    return current_user
