#!/bin/bash

echo "🚀 Starting Text-to-QR Video Encoder System..."

# Crea struttura directory
mkdir -p data/{input,output,temp}

# Build del container
echo "📦 Building Docker image..."
docker compose build

# Avvia il sistema
echo "▶️ Starting services..."
docker compose up -d

# Attendi che il servizio sia pronto
echo "⏳ Waiting for service to be ready..."
sleep 5

# Verifica health
if curl -s http://localhost:5000/health | grep -q "healthy"; then
    echo "✅ System is up and running!"
    echo "🌐 Open http://localhost:5000 in your browser"
else
    echo "❌ Failed to start. Check logs with: docker compose logs"
fi