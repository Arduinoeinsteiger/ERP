/**
 * SwissAirDry Platform - ESP8266 Firmware
 * 
 * This firmware is designed for ESP8266-based SwissAirDry devices.
 * It handles sensor readings, display output, and MQTT communication
 * with the central SwissAirDry platform.
 */

#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266mDNS.h>
#include <WiFiUdp.h>
#include <ArduinoOTA.h>
#include <ArduinoJson.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <U8g2lib.h>
#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <OneButton.h>
#include <FS.h>
#include <WiFiManager.h>

// Include common headers
#include "../common/config.h"
#include "../common/mqtt_client.h"
#include "../common/display.h"
#include "../common/ota.h"

// Device-specific configuration
#define DEVICE_TYPE "esp8266"
#define DEFAULT_DEVICE_NAME "SwissAirDry-ESP8266"
#define FIRMWARE_VERSION "1.0.0"
#define HARDWARE_VERSION "1.0"

// Pin definitions
#define DHT_PIN D4
#define DHT_TYPE DHT22
#define FAN_CONTROL_PIN D5
#define POWER_CONTROL_PIN D6
#define BUTTON_PIN D7

// Global variables
SwissAirDryConfig config;
SwissAirDryMQTT mqtt;
SwissAirDryDisplay display;
SwissAirDryOTA ota;

// Sensor objects
DHT dht(DHT_PIN, DHT_TYPE);

// Fan control (PWM)
int currentFanSpeed = 0;

// Button object
OneButton button(BUTTON_PIN, true);

// Function prototypes
void setupWiFi();
void setupSensors();
void setupControls();
void setupDisplay();
void publishDiscovery();
void publishStatus();
void publishTelemetry();
void handleButtonPress();
void handleButtonLongPress();
void handleMqttMessage(char* topic, byte* payload, unsigned int length);

void setup() {
  // Initialize serial communication
  Serial.begin(115200);
  Serial.println("\n\nSwissAirDry ESP8266 Firmware Starting...");
  Serial.println("Version: " + String(FIRMWARE_VERSION));
  
  // Initialize file system
  if (!SPIFFS.begin()) {
    Serial.println("Failed to initialize SPIFFS");
  } else {
    Serial.println("SPIFFS initialized");
  }
  
  // Load configuration
  config.init();
  config.loadFromSPIFFS();
  
  // Set default device name if not configured
  if (config.deviceName.length() == 0) {
    config.deviceName = DEFAULT_DEVICE_NAME;
    config.deviceName += "-" + String(ESP.getChipId(), HEX);
  }
  
  // Set default device ID if not configured
  if (config.deviceId.length() == 0) {
    config.deviceId = "esp8266-" + String(ESP.getChipId(), HEX);
  }

  Serial.println("Device ID: " + config.deviceId);
  Serial.println("Device Name: " + config.deviceName);
  
  // Setup WiFi
  setupWiFi();
  
  // Setup MQTT
  mqtt.init(
    config.mqttBroker, 
    config.mqttPort,
    config.mqttUsername,
    config.mqttPassword,
    config.deviceId,
    handleMqttMessage
  );
  
  // Subscribe to topics
  mqtt.subscribe("swissairdry/" + config.deviceId + "/config");
  mqtt.subscribe("swissairdry/" + config.deviceId + "/control");
  mqtt.subscribe("swissairdry/" + config.deviceId + "/command");
  mqtt.subscribe("swissairdry/" + config.deviceId + "/ota/update");
  
  // Setup OTA updates
  ota.init(config.deviceId, FIRMWARE_VERSION);
  
  // Setup display (64px OLED for ESP8266)
  display.init(DISPLAY_64PX);
  display.showBootScreen(config.deviceName, FIRMWARE_VERSION, HARDWARE_VERSION);
  
  // Setup sensors
  setupSensors();
  
  // Setup control pins
  setupControls();
  
  // Setup button
  button.attachClick(handleButtonPress);
  button.attachLongPressStart(handleButtonLongPress);
  
  // Publish initial discovery message
  publishDiscovery();
  
  // Publish initial status
  publishStatus();
  
  Serial.println("Setup complete");
}

