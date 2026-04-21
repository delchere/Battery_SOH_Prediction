import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.feature_engineering import calculate_features_from_raw_cycle


class TestFeatureEngineering:
    def test_calculates_all_features(self):
        temps = np.linspace(0, 3600, 100)
        tension = 4.2 - 0.0005 * temps
        df = pd.DataFrame({'temps_s': temps, 'tension_V': tension})

        features = calculate_features_from_raw_cycle(df)

        assert 'V_mean' in features.columns
        assert 'V_pente' in features.columns
        assert len(features) == 1

    def test_missing_columns_raises_error(self):
        df = pd.DataFrame({'wrong_col': [1, 2, 3]})
        with pytest.raises(ValueError):
            calculate_features_from_raw_cycle(df)