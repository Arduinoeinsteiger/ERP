/**
 * SwissAirDry Configuration Handler
 * 
 * This file contains the configuration handler for SwissAirDry devices.
 * It provides a unified interface for storing and retrieving device configuration.
 */

#ifndef SWISSAIRDRY_CONFIG_H
#define SWISSAIRDRY_CONFIG_H

#include <Arduino.h>
#include <ArduinoJson.h>

#ifdef ESP8266
#include <FS.h>
#else
#include <SPIFFS.h>
#endif

class SwissAirDryConfig {
private:
    const String CONFIG_FILE = "/config.json";
    bool configLoaded = false;
    
    // Save configuration to file
    bool saveConfig() {
        DynamicJsonDocument doc(1024);
        
        // Add all configuration parameters
        doc["device_id"] = deviceId;
        doc["device_name"] = deviceName;
        doc["mqtt_broker"] = mqttBroker;
        doc["mqtt_port"] = mqttPort;
        doc["mqtt_username"] = mqttUsername;
        doc["mqtt_password"] = mqttPassword;
        doc["update_interval"] = updateInterval;
        doc["display_type"] = displayType;
        doc["has_sensors"] = hasSensors;
        doc["ota_enabled"] = otaEnabled;
        
        // Open file for writing
        File configFile = SPIFFS.open(CONFIG_FILE, "w");
        if (!configFile) {
            Serial.println("Failed to open config file for writing");
            return false;
        }
        
        // Serialize JSON to file
        if (serializeJson(doc, configFile) == 0) {
            Serial.println("Failed to write to config file");
            return false;
        }
        
        configFile.close();
        Serial.println("Configuration saved");
        return true;
    }
    
public:
    // Configuration parameters
    String deviceId;
    String deviceName;
    String mqttBroker = "mqtt";
    int mqttPort = 1883;
    String mqttUsername;
    String mqttPassword;
    int updateInterval = 60;    // Update interval in seconds
    String displayType = "64px"; // 64px, 128px, or none
    bool hasSensors = true;
    bool otaEnabled = true;
    
    SwissAirDryConfig() {
        // Default constructor
    }
    
    // Initialize the configuration
    void init() {
        // Default values will be used if no configuration is loaded
    }
    
    // Load configuration from SPIFFS
    bool loadFromSPIFFS() {
        // Check if file exists
        if (!SPIFFS.exists(CONFIG_FILE)) {
            Serial.println("Config file not found, using defaults");
            return false;
        }
        
        // Open file for reading
        File configFile = SPIFFS.open(CONFIG_FILE, "r");
        if (!configFile) {
            Serial.println("Failed to open config file");
            return false;
        }
        
        // Parse JSON
        DynamicJsonDocument doc(1024);
        DeserializationError error = deserializeJson(doc, configFile);
        configFile.close();
        
        if (error) {
            Serial.println("Failed to parse config file: " + String(error.c_str()));
            return false;
        }
        
        // Load configuration parameters
        if (doc.containsKey("device_id")) deviceId = doc["device_id"].as<String>();
        if (doc.containsKey("device_name")) deviceName = doc["device_name"].as<String>();
        if (doc.containsKey("mqtt_broker")) mqttBroker = doc["mqtt_broker"].as<String>();
        if (doc.containsKey("mqtt_port")) mqttPort = doc["mqtt_port"].as<int>();
        if (doc.containsKey("mqtt_username")) mqttUsername = doc["mqtt_username"].as<String>();
        if (doc.containsKey("mqtt_password")) mqttPassword = doc["mqtt_password"].as<String>();
        if (doc.containsKey("update_interval")) updateInterval = doc["update_interval"].as<int>();
        if (doc.containsKey("display_type")) displayType = doc["display_type"].as<String>();
        if (doc.containsKey("has_sensors")) hasSensors = doc["has_sensors"].as<bool>();
        if (doc.containsKey("ota_enabled")) otaEnabled = doc["ota_enabled"].as<bool>();
        
        configLoaded = true;
        Serial.println("Configuration loaded");
        
        return true;
    }
    
    // Save configuration to SPIFFS
    bool saveToSPIFFS() {
        return saveConfig();
    }
    
    // Reset configuration to defaults
    void reset() {
        deviceId = "";
        deviceName = "";
        mqttBroker = "mqtt";
        mqttPort = 1883;
        mqttUsername = "";
        mqttPassword = "";
        updateInterval = 60;
        displayType = "64px";
        hasSensors = true;
        otaEnabled = true;
    }
    
    // Check if configuration is loaded
    bool isConfigLoaded() {
        return configLoaded;
    }
};

#endif // SWISSAIRDRY_CONFIG_H
