from pydantic import BaseModel
from typing import Optional


class Card(BaseModel):
    """Modèle pour une carte dans le sheet"""

    name_en: str
    name_fr: str
    cardmarket_url: Optional[str]
    current_price: Optional[float]
    vinted_url: Optional[str] = None
    row: int
