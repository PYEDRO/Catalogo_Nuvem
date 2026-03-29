import logging

from fastapi import HTTPException, status
from firebase_admin import auth

logger = logging.getLogger(__name__)


async def verify_token(token: str) -> dict:
    try:
        decoded = auth.verify_id_token(token)
        return decoded
    except auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
        )
    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )
    except Exception as e:
        logger.error(f"Erro ao verificar token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falha na autenticação",
        )


async def get_user_role(uid: str) -> str:
    try:
        user = auth.get_user(uid)
        claims = user.custom_claims or {}
        return claims.get("role", "user")
    except Exception as e:
        logger.error(f"Erro ao buscar role do usuário {uid}: {e}")
        return "user"
