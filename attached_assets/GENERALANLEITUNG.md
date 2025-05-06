# SwissAirDry Generalanleitung 2025

Diese Anleitung bietet einen umfassenden Überblick über das SwissAirDry-System, seine Komponenten und deren Installation, Konfiguration sowie Wartung. SwissAirDry ist eine Plattform zur Überwachung und Steuerung von Trocknungsgeräten mit IoT-Integration, Auftragsmanagement und umfassender Datenanalyse.

## Systemübersicht

SwissAirDry besteht aus folgenden Hauptkomponenten:

1. **API-System**: Der Kern des Systems, implementiert mit FastAPI (Haupt-API) und Flask (Simple API) für verschiedene Anwendungsfälle
2. **MQTT-Broker**: Für die Kommunikation mit IoT-Geräten
3. **Datenbank**: PostgreSQL für die Datenspeicherung
4. **Nextcloud ExApp**: Integration für Projektmanagement und Auftragsabwicklung (ersetzt die frühere Deck App)
5. **Web-Frontend**: Benutzeroberfläche für die Interaktion mit dem System
6. **IoT-Firmware**: Für ESP8266/ESP32-C6 basierte Geräte

## Installationsmethoden

Es gibt zwei Hauptmethoden zur Installation:

1. **Docker-Installation** (empfohlen): Alle Komponenten werden in Docker-Containern betrieben
2. **Direkte Installation**: Komponenten werden direkt auf dem Host-System installiert

## 1. Docker-Installation (Empfohlen)

Die Docker-Installation ist die empfohlene Methode, da sie eine konsistente Umgebung gewährleistet und einfach zu verwalten ist.

### Voraussetzungen

- Docker und Docker Compose
- Linux-, macOS- oder Windows-Betriebssystem
- 2 GB RAM (minimal), 4 GB empfohlen
- 20 GB freier Festplattenspeicher
- Internetverbindung für den Download der Docker-Images

### Installation mit All-in-One-Skript

Die einfachste Methode ist die Verwendung des All-in-One-Skripts:

```bash
./start-all-in-one.sh
```

Dieses Skript:
1. Prüft, ob Docker installiert ist
2. Erstellt notwendige Konfigurationsdateien, falls nicht vorhanden
3. Erstellt die Docker-Container
4. Startet alle Dienste

### Manuelle Docker-Installation

Für mehr Kontrolle können Sie die Installation auch manuell durchführen:

1. Repository klonen oder entpacken
   ```bash
   git clone https://github.com/swissairdry/swissairdry.git
   cd swissairdry
   ```

2. Konfigurationsdatei erstellen
   ```bash
   cp .env.example .env
   nano .env
   ```

3. Docker Compose ausführen
   ```bash
   docker-compose -f docker-compose-all-in-one.yml up -d
   ```

4. Status überprüfen
   ```bash
   docker-compose ps
   ```

### Standard-Ports und Komponenten

| Komponente   | Standard-Port | Beschreibung                                     |
|--------------|---------------|-------------------------------------------------|
| API          | 5000          | Haupt-API basierend auf FastAPI                  |
| Simple API   | 5001          | Vereinfachte API für einfache Anwendungsfälle    |
| MQTT-Broker  | 1883          | MQTT-Broker für IoT-Kommunikation                |
| MQTT-WebSockets | 9001       | WebSocket-Schnittstelle für MQTT                 |
| ExApp        | 3000          | Nextcloud-Integration (Web-Interface)            |
| ExApp-Daemon | 8701          | Synchronisationsdienst für ExApp                 |
| PostgreSQL   | 5432          | Datenbank                                        |
| Nextcloud    | 8080          | Nextcloud-Instanz (wenn aktiviert)               |
| Nginx        | 80/443        | Reverse Proxy (wenn aktiviert)                   |
| Portainer    | 9000          | Container-Management (wenn aktiviert)            |

## 2. Direkte Installation

Die direkte Installation installiert die Komponenten direkt auf dem Host-System.

### Voraussetzungen

- Linux- oder macOS-Betriebssystem (für Windows wird WSL empfohlen)
- Python 3.9 oder höher
- PostgreSQL 13 oder höher
- Node.js 16 oder höher (für ExApp)

### Installation mit Skript

Verwenden Sie das Hauptinstallationsskript:

```bash
./install_all.sh
```

Dieses Skript führt nacheinander die Installation aller Komponenten durch.

### Komponenten einzeln installieren

#### API-Komponente

```bash
./install_api.sh
```

#### MQTT-Broker

```bash
./install_mqtt.sh
```

#### ESP-Firmware-Entwicklungsumgebung

```bash
./install_esp.sh
```

#### ExApp-Integration

```bash
./install_exapp.sh
```

## ExApp-Integration (Neu ab 2025)

Die ExApp-Integration ist der Nachfolger der früheren Deck-Integration und bietet erweiterte Funktionen für die Projektmanagement- und Auftragsabwicklung.

### Funktionen der ExApp

- Auftrags- und Projektmanagement
- Geräte- und Standortverwaltung
- Echtzeit-Datenaustausch mit API
- Benutzerfreundliche Oberfläche
- Erweitertes Berechtigungssystem
- Multi-Mandantenfähigkeit

### ExApp-Konfiguration

Die ExApp-Konfiguration erfolgt über die `.env`-Datei mit folgenden Parametern:

