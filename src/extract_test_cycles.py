#!/usr/bin/env python
"""
Extrait 10 cycles aléatoires du CSV traité de CS2_34
"""
from src.utils import logger
from src.config import PROCESSED_DATA_PATH, TESTS_DATA_PATH, RANDOM_SEED
import pandas as pd
import numpy as np
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def extract_test_cycles():
    logger.info("=" * 50)
    logger.info("EXTRACTION DES CYCLES DE TEST")
    logger.info("=" * 50)

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
        logger.error("La colonne SOH n'existe pas")
        return None, None

    # Extraire 10 cycles aléatoires
    np.random.seed(RANDOM_SEED)
    all_indices = df_34.index.tolist()
    test_indices = np.random.choice(all_indices, size=min(10, len(all_indices)), replace=False)

    test_cycles = df_34.loc[test_indices].copy()
    train_cycles = df_34.drop(test_indices).copy()

    logger.info(f"\nCycles TEST : {sorted(test_cycles['cycle_global'].tolist())}")
    logger.info(f"Cycles ENTRAINEMENT : {len(train_cycles)}")

    # Sauvegarder
    os.makedirs(TESTS_DATA_PATH, exist_ok=True)
    test_path = os.path.join(TESTS_DATA_PATH, "test_10_cycles.csv")
    test_cycles.to_csv(test_path, index=False)
    logger.info(f"✅ Cycles test sauvegardés : {test_path}")

    train_path = os.path.join(PROCESSED_DATA_PATH, "CS2_34_train.csv")
    train_cycles.to_csv(train_path, index=False)
    logger.info(f"✅ CS2_34 (train) sauvegardé : {train_path}")

    return test_path, train_path


if __name__ == "__main__":
    extract_test_cycles()
