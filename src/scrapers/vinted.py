from seleniumbase import SB
from bs4 import BeautifulSoup
from typing import Optional
from datetime import datetime
import pytz
from models.price_info import VintedPriceInfo
from utils.logger import setup_logger
from utils.string_matcher import is_title_match

logger = setup_logger(__name__)


def parse_vinted_listings(
    html_content: str, card_name: str
) -> Optional[VintedPriceInfo]:
    """Parse les annonces Vinted depuis le HTML de la page"""
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        logger.debug(f"Recherche des annonces pour '{card_name}'")

        for item in soup.find_all("div", class_="feed-grid__item"):
            # Ignorer les éléments avec la classe feed-grid__item--full-row
            if "feed-grid__item--full-row" in item.get("class", []):
                logger.info("Ignorer l'élément full-row (probablement une publicité)")
                continue

            link = item.find(
                "a", {"data-testid": lambda x: x and x.endswith("--overlay-link")}
            )
            if not link:
                continue

            # Nettoyer le titre en ne gardant que la partie avant ", marque"
            full_title = link.get("title", "")
            title = (
                full_title.split(", marque")[0]
                if ", marque" in full_title
                else full_title
            )
            logger.debug(f"Analyse de l'annonce : {title}")

            # Utiliser le nouveau système de correspondance
            if not is_title_match(card_name, title):
                logger.info(f"Titre non correspondant ignoré : {title}")
                continue

            # Si le titre correspond, chercher le prix
            price_text = item.find(
                "span",
                class_="web_ui__Text__text web_ui__Text__subtitle web_ui__Text__left web_ui__Text__clickable web_ui__Text__underline-none",
            )
            logger.debug(f"Prix trouvé : {price_text}")
            if price_text:
                try:
                    price = float(
                        price_text.text.strip().replace("€", "").replace(",", ".")
                    )
                    logger.debug(f"Premier prix valide trouvé pour '{title}' : {price}€")

                    paris_tz = pytz.timezone("Europe/Paris")
                    current_time = datetime.now(paris_tz)
                    item_url = link.get("href", "")

                    return VintedPriceInfo(
                        min_price=price, last_update=current_time, url=item_url
                    )
                except ValueError:
                    logger.error(f"Impossible de convertir le prix en float : {price_text.text}")
                    continue

        logger.debug(f"Aucun prix trouvé sur Vinted pour la carte '{card_name}'")
        return None

    except Exception as e:
        logger.error(f"Error parsing Vinted listings: {str(e)}")
        return None


def get_vinted_prices(card_name: str) -> Optional[VintedPriceInfo]:
    """Récupère les prix d'une carte sur Vinted"""
    search_url = f"https://www.vinted.fr/catalog?search_text=Lorcana+{card_name.replace(' ', '+')}&order=price_low_to_high&page=1&price_from=2&catalog[]=3224"
    logger.debug(f"URL de recherche : {search_url}")

    with SB(uc=True, headless=True) as sb:
        try:
            sb.open(search_url)
            sb.wait_for_element("div.feed-grid", timeout=10)
            page_content = sb.get_page_source()
            return parse_vinted_listings(page_content, card_name)

        except Exception as e:
            logger.error(f"Error getting prices from Vinted: {str(e)}")
            return None
