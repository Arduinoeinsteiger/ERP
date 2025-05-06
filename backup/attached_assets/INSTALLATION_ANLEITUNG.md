# SwissAirDry Installations-Anleitung

> **HINWEIS: Diese Anleitung ist veraltet. Bitte verwenden Sie die neue [GENERALANLEITUNG.md](./GENERALANLEITUNG.md) für aktuelle Installations- und Konfigurationsanweisungen.**

Diese Anleitung beschreibt die Installation des SwissAirDry-Systems mit allen Komponenten:

- Nextcloud
- SwissAirDry API
- MQTT-Broker
- PostgreSQL-Datenbank
- Nginx als Reverse Proxy

## Voraussetzungen

- Linux-Server (Ubuntu 20.04 oder höher empfohlen)
- Root-Zugriff oder sudo-Berechtigung
- Mindestens 4GB RAM, 2 CPU-Kerne
- Mindestens 20GB freier Speicherplatz
- Internetverbindung für den Download der Docker-Images

## 1. Vorbereitungen

Stellen Sie sicher, dass Ihr Server auf dem neuesten Stand ist:

```bash
sudo apt update
sudo apt upgrade -y
```

## 2. Installation ausführen

### Automatische Installation (empfohlen)

1. Laden Sie das Installationsskript herunter:

```bash
wget https://github.com/swissairdry/swissairdry/raw/main/install.sh
```

2. Machen Sie das Skript ausführbar:

```bash
chmod +x install.sh
```

3. Führen Sie das Skript als root aus:

```bash
sudo ./install.sh
```

4. Folgen Sie den Anweisungen auf dem Bildschirm. Das Skript:
   - Installiert alle erforderlichen Abhängigkeiten
   - Richtet SSL-Zertifikate ein
   - Konfiguriert Nextcloud, SwissAirDry API, MQTT und die Datenbank
   - Erstellt sichere Passwörter
   - Startet alle Dienste

### Manuelle Installation

Wenn Sie eine manuelle Installation bevorzugen, folgen Sie diesen Schritten:

1. Installieren Sie Docker und Docker Compose:

```bash
sudo apt update
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt update
sudo apt install -y docker-ce docker-compose
```

2. Erstellen Sie ein Verzeichnis für SwissAirDry:

```bash
sudo mkdir -p /opt/swissairdry
cd /opt/swissairdry
```

3. Laden Sie die Konfigurationsdateien herunter:

```bash
sudo wget https://github.com/swissairdry/swissairdry/raw/main/docker-compose.yml
sudo wget https://github.com/swissairdry/swissairdry/raw/main/.env.example -O .env
```

4. Bearbeiten Sie die Umgebungsvariablen:

```bash
sudo nano .env
```

5. Erstellen Sie die erforderlichen Verzeichnisse:

```bash
sudo mkdir -p mqtt/config mqtt/data mqtt/log
sudo mkdir -p nginx/conf.d nginx/ssl
sudo mkdir -p postgres/data
sudo mkdir -p api
```

6. Erstellen Sie die MQTT-Konfiguration:

```bash
sudo nano mqtt/config/mosquitto.conf
```

7. Konfigurieren Sie SSL-Zertifikate:

```bash
sudo mkdir -p nginx/ssl
# Kopieren Sie Ihre SSL-Zertifikate nach nginx/ssl/fullchain.pem und nginx/ssl/privkey.pem
```

8. Starten Sie die Dienste:

```bash
sudo docker-compose up -d
```

## 3. Nach der Installation

1. Öffnen Sie Ihre Domain im Browser, um auf Nextcloud zuzugreifen:
   - https://ihre-domain.de

2. Legen Sie ein Administrator-Konto an (falls noch nicht durch das Skript erledigt).

3. Installieren Sie die erforderlichen Nextcloud-Apps:
   - External App (für die Integration der SwissAirDry-Anwendung)
   - External Storage Support (für die Integration von Speichersystemen)
   - Kalender, Aufgaben, etc. nach Bedarf

4. Zugriff auf die SwissAirDry API:
   - https://api.ihre-domain.de

## 4. Fehlerbehebung

Falls Probleme auftreten, prüfen Sie die Log-Dateien der Docker-Container:

```bash
cd /opt/swissairdry
sudo docker-compose logs -f
```

Weitere Informationen zur Fehlerbehebung finden Sie in der FEHLERBEHEBUNG.md Datei.

## 5. Sicherheitshinweise

- Ändern Sie die generierten Passwörter regelmäßig
- Halten Sie alle Container mit `docker-compose pull && docker-compose up -d` aktuell
- Sichern Sie regelmäßig die Daten mit `docker-compose exec -T db mysqldump -u root -p<PASSWORT> nextcloud > nextcloud_backup.sql`

## 6. Updates

Um das System zu aktualisieren:

```bash
cd /opt/swissairdry
git pull  # Bei Installation über Git
sudo docker-compose pull
sudo docker-compose up -d
```

## 7. Support

Bei Fragen und Problemen wenden Sie sich an:
- E-Mail: support@swissairdry.com
- Webseite: https://swissairdry.com/support
- GitHub Issues: https://github.com/swissairdry/swissairdry/issues