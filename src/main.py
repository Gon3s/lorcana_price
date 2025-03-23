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
from utils.email_notifier import send_price_alert

logger = setup_logger(__name__)
settings = get_settings()

def process_card(card, service, sheet_id, sheet_name, sources):
    """Traite une carte individuelle"""
    logger.info(f"\nTraitement de : {card.name_fr}")

    cardmarket_price_info = None
    vinted_price_info = None
    latest_cardmarket_price = card.current_price

    if "cardmarket" in sources and card.cardmarket_url:
        cardmarket_price_info = get_cardmarket_price(card.cardmarket_url)
        if cardmarket_price_info:
            update_card_prices(
                service, sheet_id, sheet_name, card.row, cardmarket_price_info
            )
            latest_cardmarket_price = cardmarket_price_info.current_price

    if "vinted" in sources:
        vinted_price_info = get_vinted_prices(card.name_fr)
        if not vinted_price_info:
            # Si on n'a pas de prix Vinted, on ne peut pas mettre à jour
            logger.warning(
                f"Pas de prix Vinted disponible pour {card.name_fr}, impossible de mettre à jour"
            )
            return

        old_vinted_url = card.vinted_url

        update_vinted_price(service, sheet_id, sheet_name, card.row, vinted_price_info)

        if vinted_price_info and latest_cardmarket_price:
            # Vérifie qu'on a un prix Cardmarket
            vinted_price = vinted_price_info.min_price
            price_diff = latest_cardmarket_price - vinted_price

            # Si le prix Vinted est inférieur avec une différence minimale
            if (
                price_diff > 0
                and (price_diff / latest_cardmarket_price * 100)
                >= settings.min_price_diff_percent
                and old_vinted_url != vinted_price_info.urlSearch
            ):
                send_price_alert(
                    card_name=card.name_fr,
                    cardmarket_price=latest_cardmarket_price,
                    vinted_price=vinted_price,
                    vinted_url=vinted_price_info.url,
                    difference=price_diff,
                )

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
