/*
 * SwissAirDry - ESP32 Touch Display mit BLE-Integration
 * 
 * Diese Firmware implementiert:
 * - BLE-Server mit SwissAirDry-spezifischen Diensten
 * - Touch-Display Schnittstelle mit lvgl
 * - Sensormessung und -steuerung
 * - QR-Code Anzeige für einfache Kopplung
 * 
 * Basierend auf dem Repository: https://github.com/Arduinoeinsteiger/Esp32TouchDisplayDeDiFeEi
 */

#include <Arduino.h>
#include <Wire.h>
#include <SPI.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <TFT_eSPI.h>
#include <lvgl.h>
#include <DHT.h>
#include <qrcode.h>
#include <WiFi.h>
#include "config.h"

// BLE Definitionen
#define SERVICE_UUID           "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define SENSOR_CHAR_UUID       "beb5483e-36e1-4688-b7f5-ea07361b26a8"
#define CONTROL_CHAR_UUID      "2b96d7a5-3cc7-47a7-a908-13942b0db6d9"
#define CONFIG_CHAR_UUID       "82f55bc5-6d47-4e9e-a868-93f9999427c0"

// Geräteinformationen
#define DEVICE_NAME            "SwissAirDry-Touch"
#define DEVICE_MODEL           "ESP32-T"
#define FIRMWARE_VERSION       "1.0.0"

// Pin-Definitionen
#define DHT_PIN                15      // DHT-Sensor Pin
#define FAN_PIN                16      // Lüftersteuerung Pin
#define HEAT_PIN               17      // Heizungssteuerung Pin
#define POWER_PIN              18      // Power-Steuerung Pin

// LVGL Buffer Definitionen
#define LVGL_BUFFER_SIZE       (TFT_WIDTH * 10)
static lv_disp_buf_t disp_buf;
static lv_color_t buf[LVGL_BUFFER_SIZE];

// Globale Variablen
TFT_eSPI tft = TFT_eSPI();
DHT dht(DHT_PIN, DHT22);  // Für DHT22-Sensor, DHT11 je nach Hardwarekonfiguration

BLEServer* pServer = NULL;
BLECharacteristic* pSensorCharacteristic = NULL;
BLECharacteristic* pControlCharacteristic = NULL;
BLECharacteristic* pConfigCharacteristic = NULL;
bool deviceConnected = false;
bool oldDeviceConnected = false;

// UI-Komponenten
lv_obj_t *mainScreen;
lv_obj_t *bleScreen;
lv_obj_t *settingsScreen;
lv_obj_t *qrCodeScreen;

lv_obj_t *tempLabel;
lv_obj_t *humidLabel;
lv_obj_t *fanSlider;
lv_obj_t *powerSwitch;
lv_obj_t *bleStatusLabel;
lv_obj_t *bleAddressLabel;
lv_obj_t *qrCodeCanvas;

// Zustands- und Konfigurationsvariablen
struct DeviceState {
    float temperature;
    float humidity;
    bool isPowered;
    int fanSpeed;        // 0-100%
    bool isHeating;
    String bleAddress;
    bool bleConnected;
} state;

struct DeviceConfig {
    int updateInterval;  // in Sekunden
    bool displayEnabled;
    bool bleEnabled;
    bool wifiEnabled;
    char wifiSSID[32];
    char wifiPassword[64];
    char mqttBroker[64];
    int mqttPort;
    char mqttUsername[32];
    char mqttPassword[32];
} config;

// Timer
unsigned long lastUpdateTime = 0;
unsigned long lastNotifyTime = 0;

// BLE Callback-Klasse für Verbindungsereignisse
class MyServerCallbacks: public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) {
        deviceConnected = true;
        state.bleConnected = true;
        Serial.println("BLE-Gerät verbunden");
        updateBleStatus();
    }

    void onDisconnect(BLEServer* pServer) {
        deviceConnected = false;
        state.bleConnected = false;
        Serial.println("BLE-Gerät getrennt");
        updateBleStatus();
    }
};

