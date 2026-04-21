"""
Fonctions utilitaires
"""
import logging
import os
import pandas as pd
import numpy as np


def setup_logger(name: str, log_file: str = "logs/app.log"):
    os.makedirs("logs", exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


logger = setup_logger(__name__)


def date_from_filename(fname):
    """Extrait date du nom de fichier Excel"""
    import re
    stem = os.path.splitext(os.path.basename(fname))[0]
    parts = stem.split('_')
    try:
        day = int(parts[-2])
        month = int(parts[-3])
        year = 2000 + int(parts[-1])
        return (year, month, day)
    except:
        return (9999, 0, 0)


def get_channel_sheet(fpath):
    """Trouve la feuille Channel dans un fichier Excel"""
    xl = pd.ExcelFile(fpath, engine='openpyxl')
    sheet = next((s for s in xl.sheet_names if s.lower().startswith('channel')), None)
    return xl, sheet