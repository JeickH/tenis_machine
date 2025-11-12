import lightgbm as lgb
import pickle
from src.models.implementations.base_model import BaseModel
from src.utils.logger import get_logger

logger = get_logger(__name__)

class LightGBMModel(BaseModel):
    def __init__(self):
        super().__init__("LightGBM")

    def get_default_hyperparameters(self):
        return {
            'max_depth': 6,
            'learning_rate': 0.1,
            'n_estimators': 100,
            'objective': 'binary',
            'metric': 'binary_logloss',
            'random_state': 42,
            'verbose': -1
        }

    def get_hyperparameter_search_space(self):
        return {
            'max_depth': [3, 5, 7, 9],
            'learning_rate': [0.01, 0.05, 0.1, 0.2],
            'n_estimators': [50, 100, 200, 300],
            'num_leaves': [31, 50, 70],
            'min_child_samples': [20, 30, 50],
            'subsample': [0.8, 0.9, 1.0]
        }

    def train(self, X_train, y_train, hyperparameters=None):
        if hyperparameters is None:
            hyperparameters = self.get_default_hyperparameters()

        self.model = lgb.LGBMClassifier(**hyperparameters)
        self.model.fit(X_train, y_train)
        self.best_params = hyperparameters

        logger.info(f"LightGBM model trained with params: {hyperparameters}")
        return self.model

    def predict(self, X):
        return self.model.predict(X)

    def predict_proba(self, X):
        return self.model.predict_proba(X)

    def save_model(self, file_path):
        with open(file_path, 'wb') as f:
            pickle.dump(self.model, f)
        logger.info(f"LightGBM model saved to {file_path}")

    def load_model(self, file_path):
        with open(file_path, 'rb') as f:
            self.model = pickle.load(f)
        logger.info(f"LightGBM model loaded from {file_path}")

    def get_feature_importance(self):
        if self.model:
            return dict(zip(
                [f'f{i}' for i in range(len(self.model.feature_importances_))],
                self.model.feature_importances_.tolist()
            ))
        return None
