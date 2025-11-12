from src.models.implementations.xgboost_model import XGBoostModel
from src.utils.logger import get_logger

logger = get_logger(__name__)

class ModelFactory:
    @staticmethod
    def create_model(model_type):
        if model_type == "XGBoost":
            return XGBoostModel()
        else:
            logger.error(f"Unknown model type: {model_type}")
            raise ValueError(f"Unknown model type: {model_type}")

    @staticmethod
    def get_available_models():
        return ["XGBoost"]