void loop() {
  // Handle MQTT connection and messages
  mqtt.loop();
  
  // Handle OTA updates
  ota.loop();
  
  // Handle button press
  button.tick();
  
  // Handle display updates
  display.loop();
  
  // Read and publish sensor data periodically
  static unsigned long lastTelemetryTime = 0;
  if (millis() - lastTelemetryTime > config.updateInterval * 1000) {
    publishTelemetry();
    lastTelemetryTime = millis();
  }
  
  // Publish status periodically
  static unsigned long lastStatusTime = 0;
  if (millis() - lastStatusTime > 60000) { // Every minute
    publishStatus();
    lastStatusTime = millis();
  }
  
  // Check for OTA updates periodically
  static unsigned long lastOtaCheckTime = 0;
  if (config.otaEnabled && (millis() - lastOtaCheckTime > 3600000)) { // Every hour
    ota.checkForUpdates();
    lastOtaCheckTime = millis();
  }
  
  // Yield to allow ESP8266 to handle background tasks
  yield();
}

void setupWiFi() {
  Serial.println("Setting up WiFi...");
  
  // Use WiFiManager for easier WiFi setup
  WiFiManager wifiManager;
  
  // Set timeout for configuration portal (2 minutes)
  wifiManager.setConfigPortalTimeout(120);
  
  // Show connecting on display
  display.showConnecting();
  
  // Define custom parameters for WiFiManager
  WiFiManagerParameter custom_mqtt_server("server", "MQTT Server", config.mqttBroker.c_str(), 40);
  WiFiManagerParameter custom_mqtt_port("port", "MQTT Port", String(config.mqttPort).c_str(), 6);
  WiFiManagerParameter custom_device_name("name", "Device Name", config.deviceName.c_str(), 32);
  
  wifiManager.addParameter(&custom_mqtt_server);
  wifiManager.addParameter(&custom_mqtt_port);
  wifiManager.addParameter(&custom_device_name);
  
  // Connect to WiFi or create AP for configuration
  String apName = "SwissAirDry-" + String(ESP.getChipId(), HEX);
  if (!wifiManager.autoConnect(apName.c_str(), "dryingdevice")) {
    Serial.println("Failed to connect to WiFi and timed out");
    // Show connection failed on display
    display.showError("WiFi connection failed");
    delay(3000);
    // Reset and try again
    ESP.restart();
    return;
  }
  
  // Extract and save custom parameters
  config.mqttBroker = custom_mqtt_server.getValue();
  config.mqttPort = atoi(custom_mqtt_port.getValue());
  config.deviceName = custom_device_name.getValue();
  config.saveToSPIFFS();
  
  // Show connected on display
  display.showConnected(WiFi.localIP().toString());
  
  Serial.println("WiFi connected");
  Serial.println("IP address: " + WiFi.localIP().toString());
  
  // Setup mDNS responder
  if (MDNS.begin(config.deviceId.c_str())) {
    Serial.println("mDNS responder started");
    // Add service to mDNS
    MDNS.addService("swissairdry", "tcp", 80);
  }
}

void setupSensors() {
  Serial.println("Setting up sensors...");
  
  // Initialize DHT sensor
  dht.begin();
  
  // Test reading
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  
  if (isnan(h) || isnan(t)) {
    Serial.println("Failed to read from DHT sensor!");
    // Show sensor error on display
    display.showError("Sensor error");
  } else {
    Serial.println("Temperature: " + String(t) + "°C");
    Serial.println("Humidity: " + String(h) + "%");
  }
}

void setupControls() {
  Serial.println("Setting up control pins...");
  
  // Set fan control pin as output (PWM)
  pinMode(FAN_CONTROL_PIN, OUTPUT);
  analogWrite(FAN_CONTROL_PIN, 0); // Start with fan off
  
  // Set power control pin as output
  pinMode(POWER_CONTROL_PIN, OUTPUT);
  digitalWrite(POWER_CONTROL_PIN, LOW); // Start with power off
}

void publishDiscovery() {
  Serial.println("Publishing discovery information...");
  
  DynamicJsonDocument doc(512);
  doc["device_id"] = config.deviceId;
  doc["type"] = DEVICE_TYPE;
  doc["firmware_version"] = FIRMWARE_VERSION;
  doc["hardware_version"] = HARDWARE_VERSION;
  doc["ip_address"] = WiFi.localIP().toString();
  doc["mac_address"] = WiFi.macAddress();
  doc["display_type"] = "64px";
  doc["has_sensors"] = config.hasSensors;
  doc["name"] = config.deviceName;
  
  String payload;
  serializeJson(doc, payload);
  
  mqtt.publish("swissairdry/" + config.deviceId + "/discovery", payload.c_str(), true);
}

