// SwissAirDry Wemos D1 Mini mit QR-Code-Anzeige
// Optimiert für 128x64 OLED-Display
// OTA-Updates + QR-Code mit IP-Adresse und Web-Passwort

#include <ESP8266WiFi.h>
#include <ESP8266mDNS.h>
#include <WiFiUdp.h>
#include <ArduinoOTA.h>
#include <Wire.h>
#include <SPI.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <EEPROM.h>
#include <ESP8266WebServer.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClientSecure.h>
#include <ArduinoJson.h>

// BLE-Scanning Bibliotheken
#include <vector>
#include <algorithm> // Für std::sort
#include <string>

// ----- WLAN-KONFIGURATION -----
// Bitte hier die WLAN-Daten eintragen
const char* ssid = "G4UG";  // Ihr WLAN-Name
const char* password = "Loeschdecke+1";  // Ihr WLAN-Passwort

// ----- API-KONFIGURATION -----
// Die API-Endpunkt-Variable wurde auf eine String-Variable geändert (apiEndpoint)
const int apiPort = 443;  // HTTPS-Port (443) für die API
const String apiBasePath = "/v1";  // API-Basispfad

// ----- HARDWARE-KONFIGURATION -----
// Festverdrahtete Pins für Wemos D1 Mini (Pins aus Wemos-Skript beibehalten)
#define LED_PIN 2        // GPIO2 (D4 auf Wemos D1 Mini) - Blau LED on-board
#define LED_ON LOW       // LED ist aktiv LOW (invertiert)
#define LED_OFF HIGH
#define RELAY_PIN D3     // Relais-Pin für Desinfektionsgerät (geändert von D5)

// Membranschalter (Taster) Pins - Für einfachere Verkabelung (alle Tasten nebeneinander)
#define BUTTON_SELECT D5 // Bestätigungstaste (OK-Button, geändert von D8)
#define BUTTON_UP D6     // Taste oben 
#define BUTTON_DOWN D7   // Taste unten
#define BUTTON_BACK D8   // Zurück-Taste (optional)

// Zusätzliche Pins für erweiterte Funktionalität
#define PRESSURE_SENSOR A0 // Analoger Drucksensor-Eingang

// Keine Konfiguration für zweites Board

// Display-Konfiguration
#define OLED_RESET -1    // Kein Reset-Pin verwendet
#define SCREEN_WIDTH 128 // OLED Display Breite in Pixeln
#define SCREEN_HEIGHT 64 // OLED Display Höhe in Pixeln
#define OLED_ADDR 0x3C   // I2C-Adresse des OLED-Displays

// Web-UI Konfiguration
String webPassword = "";   // Wird automatisch generiert
#define WEB_SERVER_PORT 80  // Webserver-Port

// Objekte initialisieren
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
ESP8266WebServer server(WEB_SERVER_PORT);
bool displayAvailable = false;

// Struktur für BLE-Geräte
struct BLEDevice {
  String address;
  String name;
  int rssi;
  bool isBeacon;
};

// Array für gefundene BLE-Geräte
std::vector<BLEDevice> foundDevices;

// Variablen für BLE-Scan (simuliert über WiFi)
unsigned long lastScanTime = 0;
const int SCAN_INTERVAL = 10000; // 10 Sekunden zwischen Scans
bool isScanning = false;
int scanIndex = 0;          // Für die Anzeige der Scan-Ergebnisse

// Hostname mit eindeutiger Chip-ID
String hostname = "SwissAirDry-";

// Relais-Status
bool relayState = false;

// Tastenstatus-Variablen

// Alte Tastenvariablen für Kompatibilität
bool buttonUpState = false;
bool buttonDownState = false;
bool buttonSelectState = false;
unsigned long lastButtonPress = 0;
const int buttonDebounceTime = 200; // Entprellzeit in ms

// Menü-Variablen
int menuPosition = 0;
bool inMenuMode = false;

// API-Status-Variablen
bool apiConnected = false;
unsigned long lastApiCheck = 0;
const unsigned long API_CHECK_INTERVAL = 60000; // 1 Minute zwischen API-Checks
String apiEndpoint = "api.vgnc.org"; // API-Endpunkt als String für einfachere Handhabung
int apiResponseCode = 0;

