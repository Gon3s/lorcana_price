import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Optional
from datetime import datetime

from models.price_info import PriceInfo

# Constantes pour les colonnes et l'API
SHEET_NAME = "data"  # Modification du nom de la feuille
RANGE = "A2:O"  # Mise à jour du range pour retirer la colonne Vinted
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets"
]  # Modification pour autoriser l'écriture

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
COL_CURRENT_PRICE = 9
COL_TREND_PRICE = 10
COL_AVG_30_DAYS = 11
COL_AVAILABLE_ITEMS = 12
COL_MIN_PRICE = 13
COL_LAST_UPDATE = 14


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
    current_price: Optional[float]
    trend_price: Optional[float]
    avg_30_days: Optional[float]
    available_items: Optional[int]

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
        card_data = {
            "name_en": row[COL_NAME_EN],
            "name_fr": row[COL_NAME_FR],
            "set_number": row[COL_SET],
            "card_number": row[COL_NUMBER],
            "color": row[COL_COLOR],
            "rarity": row[COL_RARITY],
            "price": parse_price(row[COL_PRICE]),
            "foil_price": parse_price(row[COL_FOIL_PRICE]),
            "cardmarket_url": row[COL_CARDMARKET_URL],
            "current_price": parse_price(row[COL_CURRENT_PRICE])
            if len(row) > COL_CURRENT_PRICE
            else None,
            "trend_price": parse_price(row[COL_TREND_PRICE])
            if len(row) > COL_TREND_PRICE
            else None,
            "avg_30_days": parse_price(row[COL_AVG_30_DAYS])
            if len(row) > COL_AVG_30_DAYS
            else None,
            "available_items": int(row[COL_AVAILABLE_ITEMS])
            if len(row) > COL_AVAILABLE_ITEMS and row[COL_AVAILABLE_ITEMS]
            else None,
        }
        cards.append(Card(**card_data))

    return cards


def update_card_prices(service, row: int, price_info: PriceInfo):
    """Met à jour les prix d'une carte dans le Google Sheet"""
    try:
        load_dotenv()
        sheets_url = os.getenv("GOOGLE_SHEETS_URL")
        sheet_id = get_sheet_id_from_url(sheets_url)

        # Récupérer le prix minimum actuel
        range_name = f"{SHEET_NAME}!O{row}"
        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=sheet_id, range=range_name)
            .execute()
        )
        current_min = (
            float(result.get("values", [[0]])[0][0])
            if result.get("values")
            else float("inf")
        )

        # Mettre à jour le prix minimum si nécessaire
        new_min = (
            min(current_min, price_info.current_price)
            if current_min != 0
            else price_info.current_price
        )

        # Préparation des données
        values = [
            [
                price_info.current_price,
                price_info.trend_price,
                price_info.avg_30_days,
                price_info.available_items,
                new_min,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ]
        ]

        # Construction du range pour la mise à jour
        range_name = f"{SHEET_NAME}!J{row}:O{row}"

        body = {"values": values}
        service.spreadsheets().values().update(
            spreadsheetId=sheet_id, range=range_name, valueInputOption="RAW", body=body
        ).execute()

    except Exception as e:
        print(f"Erreur lors de la mise à jour des prix dans le sheet: {e}")
