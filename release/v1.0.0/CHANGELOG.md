# SwissAirDry Changelog

Alle wichtigen Änderungen am SwissAirDry-Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
und dieses Projekt folgt [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2023-05-09

### Hinzugefügt
- Domainverwaltung mit Cloudflare API-Integration
- Umfassende DNS-Eintrags-Verwaltung
- Service-Mapping für verschiedene Anwendungskomponenten
- Automatisches Setup für mehrere Dienste
- Dunkles Design für die Benutzeroberfläche
- Installationsskripte für Linux/Mac und Windows
- System-Update-Skript für einfache Aktualisierungen
- Installations-Report-Generator

### Geändert
- Docker-Konfiguration verbessert (paho-mqtt auf Version 2.1.0 festgelegt)
- Verbesserte Fehlerbehandlung im BLE-Service für Umgebungen ohne Bluetooth-Hardware

### Behoben
- Fehler in Dockerfiles und docker-compose.yml
- BLE-Scanning-Fehler in virtuellen Umgebungen ohne Bluetooth-Hardware
- Verbesserte Fehlerbehandlung in MQTT-Verbindungen

## [0.9.0] - 2023-04-20

### Hinzugefügt
- BLE-Integration für automatische Geräteerkennung
- ESP32-Touchscreen-Integration
- Verbesserte Gerätemanagement-Funktionen
- QR-Code-Display für einfachen Zugriff

### Geändert
- Verbesserte Benutzeroberfläche mit dunklem Design
- Überarbeitete MQTT-Handler für bessere Zuverlässigkeit

### Behoben
- Probleme mit der Datenbankverbindung
- Fehler im MQTT-Nachrichtenformat

## [0.8.0] - 2023-03-15

### Hinzugefügt
- Nextcloud-Integration durch ExApp-Architektur
- Erweiterte API-Endpunkte für Gerätekontrolle
- Verbesserte Sensordaten-Visualisierung

### Geändert
- Verbesserte Docker-Konfiguration
- Optimierte Datenbankabfragen

### Behoben
- Fehler bei der Benutzerauthentifizierung
- Probleme mit der API-Dokumentation