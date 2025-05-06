NTROL:
        // Relais umschalten
        relayState = !relayState;
        digitalWrite(RELAY_PIN, relayState ? HIGH : LOW);
        Serial.print("Relais: ");
        Serial.println(relayState ? "AN" : "AUS");
        break;
        
      case BLE_SCAN:
        // Nichts tun, da der Scan bereits läuft
        break;
        
      case SCAN_RESULTS:
        // Beim Drücken von SELECT neuen Scan starten
        startBLEScan();
        break;
        
      case PRESSURE_DISPLAY:
        // Zurück zum Menü
        currentState = MAIN_MENU;
        break;
        
      case API_STATUS:
        // API-Verbindung testen
        checkApiConnection();
        // API-Status neu anzeigen
        displayApiStatus();
        break;
        
      case RESTART_CONFIRM:
        // Gerät neustarten
        display.clearDisplay();
        display.setTextSize(1);
        display.setCursor(0, 0);
        display.println("Neustart...");
        display.display();
        delay(1000);
        ESP.restart();
        break;
        
      case COUNTDOWN_SCREEN:
        // Countdown abbrechen
        currentState = MAIN_MENU;
        break;
    }
    
    Serial.println("Taste SELECT gedrückt");
  } 
  else if (!currentSelectState && buttonSelectState) {
    buttonSelectState = false;
  }
}

// Ausgewählte Menüaktion ausführen
void executeMenuAction() {
  switch (menuPosition) {
    case 0: // Zurück zum Start
      currentState = START_SCREEN;
      inMenuMode = false;
      if (WiFi.status() == WL_CONNECTED && displayAvailable) {
        displayLoginInfo();
      }
      break;
      
    case 1: // Relais schalten
      currentState = RELAY_CONTROL;
      inMenuMode = false;
      break;
      
    case 2: // WLAN-Info
      currentState = WLAN_INFO;
      inMenuMode = false;
      break;
      
    case 3: // System-Info
      currentState = SYSTEM_INFO;
      inMenuMode = false;
      break;
      
    case 4: // API-Status
      currentState = API_STATUS;
      inMenuMode = false;
      // API-Status anzeigen
      displayApiStatus();
      break;
      
    case 5: // Drucksensor anzeigen
      currentState = PRESSURE_DISPLAY;
      inMenuMode = false;
      // Sofort den Drucksensor anzeigen
      displayPressureScreen();
      break;
      
    case 6: // BLE-Scan
      currentState = BLE_SCAN;
      inMenuMode = false;
      // BLE-Scan starten
      startBLEScan();
      break;
      
    case 7: // Neustart
      currentState = RESTART_CONFIRM;
      inMenuMode = false;
      break;
  }
}

// WiFi-Scan starten (als BLE-Simulation)
void startBLEScan() {
  Serial.println("Starte WiFi-Scan als BLE-Simulation...");
  
  // Display-Zustand auf BLE-Scan setzen
  isScanning = true;
  lastScanTime = millis();
  
  // WLAN-Scan starten
  int networksFound = WiFi.scanNetworks(false, true);
  
  // Gefundene Geräte löschen
  foundDevices.clear();
  
  if (networksFound > 0) {
    Serial.printf("Scan abgeschlossen, %d Netzwerke gefunden\n", networksFound);
    
    // Maximal 20 Netzwerke speichern
    for (int i = 0; i < min(networksFound, 20); i++) {
      BLEDevice device;
      device.name = WiFi.SSID(i);
      device.address = WiFi.BSSIDstr(i);
      device.rssi = WiFi.RSSI(i);
      device.isBeacon = (device.name.indexOf("SwissAirDry") >= 0); // Markiere SwissAirDry-Geräte
      
      foundDevices.push_back(device);
      
      Serial.printf("  %2d: %s, RSSI: %d dBm, MAC: %s %s\n", 
                    i + 1, 
                    device.name.c_str(), 
                    device.rssi, 
                    device.address.c_str(),
                    device.isBeacon ? "(SwissAirDry!)" : "");
    }
    
    // Sortiere nach Signalstärke (besseres Signal zuerst)
    std::sort(foundDevices.begin(), foundDevices.end(), 
              [](const BLEDevice& a, const BLEDevice& b) { 
                return a.rssi > b.rssi; 
              });
    
    // Zum Ergebnisbildschirm wechseln
    currentState = SCAN_RESULTS;
    scanIndex = 0;
  } else {
    Serial.println("Keine Netzwerke gefunden");
  }
  
  isScanning = false;
}

// API-Funktionen für die Kommunikation mit api.vgnc.org

// Prüft die Verbindung zur API
void checkApiConnection() {
  // Prüfen, ob WLAN verbunden ist
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Keine WLAN-Verbindung für API-Check");
    apiConnected = false;
    return;
  }

  Serial.println("Prüfe API-Verbindung zu " + apiEndpoint);
  
  WiFiClient client;
  HTTPClient http;
  
  String url = "http://" + apiEndpoint;
  
  http.begin(client, url);
  
  // Status der letzten Prüfung speichern
  lastApiCheck = millis();
  
  // Anfrage senden und Antwortcode prüfen
  apiResponseCode = http.GET();
  
  if (apiResponseCode > 0) {
    Serial.print("API-Antwort: ");
    Serial.println(apiResponseCode);
    
    if (apiResponseCode == HTTP_CODE_OK) {
      String payload = http.getString();
      Serial.println("API-Antwort: " + payload);
      apiConnected = true;
    } else {
      apiConnected = false;
    }
  } else {
    Serial.print("API-Anfrage fehlgeschlagen: ");
    Serial.println(http.errorToString(apiResponseCode));
    apiConnected = false;
  }
  
  http.end();
}

