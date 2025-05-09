# ESP32 Touch-Display BLE-Firmware

Diese Dokumentation beschreibt die BLE-fähige Firmware für ESP32-Geräte mit Touch-Display, die mit der SwissAirDry-Plattform kommunizieren können.

## Überblick

Die Firmware verbindet folgende Hauptkomponenten:

1. BLE-Server mit SwissAirDry-spezifischen Diensten und Charakteristiken
2. Touch-Display-Oberfläche mit LVGL-Bibliothek
3. Sensormessung und Aktuatorsteuerung 
4. QR-Code-Anzeige für einfache Kopplung

![ESP32 Touch BLE Architektur](../static/img/esp32_ble_architecture.png)

## Unterstützte Hardware

Die Firmware unterstützt verschiedene ESP32-basierte Entwicklungsboards mit TFT-Displays:

* Standard ESP32-DevKits mit externem TFT-Display
* TTGO T-Display ESP32 (integriertes ST7789 Display)
* M5Stack Core (integriertes ILI9341 Display)
* Andere ESP32-Board mit ILI9341, ST7789 oder ST7735 Displays

## Schaltplan

Für Standard-ESP32-Boards mit externem Display:

| ESP32 Pin | Komponente    | Beschreibung        |
|-----------|---------------|---------------------|
| 5         | TFT CS        | Chip Select         |
| 4         | TFT DC        | Data/Command        |
| 22        | TFT RST       | Reset               |
| 23        | TFT BL        | Backlight           |
| 18        | TFT SCK       | SPI Clock           |
| 19        | TFT MOSI      | SPI Data            |
| 21        | TFT MISO      | SPI Data (optional) |
| 14        | TOUCH CS      | Touch Chip Select   |
| 2         | TOUCH IRQ     | Touch Interrupt     |
| 15        | DHT22/AM2302  | Temperatur/Feuchte  |
| 16        | Fan Control   | Lüftersteuerung     |
| 17        | Heat Control  | Heizungssteuerung   |
| 18        | Power Control | Stromversorgung     |

## BLE-Spezifikation

Die Firmware implementiert einen BLE-Server mit folgenden Diensten und Charakteristiken:

### Service-UUID

```
4fafc201-1fb5-459e-8fcc-c5c9c331914b
```

### Charakteristiken

1. **Sensor-Charakteristik (Notify)**
   - UUID: `beb5483e-36e1-4688-b7f5-ea07361b26a8`
   - Format: 6 Bytes - `[Temp_MSB][Temp_LSB][Humid_MSB][Humid_LSB][Fan][Power]`
   - Temperatur und Feuchtigkeit werden mit 2 Dezimalstellen multipliziert

2. **Control-Charakteristik (Write)**
   - UUID: `2b96d7a5-3cc7-47a7-a908-13942b0db6d9`
   - Format: 2 Bytes - `[Command][Value]`
   - Befehle:
     - `0x01`: Power (0x00 = aus, 0x01 = ein)
     - `0x02`: Lüftergeschwindigkeit (0x00-0x64, 0-100%)
     - `0x03`: Heizung (0x00 = aus, 0x01 = ein)

3. **Config-Charakteristik (Write)**
   - UUID: `82f55bc5-6d47-4e9e-a868-93f9999427c0`
   - Format: 2 Bytes - `[ConfigType][Value]`
   - Konfigurationstypen:
     - `0x01`: Update-Intervall (in Sekunden)
     - `0x02`: Display aktivieren (0x00 = aus, 0x01 = ein)
     - `0x03`: BLE aktivieren (0x00 = aus, 0x01 = ein)

## Installation

### PlatformIO (empfohlen)

1. Installieren Sie Visual Studio Code und die PlatformIO-Erweiterung
2. Öffnen Sie den Ordner `firmware/esp32_touch_ble`
3. Passen Sie die Konfiguration in `config.h` an Ihre Hardware an
4. Wählen Sie Ihre Umgebung in der PlatformIO-Leiste
5. Klicken Sie auf "Build" und anschließend auf "Upload"

