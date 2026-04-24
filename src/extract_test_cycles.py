#!/usr/bin/env python
"""
Extrait 10 cycles aléatoires du CSV traité de CS2_34
Ces cycles seront utilisés comme jeux de test (jamais vus par le modèle)
"""
import pandas as pd
import numpy as np
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import PROCESSED_DATA_PATH, TESTS_DATA_PATH, RANDOM_SEED
from src.utils import logger


def extract_test_cycles():
    """
    Extrait aléatoirement 10 cycles de test de CS2_34
    Sauvegarde :
        - test_10_cycles.csv : les 10 cycles test (features)
        - CS2_34_train.csv : le reste des cycles pour l'entraînement
        - test_cycles_list.txt : la liste des numéros de cycles test
    """
    logger.info("=" * 50)
    logger.info("EXTRACTION DES CYCLES DE TEST")
    logger.info("=" * 50)
    logger.info(f"Seed aléatoire : {RANDOM_SEED} (fixe pour reproductibilité)")

    # Lire le CSV déjà traité de CS2_34
    csv_path = os.path.join(PROCESSED_DATA_PATH, "dataset_CS2_34.csv")

    if not os.path.exists(csv_path):
        logger.error(f"Fichier non trouvé : {csv_path}")
        logger.info("Exécutez d'abord : python src/data_processor.py")
        return None, None

    logger.info(f"Chargement de {csv_path}")
    df_34 = pd.read_csv(csv_path)
    logger.info(f"  - {len(df_34)} cycles dans CS2_34")
    logger.info(f"  - Colonnes : {df_34.columns.tolist()}")

    # Vérifier que SOH existe
    if 'SOH' not in df_34.columns:
        logger.error("La colonne SOH n'existe pas dans le fichier")
        return None, None

    # Extraire 10 cycles aléatoires (avec seed fixe pour reproductibilité)
    np.random.seed(RANDOM_SEED)
    all_indices = df_34.index.tolist()
    test_indices = np.random.choice(all_indices, size=min(10, len(all_indices)), replace=False)

    test_cycles = df_34.loc[test_indices].copy()
    train_cycles = df_34.drop(test_indices).copy()

    test_cycles_list = sorted(test_cycles['cycle_global'].tolist())
    logger.info(f"\n🔀 Cycles TEST sélectionnés (aléatoires) : {test_cycles_list}")
    logger.info(f"📊 Cycles ENTRAINEMENT : {len(train_cycles)}")

    # 1. Sauvegarder le fichier unique avec tous les cycles test (features)
    os.makedirs(TESTS_DATA_PATH, exist_ok=True)
    test_path = os.path.join(TESTS_DATA_PATH, "test_10_cycles.csv")
    test_cycles.to_csv(test_path, index=False)
    logger.info(f"✅ Cycles test (features) : {test_path}")

    # 2. Sauvegarder CS2_34 pour l'entraînement (sans les cycles test)
    train_path = os.path.join(PROCESSED_DATA_PATH, "CS2_34_train.csv")
    train_cycles.to_csv(train_path, index=False)
    logger.info(f"✅ CS2_34 (train) : {train_path}")

    # 3. Sauvegarder la liste des cycles test (pour export des CSV bruts)
    cycles_list_path = os.path.join(TESTS_DATA_PATH, "test_cycles_list.txt")
    with open(cycles_list_path, 'w') as f:
        for cycle in test_cycles_list:
            f.write(f"{cycle}\n")
    logger.info(f"✅ Liste des cycles test : {cycles_list_path}")

    return test_path, train_path


if __name__ == "__main__":
    extract_test_cycles()