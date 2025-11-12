import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = DATA_DIR / "models"
LOGS_DIR = BASE_DIR / "logs"

DEFAULT_TRAIN_SPLIT = 0.8
DEFAULT_VAL_SPLIT = 0.2
DEFAULT_TEST_SPLIT = 0.0
DEFAULT_RANDOM_SEED = 42
USE_ERROR_FEEDBACK = False

MIN_TOURNAMENT_SERIES = ["ATP500", "Masters 1000", "Grand Slam"]

KAGGLE_DATASET_URL = "https://www.kaggle.com/datasets/dissfya/atp-tennis-2000-2023daily-pull"

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = "claude-3-5-sonnet-20241022"

EXTERNAL_PREDICTION_SOURCES = [
    {
        "name": "WinnerOdds",
        "url": "https://winnerodds.com/es/tenis/",
        "transparency": "High"
    },
    {
        "name": "Odds Scanner",
        "url": "https://oddsscanner.com/es/pronosticos/tenis",
        "transparency": "Low"
    },
    {
        "name": "William Hill News",
        "url": "https://www.williamhill.es/news/pronosticos-tenis",
        "transparency": "Low"
    },
    {
        "name": "Tipstrr",
        "url": "https://tipstrr.com/",
        "transparency": "Variable"
    }
]

SPORTS_MOOD_WEIGHTS = {
    "easy_win": 2.0,
    "hard_win": 1.0,
    "easy_loss": -2.0,
    "hard_loss": -1.0
}

PERSONAL_MOOD_CATEGORIES = {
    "positive": ["marriage", "birth", "vacation", "achievement", "award"],
    "negative": ["injury", "scandal", "breakup", "family_issue", "accident"]
}

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

SCHEDULER_JOBS = {
    "data_update": {
        "schedule": "cron",
        "hour": 6,
        "minute": 0,
        "description": "Daily data update"
    },
    "predictions": {
        "schedule": "cron",
        "hour": 8,
        "minute": 0,
        "description": "Daily predictions"
    },
    "error_analysis": {
        "schedule": "cron",
        "hour": 22,
        "minute": 0,
        "description": "Daily error analysis"
    },
    "training": {
        "schedule": "cron",
        "day_of_week": "sun",
        "hour": 2,
        "minute": 0,
        "description": "Weekly model training"
    }
}
