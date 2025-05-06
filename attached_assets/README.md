# SwissAirDry Nextcloud ExApp

Diese Komponente stellt die Integration von SwissAirDry in Nextcloud als moderne ExApp (External App) bereit.

## Komponenten

Die SwissAirDry Nextcloud Integration besteht aus zwei Hauptkomponenten:

1. **ExApp Web-Interface**: Eine PHP-basierte Web-Oberfläche, die in Nextcloud eingebettet wird.
2. **ExApp Daemon**: Ein Python-basierter Dienst, der als Brücke zwischen Nextcloud und der SwissAirDry API fungiert.

## Architektur

Die ExApp ist so konzipiert, dass sie sicher in Nextcloud integriert wird und gleichzeitig mit der SwissAirDry API kommunizieren kann.

```
+------------+      +------------+      +--------------+      +--------------+
| Nextcloud  | <--> | ExApp Web  | <--> | ExApp Daemon | <--> | SwissAirDry  |
| (Host)     |      | Interface  |      | (Bridge)     |      | API & MQTT   |
+------------+      +------------+      +--------------+      +--------------+
```

## Konfiguration

Die Hauptkonfigurationsdatei ist `appinfo/info.xml`, die definiert, wie die App in Nextcloud eingebunden wird.

Die External App wird durch diesen XML-Block konfiguriert:

```xml
<external-app>
    <load-parallel/>
    <iframe id="frame" src="https://swissairdry.ch/api/nextcloud?origin={{origin}}&amp;url={{url}}"/>
    <iframe-selector>@import @nextcloud/dialogs;</iframe-selector>
</external-app>
```

Diese Konfiguration sorgt dafür, dass:

- Die App parallel geladen wird (`load-parallel`) und nicht den Hauptthread von Nextcloud blockiert
- Die App in einem iframe läuft, der auf den SwissAirDry API-Server verweist
- Der iframe mit der korrekten Herkunft und URL konfiguriert ist

## Docker-Konfiguration

### Web-Interface Container (exapp)

Dieser Container stellt die Web-Oberfläche der ExApp bereit, die in Nextcloud eingebettet wird.

```yaml
exapp:
  build:
    context: ./nextcloud
    dockerfile: Dockerfile.exapp
  container_name: swissairdry-exapp
  restart: unless-stopped
  ports:
    - "${EXAPP_PORT:-8080}:8080"
  environment:
    - API_URL=http://api:${API_PORT:-5000}
    - SIMPLE_API_URL=http://simple-api:${SIMPLE_API_PORT:-5001}
    - NEXTCLOUD_URL=${NEXTCLOUD_URL:-https://nextcloud.example.com}
  volumes:
    - ./nextcloud:/app
```

### ExApp Daemon Container (exapp-daemon)

Dieser Container dient als Brücke zwischen Nextcloud und der SwissAirDry API und verarbeitet Anfragen zwischen den beiden Systemen.

```yaml
exapp-daemon:
  build:
    context: ./nextcloud
    dockerfile: Dockerfile.daemon
  container_name: swissairdry-exapp-daemon
  restart: unless-stopped
  ports:
    - "${EXAPP_DAEMON_PORT:-8081}:8081"
  environment:
    - APP_ID=swissairdry
    - APP_VERSION=${APP_VERSION:-1.0.0}
    - APP_HOST=0.0.0.0
    - APP_PORT=8081
    - APP_SECRET=${EXAPP_SECRET_KEY:-changeme_in_production}
    - NEXTCLOUD_URL=${NEXTCLOUD_URL:-https://nextcloud.example.com}
    - API_URL=http://api:${API_PORT:-5000}
    - SIMPLE_API_URL=http://simple-api:${SIMPLE_API_PORT:-5001}
    - MQTT_BROKER=mqtt
    - MQTT_PORT=${MQTT_PORT:-1883}
    - MQTT_WS_PORT=${MQTT_WS_PORT:-9001}
    - MQTT_USERNAME=${MQTT_USERNAME:-}
    - MQTT_PASSWORD=${MQTT_PASSWORD:-}
  volumes:
    - ./nextcloud:/app
  depends_on:
    - mqtt
    - api
    - simple-api
```

## Installation in Nextcloud

Um die ExApp in Nextcloud zu registrieren, führen Sie folgenden Befehl auf dem Nextcloud-Server aus:

```bash
sudo -u www-data php occ app_api:app:register swissairdry \
  --json-info /path/to/nextcloud/apps/swissairdry/appinfo/info.xml \
  --docker-image ghcr.io/arduinoeinsteiger/swissairdry:latest
```

## Fehlerbehebung

### Problem: Nextcloud stürzt ab

Wenn Ihre Nextcloud-Instanz beim Zugriff auf die SwissAirDry-App abstürzt:

1. Prüfen Sie, ob die `info.xml` korrekt konfiguriert ist mit dem `<external-app>`-Tag
2. Überprüfen Sie, ob der API-Server läuft und von Nextcloud aus erreichbar ist
3. Prüfen Sie die CORS-Einstellungen des API-Servers
4. Schauen Sie in die Nextcloud-Logs für weitere Hinweise auf Probleme

### Problem: Iframe bleibt leer oder zeigt einen Fehler

Wenn der iframe leer bleibt oder einen Fehler anzeigt:

1. Überprüfen Sie die URL des API-Servers in der `info.xml`
2. Stellen Sie sicher, dass die API korrekt konfiguriert ist, um Anfragen vom Nextcloud-Origin zu akzeptieren
3. Prüfen Sie die Browser-Konsole auf CORS-Fehler oder andere JavaScript-Fehler

### Problem: ExApp-Daemon ist nicht erreichbar

Wenn der ExApp-Daemon nicht erreichbar ist:

1. Überprüfen Sie, ob der Container läuft: `docker ps | grep exapp-daemon`
2. Prüfen Sie die Logs des Containers: `docker logs swissairdry-exapp-daemon`
3. Stellen Sie sicher, dass die Ports korrekt konfiguriert sind

## Entwicklung

Für die lokale Entwicklung können Sie die ExApp in einer lokalen Nextcloud-Instanz installieren und den ExApp-Daemon direkt starten:

```bash
cd nextcloud
python3 daemon.py
```

Die Konfiguration erfolgt über Umgebungsvariablen, die in der `.env`-Datei definiert sind.