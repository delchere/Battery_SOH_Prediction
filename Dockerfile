FROM python:3.10-slim

WORKDIR /app

# Copier et installer les dépendances en premier (pour le cache)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir numpy==1.24.3
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code
COPY . .

CMD ["python", "api/app.py"]