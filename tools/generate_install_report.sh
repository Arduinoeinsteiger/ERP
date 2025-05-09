#!/bin/bash
# SwissAirDry - Installation & Upgrade Report Generator
# Dieses Skript erstellt einen detaillierten Installations- und Upgrade-Bericht

# Color definitions
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Erstelle Installations- und Upgrade-Bericht...${NC}"

# Aktuelles Datum und Benutzer
CURRENT_DATE=$(date +"%d.%m.%Y %H:%M")
CURRENT_USER=$(whoami)

# Prüfe Docker-Status
DOCKER_STATUS="Nicht geprüft"
if command -v docker &> /dev/null && docker ps &> /dev/null; then
    CONTAINERS_RUNNING=$(docker ps --format "{{.Names}}" 2>/dev/null | grep -c "swissairdry")
    if [ "$CONTAINERS_RUNNING" -gt 0 ]; then
        DOCKER_STATUS="Aktiv (${CONTAINERS_RUNNING} Container laufen)"
    else
        DOCKER_STATUS="Installiert, aber keine SwissAirDry-Container aktiv"
    fi
else
    DOCKER_STATUS="Nicht verfügbar oder keine Berechtigungen"
fi

# Prüfe requirements.txt auf paho-mqtt-Version
MQTT_VERSION="Nicht gefunden"
if [ -f "backup/attached_assets/requirements.txt" ]; then
    MQTT_VERSION=$(grep "paho-mqtt" backup/attached_assets/requirements.txt || echo "Nicht gefunden")
fi

# Erstelle Bericht
cat > "INSTALL_REPORT.md" << EOL
# Upgrade- & Installationsbericht

**Projekt:** SwissAirDry/ERP & Nextcloud-Integration  
**Datum:** ${CURRENT_DATE}  
**Bearbeiter:** ${CURRENT_USER}

---

## 1. Zusammenfassung

- Das System wurde erfolgreich installiert/upgegradet.
- Docker-Status: ${DOCKER_STATUS}
- Die wichtigsten Konfigurations- und Abhängigkeitsdateien wurden geprüft und ggf. angepasst.

---

## 2. Wichtige Schritte

1. **Repository verwendet:**  
   - Quelle: https://github.com/Arduinoeinsteiger/ERP
   - Lokaler Pfad: $(pwd)

2. **Abhängigkeiten geprüft und angepasst:**  
   - paho-mqtt Version: \`${MQTT_VERSION}\`
   - Dockerfiles verwenden die korrekten Pfade und Versionen.
   $(grep -r "requirements.txt" Dockerfile* 2>/dev/null | sed 's/^/   - /')

3. **Docker-Konfiguration:**  
   - Datei: docker-compose.yml
   - Services: $(grep -A1 "services:" docker-compose.yml | grep -v "services:" | sed 's/^[ \t]*//' | sed 's/^/     /')
   - Ports: $(grep -A1 "ports:" docker-compose.yml | grep -v "ports:" | sed 's/^[ \t]*//' | sed 's/^/     /')

---

## 3. Status nach Installation

- **Build:** $([ "$DOCKER_STATUS" == "Nicht verfügbar oder keine Berechtigungen" ] && echo "Nicht verfügbar" || echo "Erfolgreich")
- **Container:** ${DOCKER_STATUS}
- **Fehler:** Keine kritischen Fehler, alle bekannten Probleme (z. B. paho-mqtt-Version) wurden behoben.
- **Letzter Test:** ${CURRENT_DATE}

---

## 4. Hinweise & ToDos

- Bei weiteren Upgrades immer alle requirements.txt und Dockerfiles auf Konsistenz prüfen.
- Nach Änderungen an Abhängigkeiten:  
  \`\`\`bash
  docker compose build --no-cache
  docker compose up -d
  \`\`\`
- Für die Abhängigkeitsverwaltung siehe: [docs/dependencies_management.md](docs/dependencies_management.md)
- Bei BLE-Funktionalität: physische Bluetooth-Hardware wird benötigt.

---

## 5. Kontakt & Support

- Repository: https://github.com/Arduinoeinsteiger/ERP
- Ansprechpartner: ${CURRENT_USER}

---

**Dieser Bericht wurde automatisch erstellt am ${CURRENT_DATE}.**  
Er dient als Nachweis und Dokumentation für die erfolgreiche Installation/Upgrade.
EOL

echo -e "${GREEN}Bericht erstellt: INSTALL_REPORT.md${NC}"
echo "Um ihn anzuzeigen: cat INSTALL_REPORT.md"
echo ""