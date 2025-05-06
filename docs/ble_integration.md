# BLE Integration für SwissAirDry

Dieses Dokument beschreibt die BLE (Bluetooth Low Energy) Integration in die SwissAirDry-Plattform.

## Architektur

Die BLE-Integration besteht aus mehreren Komponenten:

1. **BLE Service** (`ble_service.py`): Zentrale Komponente für das Scannen, Verbinden und Kommunizieren mit BLE-Geräten.
2. **Device Manager** (`device_manager.py`): Verwaltet Geräte und koordiniert BLE- und MQTT-Kommunikation.
3. **API-Endpunkte** (`main.py`): REST-API-Endpunkte für BLE-Gerätesteuerung.
4. **Datenbank-Modelle** (`models.py`): Erweiterte Datenmodelle für BLE-spezifische Attribute.

## BLE Service

Der BLE-Service nutzt die `bleak`-Bibliothek und implementiert ein Singleton-Pattern. Seine Hauptfunktionen sind:

- Scannen nach BLE-Geräten in regelmäßigen Intervallen
- Automatisches Verbinden mit erkannten SwissAirDry-Geräten
- Verwaltung von BLE-Verbindungen mit Wiederverbindungsmechanismus
- Empfangen von Sensordaten über BLE-Benachrichtigungen
- Senden von Befehlen und Konfigurationen an verbundene Geräte

```python
# Singleton-Implementierung
_ble_service_instance = None

def get_ble_service() -> BLEService:
    """Gibt die Singleton-Instanz des BLE-Service zurück."""
    global _ble_service_instance
    if _ble_service_instance is None:
        _ble_service_instance = BLEService()
    return _ble_service_instance
```

## Device Manager Integration

Der Device Manager wurde um BLE-spezifische Funktionen erweitert:

- Registrieren von Callbacks für BLE-Ereignisse
- Verarbeiten von BLE-Gerätefunden und -verbindungen
- Weiterleiten von Sensordaten an die Datenbank
- Steuerungsfunktionen für BLE-Geräte (Ein/Aus, Lüftergeschwindigkeit, Konfiguration)

```python
async def initialize_ble(self):
    """Initialisiert den BLE-Service asynchron."""
    ble_service = get_ble_service()
    
    # Registriere Callbacks
    ble_service.register_callback("device_found", self._handle_ble_device_found)
    ble_service.register_callback("device_connected", self._handle_ble_device_connected)
    ble_service.register_callback("device_disconnected", self._handle_ble_device_disconnected)
    ble_service.register_callback("sensor_data", self._handle_ble_sensor_data)
    
    # Starte den BLE-Service
    await ble_service.start()
```

## Datenbank-Erweiterungen

Das Device-Modell wurde um folgende BLE-spezifische Felder erweitert:

- `ble_address`: BLE MAC-Adresse
- `ble_connected`: BLE-Verbindungsstatus
- `ble_rssi`: Signalstärke
- `ble_last_seen`: Zeitpunkt der letzten BLE-Erkennung

Diese Felder ermöglichen die Identifikation und Statusverfolgung von BLE-Geräten.

## API-Endpunkte

Die folgenden REST-API-Endpunkte wurden für die BLE-Integration hinzugefügt:

- `GET /api/ble/devices`: Liste aller BLE-Geräte abrufen
- `POST /api/ble/device/{device_id}/power`: Gerät ein-/ausschalten
- `POST /api/ble/device/{device_id}/fan`: Lüftergeschwindigkeit einstellen
- `POST /api/ble/device/{device_id}/assign_task`: Aufgabe einem Gerät zuweisen

Details zu diesen Endpunkten finden sich in der API-Dokumentation.

## Asynchrone Verarbeitung

Die BLE-Integration ist vollständig asynchron implementiert, um die Reaktionsfähigkeit der Anwendung zu gewährleisten:

- Der BLE-Service läuft in einem eigenen Thread mit asynchronem Event-Loop
- API-Endpunkte nutzen eigene Threads für asynchrone BLE-Operationen
- Die Anwendung startet und stoppt den BLE-Service korrekt bei Start und Beendigung

```python
# Start BLE service in a separate thread to not block the main thread
ble_thread = threading.Thread(target=start_ble_service, daemon=True)
ble_thread.start()
```

## Fehlerbehandlung

Die BLE-Integration enthält umfassende Fehlerbehandlung:

- Wiederverbindungsversuche mit exponentieller Verzögerung bei Verbindungsabbrüchen
- Timeout-Behandlung für BLE-Operationen
- Fallback-Logik für Umgebungen ohne BLE-Hardware (z.B. virtuelle Server)
- Umfangreiches Logging von BLE-Operationen und Fehlern

## Firmware-Anforderungen

Für die BLE-Integration müssen die Firmware-Anwendungen auf den ESP32/STM32-Geräten folgende Funktionen implementieren:

1. BLE-Werbung (Advertising) mit definiertem SwissAirDry-Dienstkennung
2. BLE-Dienstcharakteristiken für:
   - Geräteinformationen (Name, Typ, Firmware-Version)
   - Sensordaten (Temperatur, Feuchtigkeit, etc.)
   - Steuerung (Ein/Aus, Lüftergeschwindigkeit)
   - Konfiguration (Updateintervall, Display-Typ, etc.)
3. Benachrichtigungen für Statusänderungen und neue Sensordaten