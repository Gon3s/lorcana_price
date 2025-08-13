from pydantic_settings import BaseSettings
import os
from functools import lru_cache


class Settings(BaseSettings):
    """Configuration globale de l'application"""

    google_sheets_url: str
    google_sheets_credentials_file: str = "service-account.json"
    sheet_name: str = "data"
    history_sheet_name: str = "Historique"
    log_level: str = "DEBUG"

    # SMTP Configuration
    smtp_server: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "465"))
    smtp_username: str = os.getenv("SMTP_USERNAME", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    smtp_from_email: str = os.getenv("SMTP_FROM_EMAIL", "")
    notification_email: str = os.getenv("NOTIFICATION_EMAIL", "")

    # Prix minimum de différence pour envoyer une alerte (en %)
    min_price_diff_percent: float = float(os.getenv("MIN_PRICE_DIFF_PERCENT", "10"))

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Retourne les paramètres de configuration"""
    return Settings()
