FROM python:3.10-slim

WORKDIR /app

# Installer scikit-learn via apt (version pré-compilée, fiable)
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-sklearn \
    python3-pandas \
    && rm -rf /var/lib/apt/lists/*

# Copier et installer le reste des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir numpy==1.23.5
RUN pip install --no-cache-dir flask flask-cors python-dotenv joblib openpyxl

# Copier le code
COPY . .

# Le modèle sera dans /usr/lib/python3/dist-packages/sklearn/
# Pas besoin de l'entraîner à nouveau

CMD ["python", "api/app.py"]