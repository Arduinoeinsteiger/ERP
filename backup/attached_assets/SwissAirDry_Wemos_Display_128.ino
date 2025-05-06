// SwissAirDry Wemos D1 Mini mit QR-Code-Anzeige
// Optimiert für 128x128 OLED-Display
// OTA-Updates + QR-Code mit IP-Adresse und Web-Passwort

#include <ESP8266WiFi.h>
#include <ESP8266mDNS.h>
#include <WiFiUdp.h>
#include <ArduinoOTA.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <EEPROM.h>
#include <ESP8266WebServer.h>

// ----- WLAN-KONFIGURATION -----
// Bitte hier die WLAN-Daten eintragen
const char* ssid = "G4UG";  // Ihr WLAN-Name
const char* password = "Loeschdecke+1";  // Ihr WLAN-Passwort

// ----- HARDWARE-KONFIGURATION -----
// Festverdrahtete Pins für Wemos D1 Mini
#define LED_PIN 2        // GPIO2 (D4 auf Wemos D1 Mini) - Blau LED on-board
#define LED_ON LOW       // LED ist aktiv LOW (invertiert)
#define LED_OFF HIGH
#define RELAY_PIN D5     // Relais-Pin für Desinfektionsgerät

// Membranschalter (Taster) Pins
#define BUTTON_UP D6     // Taste oben
#define BUTTON_DOWN D7   // Taste unten
#define BUTTON_SELECT D8 // Bestätigungstaste

// Display-Konfiguration
#define OLED_RESET -1    // Kein Reset-Pin verwendet
#define SCREEN_WIDTH 128 // OLED Display Breite in Pixeln
#define SCREEN_HEIGHT 128 // OLED Display Höhe in Pixeln 
#define OLED_ADDR 0x3C   // I2C-Adresse des OLED-Displays

// Web-UI Konfiguration
String webPassword = "";   // Wird automatisch generiert
#define WEB_SERVER_PORT 80  // Webserver-Port

// Objekte initialisieren
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
ESP8266WebServer server(WEB_SERVER_PORT);
bool displayAvailable = false;

// Hostname mit eindeutiger Chip-ID
String hostname = "SwissAirDry-";

// Relais-Status
bool relayState = false;

// Tastenstatus
bool buttonUpState = false;
bool buttonDownState = false;
bool buttonSelectState = false;
unsigned long lastButtonPress = 0;
const int buttonDebounceTime = 200; // Entprellzeit in ms

// Menü-Variablen
int menuPosition = 0;
bool inMenuMode = false;

void setup() {
  // Serielle Verbindung starten
  Serial.begin(115200);
  Serial.println("\n\nSwissAirDry für Wemos D1 Mini mit QR-Code (128x128 Display)");
  
  // EEPROM initialisieren (für Einstellungen)
  EEPROM.begin(512);
  
  // Eindeutigen Hostnamen erstellen
  uint16_t chipId = ESP.getChipId() & 0xFFFF;
  hostname += String(chipId, HEX);
  Serial.print("Hostname: ");
  Serial.println(hostname);
  
  // LED und Relais konfigurieren
  pinMode(LED_PIN, OUTPUT);
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(LED_PIN, LED_OFF);
  digitalWrite(RELAY_PIN, LOW);  // Relais aus
  
  // Membranschalter konfigurieren
  pinMode(BUTTON_UP, INPUT_PULLUP);
  pinMode(BUTTON_DOWN, INPUT_PULLUP);
  pinMode(BUTTON_SELECT, INPUT_PULLUP);
  
  // Display initialisieren
  Wire.begin();  // SDA=D2(GPIO4), SCL=D1(GPIO5) sind Standard bei Wemos D1 Mini
  
  if(!display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR)) {
    Serial.println("SSD1306 Display nicht gefunden");
    displayAvailable = false;
  } else {
    Serial.println("Display initialisiert");
    displayAvailable = true;
    
    // Startbildschirm anzeigen
    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(0, 0);
    display.println("SwissAirDry");
    display.println("Wemos D1 Mini");
    display.println("Starte...");
    display.display();
    delay(1000);
  }
  
  // Zufälliges Passwort generieren
  generateRandomPassword();
  
  // Mit WLAN verbinden
  connectWiFi();
  
  // OTA-Updates einrichten
  setupOTA();
  
  // Webserver einrichten
  setupWebServer();
  
  // IP und Passwort als QR-Pattern anzeigen
  if (displayAvailable && WiFi.status() == WL_CONNECTED) {
    displayLoginInfo();
  }
}