// BLE Callback-Klasse für Control-Charakteristik
class ControlCallbacks: public BLECharacteristicCallbacks {
    void onWrite(BLECharacteristic *pCharacteristic) {
        std::string value = pCharacteristic->getValue();
        if (value.length() > 0) {
            Serial.print("Control-Nachricht erhalten: ");
            for (int i = 0; i < value.length(); i++) {
                Serial.print(value[i], HEX);
                Serial.print(" ");
            }
            Serial.println();

            // Format: [Command][Value]
            // Command:
            // 0x01: Power (0x00 = off, 0x01 = on)
            // 0x02: Fan Speed (0x00-0x64, 0-100%)
            // 0x03: Heat (0x00 = off, 0x01 = on)
            
            uint8_t command = value[0];
            uint8_t arg = value[1];
            
            switch (command) {
                case 0x01:  // Power
                    state.isPowered = (arg == 0x01);
                    digitalWrite(POWER_PIN, state.isPowered ? HIGH : LOW);
                    updatePowerSwitch();
                    break;
                case 0x02:  // Fan Speed
                    state.fanSpeed = arg;
                    analogWrite(FAN_PIN, map(state.fanSpeed, 0, 100, 0, 255));
                    updateFanSlider();
                    break;
                case 0x03:  // Heat
                    state.isHeating = (arg == 0x01);
                    digitalWrite(HEAT_PIN, state.isHeating ? HIGH : LOW);
                    break;
                default:
                    Serial.println("Unbekanntes Kommando");
                    break;
            }
        }
    }
};

// BLE Callback-Klasse für Config-Charakteristik
class ConfigCallbacks: public BLECharacteristicCallbacks {
    void onWrite(BLECharacteristic *pCharacteristic) {
        std::string value = pCharacteristic->getValue();
        if (value.length() > 0) {
            Serial.print("Config-Nachricht erhalten: ");
            for (int i = 0; i < value.length(); i++) {
                Serial.print(value[i], HEX);
                Serial.print(" ");
            }
            Serial.println();
            
            // Sehr vereinfachtes Konfigurationsformat für BLE
            // Komplexere Konfigurationen sollten JSON verwenden
            
            uint8_t configType = value[0];
            uint8_t configValue = value[1];
            
            switch (configType) {
                case 0x01:  // Update Interval
                    config.updateInterval = configValue;
                    break;
                case 0x02:  // Display Enabled
                    config.displayEnabled = (configValue == 0x01);
                    if (!config.displayEnabled) {
                        // Bildschirm ausschalten oder dimmen
                        // tft.setBrightness(0);
                    } else {
                        // tft.setBrightness(255);
                    }
                    break;
                case 0x03:  // BLE Enabled
                    config.bleEnabled = (configValue == 0x01);
                    break;
                default:
                    Serial.println("Unbekannter Konfigurationstyp");
                    break;
            }
        }
    }
};

// LVGL Display Flush Funktion
void my_disp_flush(lv_disp_drv_t *disp, const lv_area_t *area, lv_color_t *color_p) {
    uint32_t w = (area->x2 - area->x1 + 1);
    uint32_t h = (area->y2 - area->y1 + 1);

    tft.startWrite();
    tft.setAddrWindow(area->x1, area->y1, w, h);
    tft.pushColors(&color_p->full, w * h, true);
    tft.endWrite();

    lv_disp_flush_ready(disp);
}

// LVGL Touchscreen Lesen
bool my_touchpad_read(lv_indev_drv_t * indev_driver, lv_indev_data_t * data) {
    uint16_t touchX, touchY;
    bool touched = tft.getTouch(&touchX, &touchY);

    if (touched) {
        data->state = LV_INDEV_STATE_PR;
        data->point.x = touchX;
        data->point.y = touchY;
    } else {
        data->state = LV_INDEV_STATE_REL;
    }

    return false;
}

// Initialisiert das BLE
void setupBLE() {
    // BLE-Gerät initialisieren
    BLEDevice::init(DEVICE_NAME);
    
    // BLE-Server erstellen
    pServer = BLEDevice::createServer();
    pServer->setCallbacks(new MyServerCallbacks());

    // BLE-Service erstellen
    BLEService *pService = pServer->createService(SERVICE_UUID);

    // Sensor-Charakteristik erstellen (Notification)
    pSensorCharacteristic = pService->createCharacteristic(
                                SENSOR_CHAR_UUID,
                                BLECharacteristic::PROPERTY_READ |
                                BLECharacteristic::PROPERTY_NOTIFY
                            );
    pSensorCharacteristic->addDescriptor(new BLE2902());

    // Control-Charakteristik erstellen (Write)
    pControlCharacteristic = pService->createCharacteristic(
                                CONTROL_CHAR_UUID,
                                BLECharacteristic::PROPERTY_WRITE
                            );
    pControlCharacteristic->setCallbacks(new ControlCallbacks());

    // Config-Charakteristik erstellen (Write)
    pConfigCharacteristic = pService->createCharacteristic(
                                CONFIG_CHAR_UUID,
                                BLECharacteristic::PROPERTY_WRITE
                            );
    pConfigCharacteristic->setCallbacks(new ConfigCallbacks());

    // Service starten
    pService->start();

    // Advertising starten
    BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
    pAdvertising->addServiceUUID(SERVICE_UUID);
    pAdvertising->setScanResponse(true);
    pAdvertising->setMinPreferred(0x06);  // Verbindungsintervall (100ms)
    pAdvertising->setMinPreferred(0x12);  // Verbindungsintervall (30ms)
    BLEDevice::startAdvertising();

    // BLE-Adresse speichern
    state.bleAddress = BLEDevice::getAddress().toString().c_str();
    Serial.print("BLE gestartet mit Adresse: ");
    Serial.println(state.bleAddress);
}

