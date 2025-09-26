FROM python:3.12-slim

# Installa dipendenze di sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libzbar0 \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0 \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Setup directory di lavoro
WORKDIR /app

# Copia requirements e installa dipendenze Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutto il codice
COPY . .

# Debug: mostra la struttura dei file
RUN ls -la /app/ && ls -la /app/app/ && ls -la /app/web/static/ && cat /app/app/__init__.py || echo "No __init__.py found"

# Crea directory per i dati
RUN mkdir -p /data/input /data/output /data/temp

# Esponi la porta per l'interfaccia web
EXPOSE 5000

# Comando di avvio
CMD ["python", "-m", "app.main"]