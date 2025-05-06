#!/bin/bash
#
# SwissAirDry ESP Firmware Installationsskript
# Dieses Skript richtet die Entwicklungsumgebung für ESP8266/ESP32-Firmware ein
#

set -e  # Bei Fehlern abbrechen

echo "
===============================================
   SwissAirDry ESP Firmware Installationsskript
===============================================
"

# Arbeitsverzeichnis erstellen, falls nicht vorhanden
INSTALL_DIR="$HOME/swissairdry"
FIRMWARE_DIR="$INSTALL_DIR/firmware"
ESP8266_DIR="$FIRMWARE_DIR/esp8266"
ESP32_DIR="$FIRMWARE_DIR/esp32"
ESP32C6_DIR="$FIRMWARE_DIR/esp32c6"

echo "[1/6] Arbeitsverzeichnis wird vorbereitet..."
mkdir -p "$FIRMWARE_DIR"
mkdir -p "$ESP8266_DIR"
mkdir -p "$ESP32_DIR"
mkdir -p "$ESP32C6_DIR"

# Aktuelle Position merken
CURRENT_DIR=$(pwd)

# PlatformIO prüfen und installieren
echo "[2/6] PlatformIO wird installiert (wenn nötig)..."
if command -v platformio &> /dev/null; then
    echo "PlatformIO ist bereits installiert."
else
    echo "PlatformIO wird installiert..."
    python -m pip install -U platformio
fi

# Konfigurationen kopieren
echo "[3/6] ESP-Konfigurationen werden vorbereitet..."

# platformio.ini kopieren oder erstellen
if [ -f "$CURRENT_DIR/platformio.ini" ]; then
    cp "$CURRENT_DIR/platformio.ini" "$FIRMWARE_DIR/"
    echo "platformio.ini kopiert."
else
    # platformio.ini erstellen
    cat > "$FIRMWARE_DIR/platformio.ini" << 'EOL'
; PlatformIO Projekt-Konfiguration
; https://docs.platformio.org/page/projectconf.html

[platformio]
default_envs = esp32c6

; Gemeinsame Einstellungen für alle Umgebungen
[env]
framework = arduino
monitor_speed = 115200
lib_deps =
    https://github.com/bblanchon/ArduinoJson.git
    https://github.com/tzapu/WiFiManager.git
    https://github.com/mathertel/OneButton.git

; ESP32-C6 XIAO mit TFT-Display und SD-Karte
[env:esp32c6]
platform = https://github.com/platformio/platform-espressif32.git
platform_packages = 
    framework-arduinoespressif32 @ https://github.com/espressif/arduino-esp32.git#master
board = esp32-c6-devkitm-1
board_build.mcu = esp32c6
board_build.f_cpu = 160000000L
board_build.f_flash = 80000000L
board_build.flash_mode = qio
board_upload.flash_size = 4MB
; Verwende USB als Upload-Methode
upload_protocol = esptool
upload_port = /dev/ttyUSB0  ; Anpassen an den tatsächlichen Port
upload_speed = 921600
; Board-Flags und Definitionen
build_flags = 
    -D ESP32
    -D ESP32C6
    -D TFT_DISPLAY
    -D SD_CARD
    -D ARDUINO_USB_MODE=1
    -D ARDUINO_USB_CDC_ON_BOOT=1
    -D ARDUINO_FIRMWARE_VERSION="1.0.0"
    -D CONFIG_SPIRAM_CACHE_WORKAROUND
    -DBOARD_HAS_PSRAM
    -DLV_LVGL_H_INCLUDE_SIMPLE
    -DSPI_HOST_DEVICE_VSPI=2  ; Wichtig für ESP32-C6 SPI-Kompatibilität
    -DSPI_HOST_DEVICE_HSPI=1  ; Wichtig für ESP32-C6 SPI-Kompatibilität
    ; TFT eSPI Konfiguration
    -DUSER_SETUP_LOADED=1
    -DST7789_DRIVER=1
    -DTFT_WIDTH=172
    -DTFT_HEIGHT=320
    -DTFT_MISO=9
    -DTFT_MOSI=10
    -DTFT_SCLK=8
    -DTFT_CS=3
    -DTFT_DC=4
    -DTFT_RST=5
    -DTFT_BL=6
    -DTFT_BACKLIGHT_ON=HIGH
    -DSPI_FREQUENCY=40000000
    -DSPI_READ_FREQUENCY=20000000
    -DSPI_TOUCH_FREQUENCY=2500000
    ; SD-Karten-Konfiguration
    -DSD_CS=7
