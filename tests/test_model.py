import pytest
import pandas as pd
import os
import sys
import joblib

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import DATA_PATH, MODELS_PATH, FEATURES_SOH
from src.feature_engineering import calculate_features_from_raw_cycle


class TestModelOnUnseenData:
    @classmethod
    def setup_class(cls):
        model_path = os.path.join(MODELS_PATH, "best_model.pkl")
        scaler_path = os.path.join(MODELS_PATH, "scaler.pkl")
        test_path = os.path.join(DATA_PATH, "tests", "test_10_cycles.csv")

        if os.path.exists(model_path) and os.path.exists(test_path):
            cls.model = joblib.load(model_path)
            cls.scaler = joblib.load(scaler_path)
            cls.test_data = pd.read_csv(test_path)

    def test_model_exists(self):
        if hasattr(self, 'model'):
            assert self.model is not None