// Initialisiert das Display und LVGL
void setupDisplay() {
    tft.begin();
    tft.setRotation(0);  // 0 oder 2 abhängig von der Ausrichtung
    
    uint16_t calData[5] = {320, 3350, 360, 3600, 2};  // Kalibrierungsdaten
    tft.setTouch(calData);
    
    lv_init();
    
    lv_disp_buf_init(&disp_buf, buf, NULL, LVGL_BUFFER_SIZE);
    
    lv_disp_drv_t disp_drv;
    lv_disp_drv_init(&disp_drv);
    disp_drv.flush_cb = my_disp_flush;
    disp_drv.buffer = &disp_buf;
    lv_disp_drv_register(&disp_drv);
    
    lv_indev_drv_t indev_drv;
    lv_indev_drv_init(&indev_drv);
    indev_drv.type = LV_INDEV_TYPE_POINTER;
    indev_drv.read_cb = my_touchpad_read;
    lv_indev_drv_register(&indev_drv);
    
    // Dunkles Farbschema erstellen
    static lv_theme_t *th = lv_theme_material_init(210, NULL);  // Blaues Farbschema
    lv_theme_set_current(th);
    
    // UI erstellen
    createUI();
}

// Erstellt die Benutzeroberfläche
void createUI() {
    // Hauptbildschirm
    mainScreen = lv_obj_create(NULL, NULL);
    
    // Titelbereich
    lv_obj_t *titleLabel = lv_label_create(mainScreen, NULL);
    lv_label_set_text(titleLabel, "SwissAirDry");
    lv_obj_align(titleLabel, NULL, LV_ALIGN_IN_TOP_MID, 0, 10);
    
    // Status-Bereich
    lv_obj_t *statusPanel = lv_obj_create(mainScreen, NULL);
    lv_obj_set_size(statusPanel, LV_HOR_RES - 20, 100);
    lv_obj_align(statusPanel, NULL, LV_ALIGN_IN_TOP_MID, 0, 40);
    
    // Temperatur & Luftfeuchtigkeit
    lv_obj_t *tempIcon = lv_label_create(statusPanel, NULL);
    lv_label_set_text(tempIcon, LV_SYMBOL_TEMP);
    lv_obj_align(tempIcon, NULL, LV_ALIGN_IN_TOP_LEFT, 10, 10);
    
    tempLabel = lv_label_create(statusPanel, NULL);
    lv_label_set_text(tempLabel, "0.0°C");
    lv_obj_align(tempLabel, tempIcon, LV_ALIGN_OUT_RIGHT_MID, 5, 0);
    
    lv_obj_t *humidIcon = lv_label_create(statusPanel, NULL);
    lv_label_set_text(humidIcon, LV_SYMBOL_REFRESH);  // Alternativ: Wassertropfen-Symbol
    lv_obj_align(humidIcon, NULL, LV_ALIGN_IN_TOP_LEFT, 10, 40);
    
    humidLabel = lv_label_create(statusPanel, NULL);
    lv_label_set_text(humidLabel, "0.0%");
    lv_obj_align(humidLabel, humidIcon, LV_ALIGN_OUT_RIGHT_MID, 5, 0);
    
    // BLE-Status
    lv_obj_t *bleIcon = lv_label_create(statusPanel, NULL);
    lv_label_set_text(bleIcon, LV_SYMBOL_BLUETOOTH);
    lv_obj_align(bleIcon, NULL, LV_ALIGN_IN_TOP_RIGHT, -60, 10);
    
    bleStatusLabel = lv_label_create(statusPanel, NULL);
    lv_label_set_text(bleStatusLabel, "Nicht verbunden");
    lv_obj_align(bleStatusLabel, bleIcon, LV_ALIGN_OUT_RIGHT_MID, 5, 0);
    
    // Steuerungen
    lv_obj_t *controlPanel = lv_obj_create(mainScreen, NULL);
    lv_obj_set_size(controlPanel, LV_HOR_RES - 20, 130);
    lv_obj_align(controlPanel, statusPanel, LV_ALIGN_OUT_BOTTOM_MID, 0, 10);
    
    // Power Switch
    lv_obj_t *powerLabel = lv_label_create(controlPanel, NULL);
    lv_label_set_text(powerLabel, "Power");
    lv_obj_align(powerLabel, NULL, LV_ALIGN_IN_TOP_LEFT, 10, 15);
    
    powerSwitch = lv_switch_create(controlPanel, NULL);
    lv_obj_align(powerSwitch, powerLabel, LV_ALIGN_OUT_RIGHT_MID, 20, 0);
    lv_obj_set_event_cb(powerSwitch, [](lv_obj_t * obj, lv_event_t event) {
        if (event == LV_EVENT_VALUE_CHANGED) {
            state.isPowered = lv_switch_get_state(obj);
            digitalWrite(POWER_PIN, state.isPowered ? HIGH : LOW);
            
            // BLE-Benachrichtigung senden
            if (deviceConnected) {
                uint8_t controlCmd[2] = {0x01, state.isPowered ? 0x01 : 0x00};
                pControlCharacteristic->setValue(controlCmd, 2);
                pControlCharacteristic->notify();
            }
        }
    });
    
    // Fan Speed Slider
    lv_obj_t *fanLabel = lv_label_create(controlPanel, NULL);
    lv_label_set_text(fanLabel, "Lüftergeschw.");
    lv_obj_align(fanLabel, NULL, LV_ALIGN_IN_TOP_LEFT, 10, 60);
    
    fanSlider = lv_slider_create(controlPanel, NULL);
    lv_obj_set_width(fanSlider, 150);
    lv_slider_set_range(fanSlider, 0, 100);
    lv_obj_align(fanSlider, fanLabel, LV_ALIGN_OUT_BOTTOM_MID, 0, 10);
    lv_obj_set_event_cb(fanSlider, [](lv_obj_t * obj, lv_event_t event) {
        if (event == LV_EVENT_VALUE_CHANGED) {
            state.fanSpeed = lv_slider_get_value(obj);
            analogWrite(FAN_PIN, map(state.fanSpeed, 0, 100, 0, 255));
            
            // BLE-Benachrichtigung senden
            if (deviceConnected) {
                uint8_t controlCmd[2] = {0x02, (uint8_t)state.fanSpeed};
                pControlCharacteristic->setValue(controlCmd, 2);
                pControlCharacteristic->notify();
            }
        }
    });
    
    // Button-Reihe unten
    lv_obj_t *btnPanel = lv_obj_create(mainScreen, NULL);
    lv_obj_set_size(btnPanel, LV_HOR_RES - 20, 50);
    lv_obj_align(btnPanel, controlPanel, LV_ALIGN_OUT_BOTTOM_MID, 0, 10);
    
    // QR-Code-Button
    lv_obj_t *qrBtn = lv_btn_create(btnPanel, NULL);
    lv_obj_set_size(qrBtn, 70, 40);
    lv_obj_align(qrBtn, NULL, LV_ALIGN_IN_LEFT_MID, 10, 0);
    lv_obj_set_event_cb(qrBtn, [](lv_obj_t * obj, lv_event_t event) {
        if (event == LV_EVENT_CLICKED) {
            createQRCode();
            lv_scr_load(qrCodeScreen);
        }
    });
    
    lv_obj_t *qrBtnLabel = lv_label_create(qrBtn, NULL);
    lv_label_set_text(qrBtnLabel, "QR");
    
    // BLE-Info-Button
    lv_obj_t *bleBtn = lv_btn_create(btnPanel, NULL);
    lv_obj_set_size(bleBtn, 70, 40);
    lv_obj_align(bleBtn, NULL, LV_ALIGN_CENTER, 0, 0);
    lv_obj_set_event_cb(bleBtn, [](lv_obj_t * obj, lv_event_t event) {
        if (event == LV_EVENT_CLICKED) {
            createBleInfoScreen();
            lv_scr_load(bleScreen);
        }
    });
    
    lv_obj_t *bleBtnLabel = lv_label_create(bleBtn, NULL);
    lv_label_set_text(bleBtnLabel, "BLE");
    
    // Einstellungs-Button
    lv_obj_t *settingsBtn = lv_btn_create(btnPanel, NULL);
    lv_obj_set_size(settingsBtn, 70, 40);
    lv_obj_align(settingsBtn, NULL, LV_ALIGN_IN_RIGHT_MID, -10, 0);
    lv_obj_set_event_cb(settingsBtn, [](lv_obj_t * obj, lv_event_t event) {
        if (event == LV_EVENT_CLICKED) {
            createSettingsScreen();
            lv_scr_load(settingsScreen);
        }
    });
    
    lv_obj_t *settingsBtnLabel = lv_label_create(settingsBtn, NULL);
    lv_label_set_text(settingsBtnLabel, LV_SYMBOL_SETTINGS);
    
    // BLE-Info-Bildschirm erstellen
    createBleInfoScreen();
    
    // QR-Code-Bildschirm erstellen
    createQRCodeScreen();
    
    // Hauptbildschirm laden
    lv_scr_load(mainScreen);
}