lib_deps = 
    ${env.lib_deps}
    https://github.com/Bodmer/TFT_eSPI.git
    https://github.com/me-no-dev/AsyncTCP.git
    https://github.com/me-no-dev/ESPAsyncWebServer.git
    https://github.com/madhephaestus/ESP32AnalogRead.git
    https://github.com/h2zero/NimBLE-Arduino.git  ; NimBLE ist kompatibler mit ESP32-C6
    https://github.com/arduino-libraries/SD.git
    https://github.com/lorol/LITTLEFS.git
board_build.partitions = huge_app.csv

; ESP32-C6 DevKitM-1 (Alternative Konfiguration für offizielles Espressif DevKit)
[env:esp32c6-devkit]
platform = https://github.com/platformio/platform-espressif32.git
platform_packages = 
    framework-arduinoespressif32 @ https://github.com/espressif/arduino-esp32.git#master
board = esp32-c6-devkitm-1
board_build.mcu = esp32c6
board_build.f_cpu = 160000000L
upload_protocol = esptool
build_flags = 
    -D ESP32
    -D ESP32C6
    -D CONFIG_SPIRAM_CACHE_WORKAROUND
    -DBOARD_HAS_PSRAM
    -DSPI_HOST_DEVICE_VSPI=2  ; Wichtig für ESP32-C6 SPI-Kompatibilität
    -DSPI_HOST_DEVICE_HSPI=1  ; Wichtig für ESP32-C6 SPI-Kompatibilität
lib_deps = 
    ${env.lib_deps}
    https://github.com/me-no-dev/AsyncTCP.git
    https://github.com/me-no-dev/ESPAsyncWebServer.git
    https://github.com/h2zero/NimBLE-Arduino.git
board_build.partitions = huge_app.csv

; ESP8266 mit Membranschalter
[env:esp8266]
platform = espressif8266
board = d1_mini
build_flags = 
    -D ESP8266
    -D MEMBRANE_BUTTONS
lib_deps = 
    ${env.lib_deps}
    https://github.com/esp8266/Arduino.git#libraries/ESP8266WebServer
    https://github.com/esp8266/Arduino.git#libraries/ESP8266HTTPClient
    https://github.com/esp8266/Arduino.git#libraries/ESP8266WiFi
    https://github.com/esp8266/Arduino.git#libraries/ESP8266mDNS

; Hinweis: 
; Um die Firmware für ESP8266 zu kompilieren:
; pio run -e esp8266
;
; Um die Firmware für ESP32-C6 zu kompilieren:
; pio run -e esp32c6
;
; Um die Firmware hochzuladen (ESP8266):
; pio run -e esp8266 -t upload
;
; Um die Firmware hochzuladen (ESP32-C6):
; pio run -e esp32c6 -t upload
;
; Um die serielle Konsole zu öffnen:
; pio device monitor
EOL
    echo "platformio.ini erstellt."
fi

# SPI-Fix für ESP32-C6 kopieren oder erstellen
mkdir -p "$FIRMWARE_DIR/src/esp32c6"
cat > "$FIRMWARE_DIR/src/esp32c6/spi_fix.h" << 'EOL'
#pragma once

#ifdef ESP32C6

// Workaround für den Fehler: 'spi_host_device_t' does not name a type
#ifndef SPI_HOST_DEVICE_HSPI
#define SPI_HOST_DEVICE_HSPI 1
#endif

#ifndef SPI_HOST_DEVICE_VSPI
#define SPI_HOST_DEVICE_VSPI 2
#endif

// Fallback-Enum für ESP32-C6, wenn der Typ nicht definiert ist
#ifdef __cplusplus
extern "C" {
#endif

#ifndef spi_host_device_t_defined
#define spi_host_device_t_defined

typedef enum {
    SPI1_HOST = SPI_HOST_DEVICE_HSPI,    // SPI1 (HSPI) ist SPI Host 1
    SPI2_HOST = SPI_HOST_DEVICE_VSPI,    // SPI2 (VSPI) ist SPI Host 2
    SPI3_HOST = 3,                       // SPI3 ist SPI Host 3
} spi_host_device_t;

#endif // spi_host_device_t_defined

#ifdef __cplusplus
}
#endif

#endif // ESP32C6
EOL
echo "SPI-Fix für ESP32-C6 erstellt."

# ESP32-C6 Hauptdatei erstellen
cat > "$FIRMWARE_DIR/src/esp32c6/main.cpp" << 'EOL'
/**
 * SwissAirDry ESP32-C6 mit TFT-Display und SD-Karten-Unterstützung
 * 
 * PlatformIO-Version
 * 
 * @version 1.0.0
 * @author Swiss Air Dry Team <info@swissairdry.com>
 * @copyright 2023-2025 Swiss Air Dry Team
 */

