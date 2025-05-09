# Release Notes: SwissAirDry v1.0.0

## Neue Funktionen: Domain-Management

Diese Version fügt die Domain-Management-Funktion mit Cloudflare-Integration hinzu. Mit dieser Funktion können Benutzer:

- Domains über die Cloudflare API verwalten
- DNS-Einträge hinzufügen, bearbeiten und löschen
- Services automatisch auf Domains mappen
- Subdomains für verschiedene Dienste konfigurieren
- HTTPS-Konfiguration für Dienste verwalten

## Technische Details

- Implementiert mit Flask, SQLAlchemy und Requests
- Vollständige Cloudflare API-Integration
- Datenbankmodelle für Domain-Zonen, DNS-Einträge und Service-Mappings
- Dunkles Design für alle UI-Komponenten
- Responsive Benutzeroberfläche

## Installationsanforderungen

- Python 3.8 oder höher
- Flask, SQLAlchemy und Requests Module
- Cloudflare API-Token (mit Zone-Berechtigungen)
- PostgreSQL-Datenbank

## Installationshinweise

Bitte folgen Sie der Anleitung in [README.md](README.md) für die Installation und Konfiguration.

## Bekannte Probleme

- In virtuellen Umgebungen ohne physische Bluetooth-Hardware ist die BLE-Funktionalität eingeschränkt.
- In einigen Docker-Konfigurationen muss die paho-mqtt-Version auf 2.1.0 festgelegt werden.

## Mitwirkende

- Entwickelt von Arduinoeinsteiger und Mitwirkenden

## Commit-Informationen

- Commit-Hash: f307b0c
- Release-Tag: ins