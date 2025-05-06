# SwissAirDry Fehlerbehebungsanleitung

Diese Anleitung hilft bei der Behebung häufiger Probleme mit dem SwissAirDry-System.

## Sicherheitspatches

### Bekannte Sicherheitslücken (April 2025)

**Problem:** Mehrere Sicherheitslücken wurden in Abhängigkeiten gefunden, darunter:
- **python-jose**: Algorithmus-Verwechslung mit OpenSSH ECDSA-Schlüsseln (Kritisch)
- **Pillow**: Möglichkeit zur beliebigen Codeausführung (Kritisch)
- **Gunicorn**: HTTP Request/Response Smuggling (Hoch)
- **Flask-CORS**: Sicherheitsprobleme mit CORS-Headern (Hoch)
- **python-multipart**: Denial of Service (DoS) durch fehlerhafte Multipart-Grenzen (Hoch)
- **Jinja2**: Sandbox-Breakout-Schwachstellen (Mittel)

**Lösung:**

1. **Automatisches Update mit security_update.sh**
   ```bash
   ./security_update.sh
   ```
   Dieses Skript aktualisiert alle requirements-Dateien auf sichere Versionen.

2. **Bilder neu bauen**
   ```bash
   ./build_and_publish_images.sh
   ```
   Dadurch werden die Docker-Images mit den aktualisierten Abhängigkeiten neu gebaut und veröffentlicht.

3. **Neustart mit aktualisierten Images**
   ```bash
   ./stop_docker.sh
   ./start_docker.sh
   ```
   Beim Start des Stacks können Sie wählen, ob Sie die aktuellen Registry-Images oder lokale Builds verwenden möchten.

## API-Probleme

### API startet nicht

**Symptom:** Die API startet nicht oder ist nicht erreichbar.

**Mögliche Ursachen und Lösungen:**

1. **Port ist bereits belegt**
   - Prüfen Sie, ob der konfigurierte Port (Standard: 5000) bereits verwendet wird:
     ```bash
     sudo lsof -i :5000
     ```
   - Beenden Sie den blockierenden Prozess oder ändern Sie den API-Port in der `.env`-Datei.

2. **Python-Abhängigkeiten fehlen**
   - Installieren Sie die erforderlichen Pakete manuell:
     ```bash
     pip install fastapi uvicorn sqlalchemy pydantic psycopg2-binary python-dotenv paho-mqtt
     ```

3. **Berechtigungsprobleme**
   - Stellen Sie sicher, dass Sie die erforderlichen Berechtigungen haben:
     ```bash
     chmod +x ~/swissairdry/start_api.sh
     chmod -R 755 ~/swissairdry/api
     ```

4. **Fehlerhafte Konfiguration**
   - Überprüfen Sie die Konfiguration in der `.env`-Datei.

### API-Fehler

**Symptom:** Die API gibt Fehler zurück oder funktioniert nicht wie erwartet.

**Lösungen:**

1. **Logdateien prüfen**
   - Sehen Sie sich die API-Logs an:
     ```bash
     tail -f ~/swissairdry/logs/api.log
     ```

2. **Neustart der API**
   - Stoppen und starten Sie die API:
     ```bash
     ~/swissairdry/stop_api.sh
     ~/swissairdry/start_api.sh
     ```

## MQTT-Probleme

### MQTT-Broker startet nicht

**Symptom:** Der MQTT-Broker startet nicht oder ist nicht erreichbar.

**Mögliche Ursachen und Lösungen:**

1. **Mosquitto ist nicht installiert**
   - Installieren Sie Mosquitto manuell:
     ```bash
     sudo apt-get update && sudo apt-get install -y mosquitto mosquitto-clients
     ```

2. **Port ist bereits belegt**
   - Prüfen Sie, ob der konfigurierte Port (Standard: 1883) bereits verwendet wird:
     ```bash
     sudo lsof -i :1883
     ```
   - Beenden Sie den blockierenden Prozess oder ändern Sie den MQTT-Port in der `.env`-Datei.

3. **Berechtigungsprobleme**
   - Stellen Sie sicher, dass Sie die erforderlichen Berechtigungen haben:
     ```bash
     chmod +x ~/swissairdry/start_mqtt.sh
     chmod -R 755 ~/swissairdry/mqtt
     ```

4. **Fehlerhafte Konfiguration**
   - Überprüfen Sie die Konfiguration in `~/swissairdry/mqtt/config/mosquitto.conf`.

### MQTT-Verbindungsprobleme

**Symptom:** Clients können keine Verbindung zum MQTT-Broker herstellen.

**Lösungen:**

