#!/bin/bash
#
# SwissAirDry Docker Stack Startskript
#

set -e

# Farben für die Konsole
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}
===============================================
   SwissAirDry Docker Stack Startskript
===============================================
${NC}"

# Prüfe, ob docker-compose installiert ist
if ! command -v docker-compose &> /dev/null && ! command -v docker &> /dev/null; then
    echo -e "${RED}Fehler: Weder docker-compose noch docker wurden gefunden.${NC}"
    echo "Bitte installieren Sie Docker und Docker Compose:"
    echo "https://docs.docker.com/engine/install/"
    exit 1
fi

# Prüfe, ob .env Datei existiert
if [ ! -f .env ]; then
    echo -e "${YELLOW}Keine .env Datei gefunden. Erstelle aus Vorlage...${NC}"
    cp .env.example .env
    echo -e "${GREEN}.env Datei erstellt. Bitte überprüfen und anpassen.${NC}"
fi

# Prüfe, ob Docker läuft
echo -e "${BLUE}Prüfe, ob Docker läuft...${NC}"
if ! docker info &> /dev/null; then
    echo -e "${RED}Docker scheint nicht zu laufen. Bitte starten Sie den Docker-Dienst.${NC}"
    exit 1
fi

# Prüfe, ob Verzeichnisse existieren und erzeuge sie, falls nötig
echo -e "${BLUE}Prüfe benötigte Verzeichnisse...${NC}"
mkdir -p ./api/app ./api/logs ./mosquitto/config ./mosquitto/data ./mosquitto/log ./nextcloud ./mqtt-config

# Prüfe, ob die MQTT-Konfiguration existiert und erzeuge sie, falls nötig
if [ ! -f ./mosquitto/config/mosquitto.conf ]; then
    echo -e "${YELLOW}Keine mosquitto.conf gefunden. Erstelle Standardkonfiguration...${NC}"
    cat > ./mosquitto/config/mosquitto.conf << 'EOL'
# SwissAirDry MQTT-Broker Konfiguration
# Diese Datei wird automatisch generiert - manuelle Änderungen werden überschrieben

# Netzwerk-Einstellungen
listener 1883
allow_anonymous true

# WebSockets für Web-Clients
listener 9001
protocol websockets

# Persistenz und Logging
persistence true
persistence_location /mosquitto/data/
log_dest stdout
log_dest file /mosquitto/log/mosquitto.log
log_type all

# Erweiterte Einstellungen
max_connections -1
max_packet_size 16384
max_inflight_messages 40
max_queued_messages 1000
queue_qos0_messages false

# SSL/TLS Konfiguration (auskommentiert)
# listener 8883
# certfile /mosquitto/certs/fullchain.pem
# keyfile /mosquitto/certs/privkey.pem
# require_certificate false

# Authentifizierung (auskommentiert)
# password_file /mosquitto/config/mosquitto.passwd
EOL
    cp ./mosquitto/config/mosquitto.conf ./mosquitto/config/mosquitto.conf.template
    echo -e "${GREEN}mosquitto.conf erstellt.${NC}"
fi

# Frage, ob nur Images aus der Registry verwendet werden sollen
read -p "Möchten Sie nur vorgefertigte Docker-Images verwenden und nicht lokal bauen? [y/N] " use_registry_only
if [ "$use_registry_only" = "y" ] || [ "$use_registry_only" = "Y" ]; then
    # Starte Docker Compose ohne Build
    echo -e "${BLUE}Starte Docker Compose Stack mit vorgefertigten Images...${NC}"
    docker-compose up -d --no-build
else
    # Starte Docker Compose mit lokalem Build
    echo -e "${BLUE}Starte Docker Compose Stack mit lokalem Build...${NC}"
    docker-compose up -d
fi

# Prüfe, ob alle Container laufen
echo -e "${BLUE}Prüfe Container-Status...${NC}"
sleep 5
if docker-compose ps | grep -q "Exit\|unhealthy"; then
    echo -e "${RED}Einige Container sind nicht ordnungsgemäß gestartet. Bitte prüfen Sie die Logs:${NC}"
    docker-compose ps
    echo -e "${YELLOW}Sie können die Logs mit 'docker-compose logs' überprüfen.${NC}"
else
    echo -e "${GREEN}Alle Container laufen!${NC}"
    docker-compose ps
    
    # Zeige die Zugangsdaten an
    echo -e "\n${BLUE}===============================================${NC}"
    echo -e "${GREEN}SwissAirDry Stack wurde erfolgreich gestartet!${NC}"
    echo -e "${BLUE}===============================================${NC}"
    echo -e "API läuft auf: http://localhost:$(grep "API_PORT" .env | cut -d= -f2 || echo "5000")"
    echo -e "Simple API läuft auf: http://localhost:$(grep "SIMPLE_API_PORT" .env | cut -d= -f2 || echo "5001")"
    echo -e "MQTT Broker läuft auf Port: $(grep "MQTT_PORT" .env | cut -d= -f2 || echo "1883")"
    echo -e "MQTT WebSockets laufen auf Port: $(grep "MQTT_WS_PORT" .env | cut -d= -f2 || echo "9001")"
    echo -e "ExApp läuft auf: http://localhost:$(grep "EXAPP_PORT" .env | cut -d= -f2 || echo "8080")"
    echo -e "ExApp-Daemon läuft auf: http://localhost:$(grep "EXAPP_DAEMON_PORT" .env | cut -d= -f2 || echo "8081")"
    echo -e "Postgres DB ist auf Port: $(grep "DB_PORT" .env | cut -d= -f2 || echo "5432") verfügbar"
    echo -e "${BLUE}===============================================${NC}"
    echo -e "Logs anzeigen mit: docker-compose logs -f"
    echo -e "Stack stoppen mit: ./stop_docker.sh"
    echo -e "${BLUE}===============================================${NC}"
fi

exit 0