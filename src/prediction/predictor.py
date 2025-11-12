import json
import pandas as pd
from datetime import datetime
from config.database import get_db
from src.models.model_factory import ModelFactory
from src.models.feature_engineer import FeatureEngineer
from src.prediction.match_fetcher import MatchFetcher
from src.utils.date_utils import get_today
from src.utils.logger import get_logger

logger = get_logger(__name__)

class Predictor:
    def __init__(self):
        self.db = get_db()
        self.active_model = None
        self.feature_engineer = None
        self.match_fetcher = MatchFetcher()

    def load_active_model(self):
        query = """
            SELECT * FROM models
            WHERE is_active = true
            ORDER BY validation_accuracy DESC
            LIMIT 1
        """

        result = self.db.execute_query(query, fetch=True)

        if not result:
            logger.error("No active model found")
            return None

        model_data = result[0]
        logger.info(f"Loading model: {model_data['model_type']} (ID: {model_data['id']})")

        model = ModelFactory.create_model(model_data['model_type'])
        model.load_model(model_data['model_file_path'])

        self.active_model = {
            'id': model_data['id'],
            'model': model,
            'model_data': model_data
        }

        self.feature_engineer = FeatureEngineer(model_data['feature_configuration_id'])

        return self.active_model

    def get_todays_matches(self, min_series=["ATP500", "Masters 1000", "Grand Slam"]):
        today = get_today()

        query = """
            SELECT
                m.id as match_id,
                m.date,
                m.tournament_id,
                m.player_1_id,
                m.player_2_id,
                m.surface_id,
                m.court_type_id,
                m.round_id,
                t.series as tournament_series,
                t.name as tournament_name,
                p1.name as player_1_name,
                p2.name as player_2_name,
                p1.current_rank as rank_1,
                p2.current_rank as rank_2,
                p1.current_points as pts_1,
                p2.current_points as pts_2,
                ps1.sports_mood_score as player_1_sports_mood,
                ps1.personal_mood_score as player_1_personal_mood,
                ps2.sports_mood_score as player_2_sports_mood,
                ps2.personal_mood_score as player_2_personal_mood,
                sh1.win_rate as player_1_surface_win_rate,
                sh2.win_rate as player_2_surface_win_rate
            FROM matches m
            JOIN tournaments t ON m.tournament_id = t.id
            JOIN players p1 ON m.player_1_id = p1.id
            JOIN players p2 ON m.player_2_id = p2.id
            LEFT JOIN player_stats ps1 ON m.player_1_id = ps1.player_id
            LEFT JOIN player_stats ps2 ON m.player_2_id = ps2.player_id
            LEFT JOIN surface_history sh1 ON m.player_1_id = sh1.player_id AND m.surface_id = sh1.surface_id
            LEFT JOIN surface_history sh2 ON m.player_2_id = sh2.player_id AND m.surface_id = sh2.surface_id
            WHERE m.date = %s
            AND m.winner_id IS NULL
            AND t.series = ANY(%s)
        """

        matches = self.db.execute_query(query, (today, min_series), fetch=True)
        logger.info(f"Found {len(matches)} matches for today ({today})")

        if not matches:
            return None

        df = pd.DataFrame(matches)

        decimal_cols = ['player_1_sports_mood', 'player_2_sports_mood',
                       'player_1_personal_mood', 'player_2_personal_mood',
                       'player_1_surface_win_rate', 'player_2_surface_win_rate']

        for col in decimal_cols:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: float(x) if x is not None else None)

        return df

    def prepare_match_features(self, match_df):
        features_df = self.feature_engineer.engineer_features(match_df, for_prediction=True)
        features_df = self.feature_engineer.apply_weights(features_df)

        feature_cols = self.feature_engineer.get_feature_columns()
        X = features_df[feature_cols]

        return X

    def predict_match(self, match_data):
        if not self.active_model:
            self.load_active_model()

        match_df = pd.DataFrame([match_data])
        X = self.prepare_match_features(match_df)

        model = self.active_model['model']
        prediction = model.predict(X)[0]
        probabilities = model.predict_proba(X)[0]

        predicted_winner_id = match_data['player_1_id'] if prediction == 1 else match_data['player_2_id']
        winner_probability = probabilities[1] if prediction == 1 else probabilities[0]

        predicted_sets = 3
        predicted_games = 20

        return {
            'predicted_winner_id': predicted_winner_id,
            'predicted_total_sets': predicted_sets,
            'predicted_total_games': predicted_games,
            'winner_probability': float(winner_probability),
            'confidence_score': float(max(probabilities))
        }

    def save_prediction(self, match_data, prediction):
        query = """
            INSERT INTO predictions
            (model_id, match_date, tournament_id, player_1_id, player_2_id,
             predicted_winner_id, predicted_total_sets, predicted_total_games,
             winner_probability, confidence_score, prediction_timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """

        result = self.db.execute_query(
            query,
            (
                self.active_model['id'],
                match_data['date'],
                match_data['tournament_id'],
                match_data['player_1_id'],
                match_data['player_2_id'],
                prediction['predicted_winner_id'],
                prediction['predicted_total_sets'],
                prediction['predicted_total_games'],
                prediction['winner_probability'],
                prediction['confidence_score'],
                datetime.now()
            ),
            fetch=True
        )

        prediction_id = result[0]['id']
        logger.info(f"Prediction saved with ID: {prediction_id}")
        return prediction_id

    def predict_all_today(self):
        logger.info("Starting predictions for today's matches")

        self.load_active_model()

        matches_df = self.get_todays_matches()

        if matches_df is None or len(matches_df) == 0:
            logger.info("No matches found for today")
            return []

        predictions = []

        for idx, match in matches_df.iterrows():
            try:
                prediction = self.predict_match(match.to_dict())
                prediction_id = self.save_prediction(match.to_dict(), prediction)

                predictions.append({
                    'prediction_id': prediction_id,
                    'match': f"{match['player_1_name']} vs {match['player_2_name']}",
                    'tournament': match['tournament_name'],
                    'predicted_winner': match['player_1_name'] if prediction['predicted_winner_id'] == match['player_1_id'] else match['player_2_name'],
                    'confidence': prediction['confidence_score']
                })

                logger.info(f"Predicted: {predictions[-1]['match']} -> {predictions[-1]['predicted_winner']}")

            except Exception as e:
                logger.error(f"Error predicting match {match['match_id']}: {e}")
                continue

        logger.info(f"Completed {len(predictions)} predictions")
        return predictions
