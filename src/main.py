from sheets import get_cards_to_track, update_card_prices, get_google_sheets_service
from scrapers.cardmarket import get_cardmarket_price
import time
from dotenv import load_dotenv

def main():
    try:
        load_dotenv()
        # Initialiser le service Google Sheets une seule fois
        service = get_google_sheets_service()

        cards = get_cards_to_track()
        print(f"Nombre de cartes trouvées : {len(cards)}")

        for i, card in enumerate(cards, start=2):  # start=2 car ligne 1 = headers
            print(f"\nTraitement de : {card.name_fr}")
            print(f"URL Cardmarket : {card.cardmarket_url}")

            # Récupération du prix avec retry en cas d'erreur
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    price_info = get_cardmarket_price(card.cardmarket_url)
                    if price_info:
                        print("Prix trouvés :")
                        print(f"Prix actuel : {price_info.current_price}€")
                        print(f"Prix tendance : {price_info.trend_price}€")
                        print(f"Moyenne 30 jours : {price_info.avg_30_days}€")
                        print(f"Items disponibles : {price_info.available_items}")

                        # Mise à jour du Google Sheet avec le service
                        update_card_prices(service, i, price_info)
                        print("Google Sheet mis à jour")
                        break

                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"Tentative {attempt + 1} échouée, nouvelle tentative...")
                        time.sleep(2)
                    else:
                        print(f"Erreur finale : {e}")

    except Exception as e:
        print(f"Erreur générale : {e}")

if __name__ == "__main__":
    main()
