# SwissAirDry Diamond App für Nextcloud

Diese Nextcloud-Integration ermöglicht die nahtlose Verbindung zwischen Nextcloud und der SwissAirDry-Plattform mithilfe des Diamond App-Pakets.

## Hauptfunktionen

- Dashboard-Widgets für SwissAirDry-Geräte
- Benachrichtigungen für Gerätestatus und Warnungen
- Dateifreigabe und -synchronisierung für Geräteprotokolle
- Benutzerverwaltung und Zugriffsberechtigungen
- Integration mit Nextcloud Calendar für geplante Aufgaben
- Mobile App-Unterstützung für Fernsteuerung

## Installation

1. Kopieren Sie das Diamond App-Paket in das Verzeichnis `/var/www/html/custom_apps`
2. Aktivieren Sie die App über die Nextcloud-Administratoroberfläche oder mit dem occ-Befehl
3. Konfigurieren Sie die Verbindungseinstellungen in den App-Einstellungen

## Konfiguration

Die Grundkonfiguration ist in der Datei `diamond.config.php` enthalten. Diese kann über die Nextcloud-Administrator-Oberfläche angepasst werden.

## Anforderungen

- Nextcloud 24 oder höher
- SwissAirDry API (Version 2.0 oder höher)
- PHP 8.0 oder höher mit Redis-Unterstützung
- MQTT-Broker-Zugangsdaten

## Support

Bei Fragen oder Problemen kontaktieren Sie das SwissAirDry-Supportteam.