// StartLogo
static const uint8_t SwissAirDry_StartLogo[] = {
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0xfc,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0xfc,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0xe0,0xff,0x0f,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0xe0,0xff,0x0f,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0xf8,0xff,0x3f,0x00,0x00,0x00,0x00,0x00
};

// Icons fuer Menü
static const uint8_t icon_check[] = {
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x04,0x00,0x0a,0x04,0x11,0x8a,0x08,0x51,0x04,
    0x22,0x02,0x04,0x01,0x88,0x00,0x50,0x00,0x20,0x00,0x00,0x00,0x00,0x00,0x00,0x00
};

static const uint8_t icon_cross[] = {
    0x00,0x00,0x00,0x00,0x00,0x00,0x04,0x01,0x8a,0x02,0x51,0x04,0x22,0x02,0x04,0x01,
    0x88,0x00,0x04,0x01,0x22,0x02,0x51,0x04,0x8a,0x02,0x04,0x01,0x00,0x00,0x00,0x00
};

// Sanduhr-Animation Frames
static const uint8_t sandclock_frame1[] = {
    0x00,0x00,0x00,0xe0,0xff,0x0f,0x20,0x00,0x08,0xc0,0xff,0x07,0x80,0x00,0x02,0x80,
    0x00,0x02,0x80,0x00,0x02,0x80,0x7c,0x02,0x00,0x39,0x01,0x00,0x92,0x00,0x00,0x44,
    0x00,0x00,0x28,0x00,0x00,0x28,0x00,0x00,0x44,0x00,0x00,0x92,0x00,0x00,0x01,0x01,
    0x80,0x7c,0x02,0x80,0xfe,0x02,0x80,0xfe,0x02,0x80,0x00,0x02,0xc0,0xff,0x07,0x20,
    0x00,0x08,0xe0,0xff,0x0f,0x00,0x00,0x00
};

static const uint8_t sandclock_frame2[] = {
    0x00,0x02,0x00,0x00,0x07,0x00,0x80,0x02,0x00,0x40,0x05,0x00,0xa0,0x08,0x00,0x50,
    0x10,0x00,0x28,0x10,0x00,0x14,0x10,0x00,0x0a,0x10,0x00,0x07,0x10,0x00,0x0a,0x10,
    0x00,0x10,0xe0,0x07,0xe0,0x07,0x08,0x00,0x28,0x50,0x00,0xe8,0xe7,0x00,0xe8,0x53,
    0x00,0xe8,0x29,0x00,0xe8,0x14,0x00,0x48,0x0a,0x00,0x10,0x05,0x00,0xa0,0x02,0x00,
    0x40,0x01,0x00,0xe0,0x00,0x00,0x40,0x00
};

static const uint8_t sandclock_frame3[] = {
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x06,
    0x00,0x60,0x0a,0x00,0x50,0xfa,0x00,0x5f,0x0a,0x81,0x50,0x0a,0x42,0x50,0x0a,0x24,
    0x50,0x0a,0x18,0x5e,0x0a,0xc0,0x5f,0x0a,0x98,0x5f,0x0a,0x24,0x5f,0x0a,0x42,0x5e,
    0x0a,0x81,0x50,0xfa,0x00,0x5f,0x0a,0x00,0x50,0x06,0x00,0x60,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00
};

// Drucksensor-Variablen und Kalibrierung
int pressureValue = 0;     // Rohwert vom Drucksensor
float pressure = 0.0;      // Umgerechneter Druckwert in hPa oder mbar
float minPressure = 900.0; // Minimaler Druckwert für Kalibrierung (entspricht 0 A0-Wert)
float maxPressure = 1100.0; // Maximaler Druckwert für Kalibrierung (entspricht 1023 A0-Wert)
const int numReadings = 10; // Anzahl der Messungen für den gleitenden Durchschnitt
int pressureReadings[10];   // Array für die letzten 10 Drucksensor-Messwerte
int readIndex = 0;          // Index für das Array
int totalPressure = 0;      // Gesamtsumme für den gleitenden Durchschnitt
int avgPressure = 0;        // Durchschnittlicher Druckwert

