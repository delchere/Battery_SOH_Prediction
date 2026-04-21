"""
Calcul des features à partir des données brutes d'un cycle de batterie
L'utilisateur envoie les données brutes, ce script calcule tout automatiquement
"""
import pandas as pd
import numpy as np
from scipy import stats
from src.config import FEATURES_SOH
from src.utils import logger


def calculate_features_from_raw_cycle(df_cycle: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule toutes les features à partir des données brutes d'un cycle

    DONNÉES D'ENTRÉE (CSV de l'utilisateur) :
    - temps_s      : temps en secondes
    - tension_V    : tension en Volts
    - courant_A    : courant en Ampères
    - capacite_Ah  : capacité cumulée en Ah (ou mAh)

    SORTIE :
    - DataFrame avec une ligne contenant toutes les features
    """

    # Vérifier les colonnes requises
    required_cols = ['temps_s', 'tension_V', 'courant_A']
    missing = [c for c in required_cols if c not in df_cycle.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes dans les données brutes : {missing}")

    # Nettoyer les données
    df = df_cycle.copy()
    df = df.dropna()

    # Calcul des features de tension
    V = df['tension_V'].values

    features = {
        # Statistiques de base
        'V_mean': np.mean(V),
        'V_std': np.std(V),
        'V_min': np.min(V),
        'V_max': np.max(V),

        # Quantiles
        'V_10pct': np.percentile(V, 10),
        'V_50pct': np.percentile(V, 50),
        'V_90pct': np.percentile(V, 90),

        # Pente de la décharge (régression linéaire)
        'V_pente': _calculate_slope(df),

        # Aire sous la courbe tension-temps
        'V_aire': _calculate_area_under_curve(df),
    }

    # Features de courant (si disponible)
    if 'courant_A' in df.columns:
        current_values = df['courant_A'].values
        features['I_mean'] = np.mean(current_values)
        features['I_std'] = np.std(current_values)
    else:
        features['I_mean'] = 0
        features['I_std'] = 0

    # Durée du cycle
    if 'temps_s' in df.columns:
        features['duree_s'] = df['temps_s'].max() - df['temps_s'].min()
    else:
        features['duree_s'] = len(df)  # fallback

    # Capacité (si disponible, sinon à déduire)
    if 'capacite_mAh' in df.columns:
        # Utiliser la capacité finale du cycle
        features['capacite_mAh'] = df['capacite_mAh'].iloc[-1] if len(df) > 0 else 0
    elif 'capacite_Ah' in df.columns:
        features['capacite_mAh'] = df['capacite_Ah'].iloc[-1] * 1000
    else:
        # Si pas de capacité, on ne peut pas calculer le SOH
        # Mais on peut quand même prédire si le modèle a été entraîné sans ?
        features['capacite_mAh'] = 0
        logger.warning("Capacité non fournie, impossible de calculer le SOH réel")

    # Convertir en DataFrame
    result = pd.DataFrame([features])

    # Garder uniquement les colonnes attendues par le modèle
    result = result[FEATURES_SOH]

    return result


def _calculate_slope(df: pd.DataFrame) -> float:
    """
    Calcule la pente de la décharge (régression linéaire)
    """
    if len(df) < 2:
        return 0.0

    x = df['temps_s'].values
    y = df['tension_V'].values

    # Régression linéaire
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

    return slope


def _calculate_area_under_curve(df: pd.DataFrame) -> float:
    """
    Calcule l'aire sous la courbe tension-temps (intégrale)
    """
    if len(df) < 2:
        return 0.0

    x = df['temps_s'].values
    y = df['tension_V'].values

    # Intégrale par méthode trapézoïdale
    area = np.trapz(y, x)

    return area


def calculate_soh_from_raw_cycle(df_cycle: pd.DataFrame, initial_capacity_mAh: float = 3350) -> float:
    """
    Calcule le SOH réel à partir des données brutes d'un cycle

    Args:
        df_cycle: Données brutes du cycle
        initial_capacity_mAh: Capacité initiale de référence

    Returns:
        SOH en pourcentage
    """
    if 'capacite_mAh' in df_cycle.columns:
        final_capacity = df_cycle['capacite_mAh'].iloc[-1]
    elif 'capacite_Ah' in df_cycle.columns:
        final_capacity = df_cycle['capacite_Ah'].iloc[-1] * 1000
    else:
        return None

    soh = (final_capacity / initial_capacity_mAh) * 100
    return round(soh, 2)


# Exemple d'utilisation
if __name__ == "__main__":
    # Simuler des données brutes d'un cycle
    temps = np.linspace(0, 3600, 1000)  # 1 heure
    tension = 4.2 - 0.0005 * temps + np.random.normal(0, 0.01, 1000)
    courant = 1.0 * np.ones(1000) + np.random.normal(0, 0.05, 1000)
    capacite = np.cumsum(courant * (temps[1] - temps[0])) / 3600 * 1000  # mAh

    df_raw = pd.DataFrame({
        'temps_s': temps,
        'tension_V': tension,
        'courant_A': courant,
        'capacite_mAh': capacite
    })

    print("Données brutes du cycle :")
    print(df_raw.head())
    print(f"\nShape : {df_raw.shape}")

    # Calculer les features
    features = calculate_features_from_raw_cycle(df_raw)
    print("\nFeatures calculées :")
    print(features.T)

    # Calculer le SOH réel
    soh = calculate_soh_from_raw_cycle(df_raw)
    print(f"\nSOH réel : {soh}%")
