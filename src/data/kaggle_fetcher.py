import pandas as pd
import requests
from pathlib import Path
from config.settings import RAW_DATA_DIR, KAGGLE_DATASET_URL
from src.utils.logger import get_logger

logger = get_logger(__name__)

class KaggleFetcher:
    def __init__(self):
        self.raw_data_dir = RAW_DATA_DIR
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)

    def download_dataset(self, force=False):
        output_file = self.raw_data_dir / "atp_tennis.csv"

        if output_file.exists() and not force:
            logger.info(f"Dataset already exists at {output_file}")
            return output_file

        logger.info("Dataset must be manually downloaded from Kaggle")
        logger.info(f"URL: {KAGGLE_DATASET_URL}")
        logger.info(f"Save it to: {output_file}")

        return None

    def get_latest_data(self):
        csv_file = self.raw_data_dir / "atp_tennis.csv"

        if not csv_file.exists():
            logger.error("ATP tennis dataset not found. Please download it first.")
            return None

        logger.info(f"Reading dataset from {csv_file}")
        return pd.read_csv(csv_file)

    def get_new_matches_since_date(self, since_date):
        df = self.get_latest_data()
        if df is None:
            return None

        df['Date'] = pd.to_datetime(df['Date'])
        new_matches = df[df['Date'] > pd.to_datetime(since_date)]

        logger.info(f"Found {len(new_matches)} new matches since {since_date}")
        return new_matches
