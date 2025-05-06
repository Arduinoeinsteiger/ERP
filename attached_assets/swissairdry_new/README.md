# SwissAirDry

<div align="center">
  <img src="images/logo.svg" alt="SwissAirDry Logo" width="400">
</div>

Ein umfassendes System zur Verwaltung von Trocknungsgeräten für Bausanierungsunternehmen. Das System bietet Echtzeit-Überwachung von Trocknungsgeräten, Auftragsmanagement, Energiekosten-Berechnung und IoT-Integration mit ESP32C6/ESP8266-Geräten.

## Funktionen

- Echtzeit-Überwachung von Trocknungsgeräten
- Verwaltung von Aufträgen und Kunden
- Visualisierung von Energie- und Feuchtigkeitsdaten
- Integration mit Bexio für Rechnungen
- QR-Code-basierte Gerätekonfiguration
- OTA-Updates für ESP32C6 und ESP8266 Geräte
- IoT-Kommunikation über MQTT
- Nextcloud-Integration als ExApp (Externe Anwendung)
- Responsive Web- und Mobile-Oberfläche

## System-Architektur

<div align="center">
  <img src="images/architecture.svg" alt="SwissAirDry Architektur" width="700">
</div>

Die SwissAirDry-Architektur besteht aus mehreren Komponenten:

1. **API-Server**: Minimal HTTP Server auf Port 5000
2. **MQTT-Broker**: Mosquitto auf Ports 1883 (MQTT) und 9001 (WebSocket)
3. **IoT-Geräte**: ESP32C6 und ESP8266 (Wemos D1 Mini) mit Sensoren
4. **Mobile App**: Android-Anwendung für die Konfiguration und Überwachung

## Projektstruktur

Das SwissAirDry-Repository ist wie folgt organisiert:

```
swissairdry_new/
├── api/                 # API-Server und Endpunkte
│   ├── minimal_http_server.py  # Minimal-Server ohne externe Abhängigkeiten
│   ├── mqtt_client.py   # MQTT-Client für IoT-Kommunikation
│   └── tests/           # Tests für die API-Komponenten
├── docs/                # Projektdokumentation
│   ├── qrcode_generator.md   # Dokumentation für QR-Code-Generator
│   └── testing.md       # Testdokumentation
├── images/              # Bilder für Dokumentation
│   ├── logo.svg         # Projekt-Logo
│   ├── architecture.svg # Architektur-Diagramm
│   └── qrcode_generator.svg # UI des QR-Code-Generators
└── mqtt/                # MQTT-Broker-Konfiguration
    └── mosquitto.conf   # Konfiguration für Mosquitto MQTT-Broker
```

## Komponenten

### API-Server

Der API-Server stellt die Hauptschnittstelle für Geräte und Benutzeranwendungen bereit.

- **Minimal HTTP Server**: Ein einfacher Server ohne externe Abhängigkeiten (`api/minimal_http_server.py`)
  - Geräte-API: Verwaltung und Abfrage von Geräten
  - QR-Code-Generator: Erzeugung von Konfigurationscodes für einfache Gerätekonfiguration
- **MQTT-Client**: Client für die Kommunikation mit IoT-Geräten (`api/mqtt_client.py`)

### MQTT-Broker

Der MQTT-Broker ermöglicht die Kommunikation mit IoT-Geräten:

- Läuft auf Port 1883 (MQTT) und 9001 (MQTT über WebSocket)
- Konfiguration in `mqtt/mosquitto.conf`
- Die MQTT-Kommunikation erfolgt ausschließlich über Python (paho-mqtt)

### QR-Code-Generator

<div align="center">
  <img src="images/qrcode_generator.svg" alt="QR-Code-Generator" width="500">
</div>

Der QR-Code-Generator ermöglicht die einfache Konfiguration von Geräten durch das Scannen von QR-Codes. Funktionen:

- Generierung von benutzerdefinierten QR-Codes
- WLAN-Konfigurationen im standardisierten WIFI-Format
- Gerätekonfiguration mit MQTT-Verbindungsdaten

Weitere Informationen finden Sie in der [QR-Code-Generator Dokumentation](docs/qrcode_generator.md).

## Entwicklung und Installation

Für Entwickler:

1. Installieren Sie die erforderlichen Abhängigkeiten:
   ```
   pip install qrcode pillow paho-mqtt
   ```

2. Starten Sie den Minimal HTTP Server:
   ```
   cd swissairdry_new/api
   python minimal_http_server.py
   ```

3. Starten Sie den MQTT Broker:
   ```
   mkdir -p /tmp/mosquitto/data /tmp/mosquitto/log
   chmod -R 777 /tmp/mosquitto
   mosquitto -c swissairdry_new/mqtt/mosquitto.conf
   ```

4. Zugriff auf den QR-Code-Generator:
   ```
   http://localhost:5003/qrcode
   ```

Alternativ können Sie das automatisierte Installationsskript verwenden:
```
chmod +x install.sh
./install.sh
```

## Testen

Führen Sie die Tests mit dem folgenden Befehl aus:

```
cd swissairdry_new
python -m unittest discover
```

Weitere Informationen finden Sie in der [Testdokumentation](docs/testing.md).

## Kontakt

Bei Fragen oder Problemen wenden Sie sich an:

- E-Mail: info@vgnc.org
- Website: https://vgnc.org

## Lizenz

Copyright © 2025 SwissAirDry - Alle Rechte vorbehalten