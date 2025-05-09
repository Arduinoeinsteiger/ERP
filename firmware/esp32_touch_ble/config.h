/*
 * SwissAirDry - ESP32 Touch Display mit BLE-Integration
 * Konfigurationsdatei
 */

#ifndef CONFIG_H
#define CONFIG_H

// WLAN-Konfiguration (optional, wenn auch WLAN verwendet werden soll)
#define WIFI_SSID "WLAN-Name"
#define WIFI_PASS "WLAN-Passwort"

// MQTT-Konfiguration (optional, wenn auch MQTT verwendet werden soll)
#define MQTT_BROKER "broker.example.com"
#define MQTT_PORT 1883
#define MQTT_USER ""
#define MQTT_PASS ""
#define MQTT_CLIENT_ID "swissairdry_esp32_"
#define MQTT_TOPIC_BASE "swissairdry/"

// Hardware-Konfiguration
// Unterstützte Display-Typen: TFT_ST7735, TFT_ILI9341, TFT_ST7789
#define DISPLAY_TYPE TFT_ILI9341

// TFT-Pins (Standardwerte für die meisten ESP32 Touch-Displays)
#define TFT_CS  5
#define TFT_DC  4
#define TFT_RST 22
#define TFT_BL  23  // Backlight

// Touch-Pins
#define TOUCH_CS 14
#define TOUCH_IRQ 2

// Sensortransformationen (optional - zum Kalibrieren von Sensorwerten)
#define TEMP_OFFSET 0.0   // Temperatur-Offset
#define TEMP_SCALE 1.0    // Temperatur-Skalierung
#define HUMID_OFFSET 0.0  // Luftfeuchtigkeits-Offset
#define HUMID_SCALE 1.0   // Luftfeuchtigkeits-Skalierung

// BLE-Konfiguration
#define BLE_DEVICE_NAME_PREFIX "SwissAirDry-"

// Erweiterte Features aktivieren/deaktivieren
#define FEATURE_WIFI_ENABLED false     // WLAN-Funktionalität aktivieren
#define FEATURE_MQTT_ENABLED false     // MQTT-Funktionalität aktivieren
#define FEATURE_QR_CODE_ENABLED true   // QR-Code-Anzeige aktivieren
#define FEATURE_OTA_UPDATES true       // OTA-Updates aktivieren
#define FEATURE_DEEP_SLEEP false       // Energiesparmodus aktivieren

// Timing-Konfiguration
#define DEFAULT_UPDATE_INTERVAL 5      // Standardwert für Update-Intervall in Sekunden
#define DEEP_SLEEP_INTERVAL_MIN 5      // Deep Sleep Zeit in Minuten (wenn aktiviert)
#define BLE_NOTIFY_INTERVAL_MS 1000    // BLE-Benachrichtigungsintervall in Millisekunden

// Farbschema
// Standardfarbschema (blau)
#define COLOR_PRIMARY_DEFAULT 0x021B
#define COLOR_SECONDARY_DEFAULT 0x3353
#define COLOR_BACKGROUND_DEFAULT 0x0000
#define COLOR_TEXT_DEFAULT 0xFFFF

// Dark-Theme (optional)
#define COLOR_PRIMARY_DARK 0x031F
#define COLOR_SECONDARY_DARK 0x4B7F
#define COLOR_BACKGROUND_DARK 0x0000
#define COLOR_TEXT_DARK 0xFFFF

// Debug-Einstellungen
#define DEBUG_ENABLED true            // Debug-Ausgaben über Serial aktivieren
#define DEBUG_SENSOR_RAW_VALUES false // Rohe Sensorwerte ausgeben
#define DEBUG_BLE_PACKETS false       // BLE-Paketinhalte ausgeben

#endif // CONFIG_H