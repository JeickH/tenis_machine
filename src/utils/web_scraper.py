import requests
from bs4 import BeautifulSoup
from time import sleep
from src.utils.logger import get_logger

logger = get_logger(__name__)

class WebScraper:
    def __init__(self, timeout=30, retry_count=3):
        self.timeout = timeout
        self.retry_count = retry_count
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def fetch_page(self, url):
        for attempt in range(self.retry_count):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < self.retry_count - 1:
                    sleep(2 ** attempt)
                else:
                    logger.error(f"Failed to fetch {url} after {self.retry_count} attempts")
                    raise

    def parse_html(self, html_content):
        return BeautifulSoup(html_content, 'html.parser')

    def fetch_and_parse(self, url):
        html = self.fetch_page(url)
        return self.parse_html(html)

    def close(self):
        self.session.close()
