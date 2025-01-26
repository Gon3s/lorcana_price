from pydantic import BaseModel, Field


class PriceInfo(BaseModel):
    current_price: float = Field(description="Prix actuel de la carte")
    trend_price: float = Field(description="Prix tendance de la carte")
    avg_30_days: float = Field(description="Prix moyen sur les 30 derniers jours")
    available_items: int = Field(description="Nombre d'articles disponibles")

    class Config:
        from_attributes = True
