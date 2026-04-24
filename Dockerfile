FROM python:3.10-slim

WORKDIR /app

# Installer les compilateurs nécessaires
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Copier requirements
COPY requirements.txt .

# Installer via requirements.txt (une seule source de vérité)
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code
COPY . .

CMD ["python", "api/app.py"]