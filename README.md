# Battery SOH Predictor

Prédiction du **State of Health (SOH)** des batteries lithium-ion à partir des données brutes de décharge.

## 📊 Performance du modèle

| Modèle | R² | MAE | Statut |
|--------|----|----|--------|
| GradientBoosting | 0.9978 | 0.176% | 🏆 Meilleur |
| XGBoost | 0.9977 | 0.221% | Très bon |
| LightGBM | 0.9975 | 0.359% | Très bon |
| RandomForest | 0.9969 | 0.149% | Très bon |

## 🚀 Installation

```bash
# 1. Cloner le projet
git clone https://github.com/TON_USER/battery_soh_predictor.git
cd battery_soh_predictor

# 2. Créer l'environnement Conda
conda create -n battery_app python=3.10 -y
conda activate battery_app

# 3. Installer les dépendances
conda install -c conda-forge pandas numpy scipy scikit-learn xgboost lightgbm -y
pip install flask flask-cors python-dotenv joblib openpyxl pytest pytest-cov
 
# 4. Utilisation
# Pipeline complet (recommendé)
conda activate battery_app
python scripts/run_full_pipeline.py

# Étapes individuelles
conda activate battery_app
python src/data_processor.py
python src/extract_test_cycles.py
python src/train.py
python api/app.py

# Tester les prédictions (dans un autre terminal)
conda activate battery_app
python test_all_cycles.py
curl -X POST http://localhost:5000/predict -F "file=@data/tests/test_10_cycles.csv"