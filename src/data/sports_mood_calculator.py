from config.database import get_db
from src.utils.database_utils import get_player_last_n_matches
from src.utils.logger import get_logger
from config.settings import SPORTS_MOOD_WEIGHTS

logger = get_logger(__name__)

class SportsMoodCalculator:
    def __init__(self):
        self.db = get_db()
        self.weights = SPORTS_MOOD_WEIGHTS

    def calculate_match_difficulty(self, match, player_id):
        if match['winner_id'] == player_id:
            is_win = True
            opponent_id = match['player_2_id'] if match['player_1_id'] == player_id else match['player_1_id']
        else:
            is_win = False
            opponent_id = match['player_1_id'] if match['player_2_id'] == player_id else match['player_2_id']

        player_rank = match['rank_1'] if match['player_1_id'] == player_id else match['rank_2']
        opponent_rank = match['rank_1'] if match['player_1_id'] == opponent_id else match['rank_2']

        if not player_rank or not opponent_rank:
            return 'hard' if is_win else 'hard'

        rank_diff = player_rank - opponent_rank

        if is_win:
            return 'easy' if rank_diff < -20 else 'hard'
        else:
            return 'easy' if rank_diff > 20 else 'hard'

    def calculate_sports_mood(self, player_id):
        last_matches = get_player_last_n_matches(player_id, n=10)

        if not last_matches:
            logger.debug(f"No match history for player {player_id}")
            return 0.0, 0, 0, []

        mood_score = 0.0
        wins = 0
        losses = 0
        match_details = []

        for match in last_matches:
            is_winner = match['winner_id'] == player_id
            difficulty = self.calculate_match_difficulty(match, player_id)

            if is_winner:
                wins += 1
                weight = self.weights['easy_win'] if difficulty == 'easy' else self.weights['hard_win']
            else:
                losses += 1
                weight = self.weights['easy_loss'] if difficulty == 'easy' else self.weights['hard_loss']

            mood_score += weight

            match_details.append({
                'match_id': match['id'],
                'date': str(match['date']),
                'is_win': is_winner,
                'difficulty': difficulty,
                'weight': weight
            })

        return mood_score, wins, losses, match_details

    def update_player_sports_mood(self, player_id):
        mood_score, wins, losses, details = self.calculate_sports_mood(player_id)

        query = """
            INSERT INTO player_stats
            (player_id, sports_mood_score, last_10_matches_wins, last_10_matches_losses, last_10_matches_details)
            VALUES (%s, %s, %s, %s, %s::jsonb)
            ON CONFLICT (player_id) DO UPDATE SET
                sports_mood_score = EXCLUDED.sports_mood_score,
                last_10_matches_wins = EXCLUDED.last_10_matches_wins,
                last_10_matches_losses = EXCLUDED.last_10_matches_losses,
                last_10_matches_details = EXCLUDED.last_10_matches_details,
                updated_at = CURRENT_TIMESTAMP
        """

        import json
        self.db.execute_query(query, (player_id, mood_score, wins, losses, json.dumps(details)))
        logger.info(f"Updated sports mood for player {player_id}: {mood_score}")

        return mood_score

    def update_all_active_players(self):
        query = "SELECT id FROM players WHERE is_active = true"
        players = self.db.execute_query(query, fetch=True)

        updated_count = 0
        for player in players:
            try:
                self.update_player_sports_mood(player['id'])
                updated_count += 1
            except Exception as e:
                logger.error(f"Error updating sports mood for player {player['id']}: {e}")

        logger.info(f"Updated sports mood for {updated_count} players")
        return updated_count
