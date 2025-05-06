# SwissAirDry Installationsanleitung

> **HINWEIS: Diese Anleitung ist veraltet. Bitte verwenden Sie die neue [GENERALANLEITUNG.md](./GENERALANLEITUNG.md) für aktuelle Installations- und Konfigurationsanweisungen.**

Diese Anleitung beschreibt die Installation und Konfiguration des SwissAirDry-Systems. Das System besteht aus mehreren Komponenten, die einzeln oder zusammen installiert werden können.

## Systemvoraussetzungen

- Linux- oder macOS-Betriebssystem (für Windows wird WSL empfohlen)
- Python 3.8 oder höher
- PlatformIO (für ESP-Firmware-Entwicklung)
- Mosquitto MQTT-Broker (wird von den Installationsskripten installiert, falls nicht vorhanden)

## Schnellinstallation (Alle Komponenten)

Um alle Komponenten zu installieren, führen Sie das Hauptinstallationsskript aus:

```bash
./install_all.sh
```

Dieses Skript führt nacheinander die Installation der API, des MQTT-Brokers und der ESP-Firmware-Entwicklungsumgebung durch.

## Komponenten einzeln installieren

### 1. API-Komponente

Die API-Komponente stellt die REST-API für das SwissAirDry-System bereit.

```bash
./install_api.sh
```

Nach der Installation können Sie die API starten mit:

```bash
~/swissairdry/start_api.sh
```

und die Simple API mit:

```bash
~/swissairdry/start_simple_api.sh
```

### 2. MQTT-Broker

Der MQTT-Broker ermöglicht die Kommunikation zwischen den IoT-Geräten und der API.

```bash
./install_mqtt.sh
```

Nach der Installation können Sie den MQTT-Broker starten mit:

```bash
~/swissairdry/start_mqtt.sh
```

### 3. ESP-Firmware-Entwicklungsumgebung

Die ESP-Firmware-Komponente enthält die Entwicklungsumgebung für die ESP8266- und ESP32-C6-Firmware.

```bash
./install_esp.sh
```

Nach der Installation können Sie die Firmware kompilieren oder hochladen mit:

```bash
~/swissairdry/install_firmware.sh
```

oder die einzelnen Skripte direkt verwenden:

```bash
# ESP8266-Firmware kompilieren
~/swissairdry/firmware/compile_esp8266.sh

# ESP32-C6-Firmware kompilieren
~/swissairdry/firmware/compile_esp32c6.sh

# ESP8266-Firmware hochladen (optional: Port angeben)
~/swissairdry/firmware/upload_esp8266.sh [/dev/ttyUSB0]

# ESP32-C6-Firmware hochladen (optional: Port angeben)
~/swissairdry/firmware/upload_esp32c6.sh [/dev/ttyUSB0]

# Serielle Konsole öffnen (optional: Port angeben)
~/swissairdry/firmware/monitor.sh [/dev/ttyUSB0]
```

## Konfiguration

### Umgebungsvariablen

Die Konfiguration des Systems erfolgt über Umgebungsvariablen in der Datei `.env` im Installationsverzeichnis (standardmäßig `~/swissairdry/.env`).

Wichtige Konfigurationsparameter sind:

- `API_HOST` und `API_PORT`: Host und Port der API
- `MQTT_BROKER` und `MQTT_PORT`: Host und Port des MQTT-Brokers
- `MQTT_WS_PORT`: WebSocket-Port des MQTT-Brokers (Standard: 9001)
- `MQTT_SSL_ENABLED`: SSL/TLS für MQTT aktivieren (true/false)
- `MQTT_AUTH_ENABLED`: Authentifizierung für MQTT aktivieren (true/false)
- `MQTT_ALLOW_ANONYMOUS`: Anonyme Verbindungen zum MQTT-Broker erlauben (true/false)

### API-Konfiguration

Die API-Konfiguration wird über die `.env`-Datei gesteuert. Bei Bedarf können Sie die API-Komponente an Ihre Anforderungen anpassen.

### MQTT-Broker-Konfiguration

Die MQTT-Broker-Konfiguration wird über die Datei `~/swissairdry/mqtt/config/mosquitto.conf` gesteuert. Das Skript `update_mqtt_config.sh` aktualisiert diese Konfigurationsdatei basierend auf den Umgebungsvariablen.

### ESP-Firmware-Konfiguration

Die ESP-Firmware-Konfiguration wird in der Datei `~/swissairdry/firmware/platformio.ini` gespeichert. Die API-Konfiguration für die ESP-Firmware befindet sich in der Datei `~/swissairdry/firmware/api_config.txt`.

## Dienste starten und stoppen

Nach der Installation können Sie die Dienste mit den folgenden Befehlen starten und stoppen:

### Starten

```bash
# API starten
~/swissairdry/start_api.sh

# Simple API starten
~/swissairdry/start_simple_api.sh

# MQTT-Broker starten
~/swissairdry/start_mqtt.sh
```

### Stoppen

```bash
# API stoppen (inkl. Simple API)
~/swissairdry/stop_api.sh

# MQTT-Broker stoppen
~/swissairdry/stop_mqtt.sh
```

## Fehlerbehebung

### API-Probleme

Prüfen Sie die Logdateien unter `~/swissairdry/logs/` auf Fehler.

### MQTT-Probleme

Prüfen Sie die MQTT-Broker-Logs unter `~/swissairdry/mqtt/log/mosquitto.log` auf Fehler.

### ESP-Firmware-Probleme

Verwenden Sie das Monitor-Skript, um die serielle Konsole zu überwachen:

```bash
~/swissairdry/firmware/monitor.sh [/dev/ttyUSB0]
```

## Unterstützung

Bei Problemen oder Fragen wenden Sie sich bitte an das SwissAirDry-Team.