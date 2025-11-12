from config.database import get_db
from src.utils.database_utils import get_player_last_n_matches
from src.utils.logger import get_logger

logger = get_logger(__name__)

class SurfaceHistoryCalculator:
    def __init__(self):
        self.db = get_db()

    def calculate_surface_history(self, player_id, surface_id):
        last_matches = get_player_last_n_matches(player_id, n=10, surface_id=surface_id)

        wins = sum(1 for m in last_matches if m['winner_id'] == player_id)
        losses = len(last_matches) - wins
        win_rate = wins / len(last_matches) if last_matches else 0.0

        total_query = """
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN winner_id = %s THEN 1 ELSE 0 END) as total_wins
            FROM matches
            WHERE (player_1_id = %s OR player_2_id = %s)
            AND surface_id = %s
            AND winner_id IS NOT NULL
        """

        result = self.db.execute_query(
            total_query,
            (player_id, player_id, player_id, surface_id),
            fetch=True
        )

        total_wins = int(result[0]['total_wins']) if result and result[0]['total_wins'] else 0
        total_matches = int(result[0]['total']) if result and result[0]['total'] else 0
        total_losses = total_matches - total_wins

        return {
            'last_10_wins': wins,
            'last_10_losses': losses,
            'win_rate': win_rate,
            'total_wins': total_wins,
            'total_losses': total_losses
        }

    def update_player_surface_history(self, player_id, surface_id):
        stats = self.calculate_surface_history(player_id, surface_id)

        query = """
            INSERT INTO surface_history
            (player_id, surface_id, last_10_wins, last_10_losses, win_rate, total_wins, total_losses)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (player_id, surface_id) DO UPDATE SET
                last_10_wins = EXCLUDED.last_10_wins,
                last_10_losses = EXCLUDED.last_10_losses,
                win_rate = EXCLUDED.win_rate,
                total_wins = EXCLUDED.total_wins,
                total_losses = EXCLUDED.total_losses,
                last_updated = CURRENT_TIMESTAMP
        """

        self.db.execute_query(
            query,
            (player_id, surface_id, stats['last_10_wins'], stats['last_10_losses'],
             stats['win_rate'], stats['total_wins'], stats['total_losses'])
        )

        logger.info(f"Updated surface history for player {player_id}, surface {surface_id}")
        return stats

    def update_all_player_surfaces(self):
        surfaces_query = "SELECT id FROM surfaces"
        surfaces = self.db.execute_query(surfaces_query, fetch=True)

        players_query = "SELECT id FROM players WHERE is_active = true"
        players = self.db.execute_query(players_query, fetch=True)

        updated_count = 0
        for player in players:
            for surface in surfaces:
                try:
                    self.update_player_surface_history(player['id'], surface['id'])
                    updated_count += 1
                except Exception as e:
                    logger.error(f"Error updating surface history: {e}")

        logger.info(f"Updated {updated_count} player-surface combinations")
        return updated_count
