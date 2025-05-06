"""
SwissAirDry MicroPython Client für ESP32-S6
-------------------------------------------

Dieses Skript implementiert einen MQTT-Client für ESP32-S6 mit MicroPython.
Es sendet regelmäßig Sensor-Daten an den MQTT-Broker und reagiert auf Steuerungsbefehle.

Funktionen:
- Verbindung mit WLAN und MQTT-Broker
- Regelmäßige Übertragung von Sensordaten (Temperatur, Luftfeuchtigkeit, etc.)
- Empfang und Verarbeitung von Steuerungsbefehlen
- Automatische Wiederverbindung bei Verbindungsabbruch
- Stromsparfunktionen für längere Akkulaufzeit
"""

import time
import json
import network
import machine
import ubinascii
from machine import Pin, ADC, deepsleep, Timer
from umqtt.simple import MQTTClient

# Konfiguration
WIFI_SSID = "SwissAirDry-Network"
WIFI_PASSWORD = "SwissAirDry2025"

# MQTT-Konfiguration
MQTT_BROKER = "192.168.1.100"  # IP-Adresse des MQTT-Brokers
MQTT_PORT = 1883
MQTT_USER = ""  # Falls der Broker Authentifizierung benötigt
MQTT_PASSWORD = ""  # Falls der Broker Authentifizierung benötigt
MQTT_CLIENT_ID = "esp32s6_" + ubinascii.hexlify(machine.unique_id()).decode()

# MQTT-Topics
DEVICE_ID = "ESP32S6_001"  # Eindeutige Geräte-ID
TOPIC_STATUS = f"swissairdry/{DEVICE_ID}/status"
TOPIC_TELEMETRY = f"swissairdry/{DEVICE_ID}/telemetry"
TOPIC_COMMAND = f"swissairdry/{DEVICE_ID}/command"
TOPIC_CONFIG = f"swissairdry/{DEVICE_ID}/config"

# Sensor-Pins
SENSOR_DHT = 12   # GPIO-Pin für DHT-Sensor
SENSOR_BATTERY = 33  # ADC-Pin für Batteriespannung

# Status-LED
LED_PIN = 2  # Builtin LED

# Globale Variablen
led = None
mqtt_client = None
timer = None
config = {
    "sleep_time": 300,  # Schlafzeit in Sekunden (Standard: 5 Minuten)
    "report_interval": 60,  # Datenübertragungsintervall in Sekunden (Standard: 1 Minute)
    "voltage_factor": 2.0,  # Faktor für Spannungsteiler
    "low_power_mode": False  # Energiesparmodus
}
is_connected = False
last_report_time = 0

# LED für Status-Anzeigen
def setup_led():
    global led
    led = Pin(LED_PIN, Pin.OUT)
    led.off()

# LED-Blinkmuster für verschiedene Status
def blink_led(count, delay_ms=200):
    for i in range(count):
        led.on()
        time.sleep_ms(delay_ms)
        led.off()
        if i < count - 1:
            time.sleep_ms(delay_ms)

# WiFi-Verbindung herstellen
def connect_wifi():
    print(f"Verbinde mit WLAN: {WIFI_SSID}")
    # Status-LED schnell blinken während Verbindungsaufbau
    blink_led(3, 100)
    
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        
        # Maximal 20 Sekunden auf Verbindung warten
        max_attempts = 20
        attempt = 0
        
        while not wlan.isconnected() and attempt < max_attempts:
            print(f"Warte auf WLAN-Verbindung... ({attempt+1}/{max_attempts})")
            attempt += 1
            # LED kurz blinken lassen
            led.on()
            time.sleep_ms(50)
            led.off()
            time.sleep_ms(950)  # Fast 1 Sekunde Pause
        
    if wlan.isconnected():
        print(f"WLAN verbunden. IP: {wlan.ifconfig()[0]}")
        # Bei erfolgreicher Verbindung zweimal blinken
        blink_led(2, 200)
        return True
    else:
        print("WLAN-Verbindung fehlgeschlagen")
        # Bei fehlgeschlagener Verbindung 5-mal schnell blinken
        blink_led(5, 100)
        return False

