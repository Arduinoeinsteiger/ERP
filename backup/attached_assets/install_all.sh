#!/bin/bash
#
# SwissAirDry Hauptinstallationsskript
# Dieses Skript installiert alle Komponenten des SwissAirDry-Systems
#

set -e  # Bei Fehlern abbrechen

echo "
===============================================
   SwissAirDry Hauptinstallationsskript
===============================================
"

# Arbeitsverzeichnis erstellen, falls nicht vorhanden
INSTALL_DIR="$HOME/swissairdry"

echo "[1/4] Arbeitsverzeichnis wird vorbereitet..."
mkdir -p "$INSTALL_DIR"

# Aktuelle Position merken
CURRENT_DIR=$(pwd)

# API-Komponente installieren
echo "[2/4] API-Komponente wird installiert..."
bash "$CURRENT_DIR/install_api.sh"
echo "API-Komponente installiert."

# MQTT-Komponente installieren
echo "[3/4] MQTT-Komponente wird installiert..."
bash "$CURRENT_DIR/install_mqtt.sh"
echo "MQTT-Komponente installiert."

# ESP-Firmware-Komponente installieren
echo "[4/4] ESP-Firmware-Komponente wird installiert..."
bash "$CURRENT_DIR/install_esp.sh"
echo "ESP-Firmware-Komponente installiert."

echo "
===============================================
   SwissAirDry Installation abgeschlossen
===============================================

Die SwissAirDry-Komponenten wurden in $INSTALL_DIR installiert.

Um die verschiedenen Komponenten zu starten:

1. API starten:
   $INSTALL_DIR/start_api.sh

2. Simple API starten:
   $INSTALL_DIR/start_simple_api.sh

3. MQTT-Broker starten:
   $INSTALL_DIR/start_mqtt.sh

4. ESP-Firmware kompilieren/hochladen:
   $INSTALL_DIR/install_firmware.sh

Um alle Dienste zu stoppen:
   $INSTALL_DIR/stop_api.sh
   $INSTALL_DIR/stop_mqtt.sh

Für weitere Informationen lesen Sie bitte die Dokumentation.
"