1. **Logdateien prüfen**
   - Sehen Sie sich die MQTT-Logs an:
     ```bash
     tail -f ~/swissairdry/mqtt/log/mosquitto.log
     ```

2. **Prüfen Sie die Authentifizierung**
   - Wenn Sie die Authentifizierung aktiviert haben (`MQTT_AUTH_ENABLED=true`), stellen Sie sicher, dass Benutzername und Passwort korrekt sind.
   - Wenn Sie anonyme Verbindungen zulassen möchten, setzen Sie `MQTT_ALLOW_ANONYMOUS=true`.

3. **Neustart des MQTT-Brokers**
   - Stoppen und starten Sie den MQTT-Broker:
     ```bash
     ~/swissairdry/stop_mqtt.sh
     ~/swissairdry/start_mqtt.sh
     ```

4. **Überprüfen Sie die Netzwerkverbindung**
   - Testen Sie die Verbindung zum MQTT-Broker:
     ```bash
     mosquitto_pub -h localhost -p 1883 -t test -m "Hallo Welt"
     ```

## ESP-Firmware-Probleme

### Kompilierungsfehler

**Symptom:** Die Firmware kann nicht kompiliert werden.

**Mögliche Ursachen und Lösungen:**

1. **PlatformIO ist nicht installiert**
   - Installieren Sie PlatformIO manuell:
     ```bash
     pip install -U platformio
     ```

2. **Abhängigkeiten fehlen**
   - Führen Sie eine Aktualisierung der PlatformIO-Abhängigkeiten durch:
     ```bash
     cd ~/swissairdry/firmware
     platformio pkg update
     ```

3. **Fehlerhafter Code**
   - Überprüfen Sie die Fehlermeldungen und korrigieren Sie den Code entsprechend.

4. **SPI-Typ-Definitionen (ESP32-C6)**
   - Bei Problemen mit `spi_host_device_t` in ESP32-C6, stellen Sie sicher, dass die `spi_fix.h` korrekt eingebunden ist.

### Upload-Probleme

**Symptom:** Die Firmware kann nicht auf das Gerät hochgeladen werden.

**Lösungen:**

1. **Überprüfen Sie die Verbindung**
   - Stellen Sie sicher, dass das Gerät korrekt angeschlossen ist und der richtige Port angegeben wurde.
   - Versuchen Sie, den Port manuell anzugeben:
     ```bash
     ~/swissairdry/firmware/upload_esp8266.sh /dev/ttyUSB0
     ```

2. **Setzen Sie das Gerät in den Flash-Modus**
   - Drücken Sie die BOOT- oder FLASH-Taste während des Uploads.

3. **Berechtigungsprobleme**
   - Stellen Sie sicher, dass Sie Zugriff auf den seriellen Port haben:
     ```bash
     sudo chmod 666 /dev/ttyUSB0
     ```
   - Fügen Sie Ihren Benutzer zur Gruppe `dialout` hinzu:
     ```bash
     sudo usermod -a -G dialout $USER
     ```
     (Anmeldung erforderlich, damit die Änderung wirksam wird)

## Allgemeine Probleme

### Dienste starten nach Neustart nicht automatisch

**Problem:** Die Dienste starten nach einem Systemneustart nicht automatisch.

**Lösung:**

Erstellen Sie systemd-Service-Dateien oder crontab-Einträge, um die Dienste automatisch zu starten:

**Beispiel für crontab:**

```bash
crontab -e
```

Fügen Sie die folgenden Zeilen hinzu:

```
@reboot ~/swissairdry/start_api.sh
@reboot ~/swissairdry/start_mqtt.sh
```

### Datenbank-Probleme

**Symptom:** Datenbankfehler in den API-Logs.

**Lösungen:**

1. **Überprüfen Sie die Datenbankverbindung**
   - Stellen Sie sicher, dass die Datenbank läuft und erreichbar ist.
   - Überprüfen Sie die Datenbankverbindungsdaten in der `.env`-Datei.

2. **Datenbankschema aktualisieren**
   - Führen Sie die Datenbankmigrationen manuell aus.

### Speicherprobleme

**Symptom:** Die ESP-Geräte stürzen ab oder starten neu.

**Lösungen:**

1. **Stacktrace überprüfen**
   - Verwenden Sie den seriellen Monitor, um die Fehlermeldungen zu sehen:
     ```bash
     ~/swissairdry/firmware/monitor.sh
     ```

2. **Speichernutzung optimieren**
   - Reduzieren Sie große statische Datenstrukturen oder Puffer.
   - Verwenden Sie dynamische Speicherverwaltung mit Bedacht.

## Kontakt und Support

Bei anhaltenden Problemen oder speziellen Fragen wenden Sie sich bitte an das SwissAirDry-Team.