#!/bin/bash

# SwissAirDry Installations-Skript
# Dieses Skript installiert alle benötigten Komponenten für das SwissAirDry-System
# Copyright (c) 2025 Swiss Air Dry Team

# Farben für Ausgaben
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner und Versionsinformationen
echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║             SwissAirDry - Installations-Skript            ║"
echo "║                    Version 1.0.0 (2025)                   ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Hilfsfunktion für Fehleranzeige
function error_exit {
    echo -e "${RED}[FEHLER] $1${NC}"
    echo -e "${YELLOW}Installation abgebrochen.${NC}"
    exit 1
}

# Hilfsfunktion für Erfolgsmeldungen
function success_msg {
    echo -e "${GREEN}[ERFOLG] $1${NC}"
}

# Hilfsfunktion für Informationen
function info_msg {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Hilfsfunktion für Warnungen
function warning_msg {
    echo -e "${YELLOW}[WARNUNG] $1${NC}"
}

# Prüfe, ob das Skript im Hauptverzeichnis ausgeführt wird
if [ ! -f "./install.sh" ]; then
    error_exit "Dieses Skript muss im Hauptverzeichnis des Projekts ausgeführt werden."
fi

# Erstelle Backup des aktuellen Zustands
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
info_msg "Erstelle Backup des aktuellen Zustands in $BACKUP_DIR..."
mkdir -p "$BACKUP_DIR"
if [ -f ".env" ]; then
    cp .env "$BACKUP_DIR/"
fi
if [ -d "docker" ]; then
    cp -r docker "$BACKUP_DIR/"
fi
success_msg "Backup erstellt."

# Prüfe, ob Docker installiert ist
info_msg "Prüfe Docker-Installation..."
if ! command -v docker &> /dev/null; then
    warning_msg "Docker ist nicht installiert."
    echo -e "Möchten Sie die Docker-Installation überspringen? [j/N]"
    read -r skip_docker
    if [[ ! "$skip_docker" =~ ^[jJ]$ ]]; then
        error_exit "Docker wird für den Betrieb benötigt. Bitte installieren Sie Docker und versuchen Sie es erneut."
    else
        warning_msg "Docker-Installation übersprungen. Einige Funktionen werden nicht verfügbar sein."
    fi
else
    success_msg "Docker ist installiert."
fi

# Prüfe, ob Docker Compose installiert ist
info_msg "Prüfe Docker Compose Installation..."
if ! command -v docker-compose &> /dev/null; then
    warning_msg "Docker Compose ist nicht installiert."
    echo -e "Möchten Sie die Docker Compose-Installation überspringen? [j/N]"
    read -r skip_compose
    if [[ ! "$skip_compose" =~ ^[jJ]$ ]]; then
        error_exit "Docker Compose wird für den Betrieb benötigt. Bitte installieren Sie Docker Compose und versuchen Sie es erneut."
    else
        warning_msg "Docker Compose-Installation übersprungen. Die Container-Orchestrierung wird nicht verfügbar sein."
    fi
else
    success_msg "Docker Compose ist installiert."
fi

# Prüfe, ob das Docker-Verzeichnis existiert
info_msg "Prüfe Docker-Konfiguration..."
if [ ! -d "docker" ]; then
    warning_msg "Docker-Verzeichnis nicht gefunden."
    
    # Suche nach alternativen Docker-Konfigurationsverzeichnissen
    DOCKER_DIRS=$(find . -type d -name "docker*" -o -name "*docker" | grep -v "$BACKUP_DIR")
    
    if [ -n "$DOCKER_DIRS" ]; then
        echo -e "Folgende potenzielle Docker-Verzeichnisse wurden gefunden:"
        echo "$DOCKER_DIRS"
        echo -e "Möchten Sie eines dieser Verzeichnisse verwenden? [j/N]"
        read -r use_found_dir
        
        if [[ "$use_found_dir" =~ ^[jJ]$ ]]; then
            echo -e "Bitte geben Sie den Pfad des zu verwendenden Verzeichnisses ein:"
            read -r docker_dir
            
            if [ -d "$docker_dir" ]; then
                info_msg "Kopiere $docker_dir nach ./docker..."
                mkdir -p docker
                cp -r "$docker_dir"/* docker/
                success_msg "Docker-Verzeichnis erstellt."
            else
                error_exit "Das angegebene Verzeichnis existiert nicht."
            fi
        else
            # Suche nach docker-compose.yml in Hauptverzeichnis
            if [ -f "docker-compose.yml" ] || [ -f "docker-compose.yaml" ]; then
                info_msg "Docker Compose-Datei im Hauptverzeichnis gefunden."
                echo -e "Möchten Sie die vorhandene Docker Compose-Datei verwenden? [j/N]"
                read -r use_compose
                
                if [[ "$use_compose" =~ ^[jJ]$ ]]; then
                    info_msg "Erstelle Docker-Verzeichnis..."
                    mkdir -p docker
                    if [ -f "docker-compose.yml" ]; then
                        cp docker-compose.yml docker/
                    else
                        cp docker-compose.yaml docker/docker-compose.yml
                    fi
                    success_msg "Docker-Verzeichnis mit Docker Compose-Datei erstellt."
                else
                    error_exit "Docker-Konfiguration wird für den Betrieb benötigt. Bitte stellen Sie ein Docker-Verzeichnis bereit und versuchen Sie es erneut."
                fi
            else
                error_exit "Docker-Verzeichnis nicht gefunden. Bitte stellen Sie sicher, dass das Verzeichnis 'docker' im Hauptverzeichnis liegt oder erstellen Sie es manuell."
            fi
        fi
    else
        error_exit "Keine Docker-Konfiguration gefunden. Bitte stellen Sie sicher, dass das Verzeichnis 'docker' im Hauptverzeichnis liegt oder dass docker-compose.yml vorhanden ist."
    fi
else
    success_msg "Docker-Verzeichnis gefunden."
fi

# Prüfe, ob das docker-compose.yml existiert
if [ ! -f "docker/docker-compose.yml" ] && [ ! -f "docker/docker-compose.yaml" ]; then
    if [ -f "docker-compose.yml" ]; then
        info_msg "Kopiere docker-compose.yml in das Docker-Verzeichnis..."
        cp docker-compose.yml docker/
        success_msg "docker-compose.yml kopiert."
    elif [ -f "docker-compose.yaml" ]; then
        info_msg "Kopiere docker-compose.yaml in das Docker-Verzeichnis als docker-compose.yml..."
        cp docker-compose.yaml docker/docker-compose.yml
        success_msg "docker-compose.yml erstellt."
    else
        error_exit "Keine Docker Compose-Datei gefunden. Bitte stellen Sie eine docker-compose.yml im Docker-Verzeichnis bereit."
    fi
fi

# Prüfe, ob die .env-Datei existiert, sonst kopiere .env.example
info_msg "Prüfe .env-Datei..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        info_msg "Kopiere .env.example nach .env..."
        cp .env.example .env
        success_msg ".env-Datei erstellt."
        warning_msg "Bitte passen Sie die .env-Datei an Ihre Umgebung an (Datenbankzugang, MQTT-Server, Nextcloud-URL, etc.)."
    else
        warning_msg "Keine .env.example-Datei gefunden. Erstelle leere .env-Datei..."
        touch .env
        echo "# SwissAirDry Umgebungsvariablen" > .env
        echo "# Bitte passen Sie diese Werte an Ihre Umgebung an" >> .env
        echo "" >> .env
        echo "# Datenbank" >> .env
        echo "DB_HOST=localhost" >> .env
        echo "DB_PORT=5432" >> .env
        echo "DB_USER=swissairdry" >> .env
        echo "DB_PASSWORD=changeme" >> .env
        echo "DB_NAME=swissairdry" >> .env
        echo "" >> .env
        echo "# MQTT" >> .env
        echo "MQTT_HOST=localhost" >> .env
        echo "MQTT_PORT=1883" >> .env
        echo "MQTT_USER=" >> .env
        echo "MQTT_PASSWORD=" >> .env
        echo "" >> .env
        echo "# API" >> .env
        echo "API_PORT=5000" >> .env
        echo "API_HOST=0.0.0.0" >> .env
        success_msg "Leere .env-Datei erstellt."
        warning_msg "Bitte passen Sie die .env-Datei an Ihre Umgebung an."
    fi
else
    success_msg ".env-Datei gefunden."
fi

# Prüfe verfügbare Ports
info_msg "Prüfe verfügbare Ports..."

# Ports, die von SwissAirDry verwendet werden
declare -A ports
ports=(
    ["API"]=5000
    ["Simple API"]=5002
    ["MQTT"]=1883
    ["MQTT Websocket"]=9001
    ["PostgreSQL"]=5432
    ["Nextcloud"]=8080
    ["ExApp Server"]=3000
    ["ExApp Daemon"]=8701
    ["Nginx"]=80
    ["Nginx SSL"]=443
    ["Portainer"]=9000
)

# Funktion zur Überprüfung, ob ein Port belegt ist
function check_port {
    # Prüfe, ob der Port bereits belegt ist (Linux und macOS)
    if command -v lsof &> /dev/null; then
        lsof -i :$1 &> /dev/null
        return $?
    # Alternative für andere Systeme
    elif command -v netstat &> /dev/null; then
        netstat -tuln | grep ":$1 " &> /dev/null
        return $?
    else
        # Wenn weder lsof noch netstat verfügbar sind, können wir nicht prüfen
        return 1
    fi
}

USED_PORTS=()
for service in "${!ports[@]}"; do
    port=${ports[$service]}
    if check_port $port; then
        USED_PORTS+=("$service (Port $port)")
    fi
done

if [ ${#USED_PORTS[@]} -gt 0 ]; then
    warning_msg "Folgende Ports sind bereits belegt:"
    for used_port in "${USED_PORTS[@]}"; do
        echo "  - $used_port"
    done
    
    echo -e "Dies könnte zu Konflikten führen. Typische Dienste auf diesen Ports sind:"
    echo "  - Port 80/443: Webserver (Apache, Nginx)"
    echo "  - Port 1883/9001: MQTT-Broker (Mosquitto)"
    echo "  - Port 5432: PostgreSQL-Datenbank"
    echo "  - Port 8080: Alternative Webserver, Nextcloud"
    
    echo -e "Möchten Sie trotzdem fortfahren? [j/N]"
    read -r continue_with_used_ports
    
    if [[ ! "$continue_with_used_ports" =~ ^[jJ]$ ]]; then
        error_exit "Bitte stoppen Sie die Dienste, die die benötigten Ports belegen, und versuchen Sie es erneut."
    else
        warning_msg "Installation wird trotz belegter Ports fortgesetzt. Dies könnte zu Problemen führen."
    fi
else
    success_msg "Alle benötigten Ports sind verfügbar."
fi

# Installiere Python-Abhängigkeiten
info_msg "Installiere Python-Abhängigkeiten..."
pip install qrcode pillow paho-mqtt &> /dev/null
success_msg "Python-Abhängigkeiten installiert."

# Erstelle erforderliche Verzeichnisse
info_msg "Erstelle erforderliche Verzeichnisse..."
mkdir -p /tmp/mosquitto/data /tmp/mosquitto/log
chmod -R 777 /tmp/mosquitto
success_msg "Verzeichnisse erstellt."

# Berechtigungen für start.sh setzen
info_msg "Setze Ausführungsrechte für start.sh..."
chmod +x start.sh
success_msg "Ausführungsrechte gesetzt."

# Zusammenfassung der Installation
echo -e "\n${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                 Installation abgeschlossen                 ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo -e ""
echo -e "SwissAirDry wurde erfolgreich installiert. Hier ist eine Zusammenfassung:"
echo -e ""
echo -e "1. ${GREEN}Konfiguration:${NC}"
echo -e "   - .env-Datei: $(if [ -f ".env" ]; then echo "✓ Vorhanden"; else echo "✗ Fehlt"; fi)"
echo -e "   - Docker-Konfiguration: $(if [ -d "docker" ]; then echo "✓ Vorhanden"; else echo "✗ Fehlt"; fi)"
echo -e ""
echo -e "2. ${GREEN}Python-Abhängigkeiten:${NC}"
echo -e "   - qrcode, pillow, paho-mqtt: ${GREEN}Installiert${NC}"
echo -e ""
echo -e "3. ${GREEN}Startskript:${NC}"
echo -e "   - ./start.sh: ${GREEN}Bereit${NC}"
echo -e ""
echo -e "${BLUE}Nächste Schritte:${NC}"
echo -e "1. Prüfen und anpassen der .env-Datei an Ihre Umgebung"
echo -e "2. Starten des Systems mit ./start.sh"
echo -e "3. Zugriff auf die API unter http://localhost:5000"
echo -e "4. Zugriff auf den QR-Code-Generator unter http://localhost:5000/qrcode"
echo -e ""
echo -e "Bei Problemen konsultieren Sie bitte die Dokumentation in README.md oder INSTALLATION.md."
echo -e ""
echo -e "${GREEN}Vielen Dank, dass Sie SwissAirDry installiert haben!${NC}"
echo -e ""

exit 0