// Diese Datei VOR allen anderen Includes einfügen, um SPI-Kompatibilitätsprobleme zu beheben
#include "spi_fix.h"

#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <WebServer.h>
#include <ESPmDNS.h>
#include <ArduinoOTA.h>
#include <ArduinoJson.h>
#include <Preferences.h>
#include <DNSServer.h>
#include <WiFiManager.h>
#include <OneButton.h>
#include <SPI.h>
#include <SD.h>
#include <TFT_eSPI.h>
#include <FS.h>
#include <LittleFS.h>

// Konstanten
#define DEVICE_VERSION "1.0.0"
#define SENSOR_READ_INTERVAL 5000    // 5 Sekunden
#define API_SEND_INTERVAL 30000      // 30 Sekunden
#define LED_UPDATE_INTERVAL 1000     // 1 Sekunde
#define WEB_CONFIG_PORT 80           // Webserver-Port
#define MAX_FAILED_API_ATTEMPTS 5    // Max. Anzahl fehlgeschlagener API-Verbindungen

// Pinnummern für ESP32-C6 XIAO Board
#define RELAY1_PIN 7     // GPIO7 für Relais 1
#define RELAY2_PIN 6     // GPIO6 für Relais 2
#define SENSOR_PIN 5     // GPIO5 für DHT Sensor (falls verwendet)
#define LED_PIN 21       // Eingebaute LED
#define SD_CS_PIN 10     // GPIO10 für SD-Karten-CS

// Display-Einstellungen
#define TFT_WIDTH 172
#define TFT_HEIGHT 320

// Physische Tasten
#define BTN_BOOT 9       // BOOT-Taste
#define BTN_RESET 3      // RESET-Taste (Hardware Reset)

// SD-Karten-Verzeichnisstruktur
#define WEB_DIR "/web"           // Webdateien auf der SD-Karte
#define CSS_DIR "/web/css"       // CSS-Dateien
#define JS_DIR "/web/js"         // JavaScript-Dateien
#define IMAGES_DIR "/web/images" // Bilddateien

// OneButton-Objekt für die BOOT-Taste
OneButton btnBoot(BTN_BOOT, true);

// TFT-Display initialisieren
TFT_eSPI tft = TFT_eSPI();

// Webserver initialisieren
WebServer server(WEB_CONFIG_PORT);

// Preferences für die Konfigurationsspeicherung
Preferences preferences;

// Globale Variablen
struct Config {
  char device_id[32];      // Geräte-ID
  char api_host[64];       // API-Host
  int api_port;            // API-Port
  char api_path[64];       // API-Pfad
  bool use_ssl;            // HTTPS verwenden
  char auth_token[64];     // API-Authentifizierung
  bool relay1_enabled;     // Relais 1 aktiviert
  bool relay2_enabled;     // Relais 2 aktiviert
  float temp_threshold;    // Temperaturschwelle
  float humid_threshold;   // Feuchtigkeitsschwelle
};

Config config;
unsigned long lastSensorRead = 0;
unsigned long lastApiSend = 0;
unsigned long lastLedUpdate = 0;
unsigned long startTime = 0;
unsigned long runTime = 0;
bool wifiConnected = false;
bool apiConnected = false;
bool relay1State = false;
bool relay2State = false;
bool sdCardAvailable = false;
float temperature = 0.0;
float humidity = 0.0;
float power = 0.0;
float energy = 0.0;
int failedApiAttempts = 0;
int currentMenuPage = 0;
int maxMenuPages = 3;

// Funktionsprototypen
void setupWifi();
void setupWebServer();
void setupOTA();
void loadConfig();
void saveConfig();
bool sendDataToApi();
void readSensors();
void updateLedStatus();
bool setupSDCard();
void setupTFTDisplay();
void updateDisplay();
void handleRoot();
void handleConfig();
void handleSave();
void handleReset();
void handleRestart();
void handleStatus();
void handleStaticFiles(String path);
void generateDeviceId();
void setupButtons();
void onBootButtonPressed();
void onBootButtonLongPressed();