void publishStatus() {
  Serial.println("Publishing status...");
  
  DynamicJsonDocument doc(512);
  doc["online"] = true;
  doc["firmware_version"] = FIRMWARE_VERSION;
  doc["ip_address"] = WiFi.localIP().toString();
  doc["mac_address"] = WiFi.macAddress();
  doc["uptime"] = millis() / 1000;
  doc["free_heap"] = ESP.getFreeHeap();
  doc["fan_speed"] = currentFanSpeed;
  doc["power"] = digitalRead(POWER_CONTROL_PIN) == HIGH;
  
  String payload;
  serializeJson(doc, payload);
  
  mqtt.publish("swissairdry/" + config.deviceId + "/status", payload.c_str(), true);
}

void publishTelemetry() {
  Serial.println("Reading and publishing sensor data...");
  
  // Read sensor data
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();
  
  // Check for invalid readings
  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }
  
  // Update display
  display.showSensorData(temperature, humidity, currentFanSpeed);
  
  // Create JSON payload
  DynamicJsonDocument doc(512);
  doc["temperature"] = temperature;
  doc["humidity"] = humidity;
  doc["fan_speed"] = currentFanSpeed;
  doc["power_consumption"] = currentFanSpeed * 0.5; // Mock calculation based on fan speed
  
  String payload;
  serializeJson(doc, payload);
  
  // Publish telemetry
  mqtt.publish("swissairdry/" + config.deviceId + "/telemetry", payload.c_str());
  
  Serial.println("Temperature: " + String(temperature) + "°C");
  Serial.println("Humidity: " + String(humidity) + "%");
}

void handleButtonPress() {
  Serial.println("Button pressed");
  
  // Toggle fan speed: 0 -> 25 -> 50 -> 75 -> 100 -> 0
  currentFanSpeed = (currentFanSpeed + 25) % 125;
  
  // Set fan speed
  int pwmValue = map(currentFanSpeed, 0, 100, 0, 1023);
  analogWrite(FAN_CONTROL_PIN, pwmValue);
  
  // Update display
  display.showFanSpeed(currentFanSpeed);
  
  // Publish status update
  publishStatus();
}

void handleButtonLongPress() {
  Serial.println("Button long-pressed");
  
  // Toggle power
  boolean currentPower = digitalRead(POWER_CONTROL_PIN) == HIGH;
  digitalWrite(POWER_CONTROL_PIN, !currentPower ? HIGH : LOW);
  
  // Update display
  display.showPowerState(!currentPower);
  
  // Publish status update
  publishStatus();
}

void handleMqttMessage(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  
  // Convert payload to string
  String message;
  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.println(message);
  
  // Parse topic
  String topicStr = String(topic);
  
  // Handle config updates
  if (topicStr.endsWith("/config")) {
    handleConfigMessage(message);
  }
  // Handle control commands
  else if (topicStr.endsWith("/control")) {
    handleControlMessage(message);
  }
  // Handle general commands
  else if (topicStr.endsWith("/command")) {
    handleCommandMessage(message);
  }
  // Handle OTA update commands
  else if (topicStr.endsWith("/ota/update")) {
    handleOtaUpdateMessage(message);
  }
}

void handleConfigMessage(String message) {
  Serial.println("Handling config message");
  
  DynamicJsonDocument doc(512);
  DeserializationError error = deserializeJson(doc, message);
  
  if (error) {
    Serial.print("deserializeJson() failed: ");
    Serial.println(error.c_str());
    return;
  }
  
  // Update configuration
  if (doc.containsKey("update_interval")) {
    config.updateInterval = doc["update_interval"];
  }
  
  if (doc.containsKey("display_type")) {
    String displayType = doc["display_type"];
    if (displayType == "64px" || displayType == "none") {
      // Only 64px and none are supported on ESP8266
      config.displayType = displayType;
    }
  }
  
  if (doc.containsKey("has_sensors")) {
    config.hasSensors = doc["has_sensors"];
  }
  
  if (doc.containsKey("ota_enabled")) {
    config.otaEnabled = doc["ota_enabled"];
  }
  
  // Save updated configuration
  config.saveToSPIFFS();
  
  Serial.println("Configuration updated");
  
  // Acknowledge config update
  DynamicJsonDocument ackDoc(256);
  ackDoc["status"] = "success";
  ackDoc["message"] = "Configuration updated";
  
  String ackPayload;
  serializeJson(ackDoc, ackPayload);
  
  mqtt.publish("swissairdry/" + config.deviceId + "/config/ack", ackPayload.c_str());
}

