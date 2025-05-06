/**
 * SwissAirDry OTA Update Handler
 * 
 * This file contains the OTA (Over-The-Air) update functionality
 * for SwissAirDry devices. It supports both Arduino OTA and HTTP OTA updates.
 */

#ifndef SWISSAIRDRY_OTA_H
#define SWISSAIRDRY_OTA_H

#include <Arduino.h>

#ifdef ESP8266
#include <ESP8266WiFi.h>
#include <ESP8266httpUpdate.h>
#include <ESP8266HTTPClient.h>
#else
#include <WiFi.h>
#include <HTTPClient.h>
#include <HTTPUpdate.h>
#endif

#include <ArduinoOTA.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <MD5Builder.h>

// Forward declaration of the MQTT client
extern PubSubClient mqttClient;

class SwissAirDryOTA {
private:
    String deviceId;
    String currentVersion;
    bool updateInProgress = false;
    
    // Update result tracking
    String updateResult;
    String updateErrorMessage;
    
    // Update progress callback
#ifdef ESP8266
    void updateCallback(int progress, int total) {
#else
    void updateCallback(size_t progress, size_t total) {
#endif
        int percent = (progress * 100) / total;
        
        // Publish update progress
        DynamicJsonDocument doc(256);
        doc["progress"] = percent;
        
        String payload;
        serializeJson(doc, payload);
        
        String topic = "swissairdry/" + deviceId + "/ota/progress";
        mqttClient.publish(topic.c_str(), payload.c_str());
        
        Serial.printf("OTA Progress: %d%%\n", percent);
    }
    
    // Calculate MD5 of a URL
    String calculateMD5(String url) {
        HTTPClient http;
        MD5Builder md5;
        md5.begin();
        
        http.begin(url);
        int httpCode = http.GET();
        
        if (httpCode == HTTP_CODE_OK) {
            String payload = http.getString();
            md5.add(payload);
            md5.calculate();
            http.end();
            return md5.toString();
        } else {
            http.end();
            return "";
        }
    }
    
public:
    SwissAirDryOTA() {
        // Default constructor
    }
    
    void init(String id, String version) {
        deviceId = id;
        currentVersion = version;
        
        // Set up Arduino OTA
        ArduinoOTA.setHostname(deviceId.c_str());
        
        ArduinoOTA.onStart([]() {
            String type;
            if (ArduinoOTA.getCommand() == U_FLASH) {
                type = "sketch";
            } else {
                type = "filesystem";
            }
            Serial.println("Start updating " + type);
        });
        
        ArduinoOTA.onEnd([]() {
            Serial.println("\nOTA update complete");
        });
        
        ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
            Serial.printf("OTA Progress: %u%%\r", (progress / (total / 100)));
        });
        
        ArduinoOTA.onError([](ota_error_t error) {
            Serial.printf("OTA Error[%u]: ", error);
            if (error == OTA_AUTH_ERROR) {
                Serial.println("Auth Failed");
            } else if (error == OTA_BEGIN_ERROR) {
                Serial.println("Begin Failed");
            } else if (error == OTA_CONNECT_ERROR) {
                Serial.println("Connect Failed");
            } else if (error == OTA_RECEIVE_ERROR) {
                Serial.println("Receive Failed");
            } else if (error == OTA_END_ERROR) {
                Serial.println("End Failed");
            }
        });
        
        ArduinoOTA.begin();
        
        Serial.println("OTA initialized");
    }
    
    void loop() {
        // Handle Arduino OTA
        ArduinoOTA.handle();
    }
    
    void checkForUpdates() {
        Serial.println("Checking for OTA updates...");
        
        // In a real implementation, this would connect to the server and check for updates
        // Here we'll just log it for demonstration
        Serial.println("No updates available");
    }
    
    bool startUpdate(String url, String expectedMd5, String newVersion) {
        if (updateInProgress) {
            Serial.println("Update already in progress");
            return false;
        }
        
        if (newVersion == currentVersion) {
            Serial.println("Already on the latest version");
            return false;
        }
        
        Serial.println("Starting OTA update");
        Serial.println("URL: " + url);
        Serial.println("Expected MD5: " + expectedMd5);
        Serial.println("New Version: " + newVersion);
        
        updateInProgress = true;
        updateResult = "";
        updateErrorMessage = "";
        
        // Set up callbacks
#ifdef ESP8266
        ESPhttpUpdate.onProgress([this](int progress, int total) {
            this->updateCallback(progress, total);
        });
        
        // Start update
        t_httpUpdate_return ret = ESPhttpUpdate.update(url);
#else
        httpUpdate.onProgress([this](size_t progress, size_t total) {
            this->updateCallback(progress, total);
        });
        
        // Start update
        HTTPUpdateResult ret = httpUpdate.update(url);
#endif
        
        updateInProgress = false;
        
        // Process update result
        switch (ret) {
            case HTTP_UPDATE_FAILED:
#ifdef ESP8266
                updateResult = "failed";
                updateErrorMessage = ESPhttpUpdate.getLastErrorString();
                Serial.println("HTTP_UPDATE_FAILED Error: " + updateErrorMessage);
#else
                updateResult = "failed";
                updateErrorMessage = httpUpdate.getLastErrorString();
                Serial.println("HTTP_UPDATE_FAILED Error: " + updateErrorMessage);
#endif
                
                // Publish update status
                {
                    DynamicJsonDocument doc(512);
                    doc["status"] = "failed";
                    doc["message"] = updateErrorMessage;
                    doc["version"] = newVersion;
                    
                    String payload;
                    serializeJson(doc, payload);
                    
                    String topic = "swissairdry/" + deviceId + "/ota/status";
                    mqttClient.publish(topic.c_str(), payload.c_str());
                }
                return false;
                
            case HTTP_UPDATE_NO_UPDATES:
                updateResult = "no_updates";
                Serial.println("HTTP_UPDATE_NO_UPDATES");
                
                // Publish update status
                {
                    DynamicJsonDocument doc(256);
                    doc["status"] = "no_updates";
                    doc["message"] = "No updates available";
                    doc["version"] = currentVersion;
                    
                    String payload;
                    serializeJson(doc, payload);
                    
                    String topic = "swissairdry/" + deviceId + "/ota/status";
                    mqttClient.publish(topic.c_str(), payload.c_str());
                }
                return false;
                
            case HTTP_UPDATE_OK:
                updateResult = "success";
                Serial.println("HTTP_UPDATE_OK");
                
                // Publish update status
                {
                    DynamicJsonDocument doc(256);
                    doc["status"] = "completed";
                    doc["message"] = "Update successful";
                    doc["version"] = newVersion;
                    
                    String payload;
                    serializeJson(doc, payload);
                    
                    String topic = "swissairdry/" + deviceId + "/ota/status";
                    mqttClient.publish(topic.c_str(), payload.c_str());
                }
                
                // Wait for message to be sent before restarting
                delay(1000);
                return true;
        }
        
        return false;
    }
    
    bool isUpdateInProgress() {
        return updateInProgress;
    }
    
    String getUpdateResult() {
        return updateResult;
    }
    
    String getUpdateErrorMessage() {
        return updateErrorMessage;
    }
};

#endif // SWISSAIRDRY_OTA_H