# MQTT-Verbindung herstellen
def connect_mqtt():
    global mqtt_client, is_connected
    print(f"Verbinde mit MQTT-Broker: {MQTT_BROKER}")
    
    try:
        client = MQTTClient(
            MQTT_CLIENT_ID, 
            MQTT_BROKER, 
            port=MQTT_PORT,
            user=MQTT_USER, 
            password=MQTT_PASSWORD,
            keepalive=30
        )
        
        # Callback für empfangene Nachrichten
        client.set_callback(on_mqtt_message)
        client.connect()
        
        # Subscriben auf Kommando- und Konfigurations-Topic
        client.subscribe(TOPIC_COMMAND)
        client.subscribe(TOPIC_CONFIG)
        
        # Status-Nachricht senden
        send_status(client, "online")
        
        mqtt_client = client
        is_connected = True
        print("MQTT-Verbindung hergestellt")
        
        # Bei erfolgreicher Verbindung einmal länger blinken
        led.on()
        time.sleep_ms(500)
        led.off()
        
        return True
    except Exception as e:
        print(f"MQTT-Verbindungsfehler: {e}")
        # Bei Fehler 3-mal blinken
        blink_led(3, 300)
        is_connected = False
        return False

# MQTT-Callback-Funktion
def on_mqtt_message(topic, msg):
    topic = topic.decode('utf-8')
    msg = msg.decode('utf-8')
    print(f"MQTT-Nachricht empfangen: {topic} = {msg}")
    
    try:
        if topic == TOPIC_COMMAND:
            handle_command(msg)
        elif topic == TOPIC_CONFIG:
            handle_config(msg)
    except Exception as e:
        print(f"Fehler bei der Verarbeitung der MQTT-Nachricht: {e}")

# Verarbeitung von Kommandos
def handle_command(message):
    try:
        command = json.loads(message)
        
        if "action" in command:
            action = command["action"]
            
            if action == "restart":
                print("Neustart wird durchgeführt...")
                machine.reset()
            elif action == "sleep":
                duration = command.get("duration", config["sleep_time"])
                print(f"Gehe in Deep-Sleep für {duration} Sekunden...")
                deepsleep(duration * 1000)
            elif action == "led_on":
                led.on()
                print("LED eingeschaltet")
            elif action == "led_off":
                led.off()
                print("LED ausgeschaltet")
            elif action == "blink":
                count = command.get("count", 3)
                delay = command.get("delay", 200)
                blink_led(count, delay)
                print(f"LED blinkt {count} mal")
    except Exception as e:
        print(f"Fehler bei der Verarbeitung des Kommandos: {e}")

# Verarbeitung von Konfigurationsänderungen
def handle_config(message):
    global config
    
    try:
        new_config = json.loads(message)
        
        # Konfiguration aktualisieren
        for key, value in new_config.items():
            if key in config:
                config[key] = value
                print(f"Konfiguration aktualisiert: {key} = {value}")
        
        # Bestätigung senden
        if mqtt_client:
            config_response = {"status": "updated", "config": config}
            mqtt_client.publish(
                TOPIC_CONFIG + "/response", 
                json.dumps(config_response)
            )
    except Exception as e:
        print(f"Fehler bei der Verarbeitung der Konfiguration: {e}")

# Status an den MQTT-Broker senden
def send_status(client, status):
    try:
        status_data = {
            "device_id": DEVICE_ID,
            "status": status,
            "timestamp": time.time(),
            "ip": network.WLAN(network.STA_IF).ifconfig()[0],
            "firmware": "MicroPython-SwissAirDry-1.0.0",
            "rssi": network.WLAN(network.STA_IF).status('rssi'),
            "uptime": time.ticks_ms() // 1000,  # Sekunden seit dem letzten Neustart
            "battery": read_battery_level(),
            "config": config
        }
        
        client.publish(TOPIC_STATUS, json.dumps(status_data))
        print(f"Status '{status}' gesendet")
    except Exception as e:
        print(f"Fehler beim Senden des Status: {e}")

# Lesen der Sensordaten
def read_sensors():
    # Hier würde normalerweise der tatsächliche Sensor ausgelesen werden
    # Für diesen Beispielcode simulieren wir die Daten
    import random
    
    return {
        "temperature": 20 + random.random() * 10,  # 20-30°C
        "humidity": 30 + random.random() * 50,     # 30-80%
        "pressure": 980 + random.random() * 40,    # 980-1020 hPa
        "battery": read_battery_level()
    }

