// Anleitung für die ESP32-C6 Konfiguration mit 1.47" TFT Display (ST7789)
//
// Um das TFT_eSPI-Display zu verwenden, müssen Sie diese Datei in das
// Verzeichnis TFT_eSPI/User_Setup.h in Ihrer Arduino-Bibliothek kopieren.
//
// Sie sollten diese Anweisungen befolgen:
// 1. Kopieren Sie diese Datei in User_Setup.h in Ihrer TFT_eSPI-Bibliothek
// 2. Kommentieren Sie alle vordefinierten Display-Konfigurationen aus
// 3. Aktivieren Sie die unten angegebenen Einstellungen

#ifndef USER_SETUP_LOADED
#define USER_SETUP_LOADED

// ##################### EINSTELLUNGEN FÜR ESP32-C6 XIAO Board #####################

// Definieren Sie die Treiber für das ST7789-Display
#define ST7789_DRIVER

// Definieren Sie die Bildschirmgröße und Formatierung
#define TFT_WIDTH  172
#define TFT_HEIGHT 320
#define TFT_ROTATION 0  // 0 = Portrait, 2 = Portrait umgedreht

// Definieren Sie die SPI-Pins für das Display
// Diese Pins müssen an Ihrem ESP32-C6 XIAO Board angepasst werden
// Bitte prüfen Sie die Dokumentation oder schematische Darstellung Ihres spezifischen Boards
#define TFT_MISO -1     // Nicht benötigt, wenn Display nur Eingänge hat (kein Lesen möglich)
#define TFT_MOSI 3      // SDA Pin (IO3 an XIAO ESP32-C6)
#define TFT_SCLK 4      // SCL Pin (IO4 an XIAO ESP32-C6)
#define TFT_CS   5      // Chip Select Pin (IO5 an XIAO ESP32-C6)
#define TFT_DC   6      // Data/Command (D/C) Pin (IO6 an XIAO ESP32-C6)
#define TFT_RST  7      // Reset Pin (IO7 an XIAO ESP32-C6)

// Farbtiefen-Einstellungen
// Kann auf 16 für 16-Bit-Farben eingestellt werden, was schneller, aber weniger farbenfroh ist
// Oder auf 24 für 24-Bit-Farben eingestellt werden, was langsamer, aber farbenreicher ist
#define SPI_FREQUENCY 40000000  // SPI-Frequenz (27MHz funktioniert normalerweise gut, kann bis zu 80MHz eingestellt werden)
#define COLOR_DEPTH 16          // 16-Bit-Modus (R5G6B5) - schneller, aber weniger Farben

// Optional: Konfigurieren Sie Hintergrundbeleuchtungs-Pin, wenn verfügbar
// Wenn Ihre Anzeige keine Hintergrundbeleuchtung hat oder die Hintergrundbeleuchtung immer an bleibt, aktivieren Sie diese nicht
// #define TFT_BL   8            // Hintergrundbeleuchtungs-Pin

// WICHTIG: Stellen Sie sicher, dass andere Anzeigetreiber deaktiviert sind
// Löschen Sie die Kommentarzeichen vor den folgenden Einstellungen und kommentieren Sie andere Display-Einstellungen aus
// #define ILI9341_DRIVER
// #define ILI9481_DRIVER
// #define ILI9486_DRIVER
// #define HX8357D_DRIVER
// usw.

// ##################### ENDE DER EINSTELLUNGEN #####################

#endif // USER_SETUP_LOADED