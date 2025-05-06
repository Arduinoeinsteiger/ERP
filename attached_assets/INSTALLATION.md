# SwissAirDry Nextcloud ExApp - Installationsanleitung

Diese Anleitung beschreibt die Installation der SwissAirDry-App als moderne ExApp (External App) in Nextcloud ab Version 25.

## Voraussetzungen

* Nextcloud Server (Version 25 oder höher)
* Docker auf dem Nextcloud-Server
* Administrator-Zugriff auf Nextcloud

## 1. Installation über den Nextcloud App Store (empfohlen)

Die einfachste Methode zur Installation ist über den Nextcloud App Store:

1. Melden Sie sich als Administrator bei Ihrer Nextcloud-Instanz an
2. Navigieren Sie zu "Apps" > "App-Verwaltung"
3. Wählen Sie die Kategorie "Integration" oder suchen Sie nach "SwissAirDry"
4. Klicken Sie auf "Installieren"

Die App wird automatisch heruntergeladen und eingerichtet, einschließlich des Docker-Containers.

## 2. Manuelle Installation

Wenn Sie die App manuell installieren möchten:

1. Laden Sie das App-Paket von GitHub herunter:
   ```bash
   git clone https://github.com/Arduinoeinsteiger/SwissAirDry.git
   ```

2. Kopieren Sie den `swissairdry`-Ordner in das Nextcloud `apps`-Verzeichnis:
   ```bash
   cp -r swissairdry /path/to/nextcloud/apps/
   ```

3. Aktivieren Sie die App über die Kommandozeile:
   ```bash
   cd /path/to/nextcloud
   sudo -u www-data php occ app:enable swissairdry
   ```

4. Da SwissAirDry eine ExApp ist, wird Nextcloud automatisch versuchen, den entsprechenden Docker-Container herunterzuladen und zu starten.

## 3. Docker-Container manuell konfigurieren

Wenn der automatische Docker-Setup nicht funktioniert, können Sie die Container manuell einrichten:

1. Ziehen Sie das Docker-Image:
   ```bash
   docker pull ghcr.io/arduinoeinsteiger/swissairdry:latest
   docker pull ghcr.io/arduinoeinsteiger/swissairdry-daemon:latest
   ```

2. Registrieren Sie die App als ExApp:
   ```bash
   sudo -u www-data php occ app_api:app:register swissairdry \
     --json-info /path/to/nextcloud/apps/swissairdry/appinfo/info.xml \
     --docker-image ghcr.io/arduinoeinsteiger/swissairdry:latest
   ```

3. Starten Sie den ExApp-Daemon:
   ```bash
   docker run -d --name swissairdry-exapp-daemon \
     -p 8081:8081 \
     -e NEXTCLOUD_URL=https://your-nextcloud-instance.com \
     -e API_URL=http://api:5000 \
     -e SIMPLE_API_URL=http://simple-api:5001 \
     -e MQTT_BROKER=mqtt \
     -e MQTT_PORT=1883 \
     -e MQTT_WS_PORT=9001 \
     -e APP_SECRET=your_secret_key \
     ghcr.io/arduinoeinsteiger/swissairdry-daemon:latest
   ```

## 4. Konfiguration

Nach der Installation:

1. Navigieren Sie zu "Einstellungen" > "SwissAirDry"
2. Konfigurieren Sie die folgenden Einstellungen:
   - API-Server-URL
   - MQTT-Broker-Einstellungen
   - Benutzer-Zugriffsrechte

## 5. ExApp-Daemon einrichten

Der ExApp-Daemon ist eine wichtige Komponente, die als Brücke zwischen Nextcloud und der SwissAirDry API fungiert. Er stellt folgende Funktionen bereit:

- Sichere Kommunikation zwischen Nextcloud und der SwissAirDry API
- Weitergabe von MQTT-Nachrichten an die Web-Oberfläche
- Authentifizierung von Benutzern über Nextcloud

### Docker Compose (empfohlen)

Für die Einrichtung mit Docker Compose verwenden Sie folgende Konfiguration:

```yaml
exapp-daemon:
  image: ghcr.io/arduinoeinsteiger/swissairdry-daemon:latest
  container_name: swissairdry-exapp-daemon
  restart: unless-stopped
  ports:
    - "8081:8081"
  environment:
    - APP_ID=swissairdry
    - APP_VERSION=1.0.0
    - APP_HOST=0.0.0.0
    - APP_PORT=8081
    - APP_SECRET=your_secret_key
    - NEXTCLOUD_URL=https://your-nextcloud-instance.com
    - API_URL=http://api:5000
    - SIMPLE_API_URL=http://simple-api:5001
    - MQTT_BROKER=mqtt
    - MQTT_PORT=1883
    - MQTT_WS_PORT=9001
    - MQTT_USERNAME=
    - MQTT_PASSWORD=
  volumes:
    - ./logs:/app/logs
  networks:
    - swissairdry-network
```

## Fehlerbehebung

### Nextcloud stürzt beim Zugriff auf die App ab

Dies deutet auf ein Problem mit der ExApp-Integration hin. Prüfen Sie:

1. Die Docker-Installation auf Ihrem Server:
   ```bash
   docker ps | grep swissairdry
   ```

2. Die ExApp-Registrierung in Nextcloud:
   ```bash
   sudo -u www-data php occ app_api:app:list
   ```

3. Kontrollieren Sie die Nextcloud-Logs:
   ```bash
   tail -f /path/to/nextcloud/data/nextcloud.log
   ```

### Container startet nicht

Wenn der Docker-Container nicht startet:

1. Prüfen Sie den Container-Status:
   ```bash
   docker logs swissairdry-exapp
   docker logs swissairdry-exapp-daemon
   ```

2. Stellen Sie sicher, dass die Ports nicht blockiert sind
3. Überprüfen Sie, ob Docker genügend Ressourcen hat

### ExApp-Daemon ist nicht erreichbar

Wenn der ExApp-Daemon nicht erreichbar ist:

1. Prüfen Sie, ob der Daemon läuft:
   ```bash
   docker ps | grep exapp-daemon
   ```

2. Überprüfen Sie die Daemon-Logs:
   ```bash
   docker logs swissairdry-exapp-daemon
   ```

3. Testen Sie die Verbindung:
   ```bash
   curl http://localhost:8081/status
   ```

## Support

Bei Problemen oder Fragen wenden Sie sich bitte an das SwissAirDry-Team.