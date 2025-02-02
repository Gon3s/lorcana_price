from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class BasePriceInfo(BaseModel):
    """Classe de base pour toutes les informations de prix"""

    min_price: float = Field(gt=0, description="Prix minimum")
    last_update: datetime = Field(
        default_factory=datetime.now, description="Date de mise à jour"
    )

    @field_validator("min_price")
    @classmethod
    def validate_price(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Le prix doit être supérieur à 0")
        return round(v, 2)


class PriceInfo(BasePriceInfo):
    current_price: float = Field(description="Prix actuel de la carte")
    trend_price: float = Field(description="Prix tendance de la carte")
    avg_30_days: float = Field(description="Prix moyen sur les 30 derniers jours")
    available_items: int = Field(description="Nombre d'articles disponibles")

    class Config:
        from_attributes = True

class VintedPriceInfo(BasePriceInfo):
    url: str = Field(description="URL de l'annonce")

    class Config:
        from_attributes = True