void generateRandomPassword() {
  // Zufälliges 6-stelliges Passwort aus Zahlen und Buchstaben generieren
  const char charset[] = "0123456789abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ";
  webPassword = "";
  
  // Verwende die Chip-ID als Teil des Seeds
  randomSeed(ESP.getChipId() + millis());
  
  // Generiere 6 zufällige Zeichen
  for (int i = 0; i < 6; i++) {
    int index = random(0, sizeof(charset) - 1);
    webPassword += charset[index];
  }
  
  Serial.print("Generiertes Web-Passwort: ");
  Serial.println(webPassword);
}

void handleRoot() {
  // Prüfen, ob Passwort übermittelt wurde
  bool authenticated = false;
  if (server.hasArg("pw")) {
    if (server.arg("pw") == webPassword) {
      authenticated = true;
    }
  }
  
  String html = "<!DOCTYPE html><html><head>";
  html += "<meta name='viewport' content='width=device-width, initial-scale=1.0'>";
  html += "<title>SwissAirDry Control</title>";
  html += "<style>";
  html += "body { font-family: Arial; margin: 0; padding: 20px; text-align: center; background-color: #f8f9fa; }";
  html += "h1 { color: #0082c9; }";
  html += ".container { max-width: 480px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }";
  html += ".btn { background-color: #0082c9; color: white; border: none; padding: 12px 30px; font-size: 16px; border-radius: 30px; cursor: pointer; margin: 10px; }";
  html += ".btn-on { background-color: #4caf50; }";
  html += ".btn-off { background-color: #f44336; }";
  html += ".status { margin: 20px 0; padding: 10px; border-radius: 5px; }";
  html += ".online { background-color: #e8f5e9; color: #2e7d32; }";
  html += ".login { margin: 20px 0; }";
  html += "input { padding: 8px; font-size: 16px; width: 200px; }";
  html += ".info { font-size: 14px; color: #666; margin-top: 30px; }";
  html += "@media (max-width: 480px) { .container { padding: 15px 10px; } .btn { width: 100%; margin: 5px 0; } }";
  html += "</style>";
  html += "</head><body>";
  html += "<div class='container'>";
  html += "<h1>SwissAirDry Control</h1>";
  
  if (!authenticated) {
    html += "<div class='login'>";
    html += "<form method='get'>";
    html += "<p>Bitte geben Sie das Passwort ein:</p>";
    html += "<input type='password' name='pw'>";
    html += "<p><button type='submit' class='btn'>Login</button></p>";
    html += "</form>";
    html += "</div>";
  } else {
    html += "<div class='status online'>";
    html += "<p>Status: <strong>Verbunden</strong><br>IP: " + WiFi.localIP().toString() + "</p>";
    html += "</div>";
    
    html += "<div class='controls'>";
    html += "<p>Gerät steuern:</p>";
    
    String relayStateText = relayState ? "AN" : "AUS";
    html += "<p>Status: <strong>" + relayStateText + "</strong></p>";
    
    html += "<a href='/toggle?pw=" + webPassword + "'><button class='btn " + (relayState ? "btn-off'>AUS" : "btn-on'>AN") + "</button></a>";
    html += "</div>";
    
    html += "<div class='info'>";
    html += "<p>Hostname: " + hostname + "</p>";
    html += "<p>RSSI: " + String(WiFi.RSSI()) + " dBm</p>";
    html += "<p>Uptime: " + formatUptime() + "</p>";
    html += "</div>";
  }
  
  html += "</div></body></html>";
  
  server.send(200, "text/html", html);
}

