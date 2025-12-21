#!/bin/bash

echo "=========================================="
echo "  Trading IA - Frontend Launcher"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -d "frontend" ]; then
    echo -e "${RED}❌ Erreur: Dossier frontend introuvable${NC}"
    exit 1
fi

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${BLUE}📦 Installation des dépendances Node.js...${NC}"
    npm install

    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Erreur lors de l'installation${NC}"
        exit 1
    fi
fi

# Check if .env.development exists
if [ ! -f ".env.development" ]; then
    echo -e "${YELLOW}⚠️  Création du fichier .env.development${NC}"
    cp .env.example .env.development
fi

echo ""
echo -e "${BLUE}🚀 Démarrage du Frontend${NC}"
echo ""
echo -e "${GREEN}Frontend démarré sur: http://localhost:5173${NC}"
echo ""
echo -e "${YELLOW}Appuyez sur Ctrl+C pour arrêter${NC}"
echo ""

# Start frontend
npm run dev
