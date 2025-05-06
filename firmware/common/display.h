/**
 * SwissAirDry Display Handler
 * 
 * This file contains the display implementation for SwissAirDry devices.
 * It supports different display types (64px and 128px OLEDs).
 */

#ifndef SWISSAIRDRY_DISPLAY_H
#define SWISSAIRDRY_DISPLAY_H

#include <Arduino.h>
#include <U8g2lib.h>
#include <Wire.h>

// Display types
#define DISPLAY_NONE 0
#define DISPLAY_64PX 1
#define DISPLAY_128PX 2

class SwissAirDryDisplay {
private:
    int displayType = DISPLAY_NONE;
    U8G2* display = nullptr;
    
    // Display buffer for messages
    static const int MESSAGE_BUFFER_SIZE = 5;
    String messageBuffer[MESSAGE_BUFFER_SIZE];
    unsigned long messageTimestamp[MESSAGE_BUFFER_SIZE];
    int messageIndex = 0;
    
    // Power state
    bool powerState = false;
    
    // Animation frame for loading/connecting
    int animationFrame = 0;
    unsigned long lastAnimationUpdate = 0;
    bool isLoading = false;
    
    // Screen saver
    unsigned long lastUserAction = 0;
    bool screenSaverActive = false;
    static const unsigned long SCREEN_SAVER_TIMEOUT = 300000; // 5 minutes
    
    void createDisplay() {
        if (display != nullptr) {
            delete display;
        }
        
        switch (displayType) {
            case DISPLAY_64PX:
                // SSD1306 64x48 OLED display with I2C
                display = new U8G2_SSD1306_64X48_ER_F_HW_I2C(U8G2_R0, /* reset=*/ U8X8_PIN_NONE);
                break;
            case DISPLAY_128PX:
                // SSD1306 128x64 OLED display with I2C
                display = new U8G2_SSD1306_128X64_NONAME_F_HW_I2C(U8G2_R0, /* reset=*/ U8X8_PIN_NONE);
                break;
            default:
                // No display
                display = nullptr;
                break;
        }
        
        if (display != nullptr) {
            display->begin();
            display->setFont(u8g2_font_6x10_tf);
            display->setDrawColor(1);
            display->setFontPosTop();
        }
    }
    
    void addMessage(String message) {
        messageBuffer[messageIndex] = message;
        messageTimestamp[messageIndex] = millis();
        messageIndex = (messageIndex + 1) % MESSAGE_BUFFER_SIZE;
        lastUserAction = millis(); // Reset screen saver timer
        screenSaverActive = false;
    }
    
public:
    SwissAirDryDisplay() {
        // Default constructor
    }
    
    ~SwissAirDryDisplay() {
        if (display != nullptr) {
            delete display;
        }
    }
    
    void init(int type) {
        displayType = type;
        createDisplay();
        
        if (display != nullptr) {
            display->clearBuffer();
            display->drawStr(0, 0, "Initializing...");
            display->sendBuffer();
        }
        
        lastUserAction = millis();
    }
    
    void loop() {
        if (displayType == DISPLAY_NONE || display == nullptr) {
            return;
        }
        
        // Handle screen saver
        if (!screenSaverActive && millis() - lastUserAction > SCREEN_SAVER_TIMEOUT) {
            screenSaverActive = true;
            // Show minimal info or turn off display
            if (displayType == DISPLAY_128PX) {
                display->clearBuffer();
                display->drawStr(0, 0, "zZz");
                display->sendBuffer();
            } else {
                display->clearBuffer();
                display->sendBuffer();
            }
        }
        
        // Update animations if needed
        if (isLoading && !screenSaverActive) {
            if (millis() - lastAnimationUpdate > 250) {
                lastAnimationUpdate = millis();
                animationFrame = (animationFrame + 1) % 4;
                
                // Redraw connecting animation
                display->clearBuffer();
                
                if (displayType == DISPLAY_128PX) {
                    display->drawStr(0, 0, "Connecting");
                    display->drawStr(70, 0, animationFrame == 0 ? "|" : 
                                          animationFrame == 1 ? "/" : 
                                          animationFrame == 2 ? "-" : "\\");
                    
                    // Draw a simple progress bar
                    display->drawFrame(0, 20, 128, 10);
                    display->drawBox(0, 20, animationFrame * 32, 10);
                } else {
                    display->drawStr(0, 0, "Conn");
                    display->drawStr(40, 0, animationFrame == 0 ? "|" : 
                                         animationFrame == 1 ? "/" : 
                                         animationFrame == 2 ? "-" : "\\");
                }
                
                display->sendBuffer();
            }
        }
    }
    