// Aktualisiert die DeviceData-Struktur mit aktuellen Daten
void updateDeviceData() {
  deviceData.deviceId = hostname;
  deviceData.pressure = pressure;
  deviceData.relayState = relayState;
  deviceData.rssi = WiFi.RSSI();
  deviceData.uptime = millis() / 1000;
}

// Sendet die aktuellen Gerätedaten an die API
bool sendDataToApi() {
  // Prüfen, ob WLAN verbunden ist
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Keine WLAN-Verbindung, API-Update übersprungen");
    return false;
  }

  // Gerätedaten aktualisieren
  updateDeviceData();

  // HTTPS-Client einrichten
  WiFiClientSecure client;
  client.setInsecure();  // SSL-Zertifikatsvalidierung deaktivieren (für einfacheren Test)

  // HTTP-Client für die Anfrage
  HTTPClient https;
  
  // URL für API-Endpunkt zusammenbauen
  String url = "https://";
  url += apiEndpoint;
  if (apiPort != 443) {
    url += ":" + String(apiPort);
  }
  url += apiBasePath + "/devices/" + hostname + "/data";

  Serial.println("Verbinde mit API: " + url);

  // Anfrage starten
  if (!https.begin(client, url)) {
    Serial.println("API-Verbindung fehlgeschlagen");
    return false;
  }

  // JSON-Daten erstellen
  StaticJsonDocument<200> doc;
  doc["pressure"] = deviceData.pressure;
  doc["relay_state"] = deviceData.relayState;
  doc["rssi"] = deviceData.rssi;
  doc["uptime"] = deviceData.uptime;

  // JSON in String umwandeln
  String jsonData;
  serializeJson(doc, jsonData);

  // Header setzen
  https.addHeader("Content-Type", "application/json");
  https.addHeader("X-Device-ID", hostname);

  // Anfrage senden
  int httpResponseCode = https.POST(jsonData);

  // Antwort verarbeiten
  if (httpResponseCode > 0) {
    String response = https.getString();
    Serial.printf("API-Antwort: %d - %s\n", httpResponseCode, response.c_str());
    return true;
  } else {
    Serial.printf("API-Fehler: %d\n", httpResponseCode);
    return false;
  }

  // Verbindung schließen
  https.end();
}

// Zeigt den API-Status und die letzten übertragenen Daten an
void displayApiStatus() {
  if (!displayAvailable) return;
  
  display.clearDisplay();
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.println("API Status");
  display.drawLine(0, 10, 128, 10, SSD1306_WHITE);
  
  display.setCursor(0, 13);
  display.print("Server: ");
  display.println(apiEndpoint);
  
  display.print("Gerät: ");
  display.println(hostname);
  
  display.print("Letztes Update: ");
  if (lastApiUpdate > 0) {
    long secondsAgo = (millis() - lastApiUpdate) / 1000;
    display.print(secondsAgo);
    display.println(" s");
    
    display.print("Druck: ");
    display.print(deviceData.pressure);
    display.println(" hPa");
    
    display.print("Relais: ");
    display.println(deviceData.relayState ? "AN" : "AUS");
  } else {
    display.println("Noch keins");
  }
  
  display.display();
}

void loop() {
  // OTA-Anfragen bearbeiten
  ArduinoOTA.handle();
  
  // Webserver verarbeiten
  server.handleClient();
  
  // API-Synchronisierung (alle 30 Sekunden)
  if (millis() - lastApiUpdate > API_UPDATE_INTERVAL) {
    if (sendDataToApi()) {
      lastApiUpdate = millis();
      Serial.println("API-Update erfolgreich");
    } else {
      Serial.println("API-Update fehlgeschlagen");
    }
  }
  
  // Tasten überwachen
  handleButtons();
  
  // Drucksensor regelmäßig auslesen (alle 5 Sekunden)
  static unsigned long lastPressureRead = 0;
  if (millis() - lastPressureRead > 5000) {
    if (currentState == PRESSURE_DISPLAY) {
      // Direkt im Display anzeigen, wenn wir auf dem Drucksensor-Bildschirm sind
      displayPressureScreen();
    } else {
      // Ansonsten im Hintergrund messen für den gleitenden Durchschnitt
      readPressureSensor();
    }
    lastPressureRead = millis();
  }
  
  // Display aktualisieren
  updateDisplay();
  
  // WLAN-Verbindung prüfen und ggf. erneut verbinden
  if (WiFi.status() != WL_CONNECTED) {
    static unsigned long lastReconnectAttempt = 0;
    unsigned long currentMillis = millis();
    
    if (currentMillis - lastReconnectAttempt > 60000) {  // Alle 60 Sekunden versuchen
      lastReconnectAttempt = currentMillis;
      Serial.println("WLAN-Verbindung verloren. Versuche neu zu verbinden...");
      WiFi.disconnect();
      delay(1000);
      WiFi.begin(ssid, password);
      
      // Bei erfolgreicher Verbindung QR anzeigen, wenn nicht im Menü
      if (WiFi.status() == WL_CONNECTED && displayAvailable && currentState == START_SCREEN) {
        displayLoginInfo();
      }
    }
  }
  
  // Heartbeat-LED
  static unsigned long lastBlink = 0;
  if (millis() - lastBlink > 3000) {  // Alle 3 Sekunden
    digitalWrite(LED_PIN, LED_ON);
    delay(50);
    digitalWrite(LED_PIN, LED_OFF);
    lastBlink = millis();
  }
  
  // Watchdog füttern (wichtig für ESP8266)
  yield();
}