// Erstellt den BLE-Info-Bildschirm
void createBleInfoScreen() {
    if (bleScreen != NULL) {
        lv_obj_del(bleScreen);
    }
    
    bleScreen = lv_obj_create(NULL, NULL);
    
    // Zurück-Button
    lv_obj_t *backBtn = lv_btn_create(bleScreen, NULL);
    lv_obj_set_size(backBtn, 70, 40);
    lv_obj_align(backBtn, NULL, LV_ALIGN_IN_TOP_LEFT, 10, 10);
    lv_obj_set_event_cb(backBtn, [](lv_obj_t * obj, lv_event_t event) {
        if (event == LV_EVENT_CLICKED) {
            lv_scr_load(mainScreen);
        }
    });
    
    lv_obj_t *backBtnLabel = lv_label_create(backBtn, NULL);
    lv_label_set_text(backBtnLabel, LV_SYMBOL_LEFT);
    
    // Titel
    lv_obj_t *titleLabel = lv_label_create(bleScreen, NULL);
    lv_label_set_text(titleLabel, "BLE-Informationen");
    lv_obj_align(titleLabel, NULL, LV_ALIGN_IN_TOP_MID, 0, 20);
    
    // BLE-Status
    lv_obj_t *statusLabel = lv_label_create(bleScreen, NULL);
    lv_label_set_text(statusLabel, "Status:");
    lv_obj_align(statusLabel, NULL, LV_ALIGN_IN_TOP_LEFT, 20, 60);
    
    lv_obj_t *statusValueLabel = lv_label_create(bleScreen, NULL);
    lv_label_set_text(statusValueLabel, state.bleConnected ? "Verbunden" : "Nicht verbunden");
    lv_obj_align(statusValueLabel, statusLabel, LV_ALIGN_OUT_RIGHT_MID, 10, 0);
    
    // BLE-Adresse
    lv_obj_t *addrLabel = lv_label_create(bleScreen, NULL);
    lv_label_set_text(addrLabel, "Adresse:");
    lv_obj_align(addrLabel, statusLabel, LV_ALIGN_OUT_BOTTOM_LEFT, 0, 20);
    
    bleAddressLabel = lv_label_create(bleScreen, NULL);
    lv_label_set_text(bleAddressLabel, state.bleAddress.c_str());
    lv_obj_align(bleAddressLabel, addrLabel, LV_ALIGN_OUT_RIGHT_MID, 10, 0);
    
    // Gerätename
    lv_obj_t *nameLabel = lv_label_create(bleScreen, NULL);
    lv_label_set_text(nameLabel, "Name:");
    lv_obj_align(nameLabel, addrLabel, LV_ALIGN_OUT_BOTTOM_LEFT, 0, 20);
    
    lv_obj_t *nameValueLabel = lv_label_create(bleScreen, NULL);
    lv_label_set_text(nameValueLabel, DEVICE_NAME);
    lv_obj_align(nameValueLabel, nameLabel, LV_ALIGN_OUT_RIGHT_MID, 10, 0);
    
    // Firmware-Version
    lv_obj_t *versionLabel = lv_label_create(bleScreen, NULL);
    lv_label_set_text(versionLabel, "Firmware:");
    lv_obj_align(versionLabel, nameLabel, LV_ALIGN_OUT_BOTTOM_LEFT, 0, 20);
    
    lv_obj_t *versionValueLabel = lv_label_create(bleScreen, NULL);
    lv_label_set_text(versionValueLabel, FIRMWARE_VERSION);
    lv_obj_align(versionValueLabel, versionLabel, LV_ALIGN_OUT_RIGHT_MID, 10, 0);
}