void handleControlMessage(String message) {
  Serial.println("Handling control message");
  
  DynamicJsonDocument doc(256);
  DeserializationError error = deserializeJson(doc, message);
  
  if (error) {
    Serial.print("deserializeJson() failed: ");
    Serial.println(error.c_str());
    return;
  }
  
  // Handle fan speed control
  if (doc.containsKey("fan_speed")) {
    int speed = doc["fan_speed"];
    // Constrain speed to 0-100%
    speed = constrain(speed, 0, 100);
    currentFanSpeed = speed;
    
    // Set fan speed
    int pwmValue = map(speed, 0, 100, 0, 1023);
    analogWrite(FAN_CONTROL_PIN, pwmValue);
    
    // Update display
    display.showFanSpeed(speed);
    
    Serial.println("Fan speed set to " + String(speed) + "%");
  }
  
  // Handle power control
  if (doc.containsKey("power")) {
    boolean power = doc["power"];
    digitalWrite(POWER_CONTROL_PIN, power ? HIGH : LOW);
    
    // Update display
    display.showPowerState(power);
    
    Serial.println("Power set to " + String(power ? "ON" : "OFF"));
  }
  
  // Publish updated status
  publishStatus();
}

void handleCommandMessage(String message) {
  Serial.println("Handling command message");
  
  DynamicJsonDocument doc(256);
  DeserializationError error = deserializeJson(doc, message);
  
  if (error) {
    Serial.print("deserializeJson() failed: ");
    Serial.println(error.c_str());
    return;
  }
  
  // Handle status_update command
  if (doc.containsKey("action") && doc["action"] == "status_update") {
    publishStatus();
    publishTelemetry();
  }
  
  // Handle reboot command
  if (doc.containsKey("action") && doc["action"] == "reboot") {
    Serial.println("Rebooting device...");
    
    // Display reboot message
    display.showMessage("Rebooting...");
    
    // Wait a moment to ensure message is sent
    delay(1000);
    
    // Reboot
    ESP.restart();
  }
  
  // Handle factory_reset command
  if (doc.containsKey("action") && doc["action"] == "factory_reset") {
    Serial.println("Performing factory reset...");
    
    // Display reset message
    display.showMessage("Factory Reset...");
    
    // Clear settings
    WiFiManager wifiManager;
    wifiManager.resetSettings();
    
    // Reset configuration
    config.reset();
    config.saveToSPIFFS();
    
    // Wait a moment to ensure message is sent
    delay(1000);
    
    // Reboot
    ESP.restart();
  }
}

void handleOtaUpdateMessage(String message) {
  Serial.println("Handling OTA update message");
  
  DynamicJsonDocument doc(512);
  DeserializationError error = deserializeJson(doc, message);
  
  if (error) {
    Serial.print("deserializeJson() failed: ");
    Serial.println(error.c_str());
    return;
  }
  
  // Check if OTA is enabled
  if (!config.otaEnabled) {
    Serial.println("OTA updates are disabled");
    
    // Send error response
    DynamicJsonDocument errorDoc(256);
    errorDoc["status"] = "error";
    errorDoc["message"] = "OTA updates are disabled";
    
    String errorPayload;
    serializeJson(errorDoc, errorPayload);
    
    mqtt.publish("swissairdry/" + config.deviceId + "/ota/status", errorPayload.c_str());
    return;
  }
  
  // Extract update information
  String version = doc["version"];
  String url = doc["url"];
  String md5Hash = doc["md5_hash"];
  
  // Show update info on display
  display.showMessage("OTA Update");
  display.showMessage("Version: " + version);
  
  // Start OTA update
  if (version != FIRMWARE_VERSION) {
    // Publish status update - starting OTA
    DynamicJsonDocument statusDoc(256);
    statusDoc["status"] = "started";
    statusDoc["version"] = version;
    
    String statusPayload;
    serializeJson(statusDoc, statusPayload);
    
    mqtt.publish("swissairdry/" + config.deviceId + "/ota/status", statusPayload.c_str());
    
    // Start OTA update process
    ota.startUpdate(url, md5Hash, version);
  } else {
    Serial.println("Already on the latest version");
    
    // Send status response
    DynamicJsonDocument statusDoc(256);
    statusDoc["status"] = "skipped";
    statusDoc["message"] = "Already on the latest version";
    statusDoc["version"] = version;
    
    String statusPayload;
    serializeJson(statusDoc, statusPayload);
    
    mqtt.publish("swissairdry/" + config.deviceId + "/ota/status", statusPayload.c_str());
  }
}
