from src.predict import SOHPredictor
import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestPredictor:
    def test_predictor_initializes(self):
        if os.path.exists("models_saved/best_model.pkl"):
            predictor = SOHPredictor()
            assert predictor is not None

    def test_predict_from_dataframe(self):
        if os.path.exists("models_saved/best_model.pkl"):
            temps = np.linspace(0, 3600, 100)
            tension = 4.2 - 0.0005 * temps
            courant = -1.0 * np.ones(100)  
            df = pd.DataFrame({
                'temps_s': temps,
                'tension_V': tension,
                'courant_A': courant   
            })

            predictor = SOHPredictor()
            result = predictor.predict_from_dataframe(df)

            assert 'soh_predicted' in result
            assert 0 <= result['soh_predicted'] <= 100