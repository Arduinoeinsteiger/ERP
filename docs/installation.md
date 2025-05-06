# SwissAirDry-Plattform Installationsanleitung

Diese Anleitung erklärt, wie Sie die SwissAirDry-Plattform mit BLE-Unterstützung installieren und ausführen können.

## Voraussetzungen

- Python 3.10 oder höher
- pip (Python-Paketmanager)
- Git
- PostgreSQL-Datenbank
- Bluetooth-fähiges Gerät (für BLE-Funktionalität)

## Installation

### 1. Repository klonen

Klonen Sie das Repository von GitHub:

```bash
git clone https://github.com/Arduinoeinsteiger/ERP.git
cd ERP
```

### 2. Python-Abhängigkeiten installieren

Erstellen Sie eine virtuelle Python-Umgebung und installieren Sie die erforderlichen Pakete:

```bash
python -m venv venv
source venv/bin/activate  # Unter Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Umgebungsvariablen konfigurieren

Erstellen Sie eine `.env`-Datei im Hauptverzeichnis mit folgenden Einstellungen:

```
DATABASE_URL=postgresql://username:password@localhost:5432/swissairdry
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=
FLASK_SECRET_KEY=generate-a-secure-random-key
```

Ersetzen Sie `username`, `password` und die anderen Werte durch Ihre tatsächlichen Daten.

### 4. Datenbank einrichten

Erstellen Sie die PostgreSQL-Datenbank und führen Sie die Migration aus:

```bash
# Datenbank erstellen
psql -U postgres -c "CREATE DATABASE swissairdry;"
psql -U postgres -c "CREATE USER swissairdry WITH PASSWORD 'password';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE swissairdry TO swissairdry;"

# Starten Sie die Anwendung - die Tabellen werden automatisch erstellt
python main.py
```

### 5. MQTT-Broker einrichten (optional)

Für die volle Funktionalität wird empfohlen, einen MQTT-Broker wie Mosquitto zu installieren:

#### Unter Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install mosquitto mosquitto-clients
sudo systemctl enable mosquitto
sudo systemctl start mosquitto
```

#### Unter Windows:
Laden Sie den Mosquitto-Installer von der [offiziellen Website](https://mosquitto.org/download/) herunter und folgen Sie der Installationsanleitung.

### 6. Anwendung starten

Starten Sie die Flask-Anwendung:

```bash
python main.py
```

Die Anwendung ist nun unter http://localhost:5000 erreichbar.

## BLE-Funktionalität

### Voraussetzungen für BLE

1. Bluetooth-fähiges Gerät (eingebautes Bluetooth oder USB-Dongle)
2. Die `bleak`-Bibliothek (sollte bereits mit `requirements.txt` installiert sein)
3. Betriebssystemspezifische Anforderungen:
   - Linux: BlueZ Stack (sollte auf den meisten Distributionen vorinstalliert sein)
   - Windows: Windows 10 oder höher wird empfohlen (Windows 8.1 mit Einschränkungen)
   - macOS: Keine zusätzliche Software erforderlich

### BLE-Geräte testen

Um die BLE-API zu testen, können Sie das bereitgestellte Testskript verwenden:

```bash
python tests/test_ble_api.py
```

## Firmware für ESP32/STM32-Geräte

Die Firmware für ESP32/STM32-Geräte finden Sie im `firmware`-Verzeichnis. 

### ESP32 Firmware flashen

1. PlatformIO installieren (empfohlen) oder die Arduino IDE
2. Öffnen Sie das Projekt im `firmware/esp32`-Verzeichnis
3. Konfigurieren Sie die WLAN- und MQTT-Einstellungen in der `config.h`-Datei
4. Kompilieren und flashen Sie die Firmware auf Ihr ESP32-Gerät

### STM32 Firmware flashen

1. PlatformIO installieren (empfohlen) oder die STM32CubeIDE
2. Öffnen Sie das Projekt im `firmware/stm32`-Verzeichnis
3. Konfigurieren Sie die WLAN- und MQTT-Einstellungen in der `config.h`-Datei
4. Kompilieren und flashen Sie die Firmware auf Ihr STM32-Gerät

## Docker-Installation (Alternative)

Alternativ können Sie die Anwendung mit Docker starten:

```bash
# Erstellen und Starten der Container
docker-compose up -d
```

Die Anwendung ist dann unter http://localhost:5000 erreichbar.

## Fehlerbehebung

### MQTT-Verbindungsprobleme
- Überprüfen Sie, ob der MQTT-Broker läuft: `mosquitto_sub -t '#' -v`
- Prüfen Sie die MQTT-Broker-IP und Ports in der `.env`-Datei

### BLE-Probleme
- Stellen Sie sicher, dass Bluetooth aktiviert ist
- Prüfen Sie mit `bluetoothctl` (Linux) oder den Bluetooth-Einstellungen (Windows/macOS), ob das Bluetooth-Gerät erkannt wird
- Unter Linux kann es nötig sein, den BLE-Dienst mit Root-Rechten zu starten

### Datenbank-Probleme
- Überprüfen Sie die Datenbankverbindungszeichenfolge in der `.env`-Datei
- Stellen Sie sicher, dass der PostgreSQL-Dienst läuft