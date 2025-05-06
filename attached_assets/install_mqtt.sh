#!/bin/bash
#
# SwissAirDry MQTT Broker Installationsskript
# Dieses Skript installiert nur die MQTT-Komponente des SwissAirDry-Systems
#

set -e  # Bei Fehlern abbrechen

echo "
===============================================
   SwissAirDry MQTT Broker Installationsskript
===============================================
"

# Arbeitsverzeichnis erstellen, falls nicht vorhanden
INSTALL_DIR="$HOME/swissairdry"
MQTT_DIR="$INSTALL_DIR/mqtt"
MQTT_DATA_DIR="$MQTT_DIR/data"
MQTT_LOG_DIR="$MQTT_DIR/log"
MQTT_CONFIG_DIR="$MQTT_DIR/config"

echo "[1/5] Arbeitsverzeichnis wird vorbereitet..."
mkdir -p "$MQTT_DIR"
mkdir -p "$MQTT_DATA_DIR"
mkdir -p "$MQTT_LOG_DIR"
mkdir -p "$MQTT_CONFIG_DIR"

# Aktuelle Position merken
CURRENT_DIR=$(pwd)

# Abhängigkeiten prüfen und installieren
echo "[2/5] Mosquitto installieren (wenn möglich)..."
if command -v apt-get &> /dev/null; then
    echo "apt-get gefunden, versuche Mosquitto zu installieren..."
    sudo apt-get update
    sudo apt-get install -y mosquitto mosquitto-clients
elif command -v yum &> /dev/null; then
    echo "yum gefunden, versuche Mosquitto zu installieren..."
    sudo yum install -y mosquitto mosquitto-clients
elif command -v brew &> /dev/null; then
    echo "Homebrew gefunden, versuche Mosquitto zu installieren..."
    brew install mosquitto
elif command -v mosquitto &> /dev/null; then
    echo "Mosquitto ist bereits installiert."
else
    echo "WARNUNG: Konnte Mosquitto nicht automatisch installieren. Bitte manuell installieren."
    echo "Installationsanleitung: http://mosquitto.org/download/"
fi

# Environment-Variablen
echo "[3/5] MQTT-Konfiguration wird erstellt..."

# Wenn .env existiert, ergänzen, sonst neu erstellen
if [ -f "$INSTALL_DIR/.env" ]; then
    # Prüfen, ob MQTT-Konfiguration bereits vorhanden ist
    if grep -q "MQTT_BROKER" "$INSTALL_DIR/.env"; then
        echo "MQTT-Konfiguration in .env Datei bereits vorhanden."
    else
        # MQTT-Konfiguration hinzufügen
        cat >> "$INSTALL_DIR/.env" << 'EOL'

# MQTT-Konfiguration
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_WS_PORT=9001
MQTT_SSL_ENABLED=false
MQTT_AUTH_ENABLED=false
MQTT_ALLOW_ANONYMOUS=true
MQTT_USERNAME=
MQTT_PASSWORD=
MQTT_CLIENT_ID=swissairdry-mqtt
MQTT_USE_SSL=false
MQTT_QOS=1
MQTT_RETAIN=true
MQTT_TOPIC_PREFIX=swissairdry
EOL
    fi
else
    # Neue .env Datei mit MQTT-Konfiguration erstellen
    cat > "$INSTALL_DIR/.env" << 'EOL'
# SwissAirDry MQTT Konfiguration
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_WS_PORT=9001
MQTT_SSL_ENABLED=false
MQTT_AUTH_ENABLED=false
MQTT_ALLOW_ANONYMOUS=true
MQTT_USERNAME=
MQTT_PASSWORD=
MQTT_CLIENT_ID=swissairdry-mqtt
MQTT_USE_SSL=false
MQTT_QOS=1
MQTT_RETAIN=true
MQTT_TOPIC_PREFIX=swissairdry
EOL
fi

# Mosquitto Konfigurationsdatei erstellen
echo "[4/5] Mosquitto-Konfiguration wird erstellt..."
cat > "$MQTT_CONFIG_DIR/mosquitto.conf" << 'EOL'
# SwissAirDry MQTT-Broker Konfiguration
# Diese Datei wird automatisch erstellt - manuelle Änderungen werden überschrieben