// Keine Sekundärboard-Kommunikation mehr

// Gerätedaten-Struktur für API-Kommunikation
struct DeviceData {
  String deviceId;      // Geräte-ID (gleich wie Hostname)
  float pressure;       // Druckwert in hPa
  bool relayState;      // Status des Relais (an/aus)
  int rssi;             // WLAN-Signalstärke in dBm
  unsigned long uptime; // Betriebszeit in Sekunden
};

// API-Variablen
DeviceData deviceData;          // Aktuelle Gerätedaten
unsigned long lastApiUpdate = 0; // Zeitpunkt der letzten API-Aktualisierung
const int API_UPDATE_INTERVAL = 30000; // Aktualisierungsintervall (30 Sekunden)

// Menüzustände
enum MenuState {
    SPLASH_SCREEN,     // Startlogo
    START_SCREEN,      // Hauptbildschirm
    MAIN_MENU,         // Hauptmenü
    RELAY_CONTROL,     // Relais steuern
    WLAN_INFO,         // WLAN-Informationen
    SYSTEM_INFO,       // Systeminformationen
    BLE_SCAN,          // BLE-Geräte scannen
    COUNTDOWN_SCREEN,  // Countdown-Anzeige mit Animation
    RESTART_CONFIRM,   // Neustartbestätigung
    SCAN_RESULTS,      // Ergebnisse des BLE-Scans anzeigen
    PRESSURE_DISPLAY,  // Anzeige des Drucksensor-Werts
    API_STATUS         // API-Verbindungsstatus
};

// Aktueller Menüzustand
MenuState currentState = SPLASH_SCREEN;

// Variablen für Animationen und Zeitsteuerung
unsigned long splashStartTime = 0;       // Zeit für den Splash-Screen
const unsigned long SPLASH_DURATION = 3000; // 3 Sekunden für Splash-Screen
unsigned long lastAnimationTime = 0;     // Für Animationen
uint8_t animationFrame = 0;              // Aktueller Animationsframe

void setup() {
  // Serielle Verbindung starten
  Serial.begin(115200);
  Serial.println("\n\nSwissAirDry für Wemos D1 Mini mit QR-Code (128x64 Display)");
  
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
  pinMode(BUTTON_BACK, INPUT_PULLUP); // Zurück-Taste statt des Sensor-Pins
  
  // Initialisierung der Drucksensor-Werte für gleitenden Durchschnitt
  for (int i = 0; i < numReadings; i++) {
    pressureReadings[i] = 0;
  }
  totalPressure = 0;
  
  // Display initialisieren
  Wire.begin();  // SDA=D2(GPIO4), SCL=D1(GPIO5) sind Standard bei Wemos D1 Mini
  
  if(!display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR)) {
    Serial.println("SSD1306 Display nicht gefunden");
    displayAvailable = false;
  } else {
    Serial.println("Display initialisiert");
    displayAvailable = true;
    
    // Startlogo anzeigen
    display.clearDisplay();
    display.drawBitmap(0, 0, SwissAirDry_StartLogo, 128, 64, SSD1306_WHITE);
    display.display();
    
    // Splash-Screen-Startzeit setzen
    splashStartTime = millis();
  }
  
  // Zufälliges Passwort generieren
  generateRandomPassword();
  
  // Mit WLAN verbinden
  connectWiFi();
  
  // OTA-Updates einrichten
  setupOTA();
  
  // Webserver einrichten
  setupWebServer();
  
  // Nach dem Splash-Screen zum Hauptbildschirm wechseln
  currentState = START_SCREEN;
  
  // IP und Passwort als QR-Pattern anzeigen, wenn WLAN verbunden
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
  display.setCursor(0, 10);
  display.print("IP: ");
  display.println(WiFi.localIP().toString());
  
  // Passwort anzeigen
  display.setCursor(0, 20);
  display.print("PW: ");
  display.println(webPassword);
  
  // Optimierte QR-Code-Größe für 128x64 Display
  drawQRPattern();
  
  display.display();
  Serial.println("Login-Informationen angezeigt");
}

