"""
Prédiction SOH à partir des données BRUTES d'un cycle
L'utilisateur envoie le CSV brut, l'ordinateur calcule tout
"""
from src.utils import logger
from src.feature_engineering import calculate_features_from_raw_cycle
from src.config import MODELS_PATH
import pandas as pd
import os
import sys
import joblib

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class SOHPredictor:
    """Prédicteur de SOH à partir de données brutes"""

    def __init__(self, model_path: str = None, scaler_path: str = None):
        if model_path is None:
            model_path = os.path.join(MODELS_PATH, "best_model.pkl")
        if scaler_path is None:
            scaler_path = os.path.join(MODELS_PATH, "scaler.pkl")

        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        logger.info("✅ Prédicteur prêt")

    def predict_from_raw_csv(self, csv_path: str) -> dict:
        """
        Prédit le SOH à partir d'un fichier CSV contenant les données brutes d'un cycle

        Args:
            csv_path: Chemin vers le fichier CSV

        Returns:
            Dict avec prédiction
        """
        df_raw = pd.read_csv(csv_path)
        return self.predict_from_dataframe(df_raw)

    def predict_from_dataframe(self, df_raw: pd.DataFrame) -> dict:
        """
        Prédit le SOH à partir d'un DataFrame de données brutes

        Args:
            df_raw: DataFrame avec colonnes (temps_s, tension_V, courant_A, capacite_mAh)

        Returns:
            Dict avec prédiction
        """
        # ÉTAPE 1 : Calculer les features à partir des données brutes
        logger.info("Calcul des features à partir des données brutes...")
        features = calculate_features_from_raw_cycle(df_raw)

        # ÉTAPE 2 : Standardiser
        features_scaled = self.scaler.transform(features.values)

        # ÉTAPE 3 : Prédire
        soh_pred = self.model.predict(features_scaled)[0]

        # ÉTAPE 4 : Retourner le résultat
        return {
            'soh_predicted': round(float(soh_pred), 2),
            'unit': '%',
            'features_used': list(features.columns),
            'status': self._get_status(soh_pred)
        }

    def _get_status(self, soh: float) -> str:
        if soh >= 90:
            return "excellent"
        elif soh >= 80:
            return "bon"
        elif soh >= 70:
            return "attention"
        else:
            return "critique"


# Singleton
_predictor = None


def get_predictor() -> SOHPredictor:
    global _predictor
    if _predictor is None:
        _predictor = SOHPredictor()
    return _predictor
