#!/bin/bash
# SwissAirDry - Installations-Report-Generator
# Dieses Skript generiert einen Bericht über die Systemumgebung und Installationsstatus
# von SwissAirDry v1.0.0

# Variablen
REPORT_FILE="swissairdry_install_report_$(date +%Y%m%d_%H%M%S).txt"

# Farben
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funktion zum Schreiben in die Report-Datei und auf die Konsole
log() {
    echo -e "$1" | tee -a "$REPORT_FILE"
}

# Report-Header
log "============================================"
log "       SwissAirDry Installation Report      "
log "             Version: v1.0.0                "
log "============================================"
log "Datum: $(date)"
log "Hostname: $(hostname)"
log ""

# Betriebssystem-Informationen
log "## Betriebssystem"
if [ -f /etc/os-release ]; then
    . /etc/os-release
    log "Name: $NAME"
    log "Version: $VERSION"
    log "ID: $ID"
elif [ -f /etc/lsb-release ]; then
    . /etc/lsb-release
    log "Distribution: $DISTRIB_ID"
    log "Release: $DISTRIB_RELEASE"
elif [ "$(uname)" == "Darwin" ]; then
    log "macOS Version: $(sw_vers -productVersion)"
else
    log "Betriebssystem konnte nicht ermittelt werden"
fi

log "Kernel: $(uname -r)"
log "Architektur: $(uname -m)"
log ""

# Python-Umgebung
log "## Python-Umgebung"
if command -v python3 &> /dev/null; then
    log "Python Version: $(python3 --version 2>&1)"
    log "Python Pfad: $(which python3)"
    
    if command -v pip3 &> /dev/null; then
        log "Pip Version: $(pip3 --version 2>&1)"
        log "Installierte Pakete:"
        pip3 list | grep -E "flask|sqlalchemy|requests|paho-mqtt|bleak|psycopg2|gunicorn|jinja2" | while read line; do
            log "  $line"
        done
    else
        log "Pip ist nicht installiert"
    fi
else
    log "Python ist nicht installiert"
fi
log ""

# Systemressourcen
log "## Systemressourcen"
if command -v free &> /dev/null; then
    log "Arbeitsspeicher:"
    free -h | grep -v + | while read line; do
        log "  $line"
    done
fi

if command -v df &> /dev/null; then
    log "Festplattenspeicher:"
    df -h / | while read line; do
        log "  $line"
    done
fi
log ""

# Netzwerk-Informationen
log "## Netzwerk"
log "Hostname: $(hostname)"
if command -v ip &> /dev/null; then
    log "IP-Adressen:"
    ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | while read line; do
        log "  $line"
    done
elif command -v ifconfig &> /dev/null; then
    log "IP-Adressen:"
    ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | while read line; do
        log "  $line"
    done
fi
log ""

# Docker-Status
log "## Docker-Status"
if command -v docker &> /dev/null; then
    log "Docker Version: $(docker --version)"
    log "Docker Compose installiert: $(command -v docker-compose &> /dev/null && echo 'Ja' || echo 'Nein')"
    
    # Prüfen, ob Docker-Daemon läuft
    if docker info &> /dev/null; then
        log "Docker-Daemon: Läuft"
        
        # SwissAirDry Docker-Container auflisten
        log "SwissAirDry Container:"
        docker ps --filter "name=swissairdry" | while read line; do
            log "  $line"
        done
    else
        log "Docker-Daemon: Gestoppt"
    fi
else
    log "Docker ist nicht installiert"
fi
log ""

# Datenbank-Status
log "## Datenbank-Status"
if command -v psql &> /dev/null; then
    log "PostgreSQL-Client installiert: Ja"
    # Hier könnten weitere PostgreSQL-spezifische Prüfungen folgen
else
    log "PostgreSQL-Client installiert: Nein"
fi
log ""

# SwissAirDry-Konfiguration
log "## SwissAirDry-Konfiguration"
# Prüfen, ob .env-Datei existiert
if [ -f ../.env ]; then
    log ".env-Datei: Vorhanden"
    # Prüfen, ob CLOUDFLARE_API_TOKEN konfiguriert ist (ohne den Wert anzuzeigen)
    if grep -q "CLOUDFLARE_API_TOKEN=" ../.env && ! grep -q "CLOUDFLARE_API_TOKEN=$" ../.env; then
        log "Cloudflare API-Token: Konfiguriert"
    else
        log "Cloudflare API-Token: Nicht konfiguriert"
    fi
else
    log ".env-Datei: Nicht vorhanden"
fi

# Prüfen, ob Domain-Management-Module vorhanden sind
if [ -d ../domain_management ]; then
    log "Domain-Management-Module: Installiert"
else
    log "Domain-Management-Module: Nicht installiert"
fi
log ""

# Zusammenfassung
log "## Zusammenfassung"
log "SwissAirDry v1.0.0 Installationsbericht wurde erstellt."
log "Für Support besuchen Sie: https://github.com/Arduinoeinsteiger/ERP"
log ""
log "Report-Datei: $REPORT_FILE"

# Ausgabe des Dateipfades
echo -e "${GREEN}Installationsbericht wurde erstellt: ${YELLOW}$REPORT_FILE${NC}"
echo -e "${GREEN}Sie können diesen Bericht für Support-Anfragen verwenden.${NC}"