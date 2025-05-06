import paho.mqtt.client as mqtt
import time
import sys

# Callback bei erfolgreicher Verbindung
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Erfolgreich mit MQTT-Broker verbunden!")
        # Bei erfolgreicher Verbindung ein Topic abonnieren
        client.subscribe("swissairdry/test")
    else:
        print(f"Verbindung fehlgeschlagen mit Code {rc}")

# Callback bei Nachrichtenempfang
def on_message(client, userdata, msg):
    print(f"Nachricht empfangen auf {msg.topic}: {msg.payload.decode()}")

# Callback bei Verbindungsverlust
def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unerwarteter Verbindungsabbruch. Versuche neu zu verbinden...")
    else:
        print("Verbindung getrennt")

# MQTT-Client erstellen
client = mqtt.Client(client_id="mqtt-test-client")

# Callbacks registrieren
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

# Verbindung herstellen
host = "localhost"  # Standard-Host (lokaler Broker)
port = 1883  # Standard-Port für MQTT

print(f"Verbinde mit MQTT-Broker auf {host}:{port}...")

try:
    client.connect(host, port, 60)
    
    # MQTT-Loop starten, aber nicht blockieren
    client.loop_start()
    
    # Warten auf erfolgreiche Verbindung
    time.sleep(2)
    
    # Test-Nachricht veröffentlichen
    print("Sende Test-Nachricht...")
    result = client.publish("swissairdry/test", "Hallo von MQTT Test Script!", qos=1)
    
    # Warten bis die Nachricht gesendet wurde
    result.wait_for_publish()
    if result.is_published():
        print("Nachricht erfolgreich veröffentlicht!")
    else:
        print("Fehler beim Veröffentlichen der Nachricht")
    
    # Einige Zeit warten, um Nachrichten zu empfangen
    print("Warte auf Nachrichten...")
    time.sleep(3)
    
    # MQTT-Loop beenden
    client.loop_stop()
    client.disconnect()
    print("Test abgeschlossen.")
    
except Exception as e:
    print(f"Fehler: {e}")
    sys.exit(1)

sys.exit(0)