    void showBootScreen(String deviceName, String firmwareVersion, String hardwareVersion) {
        if (displayType == DISPLAY_NONE || display == nullptr) {
            return;
        }
        
        display->clearBuffer();
        
        if (displayType == DISPLAY_128PX) {
            display->setFont(u8g2_font_8x13_tf);
            display->drawStr(0, 0, "SwissAirDry");
            display->setFont(u8g2_font_6x10_tf);
            display->drawStr(0, 16, deviceName.c_str());
            display->drawStr(0, 28, ("FW: " + firmwareVersion).c_str());
            display->drawStr(0, 40, ("HW: " + hardwareVersion).c_str());
        } else {
            display->setFont(u8g2_font_6x10_tf);
            display->drawStr(0, 0, "SwissAirDry");
            display->drawStr(0, 12, ("FW:" + firmwareVersion).c_str());
            display->drawStr(0, 24, ("HW:" + hardwareVersion).c_str());
        }
        
        display->sendBuffer();
        lastUserAction = millis();
        delay(2000); // Show boot screen for 2 seconds
    }
    
    void showConnecting() {
        if (displayType == DISPLAY_NONE || display == nullptr) {
            return;
        }
        
        display->clearBuffer();
        
        if (displayType == DISPLAY_128PX) {
            display->drawStr(0, 0, "Connecting to WiFi...");
        } else {
            display->drawStr(0, 0, "WiFi...");
        }
        
        display->sendBuffer();
        isLoading = true;
        lastUserAction = millis();
    }
    
    void showConnected(String ipAddress) {
        if (displayType == DISPLAY_NONE || display == nullptr) {
            return;
        }
        
        isLoading = false;
        display->clearBuffer();
        
        if (displayType == DISPLAY_128PX) {
            display->drawStr(0, 0, "Connected");
            display->drawStr(0, 16, ipAddress.c_str());
        } else {
            display->drawStr(0, 0, "OK");
            display->drawStr(0, 12, ipAddress.c_str());
        }
        
        display->sendBuffer();
        lastUserAction = millis();
        delay(2000); // Show for 2 seconds
    }
    
    void showError(String errorMessage) {
        if (displayType == DISPLAY_NONE || display == nullptr) {
            return;
        }
        
        isLoading = false;
        display->clearBuffer();
        
        if (displayType == DISPLAY_128PX) {
            display->drawStr(0, 0, "Error:");
            display->drawStr(0, 16, errorMessage.c_str());
        } else {
            display->drawStr(0, 0, "Err:");
            
            // Scrolling for long messages on small displays
            if (errorMessage.length() > 10) {
                display->drawStr(0, 12, errorMessage.substring(0, 10).c_str());
                display->drawStr(0, 24, errorMessage.substring(10).c_str());
            } else {
                display->drawStr(0, 12, errorMessage.c_str());
            }
        }
        
        display->sendBuffer();
        lastUserAction = millis();
    }
    
    void showMessage(String message) {
        if (displayType == DISPLAY_NONE || display == nullptr) {
            return;
        }
        
        addMessage(message);
        
        display->clearBuffer();
        
        if (displayType == DISPLAY_128PX) {
            display->drawStr(0, 0, "Message:");
            display->drawStr(0, 16, message.c_str());
        } else {
            display->drawStr(0, 0, "Msg:");
            
            // Scrolling for long messages on small displays
            if (message.length() > 10) {
                display->drawStr(0, 12, message.substring(0, 10).c_str());
                display->drawStr(0, 24, message.substring(10).c_str());
            } else {
                display->drawStr(0, 12, message.c_str());
            }
        }
        
        display->sendBuffer();
        lastUserAction = millis();
    }
    
