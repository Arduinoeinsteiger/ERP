/**
 * SwissAirDry MQTT Client
 * 
 * This file contains the MQTT client implementation for SwissAirDry devices.
 * It provides a unified interface for MQTT communication.
 */

#ifndef SWISSAIRDRY_MQTT_CLIENT_H
#define SWISSAIRDRY_MQTT_CLIENT_H

#include <Arduino.h>

#ifdef ESP8266
#include <ESP8266WiFi.h>
#else
#include <WiFi.h>
#endif

#include <PubSubClient.h>

// Define callback function type
typedef void (*MqttMessageCallback)(char* topic, byte* payload, unsigned int length);

class SwissAirDryMQTT {
private:
    WiFiClient wifiClient;
    PubSubClient mqttClient;
    
    String deviceId;
    String mqttBroker;
    int mqttPort;
    String mqttUsername;
    String mqttPassword;
    
    MqttMessageCallback messageCallback;
    
    // Last will message settings
    String willTopic;
    String willMessage;
    
    // Reconnect timer
    unsigned long lastReconnectAttempt = 0;
    
    // Connection status callback
    static void defaultCallback(char* topic, byte* payload, unsigned int length) {
        // Default empty callback
    }
    
    // Reconnect to MQTT broker
    boolean reconnect() {
        Serial.print("Attempting MQTT connection...");
        
        // Create client ID based on device ID
        String clientId = "SwissAirDry-" + deviceId;
        
        // Attempt to connect with last will message
        boolean connected = false;
        if (mqttUsername.length() > 0) {
            connected = mqttClient.connect(
                clientId.c_str(),
                mqttUsername.c_str(),
                mqttPassword.c_str(),
                willTopic.c_str(),
                0,
                true,
                willMessage.c_str()
            );
        } else {
            connected = mqttClient.connect(
                clientId.c_str(),
                willTopic.c_str(),
                0,
                true,
                willMessage.c_str()
            );
        }
        
        if (connected) {
            Serial.println("connected");
            
            // Once connected, resubscribe to topics
            for (auto& topic : subscribedTopics) {
                mqttClient.subscribe(topic.c_str());
                Serial.println("Subscribed to: " + topic);
            }
            
            // Publish online status
            String statusTopic = "swissairdry/" + deviceId + "/status";
            mqttClient.publish(statusTopic.c_str(), "{\"online\":true}", true);
        } else {
            Serial.print("failed, rc=");
            Serial.print(mqttClient.state());
            Serial.println(" try again in 5 seconds");
        }
        
        return connected;
    }
    
    // Store subscribed topics for resubscribing after reconnect
    std::vector<String> subscribedTopics;
    
public:
    SwissAirDryMQTT() : mqttClient(wifiClient) {
        // Default constructor
    }
    
    void init(
        String broker, 
        int port, 
        String username, 
        String password,
        String device_id,
        MqttMessageCallback callback = defaultCallback
    ) {
        mqttBroker = broker;
        mqttPort = port;
        mqttUsername = username;
        mqttPassword = password;
        deviceId = device_id;
        messageCallback = callback;
        
        // Configure last will message
        willTopic = "swissairdry/" + deviceId + "/status";
        willMessage = "{\"online\":false}";
        
        // Set server and callback
        mqttClient.setServer(mqttBroker.c_str(), mqttPort);
        mqttClient.setCallback(messageCallback);
        
        // Set buffer size for larger messages
        mqttClient.setBufferSize(1024);
        
        Serial.println("MQTT client initialized");
        Serial.println("  Broker: " + mqttBroker);
        Serial.println("  Port: " + String(mqttPort));
        Serial.println("  Device ID: " + deviceId);
    }
    
    void loop() {
        // Check connection status
        if (!mqttClient.connected()) {
            // Attempt to reconnect every 5 seconds
            unsigned long now = millis();
            if (now - lastReconnectAttempt > 5000) {
                lastReconnectAttempt = now;
                if (reconnect()) {
                    lastReconnectAttempt = 0;
                }
            }
        } else {
            // Client connected, process messages
            mqttClient.loop();
        }
    }
    
    boolean isConnected() {
        return mqttClient.connected();
    }
    
    boolean publish(String topic, const char* payload, boolean retain = false) {
        if (!mqttClient.connected()) {
            Serial.println("Cannot publish: MQTT client not connected");
            return false;
        }
        
        return mqttClient.publish(topic.c_str(), payload, retain);
    }
    
    boolean subscribe(String topic) {
        if (!mqttClient.connected()) {
            Serial.println("Cannot subscribe: MQTT client not connected");
            // Store topic for later subscription when connected
            subscribedTopics.push_back(topic);
            return false;
        }
        
        // Store topic for resubscription after reconnect
        if (std::find(subscribedTopics.begin(), subscribedTopics.end(), topic) == subscribedTopics.end()) {
            subscribedTopics.push_back(topic);
        }
        
        return mqttClient.subscribe(topic.c_str());
    }
    
    boolean unsubscribe(String topic) {
        // Remove from subscribed topics list
        auto it = std::find(subscribedTopics.begin(), subscribedTopics.end(), topic);
        if (it != subscribedTopics.end()) {
            subscribedTopics.erase(it);
        }
        
        if (!mqttClient.connected()) {
            Serial.println("Cannot unsubscribe: MQTT client not connected");
            return false;
        }
        
        return mqttClient.unsubscribe(topic.c_str());
    }
};

#endif // SWISSAIRDRY_MQTT_CLIENT_H
