"""
Configuration du projet
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Chemins
DATA_PATH = os.getenv("DATA_PATH", "./data")
RAW_DATA_PATH = os.path.join(DATA_PATH, "raw", "CS2_datasets0.5c")
PROCESSED_DATA_PATH = os.path.join(DATA_PATH, "processed")
TESTS_DATA_PATH = os.path.join(DATA_PATH, "tests")
MODELS_PATH = os.getenv("MODELS_PATH", "./models_saved")

RANDOM_SEED = int(os.getenv("RANDOM_SEED", 42))
INITIAL_CAPACITY_MAH = float(os.getenv("INITIAL_CAPACITY_MAH", 3350))
EOL_THRESHOLD = float(os.getenv("EOL_THRESHOLD", 80))

# Features pour prédire SOH (après extraction)
FEATURES_SOH = [
    'V_mean', 'V_std', 'V_min', 'V_max',
    'V_10pct', 'V_50pct', 'V_90pct',
    'V_pente', 'V_aire',
    'I_mean', 'I_std', 'duree_s'
]

# Paramètres des modèles
MODEL_PARAMS = {
    'GradientBoosting': {
        'n_estimators': 300,
        'learning_rate': 0.05,
        'max_depth': 4,
        'subsample': 0.8,
        'min_samples_leaf': 5,
        'random_state': RANDOM_SEED
    },
    'RandomForest': {
        'n_estimators': 200,
        'max_depth': 10,
        'random_state': RANDOM_SEED
    },
    'XGBoost': {
        'n_estimators': 300,
        'learning_rate': 0.05,
        'max_depth': 4,
        'random_state': RANDOM_SEED
    },
    'LightGBM': {
        'n_estimators': 300,
        'learning_rate': 0.05,
        'max_depth': 4,
        'random_state': RANDOM_SEED,
        'verbose': -1
    }
}

# Batteries
BATTERIES = {
    'CS2_33': {'color': '#2a9d8f', 'initial_capacity': 3350},
    'CS2_34': {'color': '#457b9d', 'initial_capacity': 3350},
}