### Arduino IDE

1. Installieren Sie die Arduino IDE und ESP32-Unterstützung
2. Installieren Sie alle erforderlichen Bibliotheken:
   - TFT_eSPI
   - LVGL
   - DHT sensor library
   - QRCode
   - NimBLE-Arduino
3. Kopieren Sie die Dateien `main.cpp` und `config.h` in Ihren Skizzenordner
4. Benennen Sie `main.cpp` in `main.ino` um
5. Konfigurieren Sie die TFT_eSPI-Bibliothek für Ihre Hardware (User_Setup.h)
6. Kompilieren und hochladen

## Benutzung

Nach dem Flashen startet die Firmware automatisch und zeigt den Hauptbildschirm an. Das Gerät sendet sofort BLE-Werbung (Advertising) aus und kann von der SwissAirDry-Plattform erkannt werden.

### Touch-Interface

Die Firmware bietet drei Hauptbildschirme:

1. **Hauptbildschirm**
   - Anzeige von Temperatur und Luftfeuchtigkeit
   - Ein/Aus-Schalter für das Gerät
   - Schieberegler für die Lüftergeschwindigkeit
   - BLE-Verbindungsstatus

2. **BLE-Informationsbildschirm**
   - BLE-Adresse und -Status
   - Gerätename und Firmware-Version

3. **QR-Code-Bildschirm**
   - Zeigt einen QR-Code mit der BLE-Adresse an
   - Ermöglicht einfaches Koppeln mit der SwissAirDry-App

4. **Einstellungsbildschirm**
   - BLE-Funktionalität aktivieren/deaktivieren
   - Display-Helligkeit einstellen
   - Update-Intervall konfigurieren

## Fehlerbehebung

### BLE-Verbindungsprobleme

- Stellen Sie sicher, dass BLE in Ihrer Region/Ihrem Land aktiviert ist
- Überprüfen Sie, ob die BLE-Adresse korrekt ist
- Starten Sie das ESP32-Gerät neu
- Stellen Sie sicher, dass keine andere App mit dem Gerät verbunden ist

### Display-Probleme

- Überprüfen Sie die TFT-Konfiguration in `platformio.ini` oder `User_Setup.h`
- Passen Sie die TFT-Pins in `config.h` an Ihre Hardware an
- Für benutzerdefinierte Displays kann eine angepasste Konfiguration erforderlich sein

### Sensorfehler

- Überprüfen Sie die Verkabelung des DHT22/AM2302-Sensors
- Stellen Sie sicher, dass der richtige Pin in `config.h` definiert ist
- Prüfen Sie, ob die Spannungsversorgung stabil ist (3,3V)

## Anpassung

Die Firmware kann leicht angepasst werden:

1. Bearbeiten Sie `config.h` für grundlegende Hardware- und Funktionsanpassungen
2. Ändern Sie das UI-Layout und Design in der `createUI()`-Funktion
3. Fügen Sie zusätzliche Sensoren oder Aktuatoren in `setup()` und `updateSensors()` hinzu
4. Erweitern Sie die BLE-Charakteristiken für zusätzliche Funktionen

## Erweiterte Funktionen

### OTA-Updates

Die Firmware unterstützt Over-The-Air-Updates, wenn in `config.h` aktiviert:

```cpp
#define FEATURE_OTA_UPDATES true
```

### Energiesparmodus

Für batteriebetriebene Geräte kann der Deep-Sleep-Modus aktiviert werden:

```cpp
#define FEATURE_DEEP_SLEEP true
#define DEEP_SLEEP_INTERVAL_MIN 5  // Aufwachen alle 5 Minuten
```

### MQTT-Integration

Parallel zur BLE-Kommunikation kann auch MQTT aktiviert werden:

```cpp
#define FEATURE_WIFI_ENABLED true
#define FEATURE_MQTT_ENABLED true
#define MQTT_BROKER "broker.example.com"
#define MQTT_PORT 1883
```