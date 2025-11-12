from datetime import datetime
from config.database import get_db
from src.utils.date_utils import get_yesterday, get_date_range
from src.utils.logger import get_logger

logger = get_logger(__name__)

class ErrorAnalyzer:
    def __init__(self):
        self.db = get_db()

    def get_yesterdays_results(self):
        yesterday = get_yesterday()

        query = """
            SELECT
                p.id as prediction_id,
                p.model_id,
                p.player_1_id,
                p.player_2_id,
                p.predicted_winner_id,
                p.predicted_total_sets,
                p.predicted_total_games,
                m.id as match_id,
                m.winner_id as actual_winner_id,
                m.total_sets as actual_total_sets,
                m.total_games as actual_total_games,
                m.rank_1,
                m.rank_2,
                m.date
            FROM predictions p
            JOIN matches m ON p.player_1_id = m.player_1_id
                AND p.player_2_id = m.player_2_id
                AND p.match_date = m.date
            WHERE p.match_date = %s
            AND m.winner_id IS NOT NULL
            AND p.actual_winner_id IS NULL
        """

        results = self.db.execute_query(query, (yesterday,), fetch=True)
        logger.info(f"Found {len(results)} completed matches from yesterday")

        return results

    def calculate_ranking_flags(self, rank_1, rank_2):
        flags = {}

        flags['any_top_10'] = (rank_1 and rank_1 <= 10) or (rank_2 and rank_2 <= 10)
        flags['any_top_20'] = (rank_1 and rank_1 <= 20) or (rank_2 and rank_2 <= 20)
        flags['any_top_50'] = (rank_1 and rank_1 <= 50) or (rank_2 and rank_2 <= 50)
        flags['any_top_100'] = (rank_1 and rank_1 <= 100) or (rank_2 and rank_2 <= 100)

        flags['both_top_10'] = (rank_1 and rank_1 <= 10) and (rank_2 and rank_2 <= 10)
        flags['both_top_20'] = (rank_1 and rank_1 <= 20) and (rank_2 and rank_2 <= 20)
        flags['both_top_50'] = (rank_1 and rank_1 <= 50) and (rank_2 and rank_2 <= 50)
        flags['both_top_100'] = (rank_1 and rank_1 <= 100) and (rank_2 and rank_2 <= 100)

        return flags

    def analyze_prediction_error(self, result):
        winner_correct = result['predicted_winner_id'] == result['actual_winner_id']

        sets_error = abs(result['predicted_total_sets'] - result['actual_total_sets']) if result['actual_total_sets'] else 0
        games_error = abs(result['predicted_total_games'] - result['actual_total_games']) if result['actual_total_games'] else 0

        ranking_flags = self.calculate_ranking_flags(result['rank_1'], result['rank_2'])

        error_data = {
            'prediction_id': result['prediction_id'],
            'model_id': result['model_id'],
            'match_id': result['match_id'],
            'match_date': result['date'],
            'player_1_id': result['player_1_id'],
            'player_2_id': result['player_2_id'],
            'winner_correct': winner_correct,
            'sets_error': sets_error,
            'games_error': games_error,
            'player_1_rank': result['rank_1'],
            'player_2_rank': result['rank_2'],
            **ranking_flags
        }

        return error_data

    def save_error_analysis(self, error_data):
        query = """
            INSERT INTO prediction_errors
            (prediction_id, model_id, match_id, match_date, player_1_id, player_2_id,
             winner_correct, sets_error, games_error, player_1_rank, player_2_rank,
             both_top_10, both_top_20, both_top_50, both_top_100,
             any_top_10, any_top_20, any_top_50, any_top_100)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        self.db.execute_query(
            query,
            (
                error_data['prediction_id'], error_data['model_id'], error_data['match_id'],
                error_data['match_date'], error_data['player_1_id'], error_data['player_2_id'],
                error_data['winner_correct'], error_data['sets_error'], error_data['games_error'],
                error_data['player_1_rank'], error_data['player_2_rank'],
                error_data['both_top_10'], error_data['both_top_20'],
                error_data['both_top_50'], error_data['both_top_100'],
                error_data['any_top_10'], error_data['any_top_20'],
                error_data['any_top_50'], error_data['any_top_100']
            )
        )

        update_query = """
            UPDATE predictions
            SET actual_winner_id = %s, actual_total_sets = %s, actual_total_games = %s
            WHERE id = %s
        """

        self.db.execute_query(
            update_query,
            (error_data['actual_winner_id'], error_data['actual_total_sets'],
             error_data['actual_total_games'], error_data['prediction_id'])
        )

    def aggregate_metrics(self, model_id, period):
        start_date, end_date = get_date_range(period)

        query = """
            SELECT
                COUNT(*) as total_predictions,
                SUM(CASE WHEN winner_correct THEN 1 ELSE 0 END) as correct_winners,
                AVG(sets_error) as avg_sets_error,
                AVG(games_error) as avg_games_error,
                AVG(CASE WHEN any_top_10 AND winner_correct THEN 1.0 ELSE 0.0 END) as accuracy_top_10,
                AVG(CASE WHEN any_top_20 AND winner_correct THEN 1.0 ELSE 0.0 END) as accuracy_top_20,
                AVG(CASE WHEN any_top_50 AND winner_correct THEN 1.0 ELSE 0.0 END) as accuracy_top_50,
                AVG(CASE WHEN any_top_100 AND winner_correct THEN 1.0 ELSE 0.0 END) as accuracy_top_100,
                AVG(CASE WHEN both_top_10 AND winner_correct THEN 1.0 ELSE 0.0 END) as accuracy_both_top_10,
                AVG(CASE WHEN both_top_20 AND winner_correct THEN 1.0 ELSE 0.0 END) as accuracy_both_top_20,
                AVG(CASE WHEN both_top_50 AND winner_correct THEN 1.0 ELSE 0.0 END) as accuracy_both_top_50,
                AVG(CASE WHEN both_top_100 AND winner_correct THEN 1.0 ELSE 0.0 END) as accuracy_both_top_100
            FROM prediction_errors
            WHERE model_id = %s
            AND match_date BETWEEN %s AND %s
        """

        result = self.db.execute_query(query, (model_id, start_date, end_date), fetch=True)

        if not result or result[0]['total_predictions'] == 0:
            return None

        metrics = result[0]
        accuracy = metrics['correct_winners'] / metrics['total_predictions'] if metrics['total_predictions'] > 0 else 0

        metrics_data = {
            'model_id': model_id,
            'period': period,
            'start_date': start_date,
            'end_date': end_date,
            'total_predictions': int(metrics['total_predictions']),
            'correct_winners': int(metrics['correct_winners']),
            'accuracy': float(accuracy),
            'avg_sets_error': float(metrics['avg_sets_error'] or 0),
            'avg_games_error': float(metrics['avg_games_error'] or 0),
            'accuracy_top_10': float(metrics['accuracy_top_10'] or 0),
            'accuracy_top_20': float(metrics['accuracy_top_20'] or 0),
            'accuracy_top_50': float(metrics['accuracy_top_50'] or 0),
            'accuracy_top_100': float(metrics['accuracy_top_100'] or 0),
            'accuracy_both_top_10': float(metrics['accuracy_both_top_10'] or 0),
            'accuracy_both_top_20': float(metrics['accuracy_both_top_20'] or 0),
            'accuracy_both_top_50': float(metrics['accuracy_both_top_50'] or 0),
            'accuracy_both_top_100': float(metrics['accuracy_both_top_100'] or 0)
        }

        return metrics_data

    def save_metrics(self, metrics_data):
        query = """
            INSERT INTO error_metrics
            (model_id, period, start_date, end_date, total_predictions, correct_winners,
             accuracy, avg_sets_error, avg_games_error, accuracy_top_10, accuracy_top_20,
             accuracy_top_50, accuracy_top_100, accuracy_both_top_10, accuracy_both_top_20,
             accuracy_both_top_50, accuracy_both_top_100)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (model_id, period, end_date) DO UPDATE SET
                total_predictions = EXCLUDED.total_predictions,
                correct_winners = EXCLUDED.correct_winners,
                accuracy = EXCLUDED.accuracy,
                avg_sets_error = EXCLUDED.avg_sets_error,
                avg_games_error = EXCLUDED.avg_games_error,
                accuracy_top_10 = EXCLUDED.accuracy_top_10,
                accuracy_top_20 = EXCLUDED.accuracy_top_20,
                accuracy_top_50 = EXCLUDED.accuracy_top_50,
                accuracy_top_100 = EXCLUDED.accuracy_top_100,
                accuracy_both_top_10 = EXCLUDED.accuracy_both_top_10,
                accuracy_both_top_20 = EXCLUDED.accuracy_both_top_20,
                accuracy_both_top_50 = EXCLUDED.accuracy_both_top_50,
                accuracy_both_top_100 = EXCLUDED.accuracy_both_top_100,
                updated_at = CURRENT_TIMESTAMP
        """

        self.db.execute_query(
            query,
            (
                metrics_data['model_id'], metrics_data['period'], metrics_data['start_date'],
                metrics_data['end_date'], metrics_data['total_predictions'], metrics_data['correct_winners'],
                metrics_data['accuracy'], metrics_data['avg_sets_error'], metrics_data['avg_games_error'],
                metrics_data['accuracy_top_10'], metrics_data['accuracy_top_20'],
                metrics_data['accuracy_top_50'], metrics_data['accuracy_top_100'],
                metrics_data['accuracy_both_top_10'], metrics_data['accuracy_both_top_20'],
                metrics_data['accuracy_both_top_50'], metrics_data['accuracy_both_top_100']
            )
        )

    def analyze_yesterday(self):
        logger.info("Analyzing yesterday's predictions")

        results = self.get_yesterdays_results()

        if not results:
            logger.info("No results to analyze from yesterday")
            return

        for result in results:
            error_data = self.analyze_prediction_error(result)
            error_data['actual_winner_id'] = result['actual_winner_id']
            error_data['actual_total_sets'] = result['actual_total_sets']
            error_data['actual_total_games'] = result['actual_total_games']
            self.save_error_analysis(error_data)

        active_models_query = "SELECT DISTINCT model_id FROM predictions WHERE match_date = %s"
        active_models = self.db.execute_query(active_models_query, (get_yesterday(),), fetch=True)

        for model in active_models:
            model_id = model['model_id']

            for period in ['last_day', 'last_week', 'last_15_days', 'last_month']:
                metrics = self.aggregate_metrics(model_id, period)
                if metrics:
                    self.save_metrics(metrics)
                    logger.info(f"Saved {period} metrics for model {model_id}: Accuracy={metrics['accuracy']:.4f}")

        logger.info("Error analysis completed")
