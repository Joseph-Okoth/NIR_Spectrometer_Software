import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier

class MLModel:
    def __init__(self, model_path="model.pkl"):
        with open(model_path, "rb") as file:
            self.model = pickle.load(file)

    def predict(self, features):
        features_array = np.array([list(features.values())])
        return self.model.predict(features_array)[0]