// Erstellt den Einstellungsbildschirm
void createSettingsScreen() {
    if (settingsScreen != NULL) {
        lv_obj_del(settingsScreen);
    }
    
    settingsScreen = lv_obj_create(NULL, NULL);
    
    // Zurück-Button
    lv_obj_t *backBtn = lv_btn_create(settingsScreen, NULL);
    lv_obj_set_size(backBtn, 70, 40);
    lv_obj_align(backBtn, NULL, LV_ALIGN_IN_TOP_LEFT, 10, 10);
    lv_obj_set_event_cb(backBtn, [](lv_obj_t * obj, lv_event_t event) {
        if (event == LV_EVENT_CLICKED) {
            lv_scr_load(mainScreen);
        }
    });
    
    lv_obj_t *backBtnLabel = lv_label_create(backBtn, NULL);
    lv_label_set_text(backBtnLabel, LV_SYMBOL_LEFT);
    
    // Titel
    lv_obj_t *titleLabel = lv_label_create(settingsScreen, NULL);
    lv_label_set_text(titleLabel, "Einstellungen");
    lv_obj_align(titleLabel, NULL, LV_ALIGN_IN_TOP_MID, 0, 20);
    
    // BLE Ein/Aus
    lv_obj_t *bleLabel = lv_label_create(settingsScreen, NULL);
    lv_label_set_text(bleLabel, "BLE aktivieren");
    lv_obj_align(bleLabel, NULL, LV_ALIGN_IN_TOP_LEFT, 20, 60);
    
    lv_obj_t *bleSwitch = lv_switch_create(settingsScreen, NULL);
    lv_switch_set_state(bleSwitch, config.bleEnabled);
    lv_obj_align(bleSwitch, bleLabel, LV_ALIGN_OUT_RIGHT_MID, 10, 0);
    lv_obj_set_event_cb(bleSwitch, [](lv_obj_t * obj, lv_event_t event) {
        if (event == LV_EVENT_VALUE_CHANGED) {
            config.bleEnabled = lv_switch_get_state(obj);
            if (config.bleEnabled) {
                BLEDevice::startAdvertising();
            } else {
                BLEDevice::stopAdvertising();
            }
        }
    });
    
    // Display Ein/Aus
    lv_obj_t *displayLabel = lv_label_create(settingsScreen, NULL);
    lv_label_set_text(displayLabel, "Display aktivieren");
    lv_obj_align(displayLabel, bleLabel, LV_ALIGN_OUT_BOTTOM_LEFT, 0, 20);
    
    lv_obj_t *displaySwitch = lv_switch_create(settingsScreen, NULL);
    lv_switch_set_state(displaySwitch, config.displayEnabled);
    lv_obj_align(displaySwitch, displayLabel, LV_ALIGN_OUT_RIGHT_MID, 10, 0);
    lv_obj_set_event_cb(displaySwitch, [](lv_obj_t * obj, lv_event_t event) {
        if (event == LV_EVENT_VALUE_CHANGED) {
            config.displayEnabled = lv_switch_get_state(obj);
            // Hier Display-Helligkeit anpassen
        }
    });
    
    // Update-Intervall
    lv_obj_t *updateLabel = lv_label_create(settingsScreen, NULL);
    lv_label_set_text(updateLabel, "Update-Intervall");
    lv_obj_align(updateLabel, displayLabel, LV_ALIGN_OUT_BOTTOM_LEFT, 0, 20);
    
    lv_obj_t *updateSlider = lv_slider_create(settingsScreen, NULL);
    lv_obj_set_width(updateSlider, 150);
    lv_slider_set_range(updateSlider, 1, 60);  // 1-60 Sekunden
    lv_slider_set_value(updateSlider, config.updateInterval, LV_ANIM_OFF);
    lv_obj_align(updateSlider, updateLabel, LV_ALIGN_OUT_BOTTOM_MID, 0, 10);
    lv_obj_set_event_cb(updateSlider, [](lv_obj_t * obj, lv_event_t event) {
        if (event == LV_EVENT_VALUE_CHANGED) {
            config.updateInterval = lv_slider_get_value(obj);
        }
    });
    
    lv_obj_t *updateValueLabel = lv_label_create(settingsScreen, NULL);
    char buf[32];
    sprintf(buf, "%d s", config.updateInterval);
    lv_label_set_text(updateValueLabel, buf);
    lv_obj_align(updateValueLabel, updateSlider, LV_ALIGN_OUT_BOTTOM_MID, 0, 5);
    lv_obj_set_auto_realign(updateValueLabel, true);
}

