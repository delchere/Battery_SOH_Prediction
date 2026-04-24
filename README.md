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
pip install -r requirements.txt


# 4. Utilisation

# Pipeline complet
conda activate battery_app
python scripts/run_full_pipeline.py

# Étapes individuelles
python src/data_processor.py
python src/extract_test_cycles.py
python src/train.py
python export_client_csv.py
python api/app.py


# 5. Tester l'API

# Dans un autre terminal
conda activate battery_app

# Health check
curl http://localhost:5000/health

# Prédiction avec un fichier CSV brut
curl -X POST http://localhost:5000/predict -F "file=@data/client_csv/cycle_98.csv"


# 6. Tests
pytest tests/ -v


# 7. Linting et sécurité (optionnel)
flake8 src/ api/ --max-line-length=120
bandit src/ -r -ll


# 8. Docker
docker build -t battery-soh .
docker run -p 5000:5000 battery-soh