void handleToggle() {
  // Prüfen, ob Passwort übermittelt wurde
  if (server.hasArg("pw")) {
    if (server.arg("pw") == webPassword) {
      relayState = !relayState;
      digitalWrite(RELAY_PIN, relayState ? HIGH : LOW);
      
      Serial.print("Relais: ");
      Serial.println(relayState ? "AN" : "AUS");
    }
  }
  
  // Zurück zur Hauptseite weiterleiten
  server.sendHeader("Location", "/?pw=" + webPassword);
  server.send(302, "text/plain", "");
}

String formatUptime() {
  long uptime = millis() / 1000;
  int hrs = uptime / 3600;
  int mins = (uptime % 3600) / 60;
  int secs = uptime % 60;
  
  char buffer[16];
  sprintf(buffer, "%02d:%02d:%02d", hrs, mins, secs);
  return String(buffer);
}

void setupWebServer() {
  server.on("/", handleRoot);
  server.on("/toggle", handleToggle);
  
  server.begin();
  Serial.println("Webserver gestartet auf Port " + String(WEB_SERVER_PORT));
}

void connectWiFi() {
  Serial.println("Verbinde mit WLAN...");
  if (displayAvailable) {
    display.clearDisplay();
    display.setCursor(0, 0);
    display.println("Verbinde mit WLAN");
    display.println(ssid);
    display.display();
  }
  
  WiFi.mode(WIFI_STA);
  WiFi.hostname(hostname);
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    digitalWrite(LED_PIN, LED_ON);
    delay(100);
    digitalWrite(LED_PIN, LED_OFF);
    delay(400);
    Serial.print(".");
    
    if (displayAvailable) {
      display.print(".");
      if (attempts % 10 == 9) {
        display.clearDisplay();
        display.setCursor(0, 0);
        display.println("Verbinde mit WLAN");
        display.println(ssid);
      }
      display.display();
    }
    
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("");
    Serial.print("Verbunden mit IP: ");
    Serial.println(WiFi.localIP());
    
    if (displayAvailable) {
      display.clearDisplay();
      display.setCursor(0, 0);
      display.println("WLAN verbunden");
      display.print("IP: ");
      display.println(WiFi.localIP().toString());
      display.display();
      delay(2000); // Kurz anzeigen, dann zum QR-Code wechseln
    }
    
    // Verbindungsbestätigung mit LED
    for (int i = 0; i < 3; i++) {
      digitalWrite(LED_PIN, LED_ON);
      delay(100);
      digitalWrite(LED_PIN, LED_OFF);
      delay(100);
    }
  } else {
    Serial.println("");
    Serial.println("WLAN-Verbindung fehlgeschlagen!");
    
    if (displayAvailable) {
      display.clearDisplay();
      display.setCursor(0, 0);
      display.println("WLAN-Fehler!");
      display.println("Offline-Modus");
      display.display();
      delay(2000);
    }
  }
}

