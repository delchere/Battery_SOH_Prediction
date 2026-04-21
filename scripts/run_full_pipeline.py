#!/usr/bin/env python
"""
Exécute tout le pipeline en ordre :
1. Traitement des données (Excel -> CSV avec features)
2. Extraction des cycles test
3. Entraînement du modèle
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_processor import process_all_batteries
from src.extract_test_cycles import extract_test_cycles
from src.train import main as train_main
from src.utils import logger



def run_full_pipeline():
    logger.info("=" * 60)
    logger.info("🚀 PIPELINE COMPLET SOH PREDICTION")
    logger.info("=" * 60)
    
    # Étape 1 : Traiter les données (Excel -> CSV)
    logger.info("\n📊 ÉTAPE 1: Traitement des données brutes")
    logger.info("-" * 40)
    process_all_batteries()
    
    # Étape 2 : Extraire les cycles test
    logger.info("\n📊 ÉTAPE 2: Extraction des cycles test")
    logger.info("-" * 40)
    extract_test_cycles()
    
    # Étape 3 : Entraîner le modèle
    logger.info("\n📊 ÉTAPE 3: Entraînement du modèle")
    logger.info("-" * 40)
    train_main()
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ PIPELINE COMPLET - TERMINÉ")
    logger.info("=" * 60)


if __name__ == "__main__":
    run_full_pipeline()
