# SwissAirDry Plattform

![SwissAirDry Logo](static/img/logo.png)

## Übersicht

Die SwissAirDry-Plattform ist eine umfassende IoT-Lösung zur Überwachung und Steuerung von Trocknungsgeräten mittels ESP8266/ESP32/STM32-Hardware. Die Plattform bietet eine vollständige Integration von MQTT- und BLE-Kommunikation (Bluetooth Low Energy) mit einer modernen Weboberfläche.

## Hauptfunktionen

- **IoT-Integration**: Kommunikation mit MQTT und BLE für umfassende Gerätekonnektivität
- **Weboberfläche**: Moderne, responsive Benutzeroberfläche für die Geräteverwaltung
- **Automatische Geräteerkennung**: BLE-fähige Geräte werden automatisch erkannt
- **Fernsteuerung**: Steuern Sie Ihre Geräte aus der Ferne über das Web
- **Aufgabenplanung**: Weisen Sie Trocknungsaufgaben automatisch zu und planen Sie sie
- **Datenverfolgung**: Verfolgen und analysieren Sie Umgebungsdaten (Temperatur, Luftfeuchtigkeit)
- **Nextcloud-Integration**: Erweiterte Funktionen durch Nextcloud-ExApp-Integration

## Technologien

- **Backend**: Python mit Flask
- **Datenbank**: PostgreSQL
- **Kommunikation**: MQTT, BLE (Bluetooth Low Energy)
- **Frontend**: HTML5, CSS3, JavaScript
- **IoT-Hardware**: ESP8266, ESP32, STM32
- **Containerisierung**: Docker-Unterstützung für einfache Bereitstellung

## Installation

### Plug & Play Installation (empfohlen)

Die einfachste und schnellste Möglichkeit, SwissAirDry zu installieren. Diese Option richtet alles vollautomatisch ein, ohne manuelle Eingriffe.

#### Linux/Mac:
```bash
# Als normaler Benutzer ausführen, sudo-Rechte werden bei Bedarf automatisch angefordert
wget -O - https://raw.githubusercontent.com/Arduinoeinsteiger/ERP/main/swissairdry-quickstart.sh | bash
```

#### Windows:
1. Laden Sie [swissairdry-quickstart.bat](https://raw.githubusercontent.com/Arduinoeinsteiger/ERP/main/swissairdry-quickstart.bat) herunter
2. Führen Sie die Datei als Administrator aus

[Detaillierte Anleitung zur Plug & Play Installation](docs/plug_and_play.md)

### Klassische Schnellinstallation

Die traditionelle Installationsmethode für erfahrene Benutzer.

#### Linux/Mac:
```bash
wget -O - https://raw.githubusercontent.com/Arduinoeinsteiger/ERP/main/install.sh | sudo bash
```

#### Windows:
1. Laden Sie [install.bat](https://raw.githubusercontent.com/Arduinoeinsteiger/ERP/main/install.bat) herunter
2. Führen Sie die Datei als Administrator aus

### Docker-Installation

Die SwissAirDry-Plattform kann einfach mit Docker bereitgestellt werden:

#### Automatische Installation (empfohlen):
```bash
# Repository klonen
git clone https://github.com/Arduinoeinsteiger/ERP.git
cd ERP

# Setup-Skript ausführen
# Linux/Mac:
./setup.sh

# Windows:
setup.bat
```

Das Setup-Skript führt folgende Aufgaben aus:
- Erstellt die `.env`-Datei mit sicheren Zufallsschlüsseln
- Stellt sicher, dass alle benötigten Dateien vorhanden sind
- Bietet an, die Docker-Container zu bauen und zu starten

#### Manuelle Installation:
```bash
# Repository klonen
git clone https://github.com/Arduinoeinsteiger/ERP.git
cd ERP

# .env-Datei erstellen
cp .env.example .env

# Docker-Container starten
docker-compose up -d
```

#### Docker-Konfiguration

Die Plattform besteht aus mehreren Docker-Containern:
- **swissairdry**: Der Hauptcontainer mit der Web-Anwendung
- **swissairdry-bridge**: Der MQTT-Bridge-Container für Geräteverbindungen
- **postgres**: PostgreSQL-Datenbankserver
- **mosquitto**: MQTT-Broker für die Gerätekommunikation

Hinweise:
- BLE-Funktionalität erfordert Zugriff auf Bluetooth-Hardware des Host-Systems
- In virtuellen Umgebungen ohne Bluetooth-Hardware arbeitet die Plattform im eingeschränkten Modus
- Die Docker-Konfiguration verwendet die requirements.txt-Datei aus dem Verzeichnis backup/attached_assets/

### Manuelle Installation

Eine detaillierte Installationsanleitung finden Sie in der [Installationsanleitung](docs/installation.md).

## Dokumentation

- [Benutzerhandbuch](docs/user_guide.md)
- [Plug & Play Installation](docs/plug_and_play.md)
- [Docker-Installation](docs/docker_installation.md)
- [API-Dokumentation](docs/api.md)
- [BLE-API-Dokumentation](docs/ble_api.md)
- [BLE-Integration](docs/ble_integration.md)
- [Firmware-Anleitung](docs/firmware.md)

## Hardware-Unterstützung

Die SwissAirDry-Plattform unterstützt verschiedene Hardware-Konfigurationen:

- ESP8266-Geräte mit MQTT-Verbindung
- ESP32-Geräte mit MQTT und BLE (Bluetooth Low Energy)
- STM32-Geräte mit erweiterten Funktionen

## Entwicklung

### Repository klonen

```bash
git clone https://github.com/Arduinoeinsteiger/ERP.git
cd ERP
```

### Entwicklungsumgebung einrichten

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Datenbank einrichten

```bash
# Konfigurieren Sie Ihre .env-Datei mit den Datenbankverbindungsdaten
# Starten Sie die Anwendung, die Tabellen werden automatisch erstellt
python main.py
```

## Beitragen

Wir freuen uns über Beiträge! Bitte lesen Sie [CONTRIBUTING.md](CONTRIBUTING.md) für Details zum Einreichen von Pull-Requests.

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert - siehe die [LICENSE](LICENSE) Datei für Details.

## Kontakt

- GitHub: [https://github.com/Arduinoeinsteiger/ERP](https://github.com/Arduinoeinsteiger/ERP)

---

Entwickelt von [Arduinoeinsteiger](https://github.com/Arduinoeinsteiger)