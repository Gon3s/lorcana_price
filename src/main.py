import argparse
from sheets import (
    get_cards_to_track,
    update_card_prices,
    get_google_sheets_service,
    get_sheet_id,
)
from scrapers.cardmarket import get_cardmarket_price
import time
from dotenv import load_dotenv
import os


def track_prices(sheets_url: str, sheet_name: str, max_retries: int, delay: int):
    try:
        # Récupérer les credentials depuis .env
        credentials_file = os.getenv(
            "GOOGLE_SHEETS_CREDENTIALS_FILE", "service-account.json"
        )
        service = get_google_sheets_service(credentials_file)
        sheet_id = get_sheet_id(sheets_url)

        # Récupération des cartes
        cards = get_cards_to_track(service, sheet_id, sheet_name)
        print(f"Nombre de cartes trouvées : {len(cards)}")

        for i, card in enumerate(cards, start=2):
            print(f"\nTraitement de : {card.name_fr}")
            print(f"URL Cardmarket : {card.cardmarket_url}")

            for attempt in range(max_retries):
                try:
                    price_info = get_cardmarket_price(card.cardmarket_url)
                    if price_info:
                        print("Prix trouvés :")
                        print(f"Prix actuel : {price_info.current_price}€")
                        print(f"Prix tendance : {price_info.trend_price}€")
                        print(f"Moyenne 30 jours : {price_info.avg_30_days}€")
                        print(f"Items disponibles : {price_info.available_items}")

                        update_card_prices(service, sheet_id, sheet_name, i, price_info)
                        print("Google Sheet mis à jour")
                        break

                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"Tentative {attempt + 1} échouée, nouvelle tentative...")
                        time.sleep(delay)
                    else:
                        print(f"Erreur finale : {e}")

    except Exception as e:
        print(f"Erreur générale : {e}")

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

    args = parser.parse_args()

    sheets_url = os.getenv("GOOGLE_SHEETS_URL")
    if not sheets_url:
        print("Erreur: GOOGLE_SHEETS_URL non défini dans .env")
        exit(1)

    track_prices(sheets_url, args.sheet_name, args.retries, args.delay)
