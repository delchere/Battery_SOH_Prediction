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
        courant = np.ones(100) * 1.0  # Courant constant
        df = pd.DataFrame({
            'temps_s': temps,
            'tension_V': tension,
            'courant_A': courant
        })

        features = calculate_features_from_raw_cycle(df)

        assert 'V_mean' in features.columns
        assert 'V_std' in features.columns
        assert 'V_min' in features.columns
        assert 'V_max' in features.columns
        assert 'V_10pct' in features.columns
        assert 'V_50pct' in features.columns
        assert 'V_90pct' in features.columns
        assert 'V_pente' in features.columns
        assert 'V_aire' in features.columns
        assert 'I_mean' in features.columns
        assert 'I_std' in features.columns
        assert 'duree_s' in features.columns
        assert len(features) == 1

    def test_missing_columns_raises_error(self):
        df = pd.DataFrame({'wrong_col': [1, 2, 3]})
        with pytest.raises(ValueError):
            calculate_features_from_raw_cycle(df)