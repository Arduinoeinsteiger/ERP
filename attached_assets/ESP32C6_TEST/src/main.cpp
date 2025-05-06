#include <Arduino.h>
#include <Wire.h>
#include <WiFi.h>
#include <ArduinoJson.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <LITTLEFS.h>

// WiFi-Zugangsdaten
const char* ssid = "SwissAirDry";
const char* password = "Test1234";

// MQTT-Konfiguration
const char* mqtt_server = "192.168.4.1";
const int mqtt_port = 1883;

// Webserver erstellen
AsyncWebServer server(80);

// GPIO-Definitionen
#define LED_PIN 2

void setup() {
  // Serielle Kommunikation initialisieren
  Serial.begin(115200);
  delay(1000);
  Serial.println("SwissAirDry ESP32-C6 Test");
  
  // GPIO initialisieren
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  
  // LittleFS initialisieren
  if(!LITTLEFS.begin()){
    Serial.println("Fehler beim Mounten des Dateisystems");
    return;
  }
  
  // WiFi im Access Point Modus starten
  Serial.println("AP-Modus wird gestartet");
  WiFi.softAP(ssid, password);
  
  Serial.print("AP IP-Adresse: ");
  Serial.println(WiFi.softAPIP());
  
  // Webserver-Routen definieren
  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request){
    request->send(LITTLEFS, "/index.html", "text/html");
  });
  
  server.on("/api/status", HTTP_GET, [](AsyncWebServerRequest *request){
    // JSON-Antwort erstellen
    DynamicJsonDocument doc(1024);
    doc["device"] = "ESP32-C6";
    doc["status"] = "running";
    doc["uptime"] = millis() / 1000;
    doc["firmware"] = "1.0.0";
    
    String response;
    serializeJson(doc, response);
    
    request->send(200, "application/json", response);
  });
  
  // Statische Dateien bereitstellen
  server.serveStatic("/", LITTLEFS, "/");
  
  // Webserver starten
  server.begin();
  Serial.println("Webserver gestartet");
  
  // Erfolgreiche Initialisierung signalisieren
  for (int i = 0; i < 5; i++) {
    digitalWrite(LED_PIN, HIGH);
    delay(100);
    digitalWrite(LED_PIN, LOW);
    delay(100);
  }
}

void loop() {
  // LED blinken lassen für Heartbeat
  digitalWrite(LED_PIN, HIGH);
  delay(100);
  digitalWrite(LED_PIN, LOW);
  delay(1900);
  
  // Debug-Ausgabe
  Serial.printf("Uptime: %lu Sekunden\n", millis() / 1000);
}