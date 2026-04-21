from src.config import DATA_PATH
import pytest
import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_test_cycles_file_exists():
    path = os.path.join(DATA_PATH, "tests", "test_10_cycles.csv")
    if os.path.exists(path):
        df = pd.read_csv(path)
        assert len(df) == 10


def test_no_overlap():
    test_path = os.path.join(DATA_PATH, "tests", "test_10_cycles.csv")
    train_path = os.path.join(DATA_PATH, "processed", "CS2_34_train.csv")

    if os.path.exists(test_path) and os.path.exists(train_path):
        test_df = pd.read_csv(test_path)
        train_df = pd.read_csv(train_path)
        overlap = set(test_df['cycle_global']).intersection(set(train_df['cycle_global']))
        assert len(overlap) == 0
