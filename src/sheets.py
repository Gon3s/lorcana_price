from datetime import datetime
import pytz
from typing import List
from dataclasses import dataclass
from googleapiclient.discovery import build
from google.oauth2 import service_account
from urllib.parse import urlparse

from models.price_info import PriceInfo, VintedPriceInfo
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Constantes pour les colonnes et l'API
RANGE = "A2:R"  # Mise à jour pour inclure la colonne Vinted URL
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
COL_VINTED_MIN = 15
COL_VINTED_LAST_UPDATE = 16
COL_VINTED_URL = 17  # Nouvelle colonne

# Définition des colonnes
COLUMN_NAME_FR = "B"
COLUMN_CARDMARKET_URL = "D"


@dataclass
class CardToTrack:
    """Représente une carte à suivre"""

    name_fr: str
    cardmarket_url: str | None


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


def get_cards_to_track(service, sheet_id: str, sheet_name: str) -> List[CardToTrack]:
    """Récupère la liste des cartes à suivre depuis Google Sheets"""
    try:
        # Lecture des données
        range_name = f"{sheet_name}!B2:D"  # De B2 à D pour nom_fr et cardmarket_url
        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=sheet_id, range=range_name)
            .execute()
        )
        values = result.get("values", [])

        cards = []
        for row in values:
            # Vérifier si la ligne a suffisamment de colonnes
            name_fr = row[0] if len(row) > 0 else None
            cardmarket_url = row[2] if len(row) > 2 else None

            if name_fr:  # Ne traiter que les lignes avec un nom
                cards.append(
                    CardToTrack(name_fr=name_fr, cardmarket_url=cardmarket_url)
                )

        return cards

    except Exception as e:
        raise Exception(f"Erreur lors de la récupération des cartes: {str(e)}")

def update_card_prices(
    service, sheet_id: str, sheet_name: str, row: int, price_info: PriceInfo
):
    """Met à jour les prix Cardmarket pour une carte"""
    try:
        ranges = [
            f"{sheet_name}!N{row}",
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
                "range": f"{sheet_name}!J{row}:O{row}",
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
    """Met à jour le prix minimum Vinted et la date pour une carte"""
    try:
        ranges = [
            f"{sheet_name}!P{row}",
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

        # Mettre à jour seulement si le nouveau prix est inférieur
        new_min = (
            min(current_min, price_info.min_price)
            if current_min != float("inf")
            else price_info.min_price
        )

        paris_tz = pytz.timezone("Europe/Paris")
        current_time = price_info.last_update.astimezone(paris_tz).strftime(
            "%d/%m/%Y %H:%M:%S"
        )

        data = [
            {
                "range": f"{sheet_name}!P{row}:R{row}",  # Mise à jour pour inclure l'URL
                "values": [[new_min, current_time, price_info.url]],
            }
        ]

        body = {"valueInputOption": "RAW", "data": data}

        service.spreadsheets().values().batchUpdate(
            spreadsheetId=sheet_id, body=body
        ).execute()

    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du prix Vinted dans le sheet: {e}")
