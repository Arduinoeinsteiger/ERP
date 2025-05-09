# Docker-Installation für SwissAirDry

Diese Anleitung führt Sie durch den Prozess der Installation und Konfiguration der SwissAirDry-Plattform mit Docker.

## Voraussetzungen

- Docker und Docker Compose installiert
- Git (zum Klonen des Repositories)
- Bluetooth-Hardware für BLE-Funktionalität (optional)

## Installation

### 1. Repository klonen

```bash
git clone https://github.com/Arduinoeinsteiger/ERP.git
cd ERP
```

### 2. Docker Compose starten

```bash
docker-compose up -d
```

Dieser Befehl startet alle notwendigen Container:
- swissairdry (Hauptanwendung)
- swissairdry-bridge (MQTT-Bridge)
- postgres (Datenbank)
- mosquitto (MQTT-Broker)

### 3. Überprüfen der Installation

```bash
docker-compose ps
```

Alle Container sollten den Status "Up" anzeigen.

## Docker-Konfiguration

### Konfigurationsdateien

Die Docker-Konfiguration basiert auf folgenden Dateien:
- `docker-compose.yml` - Definiert alle Services
- `Dockerfile` - Konfiguriert den Hauptcontainer
- `Dockerfile.bridge` - Konfiguriert den MQTT-Bridge-Container

### Umgebungsvariablen

Die Docker-Konfiguration verwendet Umgebungsvariablen aus der `.env`-Datei. Erstellen Sie diese basierend auf der `.env.example`:

```bash
cp .env.example .env
```

Bearbeiten Sie die `.env`-Datei und passen Sie die folgenden Variablen an:

```
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/swissairdry
MQTT_BROKER=mosquitto
MQTT_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=
FLASK_SECRET_KEY=your-secure-secret-key
```

## Hardware-Zugriff für BLE

### Bluetooth-Hardware im Container

Um BLE-Funktionalität in Docker zu nutzen, muss die Bluetooth-Hardware des Host-Systems an den Container durchgereicht werden:

```yaml
# Ausschnitt aus docker-compose.yml
services:
  swissairdry:
    # ... andere Konfigurationen ...
    privileged: true  # Für Bluetooth-Zugriff (optional)
    devices:
      - "/dev/ttyACM0:/dev/ttyACM0"  # Beispiel für serielle Geräte
    volumes:
      - "/var/run/dbus:/var/run/dbus"  # Für Bluetooth-Stack
```

**Hinweis:** Nicht alle Docker-Umgebungen unterstützen Bluetooth-Hardware-Zugriff. In virtuellen Umgebungen ohne physischen Bluetooth-Adapter wird die BLE-Funktionalität eingeschränkt sein.

## Bekannte Probleme und Fehlerbehebung

### Problem: Docker Build schlägt fehl wegen fehlender requirements.txt

**Symptom:** 
```
failed to solve: failed to compute cache key: failed to calculate checksum of ref ... "/requirements.txt": not found
```

**Lösung:** 
Die Docker-Konfiguration verwendet die requirements.txt aus dem Verzeichnis backup/attached_assets/. Stellen Sie sicher, dass diese Datei existiert:

```bash
# Prüfen, ob die Datei existiert
ls -la backup/attached_assets/requirements.txt

# Falls nicht, erstellen Sie diese
mkdir -p backup/attached_assets
cp requirements.txt backup/attached_assets/
```

### Problem: BLE-Funktionalität arbeitet nicht in Docker

**Symptom:**
```
ERROR:ble_service:BLE-Hardware nicht verfügbar oder nicht unterstützt.
```

**Lösungen:**
1. Stellen Sie sicher, dass der Docker-Container im privilegierten Modus läuft und Zugriff auf den Bluetooth-Stack hat
2. Prüfen Sie, ob der Host Bluetooth unterstützt: `hciconfig -a`
3. In virtuellen Umgebungen ohne physischen Bluetooth-Adapter funktioniert BLE nicht

## Produktions-Deployment

Für ein Produktions-Deployment empfehlen wir weitere Sicherheitsmaßnahmen:

1. Verwenden Sie sichere Passwörter für alle Dienste
2. Aktivieren Sie HTTPS mit einem Reverse-Proxy (z.B. Nginx oder Traefik)
3. Beschränken Sie den Netzwerkzugriff auf die notwendigen Ports

Beispiel für einen Traefik-Reverse-Proxy in docker-compose.yml:

```yaml
services:
  traefik:
    image: traefik:v2.5
    command:
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.myresolver.acme.tlschallenge=true"
      - "--certificatesresolvers.myresolver.acme.email=your-email@example.com"
      - "--certificatesresolvers.myresolver.acme.storage=/letsencrypt/acme.json"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
      - "./letsencrypt:/letsencrypt"

  swissairdry:
    # ... andere Konfigurationen ...
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.swissairdry.rule=Host(`swissairdry.example.com`)"
      - "traefik.http.routers.swissairdry.entrypoints=websecure"
      - "traefik.http.routers.swissairdry.tls.certresolver=myresolver"
```

## Ressourcenmanagement

Docker Container können in ihrem Ressourcenverbrauch begrenzt werden:

```yaml
services:
  swissairdry:
    # ... andere Konfigurationen ...
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
```

Diese Konfiguration begrenzt den Container auf 0,5 CPU-Kerne und 512 MB RAM.