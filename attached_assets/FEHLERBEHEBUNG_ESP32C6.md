# Fehlerbehebung für ESP32-C6

## Behebung von AsyncTCP-Kompatibilitätsproblemen

Bei der Entwicklung für den ESP32-C6 können Kompatibilitätsprobleme mit einigen Bibliotheken auftreten, insbesondere mit AsyncTCP und AsyncWebServer.

### Problem: Inkompatibilität mit AsyncTCP_RP2040W

Die Bibliothek `AsyncTCP_RP2040W` ist nur für Raspberry Pi Pico W (RP2040 Chip mit CYW43439 WiFi) konzipiert und nicht mit ESP32-C6 kompatibel. Die Verwendung dieser Bibliothek führt zu folgenden Fehlern:

```
error: #error For RASPBERRY_PI_PICO_W board using CYW43439 WiFi only
```

### Lösung: Verwendung ESP32-C6-kompatibler AsyncTCP-Bibliothek

1. In der `platformio.ini` wurde die Standard-AsyncTCP-Bibliothek durch die ESPHome-Variante ersetzt, die besser mit dem ESP32-C6 funktioniert:

```ini
lib_deps = 
    ; Andere Bibliotheken...
    https://github.com/esphome/AsyncTCP-esphome.git
    https://github.com/esphome/ESPAsyncWebServer-esphome.git
```

2. Explizit die problematische Bibliothek ausschließen:

```ini
lib_ignore =
    AsyncTCP_RP2040W
```

### SPI-Definitionen für ESP32-C6

Die SPI-Implementierung im ESP32-C6 unterscheidet sich von anderen ESP32-Versionen. Folgende Definitionen wurden zur Kompatibilität hinzugefügt:

```ini
build_flags = 
    ; Andere Flags...
    -DSPI_HOST_DEVICE_VSPI=2
    -DSPI_HOST_DEVICE_HSPI=1
```

## Hinweise zur Kompilierung und Hochladen

Um die Firmware zu kompilieren:
```
pio run -e esp32c6
```

Um die Firmware hochzuladen:
```
pio run -e esp32c6 -t upload
```

## Bekannte Einschränkungen

- Der ESP32-C6 verwendet RISC-V-Architektur, was zu Kompatibilitätsproblemen mit einigen ESP32-spezifischen Bibliotheken führen kann
- Bei Problemen mit der WiFi-Konnektivität oder WebServer-Funktionalität kann ein Reset des Boards erforderlich sein
- Die BLE-Funktionalität sollte über NimBLE statt der Standard-BLE-Bibliothek implementiert werden