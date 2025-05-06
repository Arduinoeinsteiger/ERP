# SwissAirDry BLE API Dokumentation

Diese Dokumentation beschreibt die REST-API-Endpunkte für die BLE-Funktionalität der SwissAirDry-Plattform.

## Allgemeines

Alle API-Endpunkte geben JSON-Antworten zurück. Erfolgreiche Antworten enthalten ein `success: true` Feld, während Fehlerantworten ein `success: false` und ein `error` Feld mit einer Fehlerbeschreibung enthalten.

## Endpunkte

### BLE-Geräte auflisten

Gibt eine Liste aller BLE-Geräte zurück, die von der Plattform erkannt wurden.

**URL:** `/api/ble/devices`

**Methode:** `GET`

**Erfolgreiche Antwort:**
```json
{
  "success": true,
  "devices": [
    {
      "id": 1,
      "device_id": "ble_112233445566",
      "name": "SwissAirDry BLE",
      "type": "esp32",
      "firmware_version": "1.0.0",
      "ble_address": "11:22:33:44:55:66",
      "ble_connected": true,
      "ble_rssi": -65,
      "is_online": true,
      "last_seen": "2025-05-06T18:32:45.123456"
    }
  ]
}
```

### Gerät einschalten/ausschalten

Schaltet ein Gerät ein oder aus.

**URL:** `/api/ble/device/{device_id}/power`

**Methode:** `POST`

**Parameter:**

| Name  | Typ     | Beschreibung                 |
|-------|---------|------------------------------|
| state | boolean | `true` für ein, `false` für aus |

**Beispielanfrage:**
```json
{
  "state": true
}
```

**Erfolgreiche Antwort:**
```json
{
  "success": true,
  "message": "Power-Befehl (true) erfolgreich gesendet"
}
```

### Lüftergeschwindigkeit einstellen

Stellt die Lüftergeschwindigkeit eines Geräts ein.

**URL:** `/api/ble/device/{device_id}/fan`

**Methode:** `POST`

**Parameter:**

| Name  | Typ    | Beschreibung                      |
|-------|--------|-----------------------------------|
| speed | integer | Lüftergeschwindigkeit (0-100%) |

**Beispielanfrage:**
```json
{
  "speed": 75
}
```

**Erfolgreiche Antwort:**
```json
{
  "success": true,
  "message": "Fan-Speed-Befehl (75%) erfolgreich gesendet"
}
```

### Aufgabe zuweisen

Weist einem Gerät eine Trocknungsaufgabe zu.

**URL:** `/api/ble/device/{device_id}/assign_task`

**Methode:** `POST`

**Parameter:**

| Name       | Typ    | Beschreibung                               |
|------------|--------|------------------------------------------|
| task_id    | integer | ID der zuzuweisenden Aufgabe            |
| start_time | string  | (Optional) ISO-Datums-/Zeitstring für geplanten Start |

**Beispielanfrage:**
```json
{
  "task_id": 42,
  "start_time": "2025-05-07T08:30:00"
}
```

**Erfolgreiche Antwort:**
```json
{
  "success": true,
  "message": "Aufgabe 42 erfolgreich zugewiesen"
}
```

## Fehlerbehandlung

Bei Fehlern gibt die API einen entsprechenden HTTP-Statuscode und eine JSON-Antwort mit Fehlerinformationen zurück.

**Beispiel Fehlerantwort:**
```json
{
  "success": false,
  "error": "Gerät mit ID 'abc123' nicht gefunden"
}
```

| Statuscode | Beschreibung                              |
|------------|------------------------------------------|
| 400        | Ungültige Anfrage (z.B. fehlende Parameter) |
| 404        | Ressource nicht gefunden (z.B. Gerät existiert nicht) |
| 500        | Serverfehler (z.B. BLE-Kommunikationsfehler) |