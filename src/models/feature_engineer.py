import pandas as pd
import numpy as np
from config.database import get_db
from src.utils.database_utils import get_head_to_head
from src.utils.logger import get_logger

logger = get_logger(__name__)

class FeatureEngineer:
    def __init__(self, feature_configuration_id=None):
        self.db = get_db()
        self.feature_configuration_id = feature_configuration_id
        self.feature_weights = self._load_feature_weights()

    def _load_feature_weights(self):
        if not self.feature_configuration_id:
            return {feature: 1.0 for feature in self._get_feature_names()}

        query = """
            SELECT configuration FROM feature_configurations WHERE id = %s
        """
        result = self.db.execute_query(query, (self.feature_configuration_id,), fetch=True)

        if result:
            return result[0]['configuration']
        else:
            return {feature: 1.0 for feature in self._get_feature_names()}

    def _get_feature_names(self):
        return [
            'player_1_rank', 'player_2_rank', 'rank_difference',
            'player_1_points', 'player_2_points', 'points_difference',
            'player_1_sports_mood', 'player_2_sports_mood', 'sports_mood_difference',
            'player_1_personal_mood', 'player_2_personal_mood', 'personal_mood_difference',
            'player_1_surface_win_rate', 'player_2_surface_win_rate', 'surface_advantage',
            'h2h_player_1_wins', 'h2h_player_2_wins', 'h2h_total_matches',
            'tournament_series_encoded', 'surface_encoded', 'court_type_encoded', 'round_encoded',
            'player_1_last_5_win_rate', 'player_2_last_5_win_rate'
        ]

    def extract_features_from_db(self, limit=None):
        query = """
            SELECT
                m.id as match_id,
                m.date,
                m.player_1_id,
                m.player_2_id,
                m.winner_id,
                m.rank_1,
                m.rank_2,
                m.pts_1,
                m.pts_2,
                m.total_sets,
                m.total_games,
                m.surface_id,
                m.court_type_id,
                m.round_id,
                m.tournament_id,
                t.series as tournament_series,
                ps1.sports_mood_score as player_1_sports_mood,
                ps1.personal_mood_score as player_1_personal_mood,
                ps2.sports_mood_score as player_2_sports_mood,
                ps2.personal_mood_score as player_2_personal_mood,
                sh1.win_rate as player_1_surface_win_rate,
                sh2.win_rate as player_2_surface_win_rate
            FROM matches m
            JOIN tournaments t ON m.tournament_id = t.id
            LEFT JOIN player_stats ps1 ON m.player_1_id = ps1.player_id
            LEFT JOIN player_stats ps2 ON m.player_2_id = ps2.player_id
            LEFT JOIN surface_history sh1 ON m.player_1_id = sh1.player_id AND m.surface_id = sh1.surface_id
            LEFT JOIN surface_history sh2 ON m.player_2_id = sh2.player_id AND m.surface_id = sh2.surface_id
            WHERE m.winner_id IS NOT NULL
            AND m.rank_1 IS NOT NULL
            AND m.rank_2 IS NOT NULL
            ORDER BY m.date DESC
            {limit_clause}
        """

        limit_clause = f"LIMIT {limit}" if limit else ""
        query = query.format(limit_clause=limit_clause)

        matches = self.db.execute_query(query, fetch=True)
        logger.info(f"Extracted {len(matches)} matches from database")

        df = pd.DataFrame(matches)

        decimal_cols = ['player_1_sports_mood', 'player_2_sports_mood',
                       'player_1_personal_mood', 'player_2_personal_mood',
                       'player_1_surface_win_rate', 'player_2_surface_win_rate']

        for col in decimal_cols:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: float(x) if x is not None else None)

        return df

    def calculate_last_n_win_rate(self, player_id, n=5):
        query = """
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN winner_id = %s THEN 1 ELSE 0 END) as wins
            FROM (
                SELECT winner_id FROM matches
                WHERE (player_1_id = %s OR player_2_id = %s)
                AND winner_id IS NOT NULL
                ORDER BY date DESC
                LIMIT %s
            ) recent_matches
        """

        result = self.db.execute_query(query, (player_id, player_id, player_id, n), fetch=True)

        if result and result[0]['total'] > 0:
            return result[0]['wins'] / result[0]['total']
        return 0.0

    def engineer_features(self, df, for_prediction=False):
        logger.info("Engineering features")

        df['rank_difference'] = df['rank_1'] - df['rank_2']
        df['points_difference'] = df['pts_1'].fillna(0) - df['pts_2'].fillna(0)

        df['player_1_sports_mood'] = df['player_1_sports_mood'].fillna(0)
        df['player_2_sports_mood'] = df['player_2_sports_mood'].fillna(0)
        df['sports_mood_difference'] = df['player_1_sports_mood'] - df['player_2_sports_mood']

        df['player_1_personal_mood'] = df['player_1_personal_mood'].fillna(0)
        df['player_2_personal_mood'] = df['player_2_personal_mood'].fillna(0)
        df['personal_mood_difference'] = df['player_1_personal_mood'] - df['player_2_personal_mood']

        df['player_1_surface_win_rate'] = df['player_1_surface_win_rate'].fillna(0.5)
        df['player_2_surface_win_rate'] = df['player_2_surface_win_rate'].fillna(0.5)
        df['surface_advantage'] = df['player_1_surface_win_rate'] - df['player_2_surface_win_rate']

        h2h_data = []
        for idx, row in df.iterrows():
            h2h = get_head_to_head(row['player_1_id'], row['player_2_id'])
            h2h_data.append(h2h)

        h2h_df = pd.DataFrame(h2h_data)
        df['h2h_player_1_wins'] = h2h_df['player_1_wins']
        df['h2h_player_2_wins'] = h2h_df['player_2_wins']
        df['h2h_total_matches'] = h2h_df['total_matches']

        series_mapping = {'International': 1, 'ATP250': 2, 'ATP500': 3, 'Masters 1000': 4, 'Grand Slam': 5}
        df['tournament_series_encoded'] = df['tournament_series'].map(series_mapping).fillna(1)

        df['surface_encoded'] = df['surface_id'].fillna(1)
        df['court_type_encoded'] = df['court_type_id'].fillna(1)
        df['round_encoded'] = df['round_id'].fillna(1)

        last_5_p1 = []
        last_5_p2 = []
        for idx, row in df.iterrows():
            last_5_p1.append(self.calculate_last_n_win_rate(row['player_1_id'], n=5))
            last_5_p2.append(self.calculate_last_n_win_rate(row['player_2_id'], n=5))

        df['player_1_last_5_win_rate'] = last_5_p1
        df['player_2_last_5_win_rate'] = last_5_p2

        df['player_1_rank'] = df['rank_1']
        df['player_2_rank'] = df['rank_2']
        df['player_1_points'] = df['pts_1'].fillna(0)
        df['player_2_points'] = df['pts_2'].fillna(0)

        if not for_prediction:
            df['target_winner'] = (df['winner_id'] == df['player_1_id']).astype(int)
            df['target_sets'] = df['total_sets'].fillna(3)
            df['target_games'] = df['total_games'].fillna(20)

        logger.info(f"Feature engineering completed. Shape: {df.shape}")
        return df

    def apply_weights(self, features_df):
        feature_cols = self._get_feature_names()

        for col in feature_cols:
            if col in features_df.columns and col in self.feature_weights:
                features_df[col] = features_df[col].apply(lambda x: float(x) if x is not None else 0.0)
                features_df[col] = features_df[col] * self.feature_weights[col]

        return features_df

    def get_feature_columns(self):
        return self._get_feature_names()