- `EXAPP_URL`: URL der ExApp-Instanz
- `EXAPP_API_KEY`: API-Schlüssel für die ExApp
- `EXAPP_CLIENT_ID`: Client-ID für die OAuth2-Authentifizierung
- `EXAPP_CLIENT_SECRET`: Client-Secret für die OAuth2-Authentifizierung
- `EXAPP_DAEMON_URL`: URL des ExApp-Daemons
- `EXAPP_DAEMON_PORT`: Port des ExApp-Daemons (Standard: 8701)

## Firmware für ESP-Geräte

SwissAirDry unterstützt verschiedene ESP-basierte Geräte:

1. **ESP8266 (Wemos D1 Mini)**: Kostengünstige Geräte mit WLAN
2. **ESP32-C6**: Neuere Geräte mit Bluetooth Low Energy (BLE) und WLAN

### Firmware-Konfiguration

Die Firmware wird über die Datei `firmware_config.h` konfiguriert:

```cpp
// WLAN-Konfiguration
#define WIFI_SSID "Ihr_WLAN_Name"
#define WIFI_PASSWORD "Ihr_WLAN_Passwort"

// API-Konfiguration
#define API_HOST "api.swissairdry.local"
#define API_PORT 5000

// MQTT-Konfiguration
#define MQTT_BROKER "mqtt.swissairdry.local"
#define MQTT_PORT 1883
#define MQTT_USER "mqtt_user"
#define MQTT_PASSWORD "mqtt_password"
```

### Firmware hochladen

#### ESP8266 (Wemos D1 Mini)

```bash
# Mit PlatformIO
pio run -e wemos_d1_mini -t upload

# Mit Arduino IDE
# Wählen Sie "LOLIN(WEMOS) D1 R2 & mini" als Board
```

#### ESP32-C6

```bash
# Mit PlatformIO
pio run -e esp32-c6-devkit -t upload

# Mit Arduino IDE
# Wählen Sie "ESP32C6 Dev Module" als Board
```

## Konfiguration und Anpassung

### Umgebungsvariablen

Die Konfiguration des Systems erfolgt über Umgebungsvariablen in der Datei `.env`:

```
# API-Konfiguration
API_HOST=0.0.0.0
API_PORT=5000
API_DEBUG=true
API_RELOAD=true

# Simple API
SIMPLE_API_PORT=5001

# MQTT-Konfiguration
MQTT_HOST=localhost
MQTT_PORT=1883
MQTT_WS_PORT=9001
MQTT_SSL_ENABLED=false
MQTT_AUTH_ENABLED=false
MQTT_USER=
MQTT_PASSWORD=

# Datenbank-Konfiguration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=swissairdry
DB_USER=postgres
DB_PASSWORD=postgres

# ExApp-Konfiguration
EXAPP_URL=http://localhost:3000
EXAPP_API_KEY=
EXAPP_DAEMON_URL=http://localhost:8701

# Logging
LOG_LEVEL=INFO
LOG_DIR=/var/log/swissairdry
```

### API-Anpassung

Die API kann über folgende Konfigurationsdateien angepasst werden:

- `swissairdry/api/app/config.py`: Allgemeine API-Konfiguration
- `swissairdry/api/app/schemas.py`: Datenmodelle
- `swissairdry/api/app/routes/`: API-Routen

### ExApp-Anpassung

Die ExApp kann angepasst werden durch:

- `nextcloud/exapp/config.js`: ExApp-Konfiguration
- `nextcloud/exapp/components/`: UI-Komponenten

## Wartung und Betrieb

### Log-Dateien

Wichtige Log-Dateien befinden sich:

- **Docker**: `docker logs [container-name]`
- **Direkte Installation**: 
  - API: `/var/log/swissairdry/api.log`
  - MQTT: `/var/log/mosquitto/mosquitto.log`
  - ExApp-Daemon: `/var/log/swissairdry/exapp_daemon.log`

### Datensicherung

#### Docker-Installation

```bash
# Datenbank sichern
docker exec swissairdry-db pg_dump -U postgres swissairdry > backup.sql

# Volumes sichern
docker run --rm -v swissairdry_data:/data -v $(pwd):/backup alpine tar czf /backup/data.tar.gz /data
```

#### Direkte Installation

```bash
# Datenbank sichern
pg_dump -U postgres swissairdry > backup.sql

# Konfiguration sichern
tar czf config_backup.tar.gz /etc/swissairdry /var/lib/swissairdry
```

### Updates

#### Docker-Installation

```bash
git pull
docker-compose -f docker-compose-all-in-one.yml pull
docker-compose -f docker-compose-all-in-one.yml up -d
```

#### Direkte Installation

```bash
git pull
./update.sh
```

## Problembehandlung

### Häufige Fehler

#### API startet nicht

Prüfen Sie:
- Log-Dateien
- Port-Konflikte
- Python-Abhängigkeiten

#### MQTT-Verbindungsprobleme

- Prüfen Sie die MQTT-Broker-Logs
- Testen Sie die Verbindung mit einem MQTT-Client:
  ```bash
  mosquitto_sub -h localhost -p 1883 -t '#' -v
  ```

#### ESP-Geräte verbinden nicht

- Prüfen Sie die WLAN-Konfiguration
- Stellen Sie sicher, dass die MQTT-Broker-Adresse korrekt ist
- Prüfen Sie die serielle Konsole für Debug-Informationen

#### ExApp-Synchronisationsprobleme

- Prüfen Sie die ExApp-Daemon-Logs
- Stellen Sie sicher, dass die API erreichbar ist
- Prüfen Sie die Authentifizierung

## Support und Community

- GitHub-Repository: github.com/swissairdry/swissairdry
- Support-E-Mail: support@swissairdry.com
- Community-Forum: forum.swissairdry.com

---

© 2025 SwissAirDry GmbH - Alle Rechte vorbehalten