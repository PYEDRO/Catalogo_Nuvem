import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    PROJECT_NAME: str = "Catálogo Inteligente"
    VERSION: str = "1.0.0"
    GCP_PROJECT_ID: str = os.getenv("GCP_PROJECT_ID", "")
    FIREBASE_CREDENTIALS: str = os.getenv("FIREBASE_CREDENTIALS", "")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    ALLOWED_ORIGINS: list = os.getenv(
        "ALLOWED_ORIGINS", "http://localhost:5173"
    ).split(",")


settings = Settings()
