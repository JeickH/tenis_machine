import requests
from bs4 import BeautifulSoup
from datetime import datetime
from config.database import get_db
from src.utils.database_utils import get_or_create_player, get_or_create_tournament
from src.utils.logger import get_logger

logger = get_logger(__name__)

class MatchFetcher:
    def __init__(self):
        self.db = get_db()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def fetch_todays_matches_from_web(self):
        logger.info("Fetching today's ATP matches from web")

        matches = []

        try:
            matches.extend(self._fetch_from_flashscore())
        except Exception as e:
            logger.error(f"Error fetching from Flashscore: {e}")

        try:
            matches.extend(self._fetch_from_atptour())
        except Exception as e:
            logger.error(f"Error fetching from ATP Tour: {e}")

        logger.info(f"Found {len(matches)} matches from web sources")
        return matches

    def _fetch_from_atptour(self):
        logger.info("Attempting to fetch from ATP Tour website")

        url = "https://www.atptour.com/en/scores/current"

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            matches = []

            return matches

        except Exception as e:
            logger.error(f"Error scraping ATP Tour: {e}")
            return []

    def _fetch_from_flashscore(self):
        logger.info("Flashscore scraping - stub implementation")
        return []

    def save_scheduled_matches(self, matches_data):
        saved_count = 0

        for match in matches_data:
            try:
                player_1_id = get_or_create_player(match['player_1'])
                player_2_id = get_or_create_player(match['player_2'])
                tournament_id = get_or_create_tournament(match['tournament'], match.get('series'))

                surface_id = self._get_surface_id(match.get('surface', 'Hard'))
                court_type_id = self._get_court_type_id(match.get('court_type', 'Outdoor'))
                round_id = self._get_round_id(match.get('round', '1st Round'))

                query = """
                    SELECT id FROM matches
                    WHERE tournament_id = %s
                    AND date = %s
                    AND player_1_id = %s
                    AND player_2_id = %s
                """

                existing = self.db.execute_query(
                    query,
                    (tournament_id, match['date'], player_1_id, player_2_id),
                    fetch=True
                )

                if existing:
                    logger.debug(f"Match already exists: {match['player_1']} vs {match['player_2']}")
                    continue

                insert_query = """
                    INSERT INTO matches
                    (tournament_id, date, round_id, court_type_id, surface_id,
                     player_1_id, player_2_id, rank_1, rank_2)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """

                result = self.db.execute_query(
                    insert_query,
                    (tournament_id, match['date'], round_id, court_type_id, surface_id,
                     player_1_id, player_2_id, match.get('rank_1'), match.get('rank_2')),
                    fetch=True
                )

                if result:
                    saved_count += 1
                    logger.info(f"Saved scheduled match: {match['player_1']} vs {match['player_2']}")

            except Exception as e:
                logger.error(f"Error saving match: {e}")
                continue

        return saved_count

    def _get_surface_id(self, surface_name):
        query = "SELECT id FROM surfaces WHERE name = %s"
        result = self.db.execute_query(query, (surface_name,), fetch=True)
        return result[0]['id'] if result else 1

    def _get_court_type_id(self, court_type_name):
        query = "SELECT id FROM court_types WHERE name = %s"
        result = self.db.execute_query(query, (court_type_name,), fetch=True)
        return result[0]['id'] if result else 2

    def _get_round_id(self, round_name):
        query = "SELECT id FROM rounds WHERE name = %s"
        result = self.db.execute_query(query, (round_name,), fetch=True)
        return result[0]['id'] if result else 1

    def create_sample_match_for_testing(self):
        from src.data.sports_mood_calculator import SportsMoodCalculator
        from src.data.surface_history_calculator import SurfaceHistoryCalculator

        today = datetime.now().date()

        sample_match = {
            'player_1': 'Djokovic N.',
            'player_2': 'Alcaraz C.',
            'tournament': 'ATP Finals',
            'series': 'Masters 1000',
            'surface': 'Hard',
            'court_type': 'Indoor',
            'round': 'Semifinals',
            'date': today,
            'rank_1': 1,
            'rank_2': 2
        }

        matches = [sample_match]
        saved = self.save_scheduled_matches(matches)

        if saved > 0:
            player_1_id = get_or_create_player(sample_match['player_1'])
            player_2_id = get_or_create_player(sample_match['player_2'])

            logger.info("Calculating stats for sample players...")

            sports_mood_calc = SportsMoodCalculator()
            sports_mood_calc.update_player_sports_mood(player_1_id)
            sports_mood_calc.update_player_sports_mood(player_2_id)

            surface_calc = SurfaceHistoryCalculator()
            surface_id = self._get_surface_id(sample_match['surface'])
            surface_calc.update_player_surface_history(player_1_id, surface_id)
            surface_calc.update_player_surface_history(player_2_id, surface_id)

            logger.info("Stats calculated for sample players")

        logger.info(f"Created {saved} sample match(es) for testing")
        return saved
