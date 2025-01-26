from src.scrapers.cardmarket import get_cardmarket_price


def test_single_card():
    # URL d'une carte Lorcana (Mickey, Brave Little Tailor par exemple)
    test_url = "/fr/Lorcana/Products/Singles/Azurite-Sea/Maui-Half-Shark?language=2"

    print("Récupération des prix...")
    price_info = get_cardmarket_price(test_url)

    if price_info:
        print("\nRésultats:")
        print(f"Prix actuel: {price_info.current_price}€")
        print(f"Prix tendance: {price_info.trend_price}€")
        print(f"Moyenne 30 jours: {price_info.avg_30_days}€")
        print(f"Articles disponibles: {price_info.available_items}")
    else:
        print("Échec de la récupération des prix")


if __name__ == "__main__":
    test_single_card()
