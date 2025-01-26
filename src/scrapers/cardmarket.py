from seleniumbase import SB
from bs4 import BeautifulSoup
from models.price_info import PriceInfo
from typing import Optional
import time


def parse_price_info(html_content: str) -> Optional[PriceInfo]:
    """Parse les informations de prix depuis le HTML de la page"""
    try:
        soup = BeautifulSoup(html_content, "html.parser")

        info_container = soup.find("div", class_="info-list-container")
        if not info_container:
            return None

        # Helper function to get price from dt/dd pairs
        def get_price_by_label(label: str) -> float:
            dt = info_container.find("dt", string=label)
            if dt:
                dd = dt.find_next("dd")
                if dd:
                    text = dd.get_text().strip()
                    return float(text.replace("€", "").replace(",", ".").strip())
            return 0

        # Prix actuel (De)
        current_price = get_price_by_label("De")

        # Prix tendance
        trend_price = get_price_by_label("Tendance des prix")

        # Moyenne 30 jours
        avg_30_days = get_price_by_label("Prix moyen 30 jours")

        # Nombre d'items disponibles
        available_dt = info_container.find("dt", string="Articles disponibles")
        available_items = 0
        if available_dt:
            available_dd = available_dt.find_next("dd")
            if available_dd:
                available_items = int(available_dd.text.strip())

        return PriceInfo.model_validate(
            {
                "current_price": current_price,
                "trend_price": trend_price,
                "avg_30_days": avg_30_days,
                "available_items": available_items,
            }
        )
    except Exception as e:
        print(f"Error parsing price info: {str(e)}")
        return None


def get_cardmarket_price(card_url: str) -> Optional[PriceInfo]:
    """Récupère les informations de prix d'une carte sur Cardmarket"""
    with SB(uc=True, headless=True) as sb:
        try:
            full_url = f"https://www.cardmarket.com{card_url}"
            sb.open(full_url)
            time.sleep(2)  # Attente du chargement initial

            # Attendre que les infos soient chargées
            sb.wait_for_element("div.info-list-container", timeout=10)

            # Récupérer le contenu HTML et le parser
            page_content = sb.get_page_source()
            return parse_price_info(page_content)

        except Exception as e:
            print(f"Error getting price from Cardmarket: {str(e)}")
            return None
