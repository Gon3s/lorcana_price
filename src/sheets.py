import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Optional
from datetime import datetime
import pytz

from models.price_info import PriceInfo

# Constantes pour les colonnes et l'API
SHEET_NAME = "data"
RANGE = "A2:O"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

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

# Cache des services
_sheets_service = None
_sheet_id = None


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
    global _sheets_service
    if _sheets_service is not None:
        return _sheets_service

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
        scopes=SCOPES,
    )

    _sheets_service = build("sheets", "v4", credentials=credentials)
    return _sheets_service


def get_sheet_id():
    global _sheet_id
    if _sheet_id is not None:
        return _sheet_id

    load_dotenv()
    sheets_url = os.getenv("GOOGLE_SHEETS_URL")
    if not sheets_url:
        raise ValueError("GOOGLE_SHEETS_URL not found in .env")
    _sheet_id = sheets_url.split("/")[5]
    return _sheet_id


def parse_value(value) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.replace(" €", "").replace(",", "."))
        except ValueError:
            return None
    return None


def get_cards_to_track() -> list[Card]:
    service = get_google_sheets_service()
    sheet_id = get_sheet_id()

    result = (
        service.spreadsheets()
        .values()
        .get(
            spreadsheetId=sheet_id,
            range=f"{SHEET_NAME}!{RANGE}",
            valueRenderOption="UNFORMATTED_VALUE",
        )
        .execute()
    )

    values = result.get("values", [])
    cards = []

    for row in values:
        card_data = {
            "name_en": str(row[COL_NAME_EN]),
            "name_fr": str(row[COL_NAME_FR]),
            "set_number": str(row[COL_SET]),
            "card_number": str(row[COL_NUMBER]),
            "color": str(row[COL_COLOR]),
            "rarity": str(row[COL_RARITY]),
            "price": parse_value(row[COL_PRICE]),
            "foil_price": parse_value(row[COL_FOIL_PRICE]),
            "cardmarket_url": str(row[COL_CARDMARKET_URL]),
            "current_price": parse_value(row[COL_CURRENT_PRICE])
            if len(row) > COL_CURRENT_PRICE
            else None,
            "trend_price": parse_value(row[COL_TREND_PRICE])
            if len(row) > COL_TREND_PRICE
            else None,
            "avg_30_days": parse_value(row[COL_AVG_30_DAYS])
            if len(row) > COL_AVG_30_DAYS
            else None,
            "available_items": int(row[COL_AVAILABLE_ITEMS])
            if len(row) > COL_AVAILABLE_ITEMS and row[COL_AVAILABLE_ITEMS]
            else None,
        }
        cards.append(Card(**card_data))

    return cards


def update_card_prices(service, row: int, price_info: PriceInfo):
    try:
        sheet_id = get_sheet_id()

        ranges = [
            f"{SHEET_NAME}!N{row}",
        ]
        batch_result = (
            service.spreadsheets()
            .values()
            .batchGet(spreadsheetId=sheet_id, ranges=ranges)
            .execute()
        )

        value_ranges = batch_result.get("valueRanges", [])
        current_min = float("inf")
        if value_ranges and value_ranges[0].get("values"):
            try:
                value = value_ranges[0]["values"][0][0]
                if value and str(value).strip():
                    current_min = float(value)
            except (ValueError, IndexError):
                current_min = float("inf")

        new_min = (
            min(current_min, price_info.current_price)
            if current_min != 0
            else price_info.current_price
        )

        paris_tz = pytz.timezone("Europe/Paris")
        current_time = datetime.now(paris_tz).strftime("%d/%m/%Y %H:%M:%S")

        data = [
            {
                "range": f"{SHEET_NAME}!J{row}:O{row}",
                "values": [
                    [
                        price_info.current_price,
                        price_info.trend_price,
                        price_info.avg_30_days,
                        price_info.available_items,
                        new_min,
                        current_time,
                    ]
                ],
            }
        ]

        body = {"valueInputOption": "RAW", "data": data}

        service.spreadsheets().values().batchUpdate(
            spreadsheetId=sheet_id, body=body
        ).execute()

    except Exception as e:
        print(f"Erreur lors de la mise à jour des prix dans le sheet: {e}")
