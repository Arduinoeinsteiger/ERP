#!/bin/bash
# SwissAirDry - Installationsscript
# 
# Dieses Script installiert die Domainverwaltung und alle benötigten Abhängigkeiten.

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}       SwissAirDry Installation           ${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Überprüfen, ob das Script mit Root-Rechten ausgeführt wird
if [ "$EUID" -ne 0 ]; then
  echo -e "${YELLOW}Hinweis: Dieses Script wird ohne Root-Rechte ausgeführt.${NC}"
  echo "Einige Funktionen könnten eingeschränkt sein."
  echo ""
fi

# Systemvoraussetzungen prüfen
echo -e "${YELLOW}Systemvoraussetzungen werden überprüft...${NC}"

check_command() {
    command -v $1 >/dev/null 2>&1 || { 
        echo -e "${RED}$1 ist nicht installiert.${NC}" 
        return 1
    }
    echo -e "${GREEN}$1 ist installiert.${NC}"
    return 0
}

# Überprüfen, ob Python installiert ist
check_command python3
PYTHON_OK=$?

# Überprüfen, ob pip installiert ist
check_command pip3
PIP_OK=$?

# Überprüfen, ob Git installiert ist
check_command git
GIT_OK=$?

echo ""

# Python-Pakete installieren
if [ $PYTHON_OK -eq 0 ] && [ $PIP_OK -eq 0 ]; then
    echo -e "${YELLOW}Python-Abhängigkeiten werden installiert...${NC}"
    pip3 install flask sqlalchemy requests paho-mqtt==2.1.0 bleak psycopg2-binary gunicorn jinja2
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Python-Abhängigkeiten erfolgreich installiert.${NC}"
    else
        echo -e "${RED}Fehler beim Installieren der Python-Abhängigkeiten.${NC}"
        echo "Versuchen Sie, die folgenden Pakete manuell zu installieren:"
        echo "pip3 install flask sqlalchemy requests paho-mqtt==2.1.0 bleak psycopg2-binary gunicorn jinja2"
    fi
else
    echo -e "${RED}Python oder pip ist nicht installiert. Python-Abhängigkeiten können nicht installiert werden.${NC}"
    echo "Bitte installieren Sie Python und pip und führen Sie das Script erneut aus."
fi

echo ""

# Domain-Management-Module installieren
echo -e "${YELLOW}Domain-Management wird installiert...${NC}"

# Verzeichnis erstellen, falls es nicht existiert
if [ ! -d "../domain_management" ]; then
    mkdir -p ../domain_management
    echo -e "${GREEN}Verzeichnis 'domain_management' erstellt.${NC}"
fi

# Dateien kopieren
if [ -d "../domain_management" ]; then
    cp -r ../domain_management/* ../domain_management/
    echo -e "${GREEN}Domain-Management-Module wurden installiert.${NC}"
else
    echo -e "${RED}Fehler: Verzeichnis 'domain_management' konnte nicht erstellt werden.${NC}"
fi

echo ""

# Umgebungsvariablen konfigurieren
echo -e "${YELLOW}Umgebungsvariablen werden konfiguriert...${NC}"

# .env-Datei erstellen oder aktualisieren
ENV_FILE="../.env"

# Überprüfen, ob die .env-Datei existiert
if [ -f "$ENV_FILE" ]; then
    # Sichern der bestehenden .env-Datei
    cp $ENV_FILE ${ENV_FILE}.backup
    echo -e "${GREEN}Bestehende .env-Datei gesichert unter ${ENV_FILE}.backup${NC}"
fi

# Neue oder aktualisierte Umgebungsvariablen hinzufügen
if grep -q "CLOUDFLARE_API_TOKEN" "$ENV_FILE" 2>/dev/null; then
    echo -e "${GREEN}CLOUDFLARE_API_TOKEN ist bereits in der .env-Datei konfiguriert.${NC}"
else
    echo "" >> $ENV_FILE
    echo "# Domain Management" >> $ENV_FILE
    echo "CLOUDFLARE_API_TOKEN=" >> $ENV_FILE
    echo -e "${GREEN}CLOUDFLARE_API_TOKEN zur .env-Datei hinzugefügt.${NC}"
    echo -e "${YELLOW}Bitte setzen Sie Ihren Cloudflare API-Token in der .env-Datei.${NC}"
fi

echo ""

# Datenbank-Migration
echo -e "${YELLOW}Datenbank wird initialisiert...${NC}"
if [ -f "../main.py" ]; then
    cd ..
    python3 -c "from main import models; from sqlalchemy import create_engine; engine = create_engine(os.environ.get('DATABASE_URL')); models.Base.metadata.create_all(bind=engine)" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Datenbank erfolgreich initialisiert.${NC}"
    else
        echo -e "${RED}Fehler beim Initialisieren der Datenbank.${NC}"
        echo "Bitte führen Sie die Datenbank-Migration manuell durch."
    fi
    cd -
else
    echo -e "${RED}Hauptanwendungsdatei (main.py) nicht gefunden. Datenbank-Migration wird übersprungen.${NC}"
fi

echo ""

# Abschluss
echo -e "${BLUE}============================================${NC}"
echo -e "${GREEN}Installation abgeschlossen!${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""
echo -e "Nächste Schritte:"
echo -e "1. Setzen Sie Ihren Cloudflare API-Token in der .env-Datei"
echo -e "2. Starten Sie die Anwendung mit: python3 main.py"
echo -e "3. Greifen Sie auf die Domainverwaltung zu unter: http://localhost:5000/domains"
echo ""
echo -e "Bei Problemen konsultieren Sie bitte die Dokumentation in domain_management/README.md"
echo ""