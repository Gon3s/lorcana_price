import unicodedata
import re
from typing import List
from thefuzz import fuzz
from utils.logger import setup_logger

logger = setup_logger(__name__)


def normalize_text(text: str) -> str:
    """
    Normalise un texte en retirant les accents, la ponctuation et en mettant en minuscule
    """
    # Convertir en minuscules
    text = text.lower()

    # Retirer les accents
    text = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode()

    # Retirer la ponctuation et les caractères spéciaux
    text = re.sub(r"[^\w\s]", "", text)

    # Remplacer les espaces multiples par un seul espace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def extract_keywords(text: str) -> List[str]:
    """
    Extrait les mots-clés importants d'un texte
    """
    # Liste de mots à ignorer
    stop_words = {"le", "la", "les", "de", "du", "des", "un", "une", "et", "ou", "en"}

    words = normalize_text(text).split()
    return [w for w in words if w not in stop_words]


def is_title_match(card_name: str, title: str, threshold: int = 80) -> bool:
    """
    Vérifie si le titre correspond au nom de la carte

    Args:
        card_name: Nom de la carte à rechercher
        title: Titre de l'annonce
        threshold: Seuil de similarité (0-100)
    """
    norm_card_name = normalize_text(card_name)
    norm_title = normalize_text(title)

    # Vérification exacte après normalisation
    if norm_card_name in norm_title:
        logger.debug(f"Correspondance exacte trouvée: '{card_name}' dans '{title}'")
        return True

    # Vérification par ratio de similarité
    ratio = fuzz.partial_ratio(norm_card_name, norm_title)
    if ratio >= threshold:
        logger.debug(
            f"Correspondance approximative ({ratio}%): '{card_name}' ~ '{title}'"
        )
        return True

    # Vérification par mots-clés
    card_keywords = set(extract_keywords(card_name))
    title_keywords = set(extract_keywords(title))
    common_keywords = card_keywords & title_keywords

    if (
        len(common_keywords) >= len(card_keywords) * 0.8
    ):  # 80% des mots-clés doivent correspondre
        logger.debug(f"Correspondance par mots-clés: {common_keywords}")
        return True

    logger.debug(f"Pas de correspondance: '{card_name}' ≠ '{title}'")
    return False
