import json
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from pathlib import Path
from config.settings import MODELS_DIR, DEFAULT_TRAIN_SPLIT, DEFAULT_VAL_SPLIT
from config.database import get_db
from src.models.model_factory import ModelFactory
from src.models.feature_engineer import FeatureEngineer
from src.models.hyperparameter_tuner import HyperparameterTuner
from src.utils.logger import get_logger

logger = get_logger(__name__)

class ModelTrainer:
    def __init__(self, training_configuration_id=None, feature_configuration_id=None):
        self.db = get_db()
        self.training_configuration_id = training_configuration_id
        self.feature_configuration_id = feature_configuration_id
        self.training_config = self._load_training_config()
        MODELS_DIR.mkdir(parents=True, exist_ok=True)

    def _load_training_config(self):
        if not self.training_configuration_id:
            return {
                'train_split_ratio': DEFAULT_TRAIN_SPLIT,
                'validation_split_ratio': DEFAULT_VAL_SPLIT,
                'random_seed': 42,
                'use_error_feedback': False
            }

        query = """
            SELECT * FROM training_configurations WHERE id = %s
        """
        result = self.db.execute_query(query, (self.training_configuration_id,), fetch=True)

        if result:
            return dict(result[0])
        else:
            return {
                'train_split_ratio': DEFAULT_TRAIN_SPLIT,
                'validation_split_ratio': DEFAULT_VAL_SPLIT,
                'random_seed': 42,
                'use_error_feedback': False
            }

    def prepare_data(self, limit=None):
        logger.info("Preparing data for training")

        feature_engineer = FeatureEngineer(self.feature_configuration_id)
        df = feature_engineer.extract_features_from_db(limit=limit)

        df_features = feature_engineer.engineer_features(df)
        df_features = feature_engineer.apply_weights(df_features)

        feature_cols = feature_engineer.get_feature_columns()

        X = df_features[feature_cols]
        y_winner = df_features['target_winner']
        y_sets = df_features['target_sets']
        y_games = df_features['target_games']

        logger.info(f"Data prepared. Features: {X.shape}, Samples: {len(X)}")

        return X, y_winner, y_sets, y_games, feature_cols

    def split_data(self, X, y):
        train_size = self.training_config['train_split_ratio']
        random_seed = self.training_config['random_seed']

        X_train, X_val, y_train, y_val = train_test_split(
            X, y, train_size=train_size, random_state=random_seed, stratify=y
        )

        logger.info(f"Data split: Train={len(X_train)}, Val={len(X_val)}")
        return X_train, X_val, y_train, y_val

    def train_model(self, model_type, X_train, y_train, tune_hyperparameters=True):
        logger.info(f"Training {model_type} model")

        model = ModelFactory.create_model(model_type)

        if tune_hyperparameters:
            tuner = HyperparameterTuner(n_iter=500, cv=3)
            best_params, best_score = tuner.tune(model, X_train, y_train)
            model.train(X_train, y_train, best_params)
        else:
            model.train(X_train, y_train)

        return model

    def evaluate_model(self, model, X_val, y_val):
        y_pred = model.predict(X_val)
        y_proba = model.predict_proba(X_val)

        accuracy = accuracy_score(y_val, y_pred)
        precision = precision_score(y_val, y_pred, zero_division=0)
        recall = recall_score(y_val, y_pred, zero_division=0)
        f1 = f1_score(y_val, y_pred, zero_division=0)

        metrics = {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1)
        }

        logger.info(f"Model evaluation - Accuracy: {accuracy:.4f}, F1: {f1:.4f}")
        return metrics

    def save_model_to_db(self, model, model_type, metrics, hyperparameters, feature_importance):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_filename = f"{model_type.lower()}_{timestamp}.pkl"
        model_path = MODELS_DIR / model_filename

        model.save_model(str(model_path))

        query = """
            INSERT INTO models
            (model_name, model_type, model_version, training_configuration_id,
             feature_configuration_id, hyperparameters, training_date,
             validation_accuracy, validation_metrics, model_file_path,
             feature_importance, is_active, use_error_feedback)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """

        result = self.db.execute_query(
            query,
            (
                model.model_name,
                model_type,
                timestamp,
                self.training_configuration_id,
                self.feature_configuration_id,
                json.dumps(hyperparameters),
                datetime.now(),
                metrics['accuracy'],
                json.dumps(metrics),
                str(model_path),
                json.dumps(feature_importance) if feature_importance else None,
                False,
                self.training_config.get('use_error_feedback', False)
            ),
            fetch=True
        )

        model_id = result[0]['id']
        logger.info(f"Model saved to database with ID: {model_id}")
        return model_id

    def train_all_models(self, tune_hyperparameters=True, limit=None):
        logger.info("Starting training for all models")

        X, y_winner, y_sets, y_games, feature_cols = self.prepare_data(limit=limit)

        X_train, X_val, y_train, y_val = self.split_data(X, y_winner)

        model_types = ModelFactory.get_available_models()
        results = []

        for model_type in model_types:
            try:
                model = self.train_model(model_type, X_train, y_train, tune_hyperparameters)
                metrics = self.evaluate_model(model, X_val, y_val)
                feature_importance = model.get_feature_importance()

                model_id = self.save_model_to_db(
                    model,
                    model_type,
                    metrics,
                    model.best_params,
                    feature_importance
                )

                results.append({
                    'model_id': model_id,
                    'model_type': model_type,
                    'accuracy': metrics['accuracy'],
                    'metrics': metrics
                })

                logger.info(f"Completed training for {model_type}")

            except Exception as e:
                logger.error(f"Error training {model_type}: {e}")
                continue

        if results:
            best_model = max(results, key=lambda x: x['accuracy'])
            self._set_active_model(best_model['model_id'])
            logger.info(f"Best model: {best_model['model_type']} with accuracy {best_model['accuracy']:.4f}")

        return results

    def _set_active_model(self, model_id):
        self.db.execute_query("UPDATE models SET is_active = false")

        self.db.execute_query(
            "UPDATE models SET is_active = true WHERE id = %s",
            (model_id,)
        )

        logger.info(f"Set model {model_id} as active")
