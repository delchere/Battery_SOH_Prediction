#!/usr/bin/env python
"""
Entraînement du modèle sur les CSV traités
"""
from src.utils import logger
from src.config import PROCESSED_DATA_PATH, MODELS_PATH, FEATURES_SOH, MODEL_PARAMS, RANDOM_SEED
import pandas as pd
import numpy as np
import os
import sys
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


try:
    import xgboost as xgb
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

try:
    import lightgbm as lgb
    HAS_LGB = True
except ImportError:
    HAS_LGB = False


def load_training_data():
    """Charge CS2_33 complet + CS2_34 (sans cycles test)"""
    logger.info("Chargement des données...")

    path_33 = os.path.join(PROCESSED_DATA_PATH, "dataset_CS2_33.csv")
    path_34_train = os.path.join(PROCESSED_DATA_PATH, "CS2_34_train.csv")

    if not os.path.exists(path_33):
        raise ValueError(f"Fichier non trouvé : {path_33}")
    if not os.path.exists(path_34_train):
        raise ValueError(f"Fichier non trouvé : {path_34_train}")

    df_33 = pd.read_csv(path_33)
    df_34_train = pd.read_csv(path_34_train)

    logger.info(f"  CS2_33 : {len(df_33)} cycles")
    logger.info(f"  CS2_34 (train) : {len(df_34_train)} cycles")

    df_train = pd.concat([df_33, df_34_train], ignore_index=True)
    logger.info(f"  TOTAL : {len(df_train)} cycles")

    return df_train


def main():
    logger.info("=" * 50)
    logger.info("ENTRAÎNEMENT DU MODÈLE SOH")
    logger.info("=" * 50)

    # Charger les données
    df_train = load_training_data()

    # Vérifier les colonnes
    missing_features = [f for f in FEATURES_SOH if f not in df_train.columns]
    if missing_features:
        logger.error(f"Features manquantes : {missing_features}")
        logger.info(f"Colonnes disponibles : {df_train.columns.tolist()}")
        return

    X = df_train[FEATURES_SOH].values
    y = df_train['SOH'].values

    logger.info(f"Features : {X.shape[1]}, Target : SOH")

    # Standardiser
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Split pour validation
    X_train, X_val, y_train, y_val = train_test_split(
        X_scaled, y, test_size=0.2, random_state=RANDOM_SEED
    )

    # Entraîner les modèles
    models = {}

    logger.info("\nEntraînement...")

    gb = GradientBoostingRegressor(**MODEL_PARAMS['GradientBoosting'])
    gb.fit(X_train, y_train)
    models['GradientBoosting'] = gb
    logger.info("  GradientBoosting OK")

    rf = RandomForestRegressor(**MODEL_PARAMS['RandomForest'], n_jobs=-1)
    rf.fit(X_train, y_train)
    models['RandomForest'] = rf
    logger.info("  RandomForest OK")

    if HAS_XGB:
        xgb_model = xgb.XGBRegressor(**MODEL_PARAMS['XGBoost'])
        xgb_model.fit(X_train, y_train)
        models['XGBoost'] = xgb_model
        logger.info("  XGBoost OK")

    if HAS_LGB:
        lgb_model = lgb.LGBMRegressor(**MODEL_PARAMS['LightGBM'])
        lgb_model.fit(X_train, y_train)
        models['LightGBM'] = lgb_model
        logger.info("  LightGBM OK")

    # Évaluation
    logger.info("\nÉvaluation sur validation :")
    best_model = None
    best_r2 = -np.inf

    for name, model in models.items():
        y_pred = model.predict(X_val)
        r2 = r2_score(y_val, y_pred)
        mae = mean_absolute_error(y_val, y_pred)
        rmse = np.sqrt(mean_squared_error(y_val, y_pred))
        logger.info(f"  {name}: R2={r2:.4f}, MAE={mae:.3f}%, RMSE={rmse:.3f}%")

        if r2 > best_r2:
            best_r2 = r2
            best_model = model

    # Ré-entraîner sur toutes les données
    logger.info(f"\n🏆 Meilleur modèle sélectionné (R2={best_r2:.4f})")
    best_model.fit(X_scaled, y)

    # Sauvegarder
    os.makedirs(MODELS_PATH, exist_ok=True)
    joblib.dump(best_model, os.path.join(MODELS_PATH, "best_model.pkl"))
    joblib.dump(scaler, os.path.join(MODELS_PATH, "scaler.pkl"))
    logger.info(f"✅ Modèle sauvegardé dans {MODELS_PATH}")


if __name__ == "__main__":
    main()
