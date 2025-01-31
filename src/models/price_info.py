from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class PriceInfo(BaseModel):
    current_price: float = Field(description="Prix actuel de la carte")
    trend_price: float = Field(description="Prix tendance de la carte")
    avg_30_days: float = Field(description="Prix moyen sur les 30 derniers jours")
    available_items: int = Field(description="Nombre d'articles disponibles")
    min_price: Optional[float] = Field(
        default=None, description="Prix minimum de la carte"
    )
    last_update: Optional[datetime] = Field(
        default=None, description="Date de la dernière mise à jour"
    )

    class Config:
        from_attributes = True

class VintedPriceInfo(BaseModel):
    min_price: float = Field(description="Prix minimum trouvé")
    last_update: datetime = Field(description="Date de la dernière mise à jour")
    url: str | None = None  # Ajout du champ URL optionnel

    class Config:
        from_attributes = True
