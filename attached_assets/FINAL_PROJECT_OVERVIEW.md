# SwissAirDry Projekt - Abschlussbericht

## Projektarchitektur

Die SwissAirDry-Plattform ist eine umfassende IoT-Lösung für die Überwachung und Steuerung von Trocknungsgeräten, mit folgender Architektur:

### Komponenten

1. **FastAPI Backend (Port 5000)**
   - REST API für Geräteverwaltung, Alarmverarbeitung und Reporting
   - PostgreSQL-Datenbankintegration für persistente Speicherung
   - MQTT-Client für bidirektionale Kommunikation mit Geräten
   - Dashboard-Endpunkte für zusammengefasste Daten

2. **Simple API (Port 5001)**
   - Vereinfachte API für ressourcenbeschränkte Geräte
   - MQTT-Kommunikation ohne Datenbank-Overhead
   - Optimiert für ESP32/ESP8266-Geräte

3. **MQTT Broker (Port 1883/9001)**
   - Mosquitto-basierter MQTT-Server
   - WebSocket-Unterstützung (Port 9001)
   - Strukturierte Topics (swissairdry/{device_id}/{topic})
   - QoS-Konfiguration für zuverlässige Nachrichtenübermittlung

4. **Nextcloud ExApp (Port 8080)**
   - Vollständige Integration in Nextcloud-Umgebung
   - Vue 3-basiertes Frontend mit reaktivem Design
   - Deck-Integration für Alarmmanagement
   - Moderne ExApp-Architektur mit eigenem Daemon (Port 8701)

5. **IoT-Geräte**
   - ESP32-C6-Unterstützung mit MicroPython
   - ESP8266-Kompatibler Arduino-Code
   - Robuste MQTT-Konnektivität mit automatischer Wiederverbindung
   - Konfigurierbare Sensorik und Telemetrie

### Netzwerk-Architektur

```
+----------------------+     +---------------------+     +------------------------+
|   IoT-Geräte         |     | SwissAirDry API    |     | Nextcloud ExApp        |
| (ESP32, ESP8266)     |<--->| (FastAPI, Port 5000)|<--->| (Vue.js, Port 8080)    |
+----------------------+     +---------------------+     +------------------------+
          ^                          ^                           ^
          |                          |                           |
          v                          v                           v
+----------------------+     +---------------------+     +------------------------+
| MQTT Broker          |<--->| Simple API          |     | ExApp Daemon           |
| (Mosquitto,Port 1883)|     | (FastAPI, Port 5001)|     | (Python, Port 8701)    |
+----------------------+     +---------------------+     +------------------------+
                                      ^                           ^
                                      |                           |
                                      v                           v
                             +---------------------+     +------------------------+
                             | PostgreSQL          |     | Deck Integration       |
                             | (Port 5432)         |     | (Nextcloud API)        |
                             +---------------------+     +------------------------+
```

## Domain-Konfiguration

Die Anwendung ist über folgende Domains zugänglich:

- **vgnc.org**: Hauptwebsite
- **api.vgnc.org**: SwissAirDry API
- **talk.vgnc.org**: Kommunikationsplattform

Alle Domains sind über IPv4 (83.78.73.133) und IPv6 (2a02:1210:3a07:2700:3ea8:2aff:fe9f:a9c) erreichbar und werden durch Cloudflare proxied.

## Port-Zuweisung

| Port | Dienst                 | Beschreibung                                  |
|------|------------------------|-----------------------------------------------|
| 80   | HTTP                   | Standard-Webzugriff                           |
| 443  | HTTPS                  | Verschlüsselter Webzugriff                    |
| 1883 | MQTT                   | MQTT-Broker für Gerätekommunikation           |
| 5000 | SwissAirDry API        | Hauptschnittstelle für Clients und Geräte     |
| 5001 | Simple API             | Vereinfachte API für ESP-Geräte               |
| 5432 | PostgreSQL             | Datenbankserver für persistente Speicherung   |
| 8080 | Nextcloud              | Nextcloud-Weboberfläche                       |
| 8701 | ExApp Daemon           | Daemon für die Nextcloud-ExApp                |
| 9001 | MQTT WebSocket         | Websocket-Zugriff auf MQTT                    |

## Technische Highlights

### 1. MQTT-Implementierung

Die MQTT-Kommunikation wurde mit folgenden Verbesserungen implementiert:

- **Robuste Verbindung**: Automatische Wiederverbindung mit Exponential Backoff
- **Eindeutige Client-IDs**: Generierung von kollisionsfreien Client-IDs
- **Strukturierte Topics**: Hierarchische Topic-Struktur für effiziente Filterung
- **QoS-Konfiguration**: Anpassbare QoS-Level je nach Nachrichtenpriorität

### 2. API-Design

Das API-Design folgt modernen Best-Practices:

- **RESTful Design**: Klare Endpunkte und HTTP-Methoden
- **OpenAPI-Dokumentation**: Automatisch generierte API-Dokumentation
- **Pydantic-Validierung**: Strenge Typisierung und Validierung aller Daten
- **Async-Unterstützung**: FastAPI mit asynchroner Verarbeitung für hohe Performance

### 3. Nextcloud-Integration

Die Integration in Nextcloud nutzt moderne Technologien:

- **ExApp-Architektur**: Konform mit neuesten Nextcloud-Standards (v26+)
- **Vue 3 Composition API**: Modernes reaktives Frontend
- **Deck-Integration**: Nahtlose Integrationen mit Nextcloud-Subsystemen
- **OCS-Kompatibilität**: Nutzung der offiziellen Nextcloud-APIs

### 4. ESP32/ESP8266-Support

Die Unterstützung für Mikrocontroller wurde verbessert:

- **MicroPython**: Alternative zu Arduino für ESP32-C6
- **Modulares Design**: Getrennte Module für verschiedene Funktionen
- **Konfigurierbarkeit**: JSON-basierte Konfiguration für einfache Anpassungen
- **Optimierter Energieverbrauch**: Deep-Sleep-Modi für Batteriegeräte

## Nächste Entwicklungsschritte

1. **Benutzerauthentifizierung**: Implementierung von OAuth2 mit JWT-Tokens
2. **Mobile App**: Entwicklung einer nativen Android-App mit entsprechender API-Anbindung
3. **Erweiterte Analysen**: Implementierung von Zeitreihenanalysen und Vorhersagemodellen
4. **Mehrsprachige Unterstützung**: Internationalisierung der Benutzeroberfläche
5. **Multi-Mandantenfähigkeit**: Unterstützung für mehrere Organisationen in einer Installation

## Fazit

Das SwissAirDry-Projekt wurde erfolgreich mit einer modularen, skalierbaren Architektur implementiert. Die wichtigsten Komponenten sind:

1. Eine leistungsstarke FastAPI-Backend-API für Geräteverwaltung und Datenverarbeitung
2. Eine robuste MQTT-Infrastruktur für zuverlässige Gerätekommunikation
3. Eine moderne Nextcloud-Integration für nahtlose Zusammenarbeit
4. Eine optimierte Firmware für ESP32/ESP8266-basierte IoT-Geräte

Diese Komponenten bilden zusammen eine umfassende Lösung für die Überwachung und Steuerung von Trocknungsgeräten in unterschiedlichen Umgebungen.