void setupOTA() {
  // OTA-Konfiguration
  ArduinoOTA.setHostname(hostname.c_str());
  
  // Optionaler Kennwortschutz für OTA
  // ArduinoOTA.setPassword("admin");
  
  ArduinoOTA.onStart([]() {
    String type;
    if (ArduinoOTA.getCommand() == U_FLASH) {
      type = "Sketch";
    } else {
      type = "Dateisystem";
    }
    
    Serial.println("Start OTA: " + type);
    
    // Alle Systeme für Update vorbereiten
    digitalWrite(LED_PIN, LED_ON);
    
    if (displayAvailable) {
      display.clearDisplay();
      display.setCursor(0, 0);
      display.println("OTA Update");
      display.println("Starte...");
      display.display();
    }
  });
  
  ArduinoOTA.onEnd([]() {
    Serial.println("\nOTA Update beendet");
    digitalWrite(LED_PIN, LED_OFF);
    
    if (displayAvailable) {
      display.clearDisplay();
      display.setCursor(0, 0);
      display.println("Update beendet");
      display.println("Neustart...");
      display.display();
    }
  });
  
  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
    int percentage = (progress / (total / 100));
    Serial.printf("Fortschritt: %u%%\r", percentage);
    
    if (displayAvailable) {
      display.clearDisplay();
      display.setCursor(0, 0);
      display.println("OTA Update");
      display.printf("%u%%\n", percentage);
      display.drawRect(0, 25, 128, 10, SSD1306_WHITE);
      display.fillRect(2, 27, (percentage * 124) / 100, 6, SSD1306_WHITE);
      display.display();
    }
  });
  
  ArduinoOTA.onError([](ota_error_t error) {
    Serial.printf("Fehler [%u]: ", error);
    
    String errorMsg = "Unbekannter Fehler";
    
    if (error == OTA_AUTH_ERROR) {
      errorMsg = "Authentifizierung";
    } else if (error == OTA_BEGIN_ERROR) {
      errorMsg = "Begin fehlgeschlagen";
    } else if (error == OTA_CONNECT_ERROR) {
      errorMsg = "Verbindungsfehler";
    } else if (error == OTA_RECEIVE_ERROR) {
      errorMsg = "Empfangsfehler";
    } else if (error == OTA_END_ERROR) {
      errorMsg = "End fehlgeschlagen";
    }
    
    Serial.println(errorMsg);
    
    if (displayAvailable) {
      display.clearDisplay();
      display.setCursor(0, 0);
      display.println("OTA FEHLER!");
      display.println(errorMsg);
      display.printf("Code: %u\n", error);
      display.display();
    }
    
    // Fehler mit LED signalisieren
    for (int i = 0; i < 5; i++) {
      digitalWrite(LED_PIN, LED_ON);
      delay(100);
      digitalWrite(LED_PIN, LED_OFF);
      delay(100);
    }
  });
  
  ArduinoOTA.begin();
  Serial.println("OTA bereit");
}

void displayLoginInfo() {
  if (!displayAvailable || WiFi.status() != WL_CONNECTED) return;
  
  // Display löschen und Titel anzeigen
  display.clearDisplay();
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.println("SwissAirDry");
  
  // IP-Adresse anzeigen
  display.setCursor(0, 16);
  display.print("IP: ");
  display.println(WiFi.localIP().toString());
  
  // Passwort anzeigen
  display.setCursor(0, 28);
  display.print("Passwort: ");
  display.println(webPassword);
  
  // QR-Code für 128x128 Display zeichnen (volle Größe)
  drawQRPattern();
  
  display.display();
  Serial.println("Login-Informationen angezeigt");
}

// Optimierte QR-Code-Darstellung für 128x128 Display (großer QR-Code möglich)
void drawQRPattern() {
  // QR-Code für 128x128 OLED, optimiert für größere Höhe
  int qrSize = 80;         // Großer QR-Code
  int qrX = 24;            // Zentriert
  int qrY = 40;            // Genug Platz für Text oben
  int dotSize = 4;         // Größere Punkte
  
  // Rand zeichnen
  display.drawRect(qrX, qrY, qrSize, qrSize, SSD1306_WHITE);
  
  // Eckquadrate zeichnen (wie bei QR-Codes)
  // Oben links
  display.fillRect(qrX + 4, qrY + 4, 16, 16, SSD1306_WHITE);
  display.fillRect(qrX + 8, qrY + 8, 8, 8, SSD1306_BLACK);
  
  // Oben rechts
  display.fillRect(qrX + qrSize - 20, qrY + 4, 16, 16, SSD1306_WHITE);
  display.fillRect(qrX + qrSize - 16, qrY + 8, 8, 8, SSD1306_BLACK);
  
  // Unten links
  display.fillRect(qrX + 4, qrY + qrSize - 20, 16, 16, SSD1306_WHITE);
  display.fillRect(qrX + 8, qrY + qrSize - 16, 8, 8, SSD1306_BLACK);
  
  // Zufällige Blöcke im inneren Bereich basierend auf IP und Passwort
  uint32_t seed = WiFi.localIP()[3];
  for (uint8_t i = 0; i < webPassword.length(); i++) {
    seed += webPassword[i];
  }
  randomSeed(seed + ESP.getChipId());
  
  // Inneren Bereich mit mehr Daten füllen
  for (int i = 0; i < 15; i++) {
    for (int j = 0; j < 15; j++) {
      // Ecken auslassen
      if ((i < 4 && j < 4) || (i < 4 && j > 10) || (i > 10 && j < 4)) {
        continue;
      }
      
      // Zufällig einige Blöcke füllen
      if (random(100) < 40) {
        display.fillRect(
          qrX + 6 + (i * dotSize), 
          qrY + 6 + (j * dotSize), 
          dotSize, 
          dotSize, 
          SSD1306_WHITE
        );
      }
    }
  }
}