// Optimierte QR-Code-Darstellung für 128x64 Display
// API-Status anzeigen
void displayApiStatus() {
  if (!displayAvailable) return;
  
  display.clearDisplay();
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.println("API-Status");
  display.drawLine(0, 10, 128, 10, SSD1306_WHITE);
  
  // Verbindungsstatus
  display.setCursor(0, 15);
  display.print("Server: ");
  display.println(apiEndpoint);
  
  display.setCursor(0, 25);
  display.print("Status: ");
  
  // Verbindungsstatus prüfen
  bool connected = false;
  if (WiFi.status() == WL_CONNECTED) {
    // Versuche MQTT und API zu kontaktieren
    connected = apiConnected;
    if (connected) {
      display.println("Verbunden");
    } else {
      display.println("Nicht verbunden");
    }
  } else {
    display.println("Kein WLAN");
  }
  
  // Letztes Update anzeigen
  display.setCursor(0, 35);
  display.print("Letztes Update: ");
  if (lastApiUpdate > 0) {
    unsigned long timeSince = (millis() - lastApiUpdate) / 1000;
    if (timeSince < 60) {
      display.print(timeSince);
      display.println(" Sek.");
    } else if (timeSince < 3600) {
      display.print(timeSince / 60);
      display.println(" Min.");
    } else {
      display.print(timeSince / 3600);
      display.println(" Std.");
    }
  } else {
    display.println("Noch nie");
  }
  
  // Anzahl der Geräte anzeigen
  display.setCursor(0, 45);
  display.println("Daten:");
  display.print(" - Druck: ");
  display.print(readPressureSensor(), 1);
  display.println(" hPa");
  
  display.setCursor(0, 55);
  display.println("SELECT: Test   UP/DOWN: Zurueck");
  
  display.display();
}

// Lesen und Verarbeiten des Drucksensor-Werts
float readPressureSensor() {
  // Analogwert vom Sensor lesen (0-1023)
  pressureValue = analogRead(PRESSURE_SENSOR);
  
  // Gleitenden Durchschnitt berechnen
  totalPressure = totalPressure - pressureReadings[readIndex];
  pressureReadings[readIndex] = pressureValue;
  totalPressure = totalPressure + pressureReadings[readIndex];
  readIndex = (readIndex + 1) % numReadings;
  
  avgPressure = totalPressure / numReadings;
  
  // Umrechnung in hPa (mbar), angepasst an den Kalibrierungsbereich
  // map() gibt nur ganzzahlige Werte zurück, daher manuelle Berechnung für Gleitkommawerte
  pressure = minPressure + ((float)avgPressure / 1023.0) * (maxPressure - minPressure);
  
  // Ausgabe auf serielle Schnittstelle für Debugging
  Serial.print("Druck-Rohwert: ");
  Serial.print(pressureValue);
  Serial.print(", Durchschnitt: ");
  Serial.print(avgPressure);
  Serial.print(", Druck (hPa): ");
  Serial.println(pressure);
  
  return pressure;
}

// Anzeige der Drucksensor-Werte
void displayPressureScreen() {
  if (!displayAvailable) return;
  
  // Aktuellen Druck messen
  float currentPressure = readPressureSensor();
  
  display.clearDisplay();
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.println("Drucksensor");
  
  display.setCursor(0, 16);
  display.setTextSize(2);
  display.print(currentPressure, 1);
  display.print(" hPa");
  
  // Trendanzeige (einfacher Balken)
  display.setCursor(0, 40);
  display.setTextSize(1);
  display.println("Trend:");
  
  // Einfacher Balken zur Visualisierung
  int barWidth = map(avgPressure, 0, 1023, 0, 120);
  display.drawRect(0, 50, 128, 10, SSD1306_WHITE);
  display.fillRect(2, 52, barWidth, 6, SSD1306_WHITE);
  
  display.display();
}

