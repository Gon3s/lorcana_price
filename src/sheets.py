import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Optional

# Constantes pour les colonnes et l'API
SHEET_NAME = "data"  # Modification du nom de la feuille
RANGE = "A2:K"  # A partir de A2 pour ignorer l'en-tête
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly"
]  # Déplacé ici avec les autres constantes

# Indices des colonnes dans le Google Sheet
COL_NAME_EN = 0
COL_NAME_FR = 1
COL_SET = 2
COL_NUMBER = 3
COL_COLOR = 4
COL_RARITY = 5
COL_PRICE = 6
COL_FOIL_PRICE = 7
COL_CARDMARKET_URL = 8
COL_COL9 = 9  # Colonne vide dans le CSV
COL_VINTED_URL = 10


class Card(BaseModel):
    name_en: str
    name_fr: str
    set_number: str
    card_number: str
    color: str
    rarity: str
    price: Optional[float]
    foil_price: Optional[float]
    cardmarket_url: str
    vinted_url: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name_en": "Maui - Half-Shark",
                    "name_fr": "Maui - Demi-requin",
                    "set_number": "6",
                    "card_number": "124",
                    "color": "Ruby",
                    "rarity": "Legendary",
                    "price": 38.32,
                    "foil_price": 45.62,
                    "cardmarket_url": "cardmarket/Maui - Half-Shark",
                    "vinted_url": "vinted/Maui - Demi-requin",
                }
            ]
        }
    }


def get_google_sheets_service():
    credentials_file = os.getenv(
        "GOOGLE_SHEETS_CREDENTIALS_FILE", "service-account.json"
    )

    if not os.path.exists(credentials_file):
        raise FileNotFoundError(
            f"Credentials file '{credentials_file}' not found. "
            "Please follow the setup instructions in docs/google_sheets_setup.md"
        )

    credentials = service_account.Credentials.from_service_account_file(
        credentials_file,
        scopes=SCOPES,  # Utilisation de SCOPES ici
    )

    return build("sheets", "v4", credentials=credentials)


def get_sheet_id_from_url(url: str) -> str:
    return url.split("/")[5]


def parse_price(price_str: str) -> Optional[float]:
    try:
        return (
            float(price_str.replace(" €", "").replace(",", ".")) if price_str else None
        )
    except ValueError:
        return None


def get_cards_to_track() -> list[Card]:
    load_dotenv()
    sheets_url = os.getenv("GOOGLE_SHEETS_URL")
    if not sheets_url:
        raise ValueError("GOOGLE_SHEETS_URL not found in .env")

    service = get_google_sheets_service()
    sheet_id = get_sheet_id_from_url(sheets_url)

    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=sheet_id, range=f"{SHEET_NAME}!{RANGE}")
        .execute()
    )

    values = result.get("values", [])
    cards = []

    for row in values:
        if len(row) >= 11:  # S'assurer que nous avons toutes les colonnes
            cards.append(
                Card(
                    name_en=row[COL_NAME_EN],
                    name_fr=row[COL_NAME_FR],
                    set_number=row[COL_SET],
                    card_number=row[COL_NUMBER],
                    color=row[COL_COLOR],
                    rarity=row[COL_RARITY],
                    price=parse_price(row[COL_PRICE]),
                    foil_price=parse_price(row[COL_FOIL_PRICE]),
                    cardmarket_url=row[COL_CARDMARKET_URL],
                    vinted_url=row[COL_VINTED_URL],
                )
            )

    return cards
