from scrapers.vinted import get_vinted_prices
from utils.logger import setup_logger


logger = setup_logger(__name__)

if __name__ == "__main__":
    print(get_vinted_prices("La Bête - Héros tragique"))