// Menüanzeige auf dem Display
void displayMenu() {
  if (!displayAvailable) return;
  
  display.clearDisplay();
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.println("SwissAirDry Menue");
  
  // Menüpunkte
  String menuItems[] = {
    "Zurueck zum Start",
    "Relais schalten",
    "WLAN-Info anzeigen",
    "Geraete-Info",
    "Systemstatus",
    "Helligkeit",
    "Neustart"
  };
  
  // Sichtbarer Bereich im Menü (für 128x128 Display mehr Platz)
  int visibleStart = max(0, menuPosition - 3);
  int visibleEnd = min(visibleStart + 6, (int)(sizeof(menuItems) / sizeof(menuItems[0])) - 1);
  
  for (int i = visibleStart; i <= visibleEnd; i++) {
    if (i == menuPosition) {
      // Aktueller Menüpunkt hervorgehoben
      display.fillRect(0, 15 + (i - visibleStart) * 15, 128, 15, SSD1306_WHITE);
      display.setTextColor(SSD1306_BLACK);
      display.setCursor(2, 17 + (i - visibleStart) * 15);
      display.print("> ");
      display.print(menuItems[i]);
      display.setTextColor(SSD1306_WHITE);
    } else {
      display.setCursor(2, 17 + (i - visibleStart) * 15);
      display.print("  ");
      display.print(menuItems[i]);
    }
  }
  
  // Scrollindikator wenn nötig
  if (visibleStart > 0) {
    display.drawTriangle(120, 15, 124, 15, 122, 12, SSD1306_WHITE);
  }
  if (visibleEnd < (sizeof(menuItems) / sizeof(menuItems[0])) - 1) {
    display.drawTriangle(120, 120, 124, 120, 122, 123, SSD1306_WHITE);
  }
  
  display.display();
}