# Batteriespannungsmessung
def read_battery_level():
    try:
        adc = ADC(Pin(SENSOR_BATTERY))
        # ESP32-S6 hat 12-bit ADC (0-4095)
        adc.atten(ADC.ATTN_11DB)  # Vollbereichseinstellung für 0-3.3V
        
        # Mehrfachmessung für bessere Genauigkeit
        value = 0
        samples = 10
        
        for _ in range(samples):
            value += adc.read()
            time.sleep_ms(10)
        
        value = value / samples
        
        # Umrechnung in Volt (abhängig vom genauen Board und Spannungsteiler)
        voltage = (value / 4095) * 3.3 * config["voltage_factor"]
        
        # Batterieprozentsatz berechnen (Annahme: LiPo 3.7V)
        # Entladen: ~3.2V, Voll: ~4.2V
        percentage = 100 * min(1.0, max(0.0, (voltage - 3.2) / (4.2 - 3.2)))
        
        return {
            "voltage": round(voltage, 2),
            "percentage": round(percentage, 1)
        }
    except Exception as e:
        print(f"Fehler beim Lesen der Batteriespannung: {e}")
        return {"voltage": 0, "percentage": 0}

# Daten regelmäßig senden
def report_data():
    global last_report_time
    
    current_time = time.time()
    
    # Prüfen, ob es Zeit ist, Daten zu senden
    if current_time - last_report_time >= config["report_interval"]:
        try:
            if mqtt_client and is_connected:
                # LED kurz aufleuchten lassen während der Datenübertragung
                led.on()
                
                # Sensordaten lesen
                sensor_data = read_sensors()
                
                # Telemetrie-Daten senden
                telemetry_data = {
                    "device_id": DEVICE_ID,
                    "timestamp": current_time,
                    "sensors": sensor_data
                }
                
                mqtt_client.publish(TOPIC_TELEMETRY, json.dumps(telemetry_data))
                print(f"Telemetriedaten gesendet: {sensor_data}")
                
                # LED ausschalten
                led.off()
                
                # Zeit der letzten Übertragung aktualisieren
                last_report_time = current_time
        except Exception as e:
            print(f"Fehler beim Senden der Daten: {e}")
            # Verbindung als verloren markieren
            is_connected = False

# Timer-Callback für regelmäßige Aktionen
def timer_callback(timer):
    try:
        # MQTT-Verbindung prüfen und ggf. wiederherstellen
        if mqtt_client is None or not is_connected:
            connect_mqtt()
        
        # Daten senden, wenn verbunden
        if is_connected:
            # MQTT-Client-Loop ausführen, um Nachrichten zu empfangen
            mqtt_client.check_msg()
            
            # Daten senden, wenn das Intervall erreicht ist
            report_data()
    except Exception as e:
        print(f"Fehler im Timer-Callback: {e}")

# Hauptprogramm
def main():
    global timer, last_report_time
    
    try:
        print("\n--- SwissAirDry MicroPython Client für ESP32-S6 ---")
        print(f"Geräte-ID: {DEVICE_ID}")
        print(f"MQTT Client-ID: {MQTT_CLIENT_ID}")
        
        # LED einrichten
        setup_led()
        
        # Einmalig schnell blinken zum Anzeigen des Startvorgangs
        blink_led(5, 100)
        
        # Mit WLAN verbinden
        if not connect_wifi():
            # Bei fehlgeschlagener Verbindung in den Deep-Sleep gehen und später neu versuchen
            print(f"Gehe für {config['sleep_time']} Sekunden in Deep-Sleep und versuche erneut...")
            deepsleep(config["sleep_time"] * 1000)
        
        # Mit MQTT-Broker verbinden
        connect_mqtt()
        
        # Aktuelle Zeit für Reporting speichern
        last_report_time = time.time()
        
        # Timer für regelmäßige Aktionen einrichten (alle 5 Sekunden)
        timer = Timer(0)
        timer.init(period=5000, mode=Timer.PERIODIC, callback=timer_callback)
        
        # Initialer Datenbericht
        report_data()
        
        print("Setup abgeschlossen. Gerät läuft...")
        
        # Haupt-Loop
        while True:
            # Meiste Arbeit wird vom Timer erledigt
            # Hier können zusätzliche Aufgaben ausgeführt werden
            time.sleep(1)
            
    except Exception as e:
        print(f"Unbehandelter Fehler: {e}")
        # Bei kritischem Fehler neu starten
        machine.reset()

# Programm starten
if __name__ == "__main__":
    main()