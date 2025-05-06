#!/bin/bash

# SwissAirDry Test Runner Script
# Führt alle Tests für das SwissAirDry-Projekt aus

set -e

# Farbdefinitionen
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================="
echo -e "     SwissAirDry Test Runner"
echo -e "=======================================${NC}"

# Python-Abhängigkeiten installieren
echo -e "${YELLOW}Installiere Python-Testabhängigkeiten...${NC}"
pip install -r requirements-dev.txt

# Python-Tests ausführen
echo -e "\n${YELLOW}Führe Python-Tests aus...${NC}"
python -m pytest tests/ -v --cov=swissairdry

# Lint-Check mit flake8
echo -e "\n${YELLOW}Führe Lint-Check mit flake8 aus...${NC}"
flake8 swissairdry

# Code-Formatierung mit black überprüfen
echo -e "\n${YELLOW}Überprüfe Code-Formatierung mit black...${NC}"
black --check swissairdry

# Sicherheits-Check mit bandit
echo -e "\n${YELLOW}Führe Sicherheits-Check mit bandit aus...${NC}"
bandit -r swissairdry -x tests/

# JavaScript-Tests
if [ -d "swissairdry/ExApp" ]; then
  echo -e "\n${YELLOW}Führe JavaScript-Tests aus...${NC}"
  cd swissairdry/ExApp
  
  # npm-Abhängigkeiten installieren, falls package.json existiert
  if [ -f "package.json" ]; then
    npm install
    npm test
  else
    echo -e "${RED}package.json nicht gefunden, überspringe JavaScript-Tests${NC}"
  fi
  
  cd ../..
fi

echo -e "\n${GREEN}======================================="
echo -e "     Alle Tests abgeschlossen!"
echo -e "=======================================${NC}"