// Erstellt den QR-Code-Bildschirm
void createQRCodeScreen() {
    if (qrCodeScreen != NULL) {
        lv_obj_del(qrCodeScreen);
    }
    
    qrCodeScreen = lv_obj_create(NULL, NULL);
    
    // Zurück-Button
    lv_obj_t *backBtn = lv_btn_create(qrCodeScreen, NULL);
    lv_obj_set_size(backBtn, 70, 40);
    lv_obj_align(backBtn, NULL, LV_ALIGN_IN_TOP_LEFT, 10, 10);
    lv_obj_set_event_cb(backBtn, [](lv_obj_t * obj, lv_event_t event) {
        if (event == LV_EVENT_CLICKED) {
            lv_scr_load(mainScreen);
        }
    });
    
    lv_obj_t *backBtnLabel = lv_label_create(backBtn, NULL);
    lv_label_set_text(backBtnLabel, LV_SYMBOL_LEFT);
    
    // Titel
    lv_obj_t *titleLabel = lv_label_create(qrCodeScreen, NULL);
    lv_label_set_text(titleLabel, "QR-Code zum Verbinden");
    lv_obj_align(titleLabel, NULL, LV_ALIGN_IN_TOP_MID, 0, 20);
    
    // QR-Code-Container
    qrCodeCanvas = lv_canvas_create(qrCodeScreen, NULL);
    static lv_color_t cbuf[200 * 200];  // QR-Code-Puffer
    lv_canvas_set_buffer(qrCodeCanvas, cbuf, 200, 200, LV_IMG_CF_TRUE_COLOR);
    lv_obj_align(qrCodeCanvas, NULL, LV_ALIGN_CENTER, 0, 10);
    
    // QR-Code neu erstellen
    createQRCode();
    
    // Geräteadresse anzeigen
    lv_obj_t *addrLabel = lv_label_create(qrCodeScreen, NULL);
    lv_label_set_text(addrLabel, state.bleAddress.c_str());
    lv_obj_align(addrLabel, qrCodeCanvas, LV_ALIGN_OUT_BOTTOM_MID, 0, 10);
}

