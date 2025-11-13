import requests
from bs4 import BeautifulSoup
from datetime import datetime
from config.database import get_db
from src.utils.logger import get_logger

logger = get_logger(__name__)

class BettingOddsFetcher:
    def __init__(self):
        self.db = get_db()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

        self.bookmakers = [
            {'name': 'Bet365', 'url': 'https://www.bet365.com'},
            {'name': 'Betfair', 'url': 'https://www.betfair.com'},
            {'name': 'William Hill', 'url': 'https://www.williamhill.com'},
            {'name': '888sport', 'url': 'https://www.888sport.com'},
            {'name': 'Betway', 'url': 'https://www.betway.com'}
        ]

    def fetch_odds_for_match(self, match_date, tournament_id, player_1_id, player_2_id,
                             player_1_name, player_2_name):
        logger.info(f"Fetching odds for {player_1_name} vs {player_2_name}")

        odds_found = False
        odds_data = []

        for bookmaker in self.bookmakers:
            try:
                odds = self._fetch_from_bookmaker(
                    bookmaker,
                    player_1_name,
                    player_2_name
                )

                if odds:
                    odds_data.append({
                        'match_date': match_date,
                        'tournament_id': tournament_id,
                        'player_1_id': player_1_id,
                        'player_2_id': player_2_id,
                        'bookmaker_name': bookmaker['name'],
                        'player_1_odds': odds['player_1'],
                        'player_2_odds': odds['player_2']
                    })
                    odds_found = True
                    logger.info(f"Found odds from {bookmaker['name']}: {odds['player_1']} - {odds['player_2']}")

            except Exception as e:
                logger.error(f"Error fetching from {bookmaker['name']}: {e}")
                continue

        if odds_data:
            self._save_odds(odds_data)
        else:
            logger.warning(f"No odds found for {player_1_name} vs {player_2_name}")

        return odds_data

    def _fetch_from_bookmaker(self, bookmaker, player_1_name, player_2_name):
        logger.info(f"Attempting to fetch from {bookmaker['name']}")

        if bookmaker['name'] == 'Bet365':
            return self._fetch_from_bet365(player_1_name, player_2_name)
        elif bookmaker['name'] == 'Betfair':
            return self._fetch_from_betfair(player_1_name, player_2_name)
        elif bookmaker['name'] == 'William Hill':
            return self._fetch_from_williamhill(player_1_name, player_2_name)
        elif bookmaker['name'] == '888sport':
            return self._fetch_from_888sport(player_1_name, player_2_name)
        elif bookmaker['name'] == 'Betway':
            return self._fetch_from_betway(player_1_name, player_2_name)

        return None

    def _fetch_from_bet365(self, player_1_name, player_2_name):
        try:
            url = "https://www.bet365.com/en/sports/tennis"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            return None

        except Exception as e:
            logger.debug(f"Bet365 fetch failed: {e}")
            return None

    def _fetch_from_betfair(self, player_1_name, player_2_name):
        try:
            url = "https://www.betfair.com/sport/tennis"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            return None

        except Exception as e:
            logger.debug(f"Betfair fetch failed: {e}")
            return None

    def _fetch_from_williamhill(self, player_1_name, player_2_name):
        try:
            url = "https://sports.williamhill.com/betting/en-gb/tennis"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            return None

        except Exception as e:
            logger.debug(f"William Hill fetch failed: {e}")
            return None

    def _fetch_from_888sport(self, player_1_name, player_2_name):
        try:
            url = "https://www.888sport.com/tennis"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            return None

        except Exception as e:
            logger.debug(f"888sport fetch failed: {e}")
            return None

    def _fetch_from_betway(self, player_1_name, player_2_name):
        try:
            url = "https://www.betway.com/tennis"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            return None

        except Exception as e:
            logger.debug(f"Betway fetch failed: {e}")
            return None

    def _save_odds(self, odds_data):
        for odds in odds_data:
            try:
                query = """
                    INSERT INTO betting_odds
                    (match_date, tournament_id, player_1_id, player_2_id,
                     bookmaker_name, player_1_odds, player_2_odds, fetched_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (match_date, player_1_id, player_2_id, bookmaker_name)
                    DO UPDATE SET
                        player_1_odds = EXCLUDED.player_1_odds,
                        player_2_odds = EXCLUDED.player_2_odds,
                        fetched_at = EXCLUDED.fetched_at
                """

                self.db.execute_query(
                    query,
                    (odds['match_date'], odds['tournament_id'], odds['player_1_id'],
                     odds['player_2_id'], odds['bookmaker_name'], odds['player_1_odds'],
                     odds['player_2_odds'], datetime.now())
                )

                logger.info(f"Saved odds from {odds['bookmaker_name']}")

            except Exception as e:
                logger.error(f"Error saving odds: {e}")

    def fetch_odds_for_todays_matches(self):
        today = datetime.now().date()

        query = """
            SELECT
                m.id, m.date, m.tournament_id,
                m.player_1_id, m.player_2_id,
                p1.name as player_1_name,
                p2.name as player_2_name,
                t.series
            FROM matches m
            JOIN players p1 ON m.player_1_id = p1.id
            JOIN players p2 ON m.player_2_id = p2.id
            JOIN tournaments t ON m.tournament_id = t.id
            WHERE m.date = %s
            AND m.winner_id IS NULL
            AND t.series IN ('ATP500', 'Masters 1000', 'Grand Slam')
        """

        matches = self.db.execute_query(query, (today,), fetch=True)
        logger.info(f"Found {len(matches)} matches to fetch odds for")

        total_odds = 0
        for match in matches:
            odds_data = self.fetch_odds_for_match(
                match['date'],
                match['tournament_id'],
                match['player_1_id'],
                match['player_2_id'],
                match['player_1_name'],
                match['player_2_name']
            )
            total_odds += len(odds_data)

        logger.info(f"Fetched odds from {total_odds} bookmakers")
        return total_odds

    def create_sample_odds_for_testing(self, match_date, tournament_id,
                                      player_1_id, player_2_id):
        logger.info("Creating sample odds for testing")

        sample_odds = [
            {
                'match_date': match_date,
                'tournament_id': tournament_id,
                'player_1_id': player_1_id,
                'player_2_id': player_2_id,
                'bookmaker_name': 'Bet365',
                'player_1_odds': 1.75,
                'player_2_odds': 2.10
            },
            {
                'match_date': match_date,
                'tournament_id': tournament_id,
                'player_1_id': player_1_id,
                'player_2_id': player_2_id,
                'bookmaker_name': 'Betfair',
                'player_1_odds': 1.80,
                'player_2_odds': 2.05
            }
        ]

        self._save_odds(sample_odds)
        logger.info(f"Created {len(sample_odds)} sample odds entries")
        return len(sample_odds)
