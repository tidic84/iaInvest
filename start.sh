#!/bin/bash

echo "=========================================="
echo "  Trading IA Auto-Apprenant - Launcher"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo -e "${RED}❌ Erreur: Lancez ce script depuis la racine du projet${NC}"
    exit 1
fi

echo -e "${BLUE}📦 Étape 1: Installation des dépendances Backend${NC}"
echo ""

cd backend

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Création de l'environnement virtuel...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Erreur lors de la création du venv${NC}"
        echo -e "${YELLOW}Essayez: sudo apt install python3-venv${NC}"
        exit 1
    fi
fi

# Activate venv
echo -e "${GREEN}Activation de l'environnement virtuel...${NC}"
source venv/bin/activate

# Install dependencies
echo -e "${YELLOW}Installation des dépendances Python...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Erreur lors de l'installation des dépendances${NC}"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Fichier .env manquant, copie depuis .env.example${NC}"
    cp .env.example .env
    echo -e "${RED}❌ IMPORTANT: Éditez backend/.env et ajoutez votre clé XAI_API_KEY${NC}"
    echo -e "${YELLOW}Puis relancez ce script${NC}"
    exit 1
fi

# Check if database exists
if [ ! -f "trading_ai.db" ]; then
    echo -e "${BLUE}📊 Étape 2: Initialisation de la base de données${NC}"
    echo ""

    echo -e "${YELLOW}Génération de la migration initiale...${NC}"
    alembic revision --autogenerate -m "Initial schema"

    echo -e "${YELLOW}Application des migrations...${NC}"
    alembic upgrade head

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Base de données créée avec succès${NC}"
    else
        echo -e "${RED}❌ Erreur lors de la création de la base de données${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${BLUE}🚀 Étape 3: Démarrage du Backend${NC}"
echo ""
echo -e "${GREEN}Backend démarré sur: http://localhost:8000${NC}"
echo -e "${GREEN}Documentation API: http://localhost:8000/docs${NC}"
echo ""
echo -e "${YELLOW}Appuyez sur Ctrl+C pour arrêter${NC}"
echo ""

# Start backend
python main.py
