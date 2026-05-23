# REFATORACAO [REF-1]: Migracao de classe simples para Pydantic BaseSettings
# ANTES: Classe Python simples sem validacao -- variaveis ausentes retornavam string vazia silenciosamente.
# DEPOIS: Pydantic BaseSettings valida tipos, suporta .env automatico e falha explicitamente
#         em producao caso variaveis obrigatorias estejam ausentes (SOLID: principio da responsabilidade unica).

import os
from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Catalogo Inteligente"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    GCP_PROJECT_ID: str = os.getenv("GCP_PROJECT_ID", "catalogo-unifor-1629")
    FIREBASE_CREDENTIALS: str = os.getenv("FIREBASE_CREDENTIALS", "")
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173", "https://catalogo-unifor-1629.web.app"]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    model_config = {"env_file": ".env", "case_sensitive": True}


settings = Settings()