# Netzwerk-Einstellungen
listener 1883
allow_anonymous true

# WebSockets für Web-Clients
listener 9001
protocol websockets

# Persistenz und Logging
persistence true
persistence_location /path/to/data/
log_dest stdout
log_dest file /path/to/log/mosquitto.log
log_type all

# SSL/TLS Konfiguration (auskommentiert für Test/Entwicklung)
# listener 8883
# certfile /path/to/certs/fullchain.pem
# keyfile /path/to/certs/privkey.pem
# require_certificate false

# Erweiterte Einstellungen
max_connections -1
max_packet_size 16384
max_inflight_messages 40
max_queued_messages 1000
queue_qos0_messages false

# Authentifizierung (auskommentiert für Test/Entwicklung)
# password_file /path/to/config/mosquitto.passwd
EOL

# Pfade in der Konfigurationsdatei anpassen
sed -i -e "s|/path/to/data/|$MQTT_DATA_DIR/|g" "$MQTT_CONFIG_DIR/mosquitto.conf"
sed -i -e "s|/path/to/log/|$MQTT_LOG_DIR/|g" "$MQTT_CONFIG_DIR/mosquitto.conf"
sed -i -e "s|/path/to/config/|$MQTT_CONFIG_DIR/|g" "$MQTT_CONFIG_DIR/mosquitto.conf"
sed -i -e "s|/path/to/certs/|$MQTT_DIR/certs/|g" "$MQTT_CONFIG_DIR/mosquitto.conf"

# Scripts zum Aktualisieren der Mosquitto-Konfiguration erstellen
cat > "$MQTT_DIR/update_mqtt_config.sh" << 'EOL'
#!/bin/bash

# SwissAirDry MQTT-Konfigurationsaktualisierungsskript
# Aktualisiert die Mosquitto-Konfiguration basierend auf Umgebungsvariablen

# Zum Installationsverzeichnis wechseln
cd "$(dirname "$0")"
MQTT_DIR="$(pwd)"
INSTALL_DIR="$(dirname "$MQTT_DIR")"

# Umgebungsvariablen laden
if [ -f "$INSTALL_DIR/.env" ]; then
  export $(grep -v '^#' "$INSTALL_DIR/.env" | xargs)
fi

CONFIG_FILE="$MQTT_DIR/config/mosquitto.conf"
TEMPLATE_FILE="$MQTT_DIR/config/mosquitto.conf.template"

# Wenn Template nicht existiert, aktuelle Konfiguration als Template speichern
if [ ! -f "$TEMPLATE_FILE" ]; then
  cp "$CONFIG_FILE" "$TEMPLATE_FILE"
fi

# Konfigurationsdatei aus Template erstellen
cp "$TEMPLATE_FILE" "$CONFIG_FILE"

# SSL aktivieren/deaktivieren
if [ "$MQTT_SSL_ENABLED" = "true" ]; then
  # Auskommentierung der SSL-Konfiguration entfernen
  sed -i -e 's|# listener 8883|listener 8883|g' "$CONFIG_FILE"
  sed -i -e 's|# certfile|certfile|g' "$CONFIG_FILE"
  sed -i -e 's|# keyfile|keyfile|g' "$CONFIG_FILE"
  sed -i -e 's|# require_certificate|require_certificate|g' "$CONFIG_FILE"
fi

# Authentifizierung aktivieren/deaktivieren
if [ "$MQTT_AUTH_ENABLED" = "true" ]; then
  # Anonyme Verbindungen deaktivieren
  sed -i -e 's|allow_anonymous true|allow_anonymous false|g' "$CONFIG_FILE"
  # Auskommentierung der Passwortdatei entfernen
  sed -i -e 's|# password_file|password_file|g' "$CONFIG_FILE"
  
  # Wenn Benutzername und Passwort gesetzt sind, Benutzer erstellen
  if [ -n "$MQTT_USERNAME" ] && [ -n "$MQTT_PASSWORD" ]; then
    # Passwortdatei erstellen/aktualisieren
    if [ ! -f "$MQTT_DIR/config/mosquitto.passwd" ]; then
      mosquitto_passwd -c "$MQTT_DIR/config/mosquitto.passwd" "$MQTT_USERNAME" "$MQTT_PASSWORD"
    else
      mosquitto_passwd -b "$MQTT_DIR/config/mosquitto.passwd" "$MQTT_USERNAME" "$MQTT_PASSWORD"
    fi
  fi
