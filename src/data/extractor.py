from src.data.kaggle_fetcher import KaggleFetcher
from src.data.match_loader import MatchLoader
from src.data.sports_mood_calculator import SportsMoodCalculator
from src.data.surface_history_calculator import SurfaceHistoryCalculator
from src.data.personal_mood_fetcher import PersonalMoodFetcher
from src.data.external_predictions_scraper import ExternalPredictionsScraper
from src.utils.logger import get_logger

logger = get_logger(__name__)

class DataExtractor:
    def __init__(self):
        self.kaggle_fetcher = KaggleFetcher()
        self.match_loader = MatchLoader()
        self.sports_mood_calculator = SportsMoodCalculator()
        self.surface_history_calculator = SurfaceHistoryCalculator()
        self.personal_mood_fetcher = PersonalMoodFetcher()
        self.external_predictions_scraper = ExternalPredictionsScraper()

    def extract_and_load_all_data(self):
        logger.info("Starting full data extraction and loading")

        logger.info("Step 1: Loading match data from Kaggle")
        df = self.kaggle_fetcher.get_latest_data()
        if df is None:
            logger.error("Failed to load Kaggle data")
            return False

        loaded, skipped = self.match_loader.load_from_dataframe(df)
        logger.info(f"Loaded {loaded} matches, skipped {skipped}")

        logger.info("Step 2: Calculating sports mood scores")
        self.sports_mood_calculator.update_all_active_players()

        logger.info("Step 3: Calculating surface history")
        self.surface_history_calculator.update_all_player_surfaces()

        logger.info("Step 4: Fetching personal mood data (stub)")
        self.personal_mood_fetcher.update_all_active_players()

        logger.info("Step 5: Scraping external predictions (stub)")
        self.external_predictions_scraper.update_predictions()

        logger.info("Data extraction completed successfully")
        return True

    def update_daily_data(self, since_date):
        logger.info(f"Updating data since {since_date}")

        df = self.kaggle_fetcher.get_new_matches_since_date(since_date)
        if df is not None and len(df) > 0:
            loaded, skipped = self.match_loader.load_from_dataframe(df)
            logger.info(f"Loaded {loaded} new matches, skipped {skipped}")

        self.sports_mood_calculator.update_all_active_players()
        self.surface_history_calculator.update_all_player_surfaces()

        logger.info("Daily data update completed")
        return True