void setup() {
  // Serielle Konsole initialisieren
  Serial.begin(115200);
  delay(500);
  
  Serial.println("\n\n");
  Serial.println("===========================================");
  Serial.println("  SwissAirDry ESP32-C6 Trocknungssteuerung");
  Serial.println("===========================================");
  Serial.println("Version: " DEVICE_VERSION);
  
  // GPIO-Pins initialisieren
  pinMode(RELAY1_PIN, OUTPUT);
  pinMode(RELAY2_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  
  digitalWrite(RELAY1_PIN, LOW);  // Relais initial ausschalten
  digitalWrite(RELAY2_PIN, LOW);
  digitalWrite(LED_PIN, LOW);
  
  // Startzeit speichern
  startTime = millis();
  
  // Konfiguration laden
  loadConfig();
  
  // TFT-Display initialisieren
  setupTFTDisplay();
  
  // SD-Karte initialisieren
  sdCardAvailable = setupSDCard();
  
  // Tasten initialisieren
  setupButtons();
  
  // WLAN konfigurieren und verbinden
  setupWifi();
  
  // OTA-Updates aktivieren
  setupOTA();
  
  // Webserver starten
  setupWebServer();
  
  // Initialen Display-Update durchführen
  updateDisplay();
  
  Serial.println("Initialisierung abgeschlossen");
}

void loop() {
  // OTA-Anfragen abfragen
  ArduinoOTA.handle();
  
  // Web-Server-Anfragen bearbeiten
  server.handleClient();
  
  // Boot-Taste prüfen
  btnBoot.tick();
  
  // Sensoren in regelmäßigen Abständen auslesen
  unsigned long currentMillis = millis();
  if (currentMillis - lastSensorRead >= SENSOR_READ_INTERVAL) {
    lastSensorRead = currentMillis;
    readSensors();
    
    // Laufzeit berechnen
    runTime = (currentMillis - startTime) / 1000;
    
    // Display aktualisieren
    updateDisplay();
  }
  
  // Daten an API senden
  if (currentMillis - lastApiSend >= API_SEND_INTERVAL) {
    lastApiSend = currentMillis;
    apiConnected = sendDataToApi();
  }
  
  // LED-Status aktualisieren
  if (currentMillis - lastLedUpdate >= LED_UPDATE_INTERVAL) {
    lastLedUpdate = currentMillis;
    updateLedStatus();
  }
}

// TFT-Display initialisieren
void setupTFTDisplay() {
  Serial.println("TFT-Display wird initialisiert...");
  tft.init();
  tft.setRotation(0); // Portrait-Modus (0 oder 2)
  tft.fillScreen(TFT_BLACK);
  Serial.println("TFT-Display initialisiert");
}

// Beispielimplementierung für updateDisplay()
void updateDisplay() {
  // Bildschirmseite basierend auf currentMenuPage anzeigen
  tft.fillScreen(TFT_BLACK);
  
  switch (currentMenuPage) {
    case 0: // Hauptseite - Statusübersicht
      tft.setTextColor(TFT_WHITE, TFT_BLACK);
      tft.setCursor(10, 10);
      tft.setTextSize(2);
      tft.println("SwissAirDry");
      
      tft.setTextSize(1);
      tft.setCursor(10, 40);
      tft.println("Temperatur: " + String(temperature, 1) + " C");
      
      tft.setCursor(10, 60);
      tft.println("Feuchtigkeit: " + String(humidity, 1) + " %");
      
      // Weitere Anzeigen...
      break;
      
    case 1: // Einstellungsseite
      tft.setTextColor(TFT_WHITE, TFT_BLACK);
      tft.setCursor(10, 10);
      tft.setTextSize(2);
      tft.println("Einstellungen");
      
      // Weitere Anzeigen...
      break;
      
    case 2: // Relais-Steuerungsseite
      tft.setTextColor(TFT_WHITE, TFT_BLACK);
      tft.setCursor(10, 10);
      tft.setTextSize(2);
      tft.println("Relais-Steuerung");
      
      // Weitere Anzeigen...
      break;
  }
}

// Lesen der Sensordaten (Dummy-Implementierung für Demo)
void readSensors() {
  // In einer echten Implementierung würden hier die tatsächlichen Sensoren ausgelesen
  // Für Demozwecke erzeugen wir Zufallswerte
  temperature = 20.0 + (random(100) / 10.0);  // Zwischen 20-30°C
  humidity = 40.0 + (random(400) / 10.0);     // Zwischen 40-80%
  
  // Power berechnen basierend auf Relaiszuständen
  power = (relay1State ? 1000.0 : 0.0) + (relay2State ? 800.0 : 0.0) + random(100);
  
  // Energie akkumulieren (kWh)
  energy += (power / 1000.0) * (SENSOR_READ_INTERVAL / 3600000.0);
  
  Serial.println("Sensordaten aktualisiert:");
  Serial.println("  Temperatur: " + String(temperature) + "°C");
  Serial.println("  Feuchtigkeit: " + String(humidity) + "%");
  Serial.println("  Leistung: " + String(power) + " W");
  Serial.println("  Energie: " + String(energy, 3) + " kWh");
}

// Dummy-Implementierung für andere Funktionen
void loadConfig() {
  Serial.println("Lädt Konfiguration...");
  // Standardwerte
  strncpy(config.device_id, "SAD00001", sizeof(config.device_id));
  strncpy(config.api_host, "api.swissairdry.com", sizeof(config.api_host));
  config.api_port = 443;
  strncpy(config.api_path, "/api/device/data", sizeof(config.api_path));
  config.use_ssl = true;
  strncpy(config.auth_token, "demo_token", sizeof(config.auth_token));
  config.relay1_enabled = true;
  config.relay2_enabled = true;
  config.temp_threshold = 25.0;
  config.humid_threshold = 60.0;
}

bool sendDataToApi() {
  Serial.println("Sendet Daten an API...");
  // In einer echten Implementierung würden hier Daten an die API gesendet
  return true;
}

void updateLedStatus() {
  // LED-Status basierend auf Systemzustand aktualisieren
  if (!wifiConnected) {
    // Blinken bei Verbindungsproblemen
    digitalWrite(LED_PIN, (millis() / 500) % 2 == 0 ? HIGH : LOW);
  } else if (!apiConnected) {
    // Schnelles Blinken bei API-Problemen
    digitalWrite(LED_PIN, (millis() / 200) % 2 == 0 ? HIGH : LOW);
  } else {
    // Langsames Blinken im Normalbetrieb
    digitalWrite(LED_PIN, (millis() / 1000) % 2 == 0 ? HIGH : LOW);
  }
}

// Weitere Implementierungen...

// Nützliche Hilfsfunktionen...
EOL

echo "ESP32-C6 Hauptdatei erstellt."

# ESP8266 Hauptdatei erstellen
mkdir -p "$FIRMWARE_DIR/src/esp8266"
cat > "$FIRMWARE_DIR/src/esp8266/main.cpp" << 'EOL'
/**
 * SwissAirDry ESP8266 Trocknungssteuerung
 * 
 * PlatformIO-Version
 * 
 * @version 1.0.0
 * @author Swiss Air Dry Team <info@swissairdry.com>
 * @copyright 2023-2025 Swiss Air Dry Team
 */

#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266mDNS.h>
#include <ArduinoOTA.h>
#include <ArduinoJson.h>
#include <DNSServer.h>
#include <WiFiManager.h>
#include <OneButton.h>

// Konstanten
#define DEVICE_VERSION "1.0.0"
#define SENSOR_READ_INTERVAL 5000    // 5 Sekunden
#define API_SEND_INTERVAL 30000      // 30 Sekunden
#define LED_UPDATE_INTERVAL 1000     // 1 Sekunde
#define WEB_CONFIG_PORT 80           // Webserver-Port
#define MAX_FAILED_API_ATTEMPTS 5    // Max. Anzahl fehlgeschlagener API-Verbindungen

// Pin-Definitionen für ESP8266 D1 Mini
#define RELAY1_PIN D1     // Relais 1
#define RELAY2_PIN D2     // Relais 2
#define SENSOR_PIN D3     // Sensor (falls verwendet)
#define LED_PIN LED_BUILTIN // Eingebaute LED
#define BTN_CONFIG D5     // Konfigurationstaste

// OneButton-Objekt für die Konfigurationstaste
OneButton btnConfig(BTN_CONFIG, true);

// Webserver initialisieren
ESP8266WebServer server(WEB_CONFIG_PORT);

// Globale Variablen
struct Config {
  char device_id[32];      // Geräte-ID
  char api_host[64];       // API-Host
  int api_port;            // API-Port
  char api_path[64];       // API-Pfad
  bool use_ssl;            // HTTPS verwenden
  char auth_token[64];     // API-Authentifizierung
  bool relay1_enabled;     // Relais 1 aktiviert
  bool relay2_enabled;     // Relais 2 aktiviert
  float temp_threshold;    // Temperaturschwelle
  float humid_threshold;   // Feuchtigkeitsschwelle
};

Config config;
unsigned long lastSensorRead = 0;
unsigned long lastApiSend = 0;
unsigned long lastLedUpdate = 0;
unsigned long startTime = 0;
unsigned long runTime = 0;
bool wifiConnected = false;
bool apiConnected = false;
bool relay1State = false;
bool relay2State = false;
float temperature = 0.0;
float humidity = 0.0;
float power = 0.0;
float energy = 0.0;
int failedApiAttempts = 0;

// Funktionsprototypen
void setupWifi();
void setupWebServer();
void setupOTA();
void loadConfig();
void saveConfig();
bool sendDataToApi();
void readSensors();
void updateLedStatus();
void handleRoot();
void handleConfig();
void handleSave();
void handleReset();
void handleRestart();
void handleStatus();
void onConfigButtonPressed();
void onConfigButtonLongPressed();

void setup() {
  // Serielle Konsole initialisieren
  Serial.begin(115200);
  delay(500);
  
  Serial.println("\n\n");
  Serial.println("===========================================");
  Serial.println("  SwissAirDry ESP8266 Trocknungssteuerung");
  Serial.println("===========================================");
  Serial.println("Version: " DEVICE_VERSION);
  
  // GPIO-Pins initialisieren
  pinMode(RELAY1_PIN, OUTPUT);
  pinMode(RELAY2_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  
  digitalWrite(RELAY1_PIN, LOW);  // Relais initial ausschalten
  digitalWrite(RELAY2_PIN, LOW);
  digitalWrite(LED_PIN, HIGH);    // LED ausschalten (invertiert auf ESP8266)
  
  // Startzeit speichern
  startTime = millis();
  
  // Konfiguration laden
  loadConfig();
  
  // Konfigurationstaste einrichten
  btnConfig.attachClick(onConfigButtonPressed);
  btnConfig.attachLongPressStart(onConfigButtonLongPressed);
  
  // WLAN konfigurieren und verbinden
  setupWifi();
  
  // OTA-Updates aktivieren
  setupOTA();
  
  // Webserver starten
  setupWebServer();
  
  Serial.println("Initialisierung abgeschlossen");
}

void loop() {
  // OTA-Anfragen abfragen
  ArduinoOTA.handle();
  
  // Web-Server-Anfragen bearbeiten
  server.handleClient();
  
  // Konfigurationstaste prüfen
  btnConfig.tick();
  
  // Sensoren in regelmäßigen Abständen auslesen
  unsigned long currentMillis = millis();
  if (currentMillis - lastSensorRead >= SENSOR_READ_INTERVAL) {
    lastSensorRead = currentMillis;
    readSensors();
    
    // Laufzeit berechnen
    runTime = (currentMillis - startTime) / 1000;
  }
  
  // Daten an API senden
  if (currentMillis - lastApiSend >= API_SEND_INTERVAL) {
    lastApiSend = currentMillis;
    apiConnected = sendDataToApi();
  }
  
  // LED-Status aktualisieren
  if (currentMillis - lastLedUpdate >= LED_UPDATE_INTERVAL) {
    lastLedUpdate = currentMillis;
    updateLedStatus();
  }
}

// Lesen der Sensordaten (Dummy-Implementierung für Demo)
void readSensors() {
  // In einer echten Implementierung würden hier die tatsächlichen Sensoren ausgelesen
  // Für Demozwecke erzeugen wir Zufallswerte
  temperature = 20.0 + (random(100) / 10.0);  // Zwischen 20-30°C
  humidity = 40.0 + (random(400) / 10.0);     // Zwischen 40-80%
  
  // Power berechnen basierend auf Relaiszuständen
  power = (relay1State ? 1000.0 : 0.0) + (relay2State ? 800.0 : 0.0) + random(100);
  
  // Energie akkumulieren (kWh)
  energy += (power / 1000.0) * (SENSOR_READ_INTERVAL / 3600000.0);
  
  Serial.println("Sensordaten aktualisiert:");
  Serial.println("  Temperatur: " + String(temperature) + "°C");
  Serial.println("  Feuchtigkeit: " + String(humidity) + "%");
  Serial.println("  Leistung: " + String(power) + " W");
  Serial.println("  Energie: " + String(energy, 3) + " kWh");
}

// Dummy-Implementierung für andere Funktionen
void loadConfig() {
  Serial.println("Lädt Konfiguration...");
  // Standardwerte
  strncpy(config.device_id, "SAD00001", sizeof(config.device_id));
  strncpy(config.api_host, "api.swissairdry.com", sizeof(config.api_host));
  config.api_port = 443;
  strncpy(config.api_path, "/api/device/data", sizeof(config.api_path));
  config.use_ssl = true;
  strncpy(config.auth_token, "demo_token", sizeof(config.auth_token));
  config.relay1_enabled = true;
  config.relay2_enabled = true;
  config.temp_threshold = 25.0;
  config.humid_threshold = 60.0;
}

bool sendDataToApi() {
  Serial.println("Sendet Daten an API...");
  // In einer echten Implementierung würden hier Daten an die API gesendet
  return true;
}

void updateLedStatus() {
  // LED-Status basierend auf Systemzustand aktualisieren (invertiert auf ESP8266)
  if (!wifiConnected) {
    // Blinken bei Verbindungsproblemen
    digitalWrite(LED_PIN, (millis() / 500) % 2 == 0 ? LOW : HIGH);
  } else if (!apiConnected) {
    // Schnelles Blinken bei API-Problemen
    digitalWrite(LED_PIN, (millis() / 200) % 2 == 0 ? LOW : HIGH);
  } else {
    // Langsames Blinken im Normalbetrieb
    digitalWrite(LED_PIN, (millis() / 1000) % 2 == 0 ? LOW : HIGH);
  }
}

// Weitere Implementierungen...
EOL

echo "ESP8266 Hauptdatei erstellt."

# Compile-Skripte erstellen
echo "[4/6] Compile-Skripte werden erstellt..."

cat > "$FIRMWARE_DIR/compile_esp8266.sh" << 'EOL'
#!/bin/bash

# Zum Firmware-Verzeichnis wechseln
cd "$(dirname "$0")"

echo "Kompiliere ESP8266-Firmware..."
platformio run -e esp8266

if [ $? -eq 0 ]; then
  echo "Kompilierung erfolgreich!"
  echo "Firmware-Datei befindet sich in: .pio/build/esp8266/firmware.bin"
else
  echo "Kompilierung fehlgeschlagen!"
  exit 1
fi
EOL

chmod +x "$FIRMWARE_DIR/compile_esp8266.sh"

cat > "$FIRMWARE_DIR/compile_esp32c6.sh" << 'EOL'
#!/bin/bash

# Zum Firmware-Verzeichnis wechseln
cd "$(dirname "$0")"

echo "Kompiliere ESP32-C6-Firmware..."
platformio run -e esp32c6

if [ $? -eq 0 ]; then
  echo "Kompilierung erfolgreich!"
  echo "Firmware-Datei befindet sich in: .pio/build/esp32c6/firmware.bin"
else
  echo "Kompilierung fehlgeschlagen!"
  exit 1
fi
EOL

chmod +x "$FIRMWARE_DIR/compile_esp32c6.sh"

cat > "$FIRMWARE_DIR/upload_esp8266.sh" << 'EOL'
#!/bin/bash

# Zum Firmware-Verzeichnis wechseln
cd "$(dirname "$0")"

# Port als Parameter oder Standard
PORT=${1:-/dev/ttyUSB0}

echo "Lade ESP8266-Firmware auf Port $PORT..."
platformio run -e esp8266 -t upload --upload-port $PORT

if [ $? -eq 0 ]; then
  echo "Upload erfolgreich!"
else
  echo "Upload fehlgeschlagen!"
  exit 1
fi
EOL

chmod +x "$FIRMWARE_DIR/upload_esp8266.sh"

cat > "$FIRMWARE_DIR/upload_esp32c6.sh" << 'EOL'
#!/bin/bash

# Zum Firmware-Verzeichnis wechseln
cd "$(dirname "$0")"

# Port als Parameter oder Standard
PORT=${1:-/dev/ttyUSB0}

echo "Lade ESP32-C6-Firmware auf Port $PORT..."
platformio run -e esp32c6 -t upload --upload-port $PORT

if [ $? -eq 0 ]; then
  echo "Upload erfolgreich!"
else
  echo "Upload fehlgeschlagen!"
  exit 1
fi
EOL

chmod +x "$FIRMWARE_DIR/upload_esp32c6.sh"

cat > "$FIRMWARE_DIR/monitor.sh" << 'EOL'
#!/bin/bash

# Zum Firmware-Verzeichnis wechseln
cd "$(dirname "$0")"

# Port als Parameter oder Standard
PORT=${1:-/dev/ttyUSB0}

echo "Öffne serielle Konsole auf Port $PORT..."
platformio device monitor --port $PORT --baud 115200
EOL

chmod +x "$FIRMWARE_DIR/monitor.sh"

# API-Konfigurationsdatei für die ESP-Firmware
echo "[5/6] API-Konfigurationsdatei für ESP-Firmware wird erstellt..."
cat > "$FIRMWARE_DIR/api_config.txt" << 'EOL'
# SwissAirDry API-Konfiguration für ESP-Firmware
# Diese Datei auf die SD-Karte des ESP32-C6 kopieren oder in den ESP8266-SPIFFS-Speicher hochladen

# API-Server-Einstellungen
API_HOST=api.swissairdry.com
API_PORT=443
API_PATH=/api/device/data
API_USE_SSL=true
API_AUTH_TOKEN=

# MQTT-Einstellungen
MQTT_BROKER=broker.swissairdry.com
MQTT_PORT=1883
MQTT_USE_SSL=false
MQTT_USERNAME=
MQTT_PASSWORD=
MQTT_CLIENT_ID=
MQTT_TOPIC_PREFIX=swissairdry

# Gerätekonfiguration
DEVICE_ID=
TEMP_THRESHOLD=25.0
HUMID_THRESHOLD=60.0
RELAY1_ENABLED=true
RELAY2_ENABLED=true
EOL

# Hauptinstallationsskript erstellen
echo "[6/6] Hauptinstallationsskript wird erstellt..."
cat > "$INSTALL_DIR/install_firmware.sh" << 'EOL'
#!/bin/bash

echo "==============================================="
echo "    SwissAirDry Firmware-Installationsskript    "
echo "==============================================="
echo ""
echo "Dieses Skript verwendet PlatformIO zur Kompilierung der SwissAirDry-Firmware."
echo ""

# PlatformIO Umgebung testen
if ! command -v platformio &> /dev/null; then
    echo "PlatformIO ist nicht installiert. Installation wird versucht..."
    python3 -m pip install -U platformio
    
    if ! command -v platformio &> /dev/null; then
        echo "Fehler: PlatformIO konnte nicht installiert werden."
        echo "Bitte installieren Sie PlatformIO manuell: https://platformio.org/install/cli"
        exit 1
    fi
fi

echo "PlatformIO ist installiert."
echo ""
echo "Folgende Aktionen sind verfügbar:"
echo ""
echo "1) ESP8266-Firmware kompilieren"
echo "2) ESP32-C6-Firmware kompilieren"
echo "3) ESP8266-Firmware hochladen"
echo "4) ESP32-C6-Firmware hochladen"
echo "5) Serielle Konsole öffnen"
echo "6) Beenden"
echo ""

read -p "Bitte wählen Sie eine Option (1-6): " option

case $option in
    1)
        echo "ESP8266-Firmware wird kompiliert..."
        ./firmware/compile_esp8266.sh
        ;;
    2)
        echo "ESP32-C6-Firmware wird kompiliert..."
        ./firmware/compile_esp32c6.sh
        ;;
    3)
        read -p "Bitte geben Sie den seriellen Port ein (Standard: /dev/ttyUSB0): " port
        port=${port:-/dev/ttyUSB0}
        echo "ESP8266-Firmware wird hochgeladen auf $port..."
        ./firmware/upload_esp8266.sh $port
        ;;
    4)
        read -p "Bitte geben Sie den seriellen Port ein (Standard: /dev/ttyUSB0): " port
        port=${port:-/dev/ttyUSB0}
        echo "ESP32-C6-Firmware wird hochgeladen auf $port..."
        ./firmware/upload_esp32c6.sh $port
        ;;
    5)
        read -p "Bitte geben Sie den seriellen Port ein (Standard: /dev/ttyUSB0): " port
        port=${port:-/dev/ttyUSB0}
        echo "Serielle Konsole wird geöffnet auf $port..."
        ./firmware/monitor.sh $port
        ;;
    6)
        echo "Programm wird beendet."
        exit 0
        ;;
    *)
        echo "Ungültige Option. Programm wird beendet."
        exit 1
        ;;
esac

echo ""
echo "Vorgang abgeschlossen."
EOL

chmod +x "$INSTALL_DIR/install_firmware.sh"

echo "Installation abgeschlossen!"
echo ""
echo "Die SwissAirDry ESP-Firmware-Entwicklungsumgebung wurde in $INSTALL_DIR/firmware installiert."
echo ""
echo "Um die Firmware zu kompilieren oder hochzuladen, führen Sie folgenden Befehl aus:"
echo "   $INSTALL_DIR/install_firmware.sh"
echo ""
echo "Einzelne Aktionen können auch direkt ausgeführt werden:"
echo "   $FIRMWARE_DIR/compile_esp8266.sh - ESP8266-Firmware kompilieren"
echo "   $FIRMWARE_DIR/compile_esp32c6.sh - ESP32-C6-Firmware kompilieren"
echo "   $FIRMWARE_DIR/upload_esp8266.sh [PORT] - ESP8266-Firmware hochladen"
echo "   $FIRMWARE_DIR/upload_esp32c6.sh [PORT] - ESP32-C6-Firmware hochladen"
echo "   $FIRMWARE_DIR/monitor.sh [PORT] - Serielle Konsole öffnen"
echo ""