import argparse
from scrapers.cardmarket import get_cardmarket_price
from scrapers.vinted import get_vinted_prices
from dotenv import load_dotenv
from sheets import (
    get_cards_to_track,
    get_google_sheets_service,
    get_sheet_id,
    update_card_prices,
    update_vinted_price,
)
from utils.logger import setup_logger
from config import get_settings

logger = setup_logger(__name__)
settings = get_settings()

def process_card(card, service, sheet_id, sheet_name, sources):
    """Traite une carte individuelle"""
    logger.info(f"\nTraitement de : {card.name_fr}")

    if "cardmarket" in sources and card.cardmarket_url:
        price_info = get_cardmarket_price(card.cardmarket_url)
        if price_info:
            update_card_prices(service, sheet_id, sheet_name, card.row, price_info)

    if "vinted" in sources:
        vinted_info = get_vinted_prices(card.name_fr)
        if vinted_info:
            update_vinted_price(service, sheet_id, sheet_name, card.row, vinted_info)


def track_prices(sheets_url: str, sheet_name: str, sources: list[str]):
    try:
        service = get_google_sheets_service(settings.google_sheets_credentials_file)
        sheet_id = get_sheet_id(sheets_url)

        cards = get_cards_to_track(service, sheet_id, sheet_name)
        logger.info(f"Nombre de cartes trouvées : {len(cards)}")

        for card in cards:
            process_card(card, service, sheet_id, sheet_name, sources)

    except Exception as e:
        logger.error(f"Erreur générale : {e}")

def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Suivi des prix des cartes Lorcana")
    parser.add_argument(
        "--sheet-name",
        "-s",
        default=settings.sheet_name,
        help=f"Nom de l'onglet dans le Google Sheet (défaut: {settings.sheet_name})",
    )
    parser.add_argument(
        "--sources",
        choices=["cardmarket", "vinted", "all"],
        default="all",
        help="Sources de prix à vérifier (défaut: all)",
    )

    args = parser.parse_args()

    if not settings.google_sheets_url:
        logger.error("Erreur: GOOGLE_SHEETS_URL non défini dans .env")
        exit(1)

    sources = ["cardmarket", "vinted"] if args.sources == "all" else [args.sources]
    track_prices(settings.google_sheets_url, args.sheet_name, sources)


if __name__ == "__main__":
    main()
