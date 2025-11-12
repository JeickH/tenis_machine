from config.database import get_db
from src.utils.logger import get_logger

logger = get_logger(__name__)

class ExternalPredictionsScraper:
    def __init__(self):
        self.db = get_db()

    def scrape_predictions_for_date(self, match_date):
        logger.info(f"External predictions scraping for {match_date} - stub implementation")
        return []

    def update_predictions(self):
        logger.info("External predictions update - stub implementation")
        return 0
