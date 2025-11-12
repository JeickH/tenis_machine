import pandas as pd
from pathlib import Path
from config.database import get_db
from src.utils.database_utils import (
    get_or_create_player,
    get_or_create_tournament,
    get_surface_id,
    get_court_type_id,
    get_round_id,
    match_exists,
    update_player_rank
)
from src.utils.date_utils import parse_date
from src.utils.logger import get_logger

logger = get_logger(__name__)

class MatchLoader:
    def __init__(self):
        self.db = get_db()

    def calculate_sets_and_games(self, score):
        if not score or score == '-1' or pd.isna(score):
            return None, None

        try:
            sets = score.split()
            total_sets = len(sets)
            total_games = 0

            for set_score in sets:
                games = set_score.split('-')
                if len(games) == 2:
                    total_games += int(games[0].strip()) + int(games[1].strip())

            return total_sets, total_games
        except Exception as e:
            logger.warning(f"Error parsing score '{score}': {e}")
            return None, None

    def load_match(self, match_data):
        try:
            player_1_id = get_or_create_player(match_data['Player_1'])
            player_2_id = get_or_create_player(match_data['Player_2'])
            tournament_id = get_or_create_tournament(match_data['Tournament'], match_data.get('Series'))
            surface_id = get_surface_id(match_data['Surface'])
            court_type_id = get_court_type_id(match_data['Court'])
            round_id = get_round_id(match_data['Round'])

            match_date = parse_date(match_data['Date'])

            existing_match = match_exists(tournament_id, match_date, player_1_id, player_2_id)
            if existing_match:
                logger.debug(f"Match already exists: {match_data['Player_1']} vs {match_data['Player_2']}")
                return existing_match

            winner_id = None
            if match_data.get('Winner'):
                if match_data['Winner'] == match_data['Player_1']:
                    winner_id = player_1_id
                elif match_data['Winner'] == match_data['Player_2']:
                    winner_id = player_2_id

            total_sets, total_games = self.calculate_sets_and_games(match_data.get('Score'))

            rank_1 = int(match_data['Rank_1']) if match_data.get('Rank_1') and match_data['Rank_1'] != -1 else None
            rank_2 = int(match_data['Rank_2']) if match_data.get('Rank_2') and match_data['Rank_2'] != -1 else None
            pts_1 = int(match_data['Pts_1']) if match_data.get('Pts_1') and match_data['Pts_1'] != -1 else None
            pts_2 = int(match_data['Pts_2']) if match_data.get('Pts_2') and match_data['Pts_2'] != -1 else None
            odd_1 = float(match_data['Odd_1']) if match_data.get('Odd_1') and match_data['Odd_1'] != -1.0 else None
            odd_2 = float(match_data['Odd_2']) if match_data.get('Odd_2') and match_data['Odd_2'] != -1.0 else None

            if rank_1 and pts_1:
                update_player_rank(player_1_id, rank_1, pts_1)
            if rank_2 and pts_2:
                update_player_rank(player_2_id, rank_2, pts_2)

            query = """
                INSERT INTO matches
                (tournament_id, date, round_id, court_type_id, surface_id, best_of,
                 player_1_id, player_2_id, winner_id, rank_1, rank_2, pts_1, pts_2,
                 odd_1, odd_2, score, total_sets, total_games)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """

            result = self.db.execute_query(
                query,
                (
                    tournament_id, match_date, round_id, court_type_id, surface_id,
                    match_data.get('Best of'), player_1_id, player_2_id, winner_id,
                    rank_1, rank_2, pts_1, pts_2, odd_1, odd_2,
                    match_data.get('Score'), total_sets, total_games
                ),
                fetch=True
            )

            match_id = result[0]['id']
            logger.info(f"Loaded match: {match_data['Player_1']} vs {match_data['Player_2']}")
            return match_id

        except Exception as e:
            logger.error(f"Error loading match: {e}")
            logger.error(f"Match data: {match_data}")
            raise

    def load_from_csv(self, csv_path):
        logger.info(f"Loading matches from {csv_path}")

        df = pd.read_csv(csv_path)
        total_matches = len(df)
        loaded_count = 0
        skipped_count = 0

        for idx, row in df.iterrows():
            try:
                match_id = self.load_match(row.to_dict())
                if match_id:
                    loaded_count += 1
                else:
                    skipped_count += 1

                if (idx + 1) % 100 == 0:
                    logger.info(f"Progress: {idx + 1}/{total_matches} matches processed")

            except Exception as e:
                logger.error(f"Error at row {idx}: {e}")
                skipped_count += 1
                continue

        logger.info(f"Finished loading. Loaded: {loaded_count}, Skipped: {skipped_count}")
        return loaded_count, skipped_count

    def load_from_dataframe(self, df):
        total_matches = len(df)
        loaded_count = 0
        skipped_count = 0

        for idx, row in df.iterrows():
            try:
                match_id = self.load_match(row.to_dict())
                if match_id:
                    loaded_count += 1
                else:
                    skipped_count += 1
            except Exception as e:
                logger.error(f"Error at row {idx}: {e}")
                skipped_count += 1
                continue

        return loaded_count, skipped_count
