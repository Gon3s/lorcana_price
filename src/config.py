from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Configuration globale de l'application"""

    google_sheets_url: str
    google_sheets_credentials_file: str = "service-account.json"
    sheet_name: str = "data"
    log_level: str = "DEBUG"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Retourne les paramètres de configuration"""
    return Settings()
