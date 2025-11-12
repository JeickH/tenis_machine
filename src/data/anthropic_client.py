from config.settings import ANTHROPIC_API_KEY, ANTHROPIC_MODEL
from src.utils.logger import get_logger

logger = get_logger(__name__)

class AnthropicClient:
    def __init__(self):
        self.api_key = ANTHROPIC_API_KEY
        self.model = ANTHROPIC_MODEL

    def search_missing_data(self, query):
        logger.info(f"Anthropic search - stub implementation for: {query}")
        return None
