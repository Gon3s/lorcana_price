import unicodedata
import re
from thefuzz import fuzz
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Liste de mots à ignorer
STOP_WORDS = {
    "le",
    "la",
    "les",
    "de",
    "du",
    "des",
    "un",
    "une",
    "et",
    "ou",
    "en",
    "lorcana",
    "achat",
    "carte",
}

def normalize_text(text: str) -> str:
    """
    Normalise un texte en retirant les accents, la ponctuation,
    les mots vides et retourne les mots-clés importants
    """
    # Convertir en minuscules
    text = text.lower()

    # Retirer les accents
    text = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode()

    # Retirer la ponctuation et les caractères spéciaux
    text = re.sub(r"[^\w\s]", "", text)

    # Remplacer les espaces multiples par un seul espace
    text = re.sub(r"\s+", " ", text)

    # Filtrer les mots vides
    words = [w for w in text.split() if w not in STOP_WORDS]

    return " ".join(words)

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
        logger.info(f"Correspondance exacte trouvée: '{card_name}' dans '{title}'")
        return True

    # Vérification par ratio de similarité
    ratio = fuzz.partial_ratio(norm_card_name, norm_title)
    logger.debug(f"Ratio de similarité: {ratio}%")
    if ratio >= threshold:
        logger.info(
            f"Correspondance approximative ({ratio}%): '{card_name}' ~ '{title}'"
        )
        return True

    # Vérification par mots-clés
    card_keywords = set(norm_card_name.split())
    title_keywords = set(norm_title.split())
    common_keywords = card_keywords & title_keywords

    logger.debug(f"Mots-clés communs: {len(common_keywords)}>{len(card_keywords)*0.8}")
    if (
        len(common_keywords) >= len(card_keywords) * 0.8
    ):  # 80% des mots-clés doivent correspondre
        logger.debug(f"Correspondance par mots-clés: {common_keywords}")
        return True

    logger.debug(f"Pas de correspondance: '{card_name}' ≠ '{title}'")
    return False
