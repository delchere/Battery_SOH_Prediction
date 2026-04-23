FROM python:3.10-slim

WORKDIR /app

# Installer les dépendances système (dont scikit-learn via apt)
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-sklearn \
    python3-pandas \
    && rm -rf /var/lib/apt/lists/*

# Copier le fichier requirements
COPY requirements.txt .

# Installer les dépendances Python (sans scikit-learn et pandas déjà installés via apt)
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir \
    flask \
    flask-cors \
    python-dotenv \
    joblib \
    openpyxl \
    numpy==1.23.5

# Copier le reste du code
COPY . .

CMD ["python", "api/app.py"]