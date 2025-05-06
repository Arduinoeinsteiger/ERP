#!/bin/bash
# SwissAirDry MQTT-Konfigurationsgenerator
# Generiert mosquitto.conf aus Umgebungsvariablen

set -e

CONFIG_FILE="/config/mosquitto.conf"
TEMPLATE_FILE="/config/mosquitto.conf.template"

# Warte ein bisschen, damit andere Container Zeit haben zu starten
sleep 2

echo "Starting MQTT configuration update..."

# Wenn Template nicht existiert, aktuelle Konfiguration als Template speichern oder Standardtemplate erstellen
if [ ! -f "$TEMPLATE_FILE" ]; then
  if [ -f "$CONFIG_FILE" ]; then
    echo "Creating template from existing config file..."
    cp "$CONFIG_FILE" "$TEMPLATE_FILE"
  else
    echo "Creating standard template..."
    cat > "$TEMPLATE_FILE" << 'EOL'
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
  fi
fi

# Konfigurationsdatei aus Template erstellen
echo "Generating configuration from template..."
cp "$TEMPLATE_FILE" "$CONFIG_FILE"

# MQTT Port Konfiguration
if [ -n "$MQTT_PORT" ]; then
  echo "Setting MQTT port to $MQTT_PORT..."
  sed -i -e "s|listener 1883|listener $MQTT_PORT|g" "$CONFIG_FILE"
fi

# WebSocket Port Konfiguration
if [ -n "$MQTT_WS_PORT" ]; then
  echo "Setting WebSocket port to $MQTT_WS_PORT..."
  sed -i -e "s|listener 9001|listener $MQTT_WS_PORT|g" "$CONFIG_FILE"
fi

# Maximale Verbindungen
if [ -n "$MQTT_MAX_CONNECTIONS" ]; then
  echo "Setting max connections to $MQTT_MAX_CONNECTIONS..."
  sed -i -e "s|max_connections -1|max_connections $MQTT_MAX_CONNECTIONS|g" "$CONFIG_FILE"
fi

# Paketgröße
if [ -n "$MQTT_MAX_PACKET_SIZE" ]; then
  echo "Setting max packet size to $MQTT_MAX_PACKET_SIZE..."
  sed -i -e "s|max_packet_size 16384|max_packet_size $MQTT_MAX_PACKET_SIZE|g" "$CONFIG_FILE"
fi

# Inflight Messages
if [ -n "$MQTT_MAX_INFLIGHT_MESSAGES" ]; then
  echo "Setting max inflight messages to $MQTT_MAX_INFLIGHT_MESSAGES..."
  sed -i -e "s|max_inflight_messages 40|max_inflight_messages $MQTT_MAX_INFLIGHT_MESSAGES|g" "$CONFIG_FILE"
fi

# Queued Messages
if [ -n "$MQTT_MAX_QUEUED_MESSAGES" ]; then
  echo "Setting max queued messages to $MQTT_MAX_QUEUED_MESSAGES..."
  sed -i -e "s|max_queued_messages 1000|max_queued_messages $MQTT_MAX_QUEUED_MESSAGES|g" "$CONFIG_FILE"
fi

# Queue QoS0 Messages
if [ -n "$MQTT_QUEUE_QOS0_MESSAGES" ]; then
  echo "Setting queue QoS0 messages to $MQTT_QUEUE_QOS0_MESSAGES..."
  sed -i -e "s|queue_qos0_messages false|queue_qos0_messages $MQTT_QUEUE_QOS0_MESSAGES|g" "$CONFIG_FILE"
fi

# SSL aktivieren/deaktivieren
if [ "$MQTT_SSL_ENABLED" = "true" ]; then
  echo "Enabling SSL..."
  # Auskommentierung der SSL-Konfiguration entfernen
  sed -i -e 's|# listener 8883|listener 8883|g' "$CONFIG_FILE"
  sed -i -e "s|# certfile /mosquitto/certs/fullchain.pem|certfile ${MQTT_SSL_CERT_PATH:-/mosquitto/certs/fullchain.pem}|g" "$CONFIG_FILE"
  sed -i -e "s|# keyfile /mosquitto/certs/privkey.pem|keyfile ${MQTT_SSL_KEY_PATH:-/mosquitto/certs/privkey.pem}|g" "$CONFIG_FILE"
  sed -i -e 's|# require_certificate false|require_certificate false|g' "$CONFIG_FILE"
fi

# Authentifizierung aktivieren/deaktivieren
if [ "$MQTT_AUTH_ENABLED" = "true" ]; then
  echo "Enabling authentication..."
  # Anonyme Verbindungen deaktivieren
  sed -i -e 's|allow_anonymous true|allow_anonymous false|g' "$CONFIG_FILE"
  # Auskommentierung der Passwortdatei entfernen
  sed -i -e 's|# password_file /mosquitto/config/mosquitto.passwd|password_file /mosquitto/config/mosquitto.passwd|g' "$CONFIG_FILE"
  
  # Wenn Benutzername und Passwort gesetzt sind, Benutzer erstellen
  if [ -n "$MQTT_USERNAME" ] && [ -n "$MQTT_PASSWORD" ]; then
    echo "Creating user $MQTT_USERNAME..."
    # Passwortdatei erstellen/aktualisieren
    touch /tmp/pwdfile
    mosquitto_passwd -b /tmp/pwdfile "$MQTT_USERNAME" "$MQTT_PASSWORD"
    mkdir -p /config
    cp /tmp/pwdfile /config/mosquitto.passwd
    rm /tmp/pwdfile
  fi
else
  # Anonyme Verbindungen ermöglichen, falls es explizit in der Umgebungsvariable gesetzt ist
  if [ "$MQTT_ALLOW_ANONYMOUS" = "true" ]; then
    echo "Enabling anonymous connections..."
    sed -i -e 's|allow_anonymous false|allow_anonymous true|g' "$CONFIG_FILE"
  elif [ "$MQTT_ALLOW_ANONYMOUS" = "false" ]; then
    echo "Disabling anonymous connections..."
    sed -i -e 's|allow_anonymous true|allow_anonymous false|g' "$CONFIG_FILE"
  fi
fi

echo "MQTT configuration updated successfully!"
cat "$CONFIG_FILE"

exit 0