import argparse
from sheets import (
    get_cards_to_track,
    update_card_prices,
    get_google_sheets_service,
    get_sheet_id,
    update_vinted_price,
)
from scrapers.cardmarket import get_cardmarket_price
from scrapers.vinted import get_vinted_prices
import time
from dotenv import load_dotenv
import os
from utils.logger import setup_logger

logger = setup_logger(__name__)

def track_prices(
    sheets_url: str, sheet_name: str, max_retries: int, delay: int, sources: list[str]
):
    try:
        # Récupérer les credentials depuis .env
        credentials_file = os.getenv(
            "GOOGLE_SHEETS_CREDENTIALS_FILE", "service-account.json"
        )
        service = get_google_sheets_service(credentials_file)
        sheet_id = get_sheet_id(sheets_url)

        # Récupération des cartes
        cards = get_cards_to_track(service, sheet_id, sheet_name)
        logger.info(f"Nombre de cartes trouvées : {len(cards)}")

        for i, card in enumerate(cards, start=2):
            logger.info(f"\nTraitement de : {card.name_fr}")

            if "cardmarket" in sources and card.cardmarket_url:
                logger.info("Recherche sur Cardmarket...")
                for attempt in range(max_retries):
                    try:
                        price_info = get_cardmarket_price(card.cardmarket_url)
                        if price_info:
                            logger.info("Prix Cardmarket trouvés :")
                            logger.info(f"Prix actuel : {price_info.current_price}€")
                            logger.info(f"Prix tendance : {price_info.trend_price}€")
                            logger.info(f"Moyenne 30 jours : {price_info.avg_30_days}€")
                            logger.info(
                                f"Items disponibles : {price_info.available_items}"
                            )

                            update_card_prices(
                                service, sheet_id, sheet_name, i, price_info
                            )
                            logger.info("Prix Cardmarket mis à jour")
                            break
                    except Exception as e:
                        if attempt < max_retries - 1:
                            logger.warning(
                                f"Tentative {attempt + 1} échouée, nouvelle tentative..."
                            )
                            time.sleep(delay)
                        else:
                            logger.error(f"Erreur Cardmarket : {e}")

            if "vinted" in sources:
                logger.info("Recherche sur Vinted...")
                for attempt in range(max_retries):
                    try:
                        vinted_info = get_vinted_prices(card.name_fr)
                        if vinted_info:
                            logger.info(
                                f"Prix minimum Vinted : {vinted_info.min_price}€"
                            )
                            update_vinted_price(
                                service, sheet_id, sheet_name, i, vinted_info
                            )
                            logger.info("Prix Vinted mis à jour")
                            break
                    except Exception as e:
                        if attempt < max_retries - 1:
                            logger.warning(
                                f"Tentative {attempt + 1} échouée, nouvelle tentative..."
                            )
                            time.sleep(delay)
                        else:
                            logger.error(f"Erreur Vinted : {e}")

    except Exception as e:
        logger.error(f"Erreur générale : {e}")

if __name__ == "__main__":
    load_dotenv()

    parser = argparse.ArgumentParser(description="Suivi des prix des cartes Lorcana")
    parser.add_argument(
        "--sheet-name",
        "-s",
        default=os.getenv("SHEET_NAME", "data"),
        help="Nom de l'onglet dans le Google Sheet (défaut: data)",
    )
    parser.add_argument(
        "--retries",
        "-r",
        type=int,
        default=3,
        help="Nombre maximum de tentatives par carte (défaut: 3)",
    )
    parser.add_argument(
        "--delay",
        "-d",
        type=int,
        default=2,
        help="Délai entre les tentatives en secondes (défaut: 2)",
    )
    parser.add_argument(
        "--sources",
        choices=["cardmarket", "vinted", "all"],
        default="all",
        help="Sources de prix à vérifier (défaut: all)",
    )

    args = parser.parse_args()

    sheets_url = os.getenv("GOOGLE_SHEETS_URL")
    if not sheets_url:
        logger.error("Erreur: GOOGLE_SHEETS_URL non défini dans .env")
        exit(1)

    sources = ["cardmarket", "vinted"] if args.sources == "all" else [args.sources]
    track_prices(sheets_url, args.sheet_name, args.retries, args.delay, sources)
