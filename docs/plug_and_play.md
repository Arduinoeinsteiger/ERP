# SwissAirDry Plug & Play Installation

Diese Anleitung erklärt die vollautomatische Installation des SwissAirDry-Systems mit minimalem Aufwand.

## Was ist Plug & Play?

Die Plug & Play-Installation ist ein vollautomatischer Prozess, der das SwissAirDry-System mit minimalen Benutzereingriffen einrichtet. Der Benutzer muss nur ein Skript ausführen, und alles Weitere wird automatisch konfiguriert:

- Installation erforderlicher Abhängigkeiten
- Einrichtung der Docker-Umgebung
- Konfiguration aller Dienste
- Erstellung sicherer Zufallsschlüssel
- Portanpassung bei Konflikten
- Erstellung von Hilfsbefehlen
- Desktop-Verknüpfung (Windows)

## Installation unter Linux/Mac

### Voraussetzungen

- Internet-Verbindung
- Bash-Terminal
- Sudo-Rechte (werden während der Installation automatisch angefordert)

### Installation starten

```bash
wget -O - https://raw.githubusercontent.com/Arduinoeinsteiger/ERP/main/swissairdry-quickstart.sh | bash
```

Das Skript installiert alle notwendigen Abhängigkeiten und richtet das System ein. Sudo-Rechte werden bei Bedarf automatisch angefordert.

## Installation unter Windows

### Voraussetzungen

- Internet-Verbindung
- Administrator-Rechte

### Installationsschritte

1. Laden Sie [swissairdry-quickstart.bat](https://raw.githubusercontent.com/Arduinoeinsteiger/ERP/main/swissairdry-quickstart.bat) herunter
2. Rechtsklick auf die Datei → "Als Administrator ausführen"
3. Folgen Sie den Anweisungen auf dem Bildschirm

Nach der Installation wird eine Desktop-Verknüpfung erstellt, über die Sie die SwissAirDry-Plattform steuern können.

## Systemsteuerung

Nach der Installation stehen Ihnen folgende Steuerbefehle zur Verfügung:

### Linux/Mac

Das Skript installiert einen `swissairdry`-Befehl, den Sie global im Terminal nutzen können:

```bash
# Starten aller Dienste
swissairdry start

# Stoppen aller Dienste
swissairdry stop

# Neustart aller Dienste
swissairdry restart

# Status aller Dienste anzeigen
swissairdry status

# Logs anzeigen
swissairdry logs

# Auf die neueste Version aktualisieren
swissairdry update
```

### Windows

Unter Windows können Sie die Desktop-Verknüpfung "SwissAirDry Steuerung" doppelklicken, um die Befehle auszuführen, oder die Batch-Datei direkt aufrufen:

```
C:\SwissAirDry\swissairdry-control.bat start
C:\SwissAirDry\swissairdry-control.bat stop
C:\SwissAirDry\swissairdry-control.bat restart
C:\SwissAirDry\swissairdry-control.bat status
C:\SwissAirDry\swissairdry-control.bat logs
C:\SwissAirDry\swissairdry-control.bat update
```

## Automatische Anpassungen

Das Plug & Play-System nimmt verschiedene Anpassungen vor, um eine optimale Nutzererfahrung zu gewährleisten:

### Portanpassung

Wenn die Standardports (5000, 8000, 1883) bereits belegt sind, werden automatisch alternative Ports ausgewählt und dokumentiert.

### Bluetooth-Erkennung

Das System erkennt automatisch, ob Bluetooth-Hardware verfügbar ist, und informiert den Benutzer über den Status der BLE-Funktionalität.

### Automatische Aktualisierung

Die Update-Funktion sorgt dafür, dass Ihre SwissAirDry-Installation immer auf dem neuesten Stand ist.

## Zugriff auf das Web-Interface

Nach erfolgreicher Installation können Sie auf das Web-Interface über Ihren Browser zugreifen:

```
http://IP-ADRESSE:PORT
```

Die genaue URL wird am Ende der Installation angezeigt und ist typischerweise:

```
http://localhost:5000
```

oder

```
http://IP-ADRESSE:5000
```

## Fehlerbehebung

### Installation schlägt fehl

Wenn die automatische Installation fehlschlägt, werden detaillierte Logs angezeigt. Die häufigsten Probleme sind:

1. **Docker ist nicht installiert oder nicht gestartet**
   - Lösung: Installieren Sie Docker manuell und starten Sie den Docker-Dienst

2. **Ports sind blockiert**
   - Lösung: Beenden Sie Anwendungen, die die benötigten Ports (5000, 8000, 1883) verwenden

3. **Unzureichende Berechtigungen**
   - Lösung: Stellen Sie sicher, dass Sie das Skript mit Administrator- oder Root-Rechten ausführen

### Container starten nicht

Wenn die Container nicht starten:

```bash
# Linux/Mac
docker-compose logs

# Windows
docker-compose logs
```

### Web-Interface ist nicht erreichbar

1. Prüfen Sie, ob die Container laufen:
   ```bash
   docker-compose ps
   ```

2. Prüfen Sie die Logs:
   ```bash
   docker-compose logs api
   ```

3. Überprüfen Sie Firewall-Einstellungen und stellen Sie sicher, dass die benötigten Ports freigegeben sind.

## Deinstallation

### Linux/Mac

Um das System vollständig zu deinstallieren:

```bash
cd /opt/swissairdry
docker-compose down -v
cd ..
rm -rf /opt/swissairdry
rm /usr/local/bin/swissairdry
```

### Windows

Um das System vollständig zu deinstallieren:

1. Führen Sie `C:\SwissAirDry\swissairdry-control.bat stop` aus
2. Löschen Sie den Desktop-Shortcut
3. Löschen Sie den Ordner `C:\SwissAirDry`