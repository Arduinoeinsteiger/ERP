# ESP32-C6 SwissAirDry Testprojekt

Dieses PlatformIO-Projekt dient als Testumgebung für die Entwicklung mit dem ESP32-C6 Mikrocontroller für das SwissAirDry-System.

## Übersicht

Der ESP32-C6 ist ein RISC-V basierter Mikrocontroller mit WiFi 6 und Bluetooth 5 Unterstützung. Dieses Projekt demonstriert die grundlegende Funktionalität und dient als Basis für die Entwicklung von SwissAirDry-Geräten.

## Funktionen

- WiFi Access Point (AP) Modus
- Asynchroner Webserver
- REST API mit JSON-Antworten
- LittleFS-Dateisystem für Webseiten und Konfiguration
- Status-LED für visuelle Rückmeldung

## Bibliotheken

Dieses Projekt verwendet folgende Bibliotheken:

- [AsyncTCP-esphome](https://github.com/esphome/AsyncTCP-esphome.git) - ESP32-C6 kompatible Variante von AsyncTCP
- [ESPAsyncWebServer-esphome](https://github.com/esphome/ESPAsyncWebServer-esphome.git) - ESP32-C6 kompatible Variante des AsyncWebServers
- [ArduinoJson](https://github.com/bblanchon/ArduinoJson.git) - JSON-Verarbeitung
- [LITTLEFS](https://github.com/lorol/LITTLEFS.git) - Dateisystem

## Installation & Verwendung

1. Klonen Sie dieses Repository
2. Öffnen Sie das Projektverzeichnis in PlatformIO
3. Verbinden Sie Ihren ESP32-C6 per USB
4. Kompilieren und hochladen:
   ```
   pio run -e esp32c6 -t upload
   ```
5. Öffnen Sie den seriellen Monitor:
   ```
   pio device monitor
   ```
6. Verbinden Sie sich mit dem WiFi-Netzwerk "SwissAirDry" (Passwort: "Test1234")
7. Öffnen Sie im Browser http://192.168.4.1

## Anpassung

### Access Point Konfiguration

Die WiFi-Zugangsdaten können in `src/main.cpp` angepasst werden:

```cpp
const char* ssid = "SwissAirDry";
const char* password = "Test1234";
```

### Webseiten

Die Webseiten befinden sich im `data`-Verzeichnis und können nach Bedarf angepasst werden. Anschließend müssen sie mit dem folgenden Befehl auf das ESP32-C6 Gerät hochgeladen werden:

```
pio run -e esp32c6 -t uploadfs
```

## Fehlerbehebung

### Probleme mit AsyncTCP_RP2040W

Dieses Projekt enthält einen speziellen Skript (`handle_esp32c6_libraries.py`), der die inkompatible `AsyncTCP_RP2040W`-Bibliothek automatisch deaktiviert. Diese Bibliothek ist nur für Raspberry Pi Pico W und nicht für ESP32-C6 konzipiert.

### SPI-Kompatibilität

Der ESP32-C6 verwendet andere SPI-Host-Definitionen als ältere ESP32-Modelle. Diese Anpassungen wurden in der `platformio.ini` berücksichtigt:

```ini
build_flags = 
    -DSPI_HOST_DEVICE_VSPI=2
    -DSPI_HOST_DEVICE_HSPI=1
```

## Hinweise

- Der ESP32-C6 basiert auf der RISC-V Architektur, im Gegensatz zu älteren ESP32-Chips, die Xtensa verwenden
- Für bestmögliche Kompatibilität wird die neueste Version des Arduino-ESP32 Cores empfohlen
- Bei Problemen mit Libraries sollte immer geprüft werden, ob diese explizit ESP32-C6 unterstützen