    void showSensorData(float temperature, float humidity, int fanSpeed) {
        if (displayType == DISPLAY_NONE || display == nullptr) {
            return;
        }
        
        display->clearBuffer();
        
        char tempStr[10];
        char humStr[10];
        char fanStr[10];
        
        sprintf(tempStr, "%.1f°C", temperature);
        sprintf(humStr, "%.1f%%", humidity);
        sprintf(fanStr, "Fan: %d%%", fanSpeed);
        
        if (displayType == DISPLAY_128PX) {
            display->drawStr(0, 0, "Temperature:");
            display->drawStr(80, 0, tempStr);
            
            display->drawStr(0, 16, "Humidity:");
            display->drawStr(80, 16, humStr);
            
            display->drawStr(0, 32, fanStr);
            
            display->drawStr(0, 48, powerState ? "Power: ON" : "Power: OFF");
        } else {
            display->drawStr(0, 0, "T:");
            display->drawStr(16, 0, tempStr);
            
            display->drawStr(0, 12, "H:");
            display->drawStr(16, 12, humStr);
            
            display->drawStr(0, 24, fanStr);
            
            display->drawStr(0, 36, powerState ? "ON" : "OFF");
        }
        
        display->sendBuffer();
        lastUserAction = millis();
    }
    
    void showAdditionalData(float pressure, float powerConsumption) {
        if (displayType != DISPLAY_128PX || display == nullptr) {
            return; // Only for 128px displays
        }
        
        // Save current buffer
        uint8_t* buffer = display->getBufferPtr();
        uint8_t tempBuffer[128 * 64 / 8]; // Buffer size for 128x64 display
        memcpy(tempBuffer, buffer, 128 * 64 / 8);
        
        char pressureStr[15];
        char powerStr[15];
        
        sprintf(pressureStr, "%.1f hPa", pressure);
        sprintf(powerStr, "%.1f W", powerConsumption);
        
        // Add additional data to the bottom
        display->drawStr(80, 32, pressureStr);
        display->drawStr(80, 48, powerStr);
        
        display->sendBuffer();
        lastUserAction = millis();
    }
    
    void showFanSpeed(int speed) {
        if (displayType == DISPLAY_NONE || display == nullptr) {
            return;
        }
        
        char speedStr[20];
        sprintf(speedStr, "Fan Speed: %d%%", speed);
        
        display->clearBuffer();
        
        if (displayType == DISPLAY_128PX) {
            display->setFont(u8g2_font_8x13_tf);
            display->drawStr(0, 0, "Fan Control");
            display->setFont(u8g2_font_6x10_tf);
            display->drawStr(0, 20, speedStr);
            
            // Draw progress bar
            display->drawFrame(0, 32, 100, 10);
            display->drawBox(0, 32, speed, 10);
        } else {
            display->drawStr(0, 0, "Fan");
            display->drawStr(0, 12, speedStr);
            
            // Draw mini progress bar
            display->drawFrame(0, 24, 60, 8);
            display->drawBox(0, 24, speed * 60 / 100, 8);
        }
        
        display->sendBuffer();
        lastUserAction = millis();
    }
    
    void showPowerState(bool state) {
        if (displayType == DISPLAY_NONE || display == nullptr) {
            return;
        }
        
        powerState = state;
        
        display->clearBuffer();
        
        if (displayType == DISPLAY_128PX) {
            display->setFont(u8g2_font_8x13_tf);
            display->drawStr(0, 0, "Power Control");
            display->setFont(u8g2_font_6x10_tf);
            display->drawStr(0, 20, state ? "State: ON" : "State: OFF");
            
            // Draw power icon
            if (state) {
                display->drawCircle(64, 40, 15);
                display->drawLine(64, 25, 64, 40);
            } else {
                display->drawCircle(64, 40, 15);
            }
        } else {
            display->drawStr(0, 0, "Power");
            display->drawStr(0, 16, state ? "ON" : "OFF");
            
            // Draw simple power icon
            if (state) {
                display->drawCircle(48, 16, 8);
                display->drawLine(48, 8, 48, 16);
            } else {
                display->drawCircle(48, 16, 8);
            }
        }
        
        display->sendBuffer();
        lastUserAction = millis();
    }
};

#endif // SWISSAIRDRY_DISPLAY_H
