from abc import ABC, abstractmethod

class BaseModel(ABC):
    def __init__(self, model_name):
        self.model_name = model_name
        self.model = None
        self.best_params = None

    @abstractmethod
    def get_default_hyperparameters(self):
        pass

    @abstractmethod
    def get_hyperparameter_search_space(self):
        pass

    @abstractmethod
    def train(self, X_train, y_train, hyperparameters=None):
        pass

    @abstractmethod
    def predict(self, X):
        pass

    @abstractmethod
    def predict_proba(self, X):
        pass

    @abstractmethod
    def save_model(self, file_path):
        pass

    @abstractmethod
    def load_model(self, file_path):
        pass

    def get_feature_importance(self):
        return None
