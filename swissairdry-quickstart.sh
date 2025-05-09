#!/bin/bash
# SwissAirDry - Quickstart Script
# Startet die SwissAirDry-Plattform mit allen Komponenten

# Farben
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}       SwissAirDry Quickstart v1.0.0       ${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Prüfen, ob eine Aktualisierung gewünscht ist
if [ "$1" == "--update" ] || [ "$1" == "-u" ]; then
    echo -e "${YELLOW}Aktualisierung wird gestartet...${NC}"
    if [ -f "tools/update_system.sh" ]; then
        chmod +x tools/update_system.sh
        ./tools/update_system.sh
    else
        echo -e "${RED}Update-Script nicht gefunden.${NC}"
        echo "Bitte führen Sie die Aktualisierung manuell durch."
    fi
    echo ""
fi

# Umgebungsvariablen aus .env-Datei laden
if [ -f ".env" ]; then
    echo -e "${GREEN}Umgebungsvariablen werden geladen...${NC}"
    export $(grep -v '^#' .env | xargs)
    echo -e "${GREEN}Umgebungsvariablen geladen.${NC}"
else
    echo -e "${YELLOW}Keine .env-Datei gefunden. Umgebungsvariablen müssen manuell gesetzt werden.${NC}"
fi
echo ""

# Prüfen, ob der Cloudflare API-Token konfiguriert ist
if [ -z "$CLOUDFLARE_API_TOKEN" ]; then
    echo -e "${YELLOW}Warnung: CLOUDFLARE_API_TOKEN ist nicht konfiguriert.${NC}"
    echo "Die Domainverwaltung wird nicht funktionieren."
    echo "Bitte setzen Sie den Token in der .env-Datei:"
    echo "CLOUDFLARE_API_TOKEN=Ihr_Cloudflare_API_Token"
    echo ""
fi

# Prüfen, ob Python installiert ist
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 ist nicht installiert.${NC}"
    echo "Bitte installieren Sie Python 3 und versuchen Sie es erneut."
    exit 1
fi

# Prüfen, ob Docker installiert ist und läuft (falls vorhanden)
USE_DOCKER=false
if command -v docker &> /dev/null && docker info &> /dev/null; then
    echo -e "${GREEN}Docker ist installiert und läuft.${NC}"
    
    # Prüfen, ob docker-compose vorhanden ist
    if [ -f "docker-compose.yml" ] && command -v docker-compose &> /dev/null; then
        echo -e "${YELLOW}Möchten Sie die Anwendung mit Docker starten? (j/n)${NC}"
        read -p "> " START_WITH_DOCKER
        
        if [[ $START_WITH_DOCKER =~ ^[Jj]$ ]]; then
            USE_DOCKER=true
        fi
    fi
    echo ""
fi

# Anwendung starten (mit Docker oder direkt)
if [ "$USE_DOCKER" = true ]; then
    echo -e "${GREEN}Starte SwissAirDry mit Docker...${NC}"
    docker-compose down
    docker-compose up -d
    
    echo -e "${GREEN}SwissAirDry wurde erfolgreich mit Docker gestartet.${NC}"
    echo "Zugangsdaten:"
    echo "- Web-Interface: http://localhost:5000"
    echo "- Domain-Verwaltung: http://localhost:5000/domains"
    echo "- MQTT-Broker: localhost:1883"
    
    echo ""
    echo -e "${YELLOW}Container-Status:${NC}"
    docker-compose ps
else
    echo -e "${GREEN}Starte SwissAirDry direkt...${NC}"
    
    # Datenbank initialisieren (falls notwendig)
    if [ -f "main.py" ]; then
        echo -e "${GREEN}Initialisiere Datenbank...${NC}"
        python3 -c "from main import models; from sqlalchemy import create_engine; import os; engine = create_engine(os.environ.get('DATABASE_URL')); models.Base.metadata.create_all(bind=engine)" 2>/dev/null
    fi
    
    # Anwendung starten
    echo -e "${GREEN}Starte Hauptanwendung...${NC}"
    python3 main.py &
    APP_PID=$!
    
    # Warten, bis die Anwendung gestartet ist
    sleep 2
    
    # Prüfen, ob die Anwendung läuft
    if ps -p $APP_PID > /dev/null; then
        echo -e "${GREEN}SwissAirDry wurde erfolgreich gestartet.${NC}"
        echo "Zugangsdaten:"
        echo "- Web-Interface: http://localhost:5000"
        echo "- Domain-Verwaltung: http://localhost:5000/domains"
    else
        echo -e "${RED}Fehler beim Starten der Anwendung.${NC}"
        echo "Bitte überprüfen Sie die Logs für weitere Informationen."
    fi
fi

echo ""
echo -e "${BLUE}============================================${NC}"
echo -e "${GREEN}     SwissAirDry läuft jetzt!     ${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""
echo -e "Informationen:"
echo -e "- Version: ${YELLOW}v1.0.0${NC}"
echo -e "- Release-Tag: ${YELLOW}ins${NC}"
echo -e "- Commit-Hash: ${YELLOW}f307b0c${NC}"
echo ""
echo -e "Bei Problemen:"
echo -e "- Überprüfen Sie die Logdateien"
echo -e "- Führen Sie './tools/generate_install_report.sh' aus"
echo -e "- Besuchen Sie die GitHub-Seite: https://github.com/Arduinoeinsteiger/ERP"
echo ""
echo -e "Zum Beenden: STRG+C drücken"

# Auf Benutzerinteraktion warten
if [ "$USE_DOCKER" = false ] && ps -p $APP_PID > /dev/null; then
    wait $APP_PID
fi