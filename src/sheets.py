from datetime import datetime
import pytz
from typing import List
from pydantic import BaseModel
from googleapiclient.discovery import build
from google.oauth2 import service_account
from urllib.parse import urlparse

from models.price_info import PriceInfo, VintedPriceInfo
from models.card import Card
from utils.logger import setup_logger

logger = setup_logger(__name__)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Indices des colonnes dans le Google Sheet
COL_NAME_EN = 0
COL_NAME_FR = 1
COL_CARDMARKET_URL = 8
COL_CURRENT_PRICE = 9  # J - Prix actuel
COL_TREND_PRICE = 10  # K - Prix tendance
COL_AVG_30_DAYS = 11  # L - Moyenne 30 jours
COL_AVAILABLE_ITEMS = 12  # M - Articles disponibles
COL_MIN_PRICE = 13  # N - Prix Min
COL_LAST_UPDATE = 14  # O - Dernière MAJ
COL_VINTED_MIN = 15  # P - Prix Vinted
COL_VINTED_LAST_UPDATE = 16  # Q - Dernière MAJ Vinted
COL_VINTED_URL = 17  # R - URL Vinted
COL_VINTED_URL_SEARCH = 18  # S - URL de recherche Vinted


class CardToTrack(BaseModel):
    """Représente une carte à suivre"""
    name_fr: str
    cardmarket_url: str | None
    row: int


def get_google_sheets_service(credentials_file: str):
    """Initialise le service Google Sheets"""
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = service_account.Credentials.from_service_account_file(
        credentials_file, scopes=SCOPES
    )
    return build("sheets", "v4", credentials=credentials)


def get_sheet_id(sheets_url: str) -> str:
    """Extrait l'ID du document depuis l'URL"""
    path = urlparse(sheets_url).path
    return path.split("/")[3]


def get_cards_to_track(service, sheet_id: str, sheet_name: str) -> List[Card]:
    """Récupère la liste des cartes à suivre depuis le Google Sheet"""
    try:
        result = (
            service.spreadsheets()
            .values()
            .get(
                spreadsheetId=sheet_id,
                range=f"{sheet_name}!A2:S",
            )
            .execute()
        )

        rows = result.get("values", [])
        cards = []

        for i, row in enumerate(rows, start=2):
            # Conversion du prix avec gestion des erreurs
            try:
                current_price = (
                    float(
                        row[COL_CURRENT_PRICE]
                        .replace("€", "")
                        .replace(",", ".")
                        .strip()
                    )
                    if row[COL_CURRENT_PRICE]
                    else None
                )
            except (ValueError, IndexError):
                current_price = None

            card = Card(
                name_en=row[COL_NAME_EN],
                name_fr=row[COL_NAME_FR],
                cardmarket_url=row[COL_CARDMARKET_URL],
                current_price=current_price,
                vinted_url=row[COL_VINTED_URL_SEARCH]
                if len(row) > COL_VINTED_URL_SEARCH
                else None,
                row=i,
            )
            cards.append(card)

        return cards

    except Exception as e:
        logger.error(f"Erreur lors de la lecture du sheet: {e}")
        return []


def update_card_prices(
    service, sheet_id: str, sheet_name: str, row: int, price_info: PriceInfo
):
    """Met à jour les prix Cardmarket pour une carte"""
    try:
        ranges = [
            f"{sheet_name}!{chr(65 + COL_MIN_PRICE)}{row}",
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
                "range": f"{sheet_name}!{chr(65 + COL_CURRENT_PRICE)}{row}:{chr(65 + COL_LAST_UPDATE)}{row}",
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
        logger.error(f"Erreur lors de la mise à jour des prix dans le sheet: {e}")


def update_vinted_price(
    service, sheet_id: str, sheet_name: str, row: int, price_info: VintedPriceInfo
):
    """Met à jour le prix Vinted et la date pour une carte"""
    try:
        paris_tz = pytz.timezone("Europe/Paris")
        current_time = price_info.last_update.astimezone(paris_tz).strftime(
            "%d/%m/%Y %H:%M:%S"
        )

        data = [
            {
                "range": f"{sheet_name}!P{row}:S{row}",
                "values": [
                    [
                        price_info.min_price,
                        current_time,
                        price_info.url,
                        price_info.urlSearch,
                    ]
                ],
            }
        ]

        body = {"valueInputOption": "RAW", "data": data}

        service.spreadsheets().values().batchUpdate(
            spreadsheetId=sheet_id, body=body
        ).execute()

    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du prix Vinted dans le sheet: {e}")
