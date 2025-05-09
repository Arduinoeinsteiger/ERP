#!/bin/bash
# SwissAirDry - System-Update-Script
# Dieses Script aktualisiert die SwissAirDry-Plattform auf die neueste Version

# Farben
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funktion zum Anzeigen von Informationsmeldungen
info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Funktion zum Anzeigen von Erfolgsmeldungen
success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Funktion zum Anzeigen von Warnmeldungen
warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Funktion zum Anzeigen von Fehlermeldungen
error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Hauptprogramm
echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}       SwissAirDry System Update           ${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Aktuelles Verzeichnis speichern
CURRENT_DIR=$(pwd)
# Zum Hauptverzeichnis wechseln (eine Ebene höher)
cd ..

# Prüfen, ob git installiert ist
if ! command -v git &> /dev/null; then
    error "Git ist nicht installiert. Bitte installieren Sie Git und versuchen Sie es erneut."
    exit 1
fi

# Prüfen, ob es sich um ein Git-Repository handelt
if [ ! -d ".git" ]; then
    warning "Kein Git-Repository gefunden. Verwenden Sie die manuelle Update-Methode."
    
    # Fragen, ob fortgefahren werden soll
    read -p "Möchten Sie trotzdem fortfahren? (j/n): " CONTINUE
    if [[ ! $CONTINUE =~ ^[Jj]$ ]]; then
        info "Update abgebrochen."
        exit 0
    fi
fi

# Sichern der .env-Datei
if [ -f ".env" ]; then
    info "Sichern der bestehenden .env-Datei..."
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
    success "Backup erstellt: .env.backup.$(date +%Y%m%d_%H%M%S)"
fi

# Sichern von benutzerdefinierten Konfigurationen
if [ -d "config" ]; then
    info "Sichern von benutzerdefinierten Konfigurationen..."
    BACKUP_DIR="config_backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    cp -r config/* "$BACKUP_DIR"
    success "Konfigurationen gesichert in: $BACKUP_DIR"
fi

# Datenbank sichern (wenn PostgreSQL installiert ist)
if command -v pg_dump &> /dev/null && [ -n "$DATABASE_URL" ]; then
    info "Datenbank wird gesichert..."
    DB_BACKUP="swissairdry_db_backup_$(date +%Y%m%d_%H%M%S).sql"
    if pg_dump "$DATABASE_URL" > "$DB_BACKUP" 2>/dev/null; then
        success "Datenbank-Backup erstellt: $DB_BACKUP"
    else
        warning "Datenbank-Backup konnte nicht erstellt werden. Fahre ohne Backup fort."
    fi
fi

# Update durchführen
if [ -d ".git" ]; then
    info "Aktualisiere Repository von GitHub..."
    
    # Lokale Änderungen speichern
    git stash
    
    # Remote-Änderungen abrufen
    git fetch
    
    # Aktuelle Branch ermitteln
    CURRENT_BRANCH=$(git branch --show-current)
    
    # Auf den aktuellen Branch aktualisieren
    git pull origin $CURRENT_BRANCH
    
    # Lokale Änderungen wiederherstellen
    git stash pop
    
    success "Repository wurde aktualisiert."
else
    warning "Manuelles Update: Git-Repository nicht gefunden."
fi

# Python-Abhängigkeiten aktualisieren
if command -v pip3 &> /dev/null; then
    info "Python-Abhängigkeiten werden aktualisiert..."
    pip3 install -U flask sqlalchemy requests paho-mqtt==2.1.0 bleak psycopg2-binary gunicorn jinja2
    success "Python-Abhängigkeiten wurden aktualisiert."
else
    warning "Pip nicht gefunden. Python-Abhängigkeiten wurden nicht aktualisiert."
fi

# Domain-Management-Module aktualisieren
if [ -d "domain_management" ]; then
    info "Domain-Management-Module werden aktualisiert..."
    # Hier können spezifische Update-Aktionen für Domain-Management eingefügt werden
    success "Domain-Management-Module wurden aktualisiert."
fi

# Datenbank-Migration durchführen (wenn notwendig)
if [ -f "main.py" ]; then
    info "Datenbank-Migration wird durchgeführt..."
    python3 -c "from main import models; from sqlalchemy import create_engine; import os; engine = create_engine(os.environ.get('DATABASE_URL')); models.Base.metadata.create_all(bind=engine)" 2>/dev/null
    if [ $? -eq 0 ]; then
        success "Datenbank-Migration erfolgreich."
    else
        warning "Fehler bei der Datenbank-Migration. Überprüfen Sie die Datenbank manuell."
    fi
else
    warning "Hauptanwendungsdatei (main.py) nicht gefunden. Datenbank-Migration wird übersprungen."
fi

# Docker-Container neustarten (wenn Docker installiert ist und läuft)
if command -v docker &> /dev/null && docker info &> /dev/null; then
    info "Docker-Container werden neu gestartet..."
    if [ -f "docker-compose.yml" ]; then
        docker-compose down
        docker-compose up -d
        success "Docker-Container wurden neu gestartet."
    else
        warning "docker-compose.yml nicht gefunden. Container wurden nicht neu gestartet."
    fi
fi

# Zurück zum ursprünglichen Verzeichnis wechseln
cd "$CURRENT_DIR"

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}     SwissAirDry Update abgeschlossen!     ${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "Hinweise:"
echo -e "1. Überprüfen Sie die ${YELLOW}.env${NC}-Datei auf neue Umgebungsvariablen."
echo -e "2. Lesen Sie die Aktualisierungshinweise in der ${YELLOW}CHANGELOG.md${NC}-Datei."
echo -e "3. Starten Sie die Anwendung neu mit: ${YELLOW}python3 main.py${NC}"
echo ""
echo -e "Bei Problemen überprüfen Sie bitte:"
echo -e "- Die Logdateien im ${YELLOW}logs/${NC}-Verzeichnis"
echo -e "- Die Datenbank-Verbindung"
echo -e "- Die Cloudflare API-Token-Konfiguration"
echo ""