// Generiert und zeichnet den QR-Code
void createQRCode() {
    if (qrCodeCanvas == NULL) return;
    
    // Canvas leeren
    lv_canvas_fill_bg(qrCodeCanvas, LV_COLOR_WHITE, LV_OPA_COVER);
    
    // QR-Code-Daten erstellen
    String qrData = "SwissAirDry:";
    qrData += state.bleAddress;
    
    // QR-Code generieren
    QRCode qrcode;
    uint8_t qrcodeData[qrcode_getBufferSize(4)];
    qrcode_initText(&qrcode, qrcodeData, 4, 0, qrData.c_str());
    
    // QR-Code zeichnen (vereinfacht)
    int scale = 4;  // Skalierungsfaktor
    for (uint8_t y = 0; y < qrcode.size; y++) {
        for (uint8_t x = 0; x < qrcode.size; x++) {
            if (qrcode_getModule(&qrcode, x, y)) {
                // Schwarzes Quadrat zeichnen
                for (int i = 0; i < scale; i++) {
                    for (int j = 0; j < scale; j++) {
                        lv_canvas_set_px(qrCodeCanvas, x * scale + i, y * scale + j, LV_COLOR_BLACK);
                    }
                }
            }
        }
    }
}

// Aktualisiert die UI basierend auf dem Gerätestatus
void updateUI() {
    char buffer[32];
    
    // Aktualisiere Temperatur & Luftfeuchtigkeit
    sprintf(buffer, "%.1f°C", state.temperature);
    lv_label_set_text(tempLabel, buffer);
    
    sprintf(buffer, "%.1f%%", state.humidity);
    lv_label_set_text(humidLabel, buffer);
    
    // Aktualisiere BLE-Status
    updateBleStatus();
    
    // Aktualisiere Schalter & Schieberegler
    updatePowerSwitch();
    updateFanSlider();
}

