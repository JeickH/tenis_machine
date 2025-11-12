from sklearn.model_selection import RandomizedSearchCV
from src.utils.logger import get_logger

logger = get_logger(__name__)

class HyperparameterTuner:
    def __init__(self, n_iter=10, cv=3, random_state=42):
        self.n_iter = n_iter
        self.cv = cv
        self.random_state = random_state

    def tune(self, model_instance, X_train, y_train):
        logger.info(f"Starting hyperparameter tuning for {model_instance.model_name}")

        search_space = model_instance.get_hyperparameter_search_space()
        base_params = model_instance.get_default_hyperparameters()

        temp_model_class = type(model_instance.model)
        temp_model = temp_model_class(**base_params)

        search = RandomizedSearchCV(
            estimator=temp_model,
            param_distributions=search_space,
            n_iter=self.n_iter,
            cv=self.cv,
            random_state=self.random_state,
            n_jobs=-1,
            verbose=1
        )

        search.fit(X_train, y_train)

        logger.info(f"Best parameters: {search.best_params_}")
        logger.info(f"Best score: {search.best_score_:.4f}")

        return search.best_params_, search.best_score_
