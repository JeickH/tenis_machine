import xgboost as xgb
import pickle
from src.models.implementations.base_model import BaseModel
from src.utils.logger import get_logger

logger = get_logger(__name__)

class XGBoostModel(BaseModel):
    def __init__(self):
        super().__init__("XGBoost")

    def get_default_hyperparameters(self):
        return {
            'max_depth': 6,
            'learning_rate': 0.1,
            'n_estimators': 100,
            'objective': 'binary:logistic',
            'eval_metric': 'logloss',
            'random_state': 42
        }

    def get_hyperparameter_search_space(self):
        return {
            'max_depth': [3, 5, 7, 9],
            'learning_rate': [0.01, 0.05, 0.1, 0.2],
            'n_estimators': [50, 100, 200, 300],
            'min_child_weight': [1, 3, 5],
            'subsample': [0.8, 0.9, 1.0],
            'colsample_bytree': [0.8, 0.9, 1.0]
        }

    def train(self, X_train, y_train, hyperparameters=None):
        if hyperparameters is None:
            hyperparameters = self.get_default_hyperparameters()

        self.model = xgb.XGBClassifier(**hyperparameters)
        self.model.fit(X_train, y_train)
        self.best_params = hyperparameters

        logger.info(f"XGBoost model trained with params: {hyperparameters}")
        return self.model

    def predict(self, X):
        return self.model.predict(X)

    def predict_proba(self, X):
        return self.model.predict_proba(X)

    def save_model(self, file_path):
        with open(file_path, 'wb') as f:
            pickle.dump(self.model, f)
        logger.info(f"XGBoost model saved to {file_path}")

    def load_model(self, file_path):
        with open(file_path, 'rb') as f:
            self.model = pickle.load(f)
        logger.info(f"XGBoost model loaded from {file_path}")

    def get_feature_importance(self):
        if self.model:
            return dict(zip(
                [f'f{i}' for i in range(len(self.model.feature_importances_))],
                self.model.feature_importances_.tolist()
            ))
        return None