// Aktualisiert den BLE-Status in der UI
void updateBleStatus() {
    if (bleStatusLabel != NULL) {
        lv_label_set_text(bleStatusLabel, state.bleConnected ? "Verbunden" : "Nicht verbunden");
    }
    
    if (bleAddressLabel != NULL) {
        lv_label_set_text(bleAddressLabel, state.bleAddress.c_str());
    }
}

// Aktualisiert den Powerschalter in der UI
void updatePowerSwitch() {
    if (powerSwitch != NULL) {
        lv_switch_set_state(powerSwitch, state.isPowered);
    }
}

// Aktualisiert den Lüfterregler in der UI
void updateFanSlider() {
    if (fanSlider != NULL) {
        lv_slider_set_value(fanSlider, state.fanSpeed, LV_ANIM_OFF);
    }
}

// Aktualisiert die Sensordaten
void updateSensors() {
    // Sensoren auslesen
    float newTemp = dht.readTemperature();
    float newHumid = dht.readHumidity();
    
    // Prüfen, ob gültige Werte
    if (!isnan(newTemp) && !isnan(newHumid)) {
        state.temperature = newTemp;
        state.humidity = newHumid;
    }
    
    // UI aktualisieren
    updateUI();
    
    // BLE-Sensordaten aktualisieren
    if (deviceConnected && (millis() - lastNotifyTime > 1000)) {
        lastNotifyTime = millis();
        
        // Erstelle ein einfaches Datenpaket: [Temp_MSB][Temp_LSB][Humid_MSB][Humid_LSB][Fan][Power]
        uint16_t temp = state.temperature * 100;  // 2 Dezimalstellen
        uint16_t humid = state.humidity * 100;    // 2 Dezimalstellen
        
        uint8_t sensorData[6];
        sensorData[0] = temp >> 8;
        sensorData[1] = temp & 0xFF;
        sensorData[2] = humid >> 8;
        sensorData[3] = humid & 0xFF;
        sensorData[4] = state.fanSpeed;
        sensorData[5] = state.isPowered ? 1 : 0;
        
        pSensorCharacteristic->setValue(sensorData, 6);
        pSensorCharacteristic->notify();
    }
}

// Hauptsetup-Funktion
void setup() {
    Serial.begin(115200);
    Serial.println("SwissAirDry ESP32 Touch BLE startet...");
    
    // Konfiguration initialisieren
    config.updateInterval = 5;  // 5 Sekunden
    config.displayEnabled = true;
    config.bleEnabled = true;
    config.wifiEnabled = false;
    
    // Pins initialisieren
    pinMode(FAN_PIN, OUTPUT);
    pinMode(HEAT_PIN, OUTPUT);
    pinMode(POWER_PIN, OUTPUT);
    
    // Geräte-Status initialisieren
    state.temperature = 0.0;
    state.humidity = 0.0;
    state.isPowered = false;
    state.fanSpeed = 0;
    state.isHeating = false;
    state.bleConnected = false;
    state.bleAddress = "";
    
    // Hardware initialisieren
    dht.begin();
    
    // Display & LVGL initialisieren
    setupDisplay();
    
    // BLE initialisieren
    setupBLE();
    
    Serial.println("Setup abgeschlossen");
}

// Hauptschleife
void loop() {
    lv_task_handler();
    
    // Sensordaten aktualisieren
    unsigned long currentTime = millis();
    if (currentTime - lastUpdateTime > (config.updateInterval * 1000)) {
        lastUpdateTime = currentTime;
        updateSensors();
    }
    
    // BLE-Verbindungsstatus-Änderungen behandeln
    if (!deviceConnected && oldDeviceConnected) {
        delay(500); // Wartezeit für die Verbindungstrennung
        Serial.println("BLE-Gerät getrennt");
        oldDeviceConnected = deviceConnected;
        pServer->startAdvertising(); // Advertising neu starten
        state.bleConnected = false;
        updateBleStatus();
    }
    
    if (deviceConnected && !oldDeviceConnected) {
        Serial.println("BLE-Gerät verbunden");
        oldDeviceConnected = deviceConnected;
        state.bleConnected = true;
        updateBleStatus();
    }
    
    delay(10); // Kurze Pause
}