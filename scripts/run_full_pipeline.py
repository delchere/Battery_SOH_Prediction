#!/usr/bin/env python
"""
Exécute tout le pipeline en ordre :
1. Traitement des données (Excel -> CSV avec features)
2. Extraction des cycles test
3. Export des CSV bruts pour le client
4. Entraînement du modèle
"""
import sys
import os

# Ajouter la racine du projet au PYTHONPATH
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
    
    # Étape 3 : Exporter les CSV bruts pour le client
    logger.info("\n📊 ÉTAPE 3: Export des CSV bruts pour le client")
    logger.info("-" * 40)
    try:
        from export_client_csv import main as export_main
        export_main()
    except ImportError:
        logger.warning("⚠️ export_client_csv.py non trouvé, passage à l'étape suivante")
    
    # Étape 4 : Entraîner le modèle
    logger.info("\n📊 ÉTAPE 4: Entraînement du modèle")
    logger.info("-" * 40)
    train_main()
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ PIPELINE COMPLET - TERMINÉ")
    logger.info("=" * 60)
    logger.info("\n🎯 Pour lancer l'API : python api/app.py")
    logger.info("📁 Les CSV bruts sont dans : data/client_csv/")


if __name__ == "__main__":
    run_full_pipeline()