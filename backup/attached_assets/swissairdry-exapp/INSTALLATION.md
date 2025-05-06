# SwissAirDry ExApp - Installationsanleitung

Diese Anleitung beschreibt die Installation und Konfiguration der SwissAirDry ExApp für Nextcloud. Die ExApp integriert die SwissAirDry-Plattform nahtlos in Ihre Nextcloud-Umgebung und ermöglicht die Überwachung und Steuerung von Trocknungsgeräten direkt aus Nextcloud heraus.

## Voraussetzungen

- Nextcloud 26 oder neuer
- PHP 8.0 oder neuer
- Node.js 16.x oder neuer und npm 7.x oder neuer
- PostgreSQL 12 oder neuer
- Docker und Docker Compose (für vereinfachte Installation)
- Mosquitto MQTT-Broker

## Installation

### Option 1: Docker-basierte Installation (empfohlen)

Die einfachste Art, die SwissAirDry ExApp zu installieren, ist über Docker Compose:

1. Repository klonen:
   ```bash
   git clone https://github.com/swissairdry/swissairdry-exapp.git
   cd swissairdry-exapp
   ```

2. Umgebungsvariablen konfigurieren:
   ```bash
   cp .env.example .env
   # Bearbeiten Sie .env mit Ihren Einstellungen
   nano .env
   ```

3. Docker Compose starten:
   ```bash
   docker-compose up -d
   ```

4. ExApp in Nextcloud aktivieren:
   - Öffnen Sie Nextcloud als Administrator
   - Gehen Sie zu "Apps" → "App-Verwaltung"
   - Suchen Sie nach "SwissAirDry" und aktivieren Sie die App

### Option 2: Manuelle Installation

1. Repository klonen oder Release-Archiv herunterladen:
   ```bash
   git clone https://github.com/swissairdry/swissairdry-exapp.git
   # oder
   wget https://github.com/swissairdry/swissairdry-exapp/releases/latest/download/swissairdry-exapp.tar.gz
   tar -xzf swissairdry-exapp.tar.gz
   ```

2. App-Verzeichnis vorbereiten:
   ```bash
   mkdir -p /var/www/html/custom_apps/swissairdry
   cp -r swissairdry-exapp/* /var/www/html/custom_apps/swissairdry/
   chown -R www-data:www-data /var/www/html/custom_apps/swissairdry
   ```

3. Frontend-Assets bauen:
   ```bash
   cd /var/www/html/custom_apps/swissairdry
   npm install
   npm run build
   ```

4. ExApp-Daemon einrichten:
   ```bash
   cd daemon
   pip install -r requirements.txt
   # Systemd-Service einrichten (optional)
   cp swissairdry-daemon.service /etc/systemd/system/
   systemctl enable swissairdry-daemon
   systemctl start swissairdry-daemon
   ```

5. ExApp in Nextcloud aktivieren:
   - Öffnen Sie Nextcloud als Administrator
   - Gehen Sie zu "Apps" → "App-Verwaltung"
   - Wählen Sie "Nicht aktivierte Apps" und aktivieren Sie "SwissAirDry"

## Port-Konfiguration

Die folgenden Ports werden für die verschiedenen Komponenten verwendet:

| Port | Dienst                 | Beschreibung                            |
|------|------------------------|------------------------------------------|
| 8080 | Nextcloud              | Nextcloud-Weboberfläche                 |
| 3000 | ExApp Frontend         | SwissAirDry ExApp Frontend (Development) |
| 8701 | ExApp Daemon           | Daemon für Kommunikation mit API         |
| 5000 | SwissAirDry API        | Hauptschnittstelle für Clients/Geräte    |
| 5001 | SwissAirDry Simple API | Vereinfachte API für ESP-Geräte          |
| 1883 | MQTT Broker            | MQTT-Broker für Gerätekommunikation      |
| 9001 | MQTT WebSocket         | WebSocket-Zugriff auf MQTT               |
| 5432 | PostgreSQL             | Datenbankserver                          |

Stellen Sie sicher, dass diese Ports in Ihrer Firewall geöffnet sind, sofern der externe Zugriff benötigt wird.

## Konfiguration

### Umgebungsvariablen

Die wichtigsten Konfigurationsparameter können über Umgebungsvariablen gesetzt werden:

- `SWISSAIRDRY_API_URL`: URL zur SwissAirDry API (Standard: http://localhost:5000)
- `MQTT_BROKER`: Hostname/IP des MQTT-Brokers (Standard: localhost)
- `MQTT_PORT`: Port des MQTT-Brokers (Standard: 1883)
- `MQTT_USERNAME`: Benutzername für MQTT (optional)
- `MQTT_PASSWORD`: Passwort für MQTT (optional)
- `NEXTCLOUD_URL`: URL zur Nextcloud-Instanz (Standard: http://localhost:8080)
- `DATABASE_URL`: PostgreSQL-Verbindungsstring (Standard: postgresql://swissairdry:swissairdry@postgres:5432/swissairdry)

### ExApp-Einstellungen

Nach der Installation können weitere Einstellungen in der Nextcloud-Benutzeroberfläche vorgenommen werden:

1. Gehen Sie zu "Einstellungen" → "Administration" → "SwissAirDry"
2. Konfigurieren Sie die gewünschten Parameter:
   - API-Verbindungseinstellungen
   - Deck-Integration aktivieren/deaktivieren
   - Aktualisierungsintervall für Gerätedaten
   - Benachrichtigungseinstellungen für Alarme

## Docker-Umgebungen

### Production

Für den Produktionseinsatz mit Docker:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Development

Für die Entwicklung mit Hot-Reloading:

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

## Fehlerbehebung

### MQTT-Verbindungsprobleme

Bei MQTT-Verbindungsproblemen:

1. Überprüfen Sie, ob der MQTT-Broker läuft:
   ```bash
   docker-compose ps mqtt-broker
   # oder
   systemctl status mosquitto
   ```

2. Testen Sie die MQTT-Verbindung:
   ```bash
   mosquitto_sub -h localhost -p 1883 -t 'swissairdry/#' -v
   ```

3. Überprüfen Sie Authentifizierung und ACLs:
   ```bash
   # Beispiel-Befehl mit Authentifizierung
   mosquitto_sub -h localhost -p 1883 -t 'swissairdry/#' -v -u USERNAME -P PASSWORD
   ```

### Datenbank-Verbindungsprobleme

Bei Datenbank-Verbindungsproblemen:

1. Überprüfen Sie, ob PostgreSQL läuft:
   ```bash
   docker-compose ps postgres
   # oder
   systemctl status postgresql
   ```

2. Testen Sie die Datenbankverbindung:
   ```bash
   psql "postgresql://swissairdry:swissairdry@localhost:5432/swissairdry" -c "SELECT 1"
   ```

### Daemon-Probleme

Bei Problemen mit dem ExApp-Daemon:

1. Überprüfen Sie die Daemon-Logs:
   ```bash
   docker-compose logs exapp-daemon
   # oder
   journalctl -u swissairdry-daemon
   ```

2. Starten Sie den Daemon neu:
   ```bash
   docker-compose restart exapp-daemon
   # oder
   systemctl restart swissairdry-daemon
   ```

## Support

Bei weiteren Fragen oder Problemen:

- GitHub Issues: [https://github.com/swissairdry/swissairdry-exapp/issues](https://github.com/swissairdry/swissairdry-exapp/issues)
- E-Mail: [support@swissairdry.com](mailto:support@swissairdry.com)
- Dokumentation: [https://docs.swissairdry.com](https://docs.swissairdry.com)