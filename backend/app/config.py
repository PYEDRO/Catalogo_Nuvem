# REFATORAÇÃO [REF-1]: Migração de classe simples para Pydantic BaseSettings
# ANTES: Classe Python simples sem validação — variáveis ausentes retornavam string vazia silenciosamente.
# DEPOIS: Pydantic BaseSettings valida tipos, suporta .env automático e falha explicitamente
#         em produção caso variáveis obrigatórias estejam ausentes (SOLID: princípio da responsabilidade única).

from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Metadados da aplicação (constantes — não dependem de env vars)
    PROJECT_NAME: str = "Catálogo Inteligente"
    VERSION: str = "1.0.0"

    # Variáveis de ambiente — obrigatórias em produção, com defaults para desenvolvimento local
    GCP_PROJECT_ID: str = Field(default="", description="ID do projeto GCP")
    FIREBASE_CREDENTIALS: str = Field(default="", description="JSON das credenciais Firebase (base64 ou raw)")
    ENVIRONMENT: str = Field(default="development", description="Ambiente de execução: development | production | test")
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:5173"],
        description="Lista de origens permitidas pelo CORS",
    )

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        allowed = {"development", "production", "test"}
        if v not in allowed:
            raise ValueError(f"ENVIRONMENT deve ser um de {allowed}, recebido: '{v}'")
        return v

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, v):
        """Aceita string CSV (ex: 'https://a.com,https://b.com') ou lista nativa."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


settings = Settings()