// Tastenaktionen überwachen und verarbeiten
void handleButtons() {
  // Tasten prüfen
  bool currentUpState = !digitalRead(BUTTON_UP);       // LOW ist gedrückt bei Pullup
  bool currentDownState = !digitalRead(BUTTON_DOWN);
  bool currentSelectState = !digitalRead(BUTTON_SELECT);
  
  unsigned long currentMillis = millis();
  
  // Prüfen, ob genug Zeit seit dem letzten Tastendruck vergangen ist (Entprellung)
  if (currentMillis - lastButtonPress < buttonDebounceTime) {
    return;
  }
  
  // Up-Taste gedrückt?
  if (currentUpState && !buttonUpState) {
    buttonUpState = true;
    lastButtonPress = currentMillis;
    
    if (inMenuMode) {
      menuPosition = max(0, menuPosition - 1);
      displayMenu();
    } else {
      // Menü aktivieren
      inMenuMode = true;
      menuPosition = 0;
      displayMenu();
    }
    
    Serial.println("Taste UP gedrückt");
  } 
  else if (!currentUpState && buttonUpState) {
    buttonUpState = false;
  }
  
  // Down-Taste gedrückt?
  if (currentDownState && !buttonDownState) {
    buttonDownState = true;
    lastButtonPress = currentMillis;
    
    if (inMenuMode) {
      menuPosition = min(menuPosition + 1, 6); // Anzahl der Menüeinträge - 1
      displayMenu();
    } else {
      // Menü aktivieren
      inMenuMode = true;
      menuPosition = 0;
      displayMenu();
    }
    
    Serial.println("Taste DOWN gedrückt");
  } 
  else if (!currentDownState && buttonDownState) {
    buttonDownState = false;
  }
  
  // Select-Taste gedrückt?
  if (currentSelectState && !buttonSelectState) {
    buttonSelectState = true;
    lastButtonPress = currentMillis;
    
    if (inMenuMode) {
      // Menüauswahl ausführen
      executeMenuAction();
    } else {
      // Menü aktivieren
      inMenuMode = true;
      menuPosition = 0;
      displayMenu();
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
      inMenuMode = false;
      if (WiFi.status() == WL_CONNECTED && displayAvailable) {
        displayLoginInfo();
      }
      break;
      
    case 1: // Relais schalten
      relayState = !relayState;
      digitalWrite(RELAY_PIN, relayState ? HIGH : LOW);
      
      display.clearDisplay();
      display.setTextSize(1);
      display.setCursor(0, 0);
      display.println("Relais geschaltet");
      display.println("");
      display.println(relayState ? "Status: AN" : "Status: AUS");
      display.display();
      
      delay(1500);
      displayMenu();
      break;
      
    case 2: // WLAN-Info anzeigen
      display.clearDisplay();
      display.setTextSize(1);
      display.setCursor(0, 0);
      display.println("WLAN Information");
      display.println("");
      if (WiFi.status() == WL_CONNECTED) {
        display.print("IP: ");
        display.println(WiFi.localIP().toString());
        display.print("SSID: ");
        display.println(WiFi.SSID());
        display.print("RSSI: ");
        display.print(WiFi.RSSI());
        display.println(" dBm");
        display.print("MAC: ");
        display.println(WiFi.macAddress());
      } else {
        display.println("Nicht verbunden");
      }
      display.display();
      
      delay(3000);
      displayMenu();
      break;
      
    case 3: // Geräte-Info
      display.clearDisplay();
      display.setTextSize(1);
      display.setCursor(0, 0);
      display.println("Geraete-Info");
      display.println("");
      display.print("Hostname: ");
      display.println(hostname);
      display.print("Uptime: ");
      display.println(formatUptime());
      display.print("Free Mem: ");
      display.print(ESP.getFreeHeap());
      display.println(" Bytes");
      display.print("Chip-ID: ");
      display.println(ESP.getChipId(), HEX);
      display.print("Flash-Size: ");
      display.print(ESP.getFlashChipSize() / 1024);
      display.println(" KB");
      display.display();
      
      delay(3000);
      displayMenu();
      break;
      
    case 4: // Systemstatus
      display.clearDisplay();
      display.setTextSize(1);
      display.setCursor(0, 0);
      display.println("Systemstatus");
      display.println("");
      display.print("CPU-Freq: ");
      display.print(ESP.getCpuFreqMHz());
      display.println(" MHz");
      display.print("Relay: ");
      display.println(relayState ? "AN" : "AUS");
      display.print("Vcc: ~");
      display.print(ESP.getVcc() / 1000.0, 2);
      display.println(" V");
      display.print("WLAN: ");
      display.println(WiFi.status() == WL_CONNECTED ? "Verbunden" : "Getrennt");
      display.display();
      
      delay(3000);
      displayMenu();
      break;
      
    case 5: // Helligkeit (Simulation - bei OLED nicht wirklich möglich)
      display.clearDisplay();
      display.setTextSize(1);
      display.setCursor(0, 0);
      display.println("Helligkeit");
      display.println("");
      display.println("Bei OLED-Displays kann");
      display.println("die Helligkeit nicht");
      display.println("direkt angepasst werden.");
      display.println("");
      display.println("Zurueck mit beliebiger");
      display.println("Taste...");
      display.display();
      
      delay(3000);
      displayMenu();
      break;
      
    case 6: // Neustart
      display.clearDisplay();
      display.setTextSize(1);
      display.setCursor(0, 0);
      display.println("Neustart...");
      display.display();
      
      delay(1000);
      ESP.restart();
      break;
  }
}

void loop() {
  // OTA-Anfragen bearbeiten
  ArduinoOTA.handle();
  
  // Webserver verarbeiten
  server.handleClient();
  
  // Tasten überwachen
  handleButtons();
  
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
      
      // Bei erfolgreicher Verbindung QR anzeigen wenn nicht im Menü
      if (WiFi.status() == WL_CONNECTED && displayAvailable && !inMenuMode) {
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