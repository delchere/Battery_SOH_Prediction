FROM python:3.10-slim

WORKDIR /app

# Installer les compilateurs nécessaires
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Copier requirements
COPY requirements.txt .

# Installer toutes les dépendances via pip (versions compatibles)
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir \
    numpy==1.23.5 \
    scikit-learn==1.2.2 \
    pandas==2.0.3 \
    flask==2.3.3 \
    flask-cors==4.0.0 \
    python-dotenv==1.0.0 \
    joblib==1.3.2 \
    openpyxl==3.1.2 \
    scipy==1.10.1

# Copier le code
COPY . .

CMD ["python", "api/app.py"]