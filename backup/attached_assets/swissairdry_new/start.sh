#!/bin/bash

# SwissAirDry Start-Skript
# Dieses Skript startet alle benötigten Komponenten des SwissAirDry-Systems

# Farben für Ausgaben
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}SwissAirDry Starter${NC}"
echo "------------------------------"

# Prüfen, ob die benötigten Abhängigkeiten installiert sind
echo -e "${YELLOW}Prüfe Abhängigkeiten...${NC}"
MISSING_DEPS=0

# Python prüfen
if ! command -v python &> /dev/null; then
    echo -e "${RED}Python nicht gefunden!${NC}"
    MISSING_DEPS=1
fi

# Mosquitto prüfen
if ! command -v mosquitto &> /dev/null; then
    echo -e "${RED}Mosquitto MQTT Broker nicht gefunden!${NC}"
    MISSING_DEPS=1
fi

# Python-Module prüfen
echo "Prüfe Python-Module..."
python -c "import qrcode" 2>/dev/null || { echo -e "${RED}Python-Modul 'qrcode' nicht gefunden!${NC}"; MISSING_DEPS=1; }
python -c "import PIL" 2>/dev/null || { echo -e "${RED}Python-Modul 'pillow' nicht gefunden!${NC}"; MISSING_DEPS=1; }
python -c "import paho.mqtt.client" 2>/dev/null || { echo -e "${RED}Python-Modul 'paho-mqtt' nicht gefunden!${NC}"; MISSING_DEPS=1; }

# Wenn Abhängigkeiten fehlen, Installationshinweise anzeigen
if [ $MISSING_DEPS -eq 1 ]; then
    echo -e "${YELLOW}Fehlende Abhängigkeiten gefunden. Bitte installieren Sie die fehlenden Komponenten:${NC}"
    echo "pip install qrcode pillow paho-mqtt"
    echo "apt-get install mosquitto  # oder entsprechender Paketmanager"
    echo -e "${RED}Start abgebrochen.${NC}"
    exit 1
fi

echo -e "${GREEN}Alle Abhängigkeiten vorhanden.${NC}"

# MQTT-Broker starten
echo -e "${YELLOW}Starte MQTT-Broker...${NC}"
mkdir -p /tmp/mosquitto/data /tmp/mosquitto/log
chmod -R 777 /tmp/mosquitto
mosquitto -c mqtt/mosquitto.conf -d

if [ $? -eq 0 ]; then
    echo -e "${GREEN}MQTT-Broker erfolgreich gestartet.${NC}"
else
    echo -e "${RED}Fehler beim Starten des MQTT-Brokers!${NC}"
    exit 1
fi

# API-Server starten
echo -e "${YELLOW}Starte Minimal HTTP Server...${NC}"
echo -e "${GREEN}Server wird auf Port 5000 gestartet.${NC}"
echo -e "${YELLOW}Drücken Sie Ctrl+C, um alle Dienste zu beenden.${NC}"
echo ""

# In Verzeichnis wechseln und Server starten
cd api
python minimal_http_server.py

# Cleanup beim Beenden
function cleanup {
    echo -e "\n${YELLOW}Beende Dienste...${NC}"
    pkill -f mosquitto
    echo -e "${GREEN}Alle Dienste beendet.${NC}"
}

# Trap für Ctrl+C
trap cleanup EXIT

# Warten auf Benutzerinteraktion
wait