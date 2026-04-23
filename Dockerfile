FROM python:3.10-slim

WORKDIR /app

# Installer les compilateurs nécessaires pour scikit-learn
RUN apt-get update && apt-get install -y build-essential

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir numpy==1.24.3
# Forcer la compilation de scikit-learn sur place
RUN pip install --no-cache-dir --no-binary scikit-learn scikit-learn==1.3.0
# Puis installer le reste
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "api/app.py"]