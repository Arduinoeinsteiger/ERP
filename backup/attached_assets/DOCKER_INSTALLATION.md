# SwissAirDry Docker Installation

> **HINWEIS: Diese Anleitung ist veraltet. Bitte verwenden Sie die neue [GENERALANLEITUNG.md](./GENERALANLEITUNG.md) für aktuelle Installations- und Konfigurationsanweisungen.**

Diese Anleitung beschreibt die Installation und Konfiguration des SwissAirDry-Systems mit Docker.

## Systemvoraussetzungen

- Docker und Docker Compose
- Linux-, macOS- oder Windows-Betriebssystem
- Internetverbindung für den Download der Docker-Images

## Installation

### 1. Repository klonen

Klonen Sie das Repository oder entpacken Sie das Archiv an den gewünschten Ort:

```bash
git clone https://github.com/swissairdry/swissairdry.git
cd swissairdry
```

### 2. Konfiguration anpassen

Kopieren Sie die Beispielkonfiguration und passen Sie sie an Ihre Bedürfnisse an:

```bash
cp .env.example .env
nano .env
```

Die `.env`-Datei enthält alle Konfigurationsparameter für alle Docker-Container. Wichtige Parameter sind:

- `API_PORT`: Port für die Haupt-API
- `SIMPLE_API_PORT`: Port für die Simple API
- `MQTT_PORT`: Port für den MQTT-Broker
- `MQTT_WS_PORT`: WebSocket-Port für den MQTT-Broker
- `DB_PASSWORD`: Passwort für die PostgreSQL-Datenbank
- `MQTT_AUTH_ENABLED`: MQTT-Authentifizierung aktivieren/deaktivieren
- `MQTT_USERNAME` und `MQTT_PASSWORD`: Zugangsdaten für MQTT (wenn Authentifizierung aktiviert)

### 3. Stack starten

Starten Sie den gesamten Docker-Stack mit dem Startskript:

```bash
./start_docker.sh
```

Das Skript prüft die Voraussetzungen, erstellt fehlende Verzeichnisse und startet alle Container. Am Ende werden die URLs und Ports angezeigt.

### 4. Stack stoppen

Um den Stack zu stoppen, verwenden Sie das Stoppskript:

```bash
./stop_docker.sh
```

Das Skript wird fragen, ob Sie auch die Datenvolumes und ungenutzte Docker-Images löschen möchten.

## Komponenten und Ports

Der SwissAirDry-Stack besteht aus folgenden Komponenten:

| Komponente   | Standard-Port | Beschreibung                                     |
|--------------|---------------|-------------------------------------------------|
| API          | 5000          | Haupt-API basierend auf FastAPI                  |
| Simple API   | 5001          | Vereinfachte API basierend auf Flask             |
| MQTT-Broker  | 1883          | MQTT-Broker für IoT-Kommunikation                |
| MQTT-WebSockets | 9001       | WebSocket-Schnittstelle für MQTT                 |
| ExApp        | 8080          | Nextcloud-Integration (Web-Interface)            |
| ExApp-Daemon | 8081          | Brücke zwischen Nextcloud und SwissAirDry API    |
| PostgreSQL   | 5432          | Datenbank                                        |

## Sicherheit

In der Standardkonfiguration sind keine Sicherheitsmaßnahmen aktiviert. Für den Produktionseinsatz sollten Sie mindestens folgende Einstellungen anpassen:

1. Sichere Passwörter für die Datenbank setzen
2. MQTT-Authentifizierung aktivieren und sichere Zugangsdaten festlegen
3. SSL für MQTT aktivieren
4. API-Sicherheitseinstellungen konfigurieren
5. Geeignete Netzwerkkonfiguration vornehmen

## Struktur

Die Docker-Konfiguration verwendet folgende Verzeichnisstruktur:

```
swissairdry/
├── api/                   # API-Code und Konfiguration
│   ├── app/              # Haupt-API (FastAPI)
│   └── start_simple.py   # Simple API (Flask)
├── mosquitto/            # MQTT-Broker-Konfiguration
│   ├── config/           # MQTT-Konfigurationsdateien
│   ├── data/             # MQTT-Persistenz-Daten
│   └── log/              # MQTT-Logs
├── mqtt-config/          # MQTT-Konfigurationstool
├── nextcloud/            # Nextcloud ExApp
├── docker-compose.yml    # Docker Compose Konfiguration
├── .env                  # Umgebungsvariablen für Docker
├── start_docker.sh       # Startskript
└── stop_docker.sh        # Stoppskript
```

## Zentralisierte Konfiguration

Die Konfiguration erfolgt zentral über die `.env`-Datei. Änderungen an der Konfiguration werden automatisch an alle Container weitergegeben:

- API und Simple API lesen die Umgebungsvariablen direkt aus der `.env`-Datei
- Der MQTT-Broker wird über den `mqtt-config`-Container konfiguriert, der die `mosquitto.conf` basierend auf den Umgebungsvariablen generiert
- Die Datenbank verwendet die entsprechenden Umgebungsvariablen für die Konfiguration
- Die ExApp-Komponenten (Web-Interface und Daemon) werden über die Umgebungsvariablen konfiguriert

Diese zentrale Konfiguration stellt sicher, dass alle Komponenten konsistent konfiguriert sind und vermeidet Fehler durch inkonsistente Einstellungen.

## Fehlerbehebung

### Container startet nicht

Prüfen Sie die Logs des betroffenen Containers:

```bash
docker-compose logs <container-name>
```

Typische Container-Namen sind:
- `swissairdry-api`
- `swissairdry-simple-api`
- `swissairdry-mqtt`
- `swissairdry-db`
- `swissairdry-exapp`
- `swissairdry-exapp-daemon`
- `swissairdry-mqtt-config`

### Netzwerkprobleme

Prüfen Sie, ob die Ports korrekt freigegeben sind:

```bash
docker-compose ps
```

### Datenbank-Probleme

Prüfen Sie die Datenbankverbindung:

```bash
docker exec -it swissairdry-db psql -U postgres -d swissairdry
```

### MQTT-Probleme

Prüfen Sie die MQTT-Verbindung mit einem MQTT-Client:

```bash
docker exec -it swissairdry-mqtt mosquitto_sub -t '#' -v
```

### Vollständiger Neustart

Um alle Container, Volumes und Netzwerke neu zu erstellen:

```bash
./stop_docker.sh
# Wählen Sie "y" für das Löschen der Volumes
# Wählen Sie "y" für das Löschen der Images
./start_docker.sh
```

## Support

Bei Problemen oder Fragen wenden Sie sich bitte an das SwissAirDry-Team.