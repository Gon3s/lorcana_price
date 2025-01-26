from sheets import get_cards_to_track


def main():
    try:
        cards = get_cards_to_track()
        print(f"Nombre de cartes trouvées : {len(cards)}")
        print("\nExemple des 3 premières cartes :")
        for card in cards[:3]:
            print(f"\nCarte: {card.name_fr}")
            print(f"Prix: {card.price}€")
            print(f"Prix Foil: {card.foil_price}€")
            print(f"URL Cardmarket: {card.cardmarket_url}")
    except Exception as e:
        print(f"Erreur: {e}")


if __name__ == "__main__":
    main()