void drawQRPattern() {
  // QR-Code für 128x64 OLED, optimiert für kleinere Höhe
  int qrSize = 42;  // Kleinerer QR-Code
  int qrX = 84;     // Rechts ausgerichtet
  int qrY = 10;     // Angepasste Y-Position
  int dotSize = 3;  // Kleinere Punkte
  
  // Rand zeichnen
  display.drawRect(qrX, qrY, qrSize, qrSize, SSD1306_WHITE);
  
  // Eckquadrate zeichnen (wie bei QR-Codes)
  // Oben links
  display.fillRect(qrX + 3, qrY + 3, 9, 9, SSD1306_WHITE);
  display.fillRect(qrX + 5, qrY + 5, 5, 5, SSD1306_BLACK);
  
  // Oben rechts
  display.fillRect(qrX + qrSize - 12, qrY + 3, 9, 9, SSD1306_WHITE);
  display.fillRect(qrX + qrSize - 10, qrY + 5, 5, 5, SSD1306_BLACK);
  
  // Unten links
  display.fillRect(qrX + 3, qrY + qrSize - 12, 9, 9, SSD1306_WHITE);
  display.fillRect(qrX + 5, qrY + qrSize - 10, 5, 5, SSD1306_BLACK);
  
  // Zufällige Blöcke im inneren Bereich (Daten)
  // Basierend auf der IP-Adresse und dem Passwort für eine eindeutige Darstellung
  // Dies ist kein echter QR-Code, sondern ahmt nur das Aussehen nach
  uint32_t seed = WiFi.localIP()[3];
  for (uint8_t i = 0; i < webPassword.length(); i++) {
    seed += webPassword[i];
  }
  randomSeed(seed + ESP.getChipId());
  
  for (int i = 0; i < 10; i++) {
    for (int j = 0; j < 10; j++) {
      // Ecken auslassen
      if ((i < 3 && j < 3) || (i < 3 && j > 6) || (i > 6 && j < 3)) {
        continue;
      }
      
      // Zufällig einige Blöcke füllen
      if (random(100) < 40) {
        display.fillRect(
          qrX + 4 + (i * dotSize), 
          qrY + 4 + (j * dotSize), 
          dotSize, 
          dotSize, 
          SSD1306_WHITE
        );
      }
    }
  }
  
  // Texte für den Zugriff hinzufügen
  display.setCursor(0, 48);
  display.println("Besuchen Sie:");
  display.println(WiFi.localIP().toString());
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
    "API-Status",
    "Drucksensor anzeigen",
    "BLE-Scan starten",
    "Neustart"
  };
  
  // Sichtbarer Bereich im Menü (max 5 Einträge)
  int visibleStart = max(0, menuPosition - 2);
  int visibleEnd = min(visibleStart + 4, (int)(sizeof(menuItems) / sizeof(menuItems[0])) - 1);
  
  for (int i = visibleStart; i <= visibleEnd; i++) {
    if (i == menuPosition) {
      // Aktueller Menüpunkt hervorgehoben
      display.fillRect(0, 10 + (i - visibleStart) * 10, 128, 10, SSD1306_WHITE);
      display.setTextColor(SSD1306_BLACK);
      display.setCursor(2, 11 + (i - visibleStart) * 10);
      display.print("> ");
      display.print(menuItems[i]);
      display.setTextColor(SSD1306_WHITE);
    } else {
      display.setCursor(2, 11 + (i - visibleStart) * 10);
      display.print("  ");
      display.print(menuItems[i]);
    }
  }
  
  // Scrollindikator wenn nötig
  if (visibleStart > 0) {
    display.drawTriangle(120, 10, 124, 10, 122, 7, SSD1306_WHITE);
  }
  if (visibleEnd < (sizeof(menuItems) / sizeof(menuItems[0])) - 1) {
    display.drawTriangle(120, 53, 124, 53, 122, 56, SSD1306_WHITE);
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
      menuPosition = min(menuPosition + 1, 7); // Anzahl der Menüeinträge - 1
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
      display.display();
      
      delay(3000);
      displayMenu();
      break;
      
    case 4: // API-Status anzeigen
      // Zum API-Status-Bildschirm wechseln
      currentState = API_STATUS;
      inMenuMode = false;
      break;
      
    case 5: // Drucksensor anzeigen
      // Zum Drucksensor-Bildschirm wechseln
      currentState = PRESSURE_DISPLAY;
      inMenuMode = false;
      break;
      
    case 6: // BLE-Scan starten
      // Zum BLE-Scan-Bildschirm wechseln
      currentState = BLE_SCAN;
      inMenuMode = false;
      isScanning = true;
      startBLEScan(); // WiFi-Scan als BLE-Simulation starten
      break;
      
    case 7: // Neustart
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

// Aktuellen Menüzustand auf dem Display anzeigen
void updateDisplay() {
  if (!displayAvailable) return;
  
  display.clearDisplay();
  
  switch (currentState) {
    case SPLASH_SCREEN:
      // Logo anzeigen
      display.drawBitmap(0, 0, SwissAirDry_StartLogo, 128, 64, SSD1306_WHITE);
      
      // Prüfen, ob die Splash-Screen-Zeit abgelaufen ist
      if (millis() - splashStartTime >= SPLASH_DURATION) {
        currentState = START_SCREEN;
      }
      break;
      
    case API_STATUS:
      // API-Status-Bildschirm
      displayApiStatus();
      break;
      
    case START_SCREEN:
      // Standard-Startbildschirm mit IP und QR-Code
      if (WiFi.status() == WL_CONNECTED) {
        displayLoginInfo();
      } else {
        display.setCursor(0, 0);
        display.setTextSize(1);
        display.println("SwissAirDry");
        display.println("Wemos D1 Mini");
        display.println("Kein WLAN");
        display.println("Druecke SELECT fuer Menu");
      }
      break;
      
    case BLE_SCAN:
      // BLE-Scan-Bildschirm
      display.setTextSize(1);
      display.setCursor(0, 0);
      display.println("BLE Geraetescan");
      display.drawLine(0, 10, 128, 10, SSD1306_WHITE);
      
      if (isScanning) {
        // Animation während des Scans
        const uint8_t* frames[] = {sandclock_frame1, sandclock_frame2, sandclock_frame3};
        display.drawBitmap(48, 15, frames[animationFrame], 32, 32, SSD1306_WHITE);
        
        display.setCursor(0, 50);
        display.println("Suche Geraete...");
        
        // Animation alle 500ms
        if (millis() - lastAnimationTime > 500) {
          animationFrame = (animationFrame + 1) % 3;
          lastAnimationTime = millis();
        }
      } else {
        display.setCursor(0, 25);
        display.println("Scanning...");
        display.println("Bitte warten");
      }
      break;
      
    case SCAN_RESULTS:
      // Ergebnisse des BLE-Scans anzeigen
      display.setTextSize(1);
      display.setCursor(0, 0);
      display.println("BLE-Scan Ergebnisse");
      display.drawLine(0, 10, 128, 10, SSD1306_WHITE);
      
      if (foundDevices.size() > 0) {
        int startIdx = scanIndex;
        int endIdx = min(startIdx + 4, (int)foundDevices.size() - 1);
        
        for (int i = startIdx; i <= endIdx; i++) {
          int y = 15 + (i - startIdx) * 12;
          display.setCursor(0, y);
          
          // Name abschneiden, wenn zu lang
          String name = foundDevices[i].name;
          if (name.length() > 10) {
            name = name.substring(0, 8) + "..";
          }
          
          // RSSI-Balken zeichnen (0-4 Blöcke)
          int rssi = foundDevices[i].rssi;
          int bars = 0;
          if (rssi > -50) bars = 4;
          else if (rssi > -65) bars = 3;
          else if (rssi > -75) bars = 2;
          else if (rssi > -85) bars = 1;
          
          // Gerätename und Signalstärke
          display.print(name);
          display.setCursor(85, y);
          
          // Signal-Stärke Balken
          for (int b = 0; b < 4; b++) {
            if (b < bars) {
              display.fillRect(85 + (b * 6), y, 4, 10 - (b * 2), SSD1306_WHITE);
            } else {
              display.drawRect(85 + (b * 6), y, 4, 10 - (b * 2), SSD1306_WHITE);
            }
          }
          
          // SwissAirDry Geräte markieren
          if (foundDevices[i].isBeacon) {
            display.drawBitmap(110, y, icon_check, 8, 8, SSD1306_WHITE);
          }
        }
        
        // Scrollanzeiger
        if (startIdx > 0) {
          display.drawTriangle(120, 15, 124, 15, 122, 11, SSD1306_WHITE);
        }
        if (endIdx < foundDevices.size() - 1) {
          display.drawTriangle(120, 60, 124, 60, 122, 63, SSD1306_WHITE);
        }
        
        display.setCursor(0, 55);
        display.println("UP/DOWN: Scrollen");
      } else {
        display.setCursor(0, 25);
        display.println("Keine Geraete");
        display.println("gefunden!");
      }
      break;
      
    case MAIN_MENU:
      display.setTextSize(1);
      display.setCursor(0, 0);
      display.println("Hauptmenue");
      display.drawLine(0, 10, 128, 10, SSD1306_WHITE);
      
      // Menüpunkte
      String menuItems[] = {
        "Zurueck zum Start",
        "Relais schalten",
        "WLAN-Info",
        "System-Info",
        "API-Status",
        "Drucksensor",
        "BLE-Scan",
        "Neustart"
      };
      
      // Sichtbarer Bereich im Menü (max 5 Einträge)
      int visibleStart = max(0, menuPosition - 2);
      int visibleEnd = min(visibleStart + 4, (int)(sizeof(menuItems) / sizeof(menuItems[0])) - 1);
      
      for (int i = visibleStart; i <= visibleEnd; i++) {
        if (i == menuPosition) {
          // Aktueller Menüpunkt hervorgehoben
          display.fillRect(0, 12 + (i - visibleStart) * 10, 128, 10, SSD1306_WHITE);
          display.setTextColor(SSD1306_BLACK);
          display.setCursor(2, 13 + (i - visibleStart) * 10);
          display.print("> ");
          display.print(menuItems[i]);
          display.setTextColor(SSD1306_WHITE);
        } else {
          display.setCursor(2, 13 + (i - visibleStart) * 10);
          display.print("  ");
          display.print(menuItems[i]);
        }
      }
      
      // Scrollanzeiger
      if (visibleStart > 0) {
        display.drawTriangle(120, 12, 124, 12, 122, 8, SSD1306_WHITE);
      }
      if (visibleEnd < (sizeof(menuItems) / sizeof(menuItems[0])) - 1) {
        display.drawTriangle(120, 60, 124, 60, 122, 63, SSD1306_WHITE);
      }
      break;
      
    case RELAY_CONTROL:
      display.setTextSize(1);
      display.setCursor(0, 0);
      display.println("Relais steuern");
      display.drawLine(0, 10, 128, 10, SSD1306_WHITE);
      display.setCursor(0, 20);
      display.println("Status: " + String(relayState ? "AN" : "AUS"));
      display.setCursor(0, 35);
      display.println("SELECT: Umschalten");
      display.setCursor(0, 45);
      display.println("UP/DOWN: Zurueck");
      break;
      
    case WLAN_INFO:
      display.setTextSize(1);
      display.setCursor(0, 0);
      display.println("WLAN Information");
      display.drawLine(0, 10, 128, 10, SSD1306_WHITE);
      display.setCursor(0, 15);
      
      if (WiFi.status() == WL_CONNECTED) {
        display.println("SSID: " + String(ssid));
        display.println("IP: " + WiFi.localIP().toString());
        display.println("Signal: " + String(WiFi.RSSI()) + " dBm");
        display.println("MAC: " + WiFi.macAddress());
      } else {
        display.println("Nicht verbunden");
        display.println("Verbinde mit: " + String(ssid));
      }
      
      display.setCursor(0, 55);
      display.println("UP/DOWN: Zurueck");
      break;
      
    case SYSTEM_INFO:
      display.setTextSize(1);
      display.setCursor(0, 0);
      display.println("System Information");
      display.drawLine(0, 10, 128, 10, SSD1306_WHITE);
      display.setCursor(0, 15);
      display.println("Hostname: " + hostname);
      display.println("Uptime: " + formatUptime());
      display.println("Freier RAM: " + String(ESP.getFreeHeap()) + " Bytes");
      display.println("Flash: " + String(ESP.getFlashChipSize() / 1024) + " KB");
      
      display.setCursor(0, 55);
      display.println("UP/DOWN: Zurueck");
      break;
      
    case COUNTDOWN_SCREEN:
      display.setTextSize(1);
      display.setCursor(0, 0);
      display.println("Countdown");
      display.drawLine(0, 10, 128, 10, SSD1306_WHITE);
      
      // Sanduhr-Animation
      const uint8_t* frames[] = {sandclock_frame1, sandclock_frame2, sandclock_frame3};
      display.drawBitmap(48, 15, frames[animationFrame], 32, 32, SSD1306_WHITE);
      
      // Animation alle 500ms
      if (millis() - lastAnimationTime > 500) {
        animationFrame = (animationFrame + 1) % 3;
        lastAnimationTime = millis();
      }
      
      display.setCursor(0, 55);
      display.println("SELECT: Abbrechen");
      break;
      
    case RESTART_CONFIRM:
      display.setTextSize(1);
      display.setCursor(0, 0);
      display.println("Neustart bestaetigen");
      display.drawLine(0, 10, 128, 10, SSD1306_WHITE);
      display.setCursor(0, 20);
      display.println("Moechten Sie das");
      display.println("Geraet neu starten?");
      display.setCursor(0, 45);
      display.println("SELECT: Ja");
      display.println("UP/DOWN: Abbrechen");
      break;
      
    case PRESSURE_DISPLAY:
      // Drucksensor-Bildschirm anzeigen
      displayPressureScreen();
      
      // Tastensteuerung für diesen Bildschirm prüfen
      if (currentUpState || currentDownState) {
        // Zurück zum Menü bei Tastendruck
        inMenuMode = true;
        displayMenu();
      }
      break;
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
    
    switch (currentState) {
      case START_SCREEN:
        // Zum Menü wechseln
        currentState = MAIN_MENU;
        menuPosition = 0;
        break;
        
      case MAIN_MENU:
        // Im Menü nach oben
        menuPosition = max(0, menuPosition - 1);
        break;
        
      case RELAY_CONTROL:
      case WLAN_INFO:
      case SYSTEM_INFO:
      case BLE_SCAN:
      case RESTART_CONFIRM:
      case PRESSURE_DISPLAY:
        // Zurück zum Hauptmenü
        currentState = MAIN_MENU;
        break;
        
      case SCAN_RESULTS:
        // Bei UP-Taste nach oben scrollen
        if (foundDevices.size() > 0 && scanIndex > 0) {
          scanIndex--;
        }
        break;
        
      case COUNTDOWN_SCREEN:
        // Countdown abbrechen
        currentState = MAIN_MENU;
        break;
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
    
    switch (currentState) {
      case START_SCREEN:
        // Zum Menü wechseln
        currentState = MAIN_MENU;
        menuPosition = 0;
        break;
        
      case MAIN_MENU:
        // Im Menü nach unten
        menuPosition = min(menuPosition + 1, 7); // Anzahl der Menüeinträge - 1
        break;
        
      case RELAY_CONTROL:
      case WLAN_INFO:
      case SYSTEM_INFO:
      case BLE_SCAN:
      case RESTART_CONFIRM:
      case PRESSURE_DISPLAY:
        // Zurück zum Hauptmenü
        currentState = MAIN_MENU;
        break;
        
      case SCAN_RESULTS:
        // Bei DOWN-Taste nach unten scrollen
        if (foundDevices.size() > 0 && scanIndex < foundDevices.size() - 1) {
          scanIndex++;
        }
        break;
        
      case COUNTDOWN_SCREEN:
        // Countdown abbrechen
        currentState = MAIN_MENU;
        break;
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
    
    switch (currentState) {
      case SPLASH_SCREEN:
        // Splash-Screen überspringen
        currentState = START_SCREEN;
        break;
        
      case START_SCREEN:
        // Zum Menü wechseln
        currentState = MAIN_MENU;
        menuPosition = 0;
        break;
        
      case MAIN_MENU:
        // Menüpunkt auswählen
        executeMenuAction();
        break;
        
      case RELAY_CONTROL:
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