else
  # Anonyme Verbindungen ermöglichen
  sed -i -e 's|allow_anonymous false|allow_anonymous true|g' "$CONFIG_FILE"
fi

# WebSocket-Port konfigurieren
if [ -n "$MQTT_WS_PORT" ]; then
  sed -i -e "s|listener 9001|listener $MQTT_WS_PORT|g" "$CONFIG_FILE"
fi

echo "MQTT-Konfiguration aktualisiert in $CONFIG_FILE"
EOL

chmod +x "$MQTT_DIR/update_mqtt_config.sh"

# Mosquitto als Template speichern
cp "$MQTT_CONFIG_DIR/mosquitto.conf" "$MQTT_CONFIG_DIR/mosquitto.conf.template"

# Startup-Skript erstellen
echo "[5/5] Startup-Skript wird erstellt..."
cat > "$INSTALL_DIR/start_mqtt.sh" << 'EOL'
#!/bin/bash

# SwissAirDry MQTT-Broker-Startskript
echo "SwissAirDry MQTT-Broker wird gestartet..."

# Zum Installationsverzeichnis wechseln
cd "$(dirname "$0")"

# Umgebungsvariablen laden
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

# MQTT-Konfiguration aktualisieren
./mqtt/update_mqtt_config.sh

# Mosquitto starten
echo "Starte Mosquitto MQTT-Broker..."
mkdir -p mqtt/data mqtt/log
mosquitto -c mqtt/config/mosquitto.conf -d -v > mqtt/log/mosquitto.log 2>&1
echo $! > mqtt.pid

echo "MQTT-Broker läuft auf Port $MQTT_PORT und WebSocket-Port $MQTT_WS_PORT"
echo "Logs: $PWD/mqtt/log/mosquitto.log"
echo "PID: $(cat mqtt.pid)"

echo "MQTT-Broker erfolgreich gestartet!"
EOL

chmod +x "$INSTALL_DIR/start_mqtt.sh"

# Stop-Skript erstellen
cat > "$INSTALL_DIR/stop_mqtt.sh" << 'EOL'
#!/bin/bash

# SwissAirDry MQTT-Broker-Stoppskript
echo "SwissAirDry MQTT-Broker wird gestoppt..."

# Zum Installationsverzeichnis wechseln
cd "$(dirname "$0")"

# MQTT-Broker stoppen
if [ -f mqtt.pid ]; then
  PID=$(cat mqtt.pid)
  if ps -p $PID > /dev/null; then
    echo "Beende MQTT-Broker-Prozess (PID: $PID)..."
    kill $PID
    rm mqtt.pid
  else
    echo "MQTT-Broker-Prozess ist nicht mehr aktiv."
    rm mqtt.pid
  fi
else
  echo "Keine MQTT-Broker-PID-Datei gefunden."
fi

echo "SwissAirDry MQTT-Broker gestoppt!"
EOL

chmod +x "$INSTALL_DIR/stop_mqtt.sh"

echo "Installation abgeschlossen!"
echo ""
echo "Der SwissAirDry MQTT-Broker wurde in $INSTALL_DIR installiert."
echo ""
echo "Um den MQTT-Broker zu starten, führen Sie folgenden Befehl aus:"
echo "   $INSTALL_DIR/start_mqtt.sh"
echo ""
echo "Um den MQTT-Broker zu stoppen, führen Sie folgenden Befehl aus:"
echo "   $INSTALL_DIR/stop_mqtt.sh"
echo ""
echo "Der MQTT-Broker ist erreichbar unter:"
echo "   MQTT: localhost:1883"
echo "   WebSocket: localhost:9001"
echo ""