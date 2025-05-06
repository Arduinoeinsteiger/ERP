#!/bin/bash
# ------------------------------------------------------------------------------
# SwissAirDry - Nextcloud Deck App Modifier
# ------------------------------------------------------------------------------
# Dieses Skript modifiziert die Nextcloud Deck App, um sie für die Verwendung
# mit SwissAirDry anzupassen. Es führt folgende Anpassungen durch:
# - Hinzufügen eines benutzerdefinierten CSS-Stils
# - Integration von Google Maps für Gerätestandorte
# - Hinzufügen der SwissAirDry-spezifischen Icons und Farben
# ------------------------------------------------------------------------------

set -e

# Farben für die Ausgabe
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Konfigurationsvariablen
NEXTCLOUD_DIR=${NEXTCLOUD_DIR:-"/var/www/html"}
DECK_APP_DIR="$NEXTCLOUD_DIR/apps/deck"
DECK_APP_CSS_DIR="$DECK_APP_DIR/css"
DECK_APP_JS_DIR="$DECK_APP_DIR/js"
DECK_APP_IMG_DIR="$DECK_APP_DIR/img"
BACKUP_DIR="$DECK_APP_DIR/swissairdry_backup_$(date +%Y%m%d)"

# Banner anzeigen
echo -e "${BLUE}${BOLD}"
echo "SwissAirDry - Nextcloud Deck App Modifier"
echo "========================================="
echo -e "${NC}"

# Prüfen, ob das Skript mit Root-Rechten ausgeführt wird
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}Fehler: Dieses Skript muss mit Root-Rechten ausgeführt werden.${NC}"
  echo "Bitte mit 'sudo' ausführen."
  exit 1
fi

# Prüfen, ob Nextcloud existiert
if [ ! -d "$NEXTCLOUD_DIR" ]; then
  echo -e "${RED}Fehler: Nextcloud wurde nicht gefunden in $NEXTCLOUD_DIR${NC}"
  echo "Bitte den Pfad zu Nextcloud mit NEXTCLOUD_DIR=/pfad/zu/nextcloud angeben."
  exit 1
fi

# Prüfen, ob die Deck-App installiert ist
if [ ! -d "$DECK_APP_DIR" ]; then
  echo -e "${RED}Fehler: Die Deck-App wurde nicht gefunden in $DECK_APP_DIR${NC}"
  echo "Bitte stellen Sie sicher, dass die Deck-App in Nextcloud installiert ist."
  exit 1
fi

# Erstellen eines Backup-Verzeichnisses
echo -e "${YELLOW}Erstelle Backup der Deck-App...${NC}"
mkdir -p "$BACKUP_DIR"
cp -r "$DECK_APP_CSS_DIR" "$BACKUP_DIR/css"
cp -r "$DECK_APP_JS_DIR" "$BACKUP_DIR/js"
echo -e "${GREEN}Backup erstellt in $BACKUP_DIR${NC}"

# SwissAirDry-spezifischen CSS-Stil erstellen
echo -e "${YELLOW}Erstelle SwissAirDry-spezifischen CSS-Stil...${NC}"
cat > "$DECK_APP_CSS_DIR/swissairdry.css" << 'EOF'
/* SwissAirDry spezifisches Styling für Nextcloud Deck */

/* Anpassung der Farbpalette */
:root {
    --swissairdry-primary: #0082c9;
    --swissairdry-secondary: #00629a;
    --swissairdry-accent: #e6f3fa;
    --swissairdry-text: #333333;
    --swissairdry-success: #4caf50;
    --swissairdry-warning: #ff9800;
    --swissairdry-error: #f44336;
}

/* Karten-Styling für SwissAirDry-Karten */
.card.swissairdry-device .card-title {
    display: flex;
    align-items: center;
}

.card.swissairdry-device .card-title:before {
    content: "";
    display: inline-block;
    width: 16px;
    height: 16px;
    margin-right: 8px;
    background-image: url('../img/swissairdry-icon.svg');
    background-size: contain;
    background-repeat: no-repeat;
}

/* Standort-Karten */
.card.swissairdry-location {
    border-left: 3px solid var(--swissairdry-primary);
}

/* Alarm-Karten */
.card.swissairdry-alert {
    border-left: 3px solid var(--swissairdry-error);
}

/* Aufgaben-Karten */
.card.swissairdry-task {
    border-left: 3px solid var(--swissairdry-warning);
}

/* Koordinaten und Karten-Links hervorheben */
.markdown-body a[href*="maps.google.com"],
.markdown-body a[href*="map-view"] {
    display: inline-flex;
    align-items: center;
    padding: 4px 8px;
    margin: 2px 0;
    background-color: var(--swissairdry-accent);
    border-radius: 4px;
    text-decoration: none;
    color: var(--swissairdry-primary);
    font-weight: 600;
    transition: background-color 0.2s;
}

.markdown-body a[href*="maps.google.com"]:hover,
.markdown-body a[href*="map-view"]:hover {
    background-color: var(--color-primary-light);
}

.markdown-body a[href*="maps.google.com"]:before {
    content: "";
    display: inline-block;
    width: 16px;
    height: 16px;
    margin-right: 6px;
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%230082c9"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>');
    background-size: contain;
    background-repeat: no-repeat;
}

.markdown-body a[href*="map-view"]:before {
    content: "";
    display: inline-block;
    width: 16px;
    height: 16px;
    margin-right: 6px;
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%230082c9"><path d="M20.5 3l-.16.03L15 5.1 9 3 3.36 4.9c-.21.07-.36.25-.36.48V20.5c0 .28.22.5.5.5l.16-.03L9 18.9l6 2.1 5.64-1.9c.21-.07.36-.25.36-.48V3.5c0-.28-.22-.5-.5-.5zM15 19l-6-2.11V5l6 2.11V19z"/></svg>');
    background-size: contain;
    background-repeat: no-repeat;
}

/* Styling für Status-Anzeigen */
.swissairdry-status {
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    margin-right: 5px;
}

.swissairdry-status.online {
    background-color: var(--swissairdry-success);
}

.swissairdry-status.warning {
    background-color: var(--swissairdry-warning);
}

.swissairdry-status.offline {
    background-color: var(--swissairdry-error);
}

/* Anpassungen für die mobile Ansicht */
@media (max-width: 768px) {
    .markdown-body a[href*="maps.google.com"],
    .markdown-body a[href*="map-view"] {
        display: flex;
        margin: 4px 0;
    }
}
EOF

# SwissAirDry-Icon erstellen
echo -e "${YELLOW}Erstelle SwissAirDry-Icon...${NC}"
mkdir -p "$DECK_APP_IMG_DIR"
cat > "$DECK_APP_IMG_DIR/swissairdry-icon.svg" << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#0082c9">
  <path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM19 18H6c-2.21 0-4-1.79-4-4 0-2.05 1.53-3.76 3.56-3.97l1.07-.11.5-.95C8.08 7.14 9.94 6 12 6c2.62 0 4.88 1.86 5.39 4.43l.3 1.5 1.53.11c1.56.1 2.78 1.41 2.78 2.96 0 1.65-1.35 3-3 3zM8 13h2.55v3h2.9v-3H16l-4-4z" />
</svg>
EOF

# CSS in die Hauptseite integrieren
echo -e "${YELLOW}Integriere CSS in die Hauptseite...${NC}"
DECK_APP_PHP="$DECK_APP_DIR/lib/AppInfo/Application.php"
if [ -f "$DECK_APP_PHP" ]; then
    # Backup der Datei erstellen
    cp "$DECK_APP_PHP" "$BACKUP_DIR/Application.php.bak"
    
    # Prüfen, ob die CSS-Integration bereits vorhanden ist
    if ! grep -q "swissairdry.css" "$DECK_APP_PHP"; then
        # Stelle sicher, dass wir den richtigen Bereich finden
        if grep -q "public function register" "$DECK_APP_PHP"; then
            # Füge den CSS-Link hinzu
            sed -i '/\$styleManager = $this->getContainer()->get(IAppManager::class);/a \\\t\t$styleManager->addCSS("deck", "swissairdry.css");' "$DECK_APP_PHP"
            echo -e "${GREEN}CSS wurde in die Hauptseite integriert.${NC}"
        else
            echo -e "${RED}Die Datei hat nicht das erwartete Format. Manuelle Integration erforderlich.${NC}"
        fi
    else
        echo -e "${YELLOW}SwissAirDry CSS ist bereits integriert.${NC}"
    fi
else
    echo -e "${RED}Deck App PHP-Datei nicht gefunden: $DECK_APP_PHP${NC}"
    echo "Manuelle Integration erforderlich."
fi

# Berechtigungen anpassen
echo -e "${YELLOW}Passe Berechtigungen an...${NC}"
chown -R www-data:www-data "$DECK_APP_DIR"
chmod -R 755 "$DECK_APP_DIR"

# Nextcloud-Cache leeren
echo -e "${YELLOW}Leere Nextcloud-Cache...${NC}"
if command -v sudo >/dev/null 2>&1 && command -v -p sudo >/dev/null 2>&1; then
    if [ -f "$NEXTCLOUD_DIR/occ" ]; then
        sudo -u www-data php "$NEXTCLOUD_DIR/occ" maintenance:repair
        sudo -u www-data php "$NEXTCLOUD_DIR/occ" maintenance:mode --off
    else
        echo -e "${RED}Nextcloud OCC nicht gefunden. Bitte Cache manuell leeren.${NC}"
    fi
else
    echo -e "${YELLOW}Sudo nicht verfügbar. Bitte Cache manuell leeren.${NC}"
fi

echo -e "${GREEN}${BOLD}Die Deck-App wurde erfolgreich für SwissAirDry angepasst!${NC}"
echo ""
echo -e "${BLUE}Folgende Änderungen wurden vorgenommen:${NC}"
echo "- SwissAirDry-CSS hinzugefügt"
echo "- SwissAirDry-Icon hinzugefügt"
echo "- CSS in die Hauptseite integriert"
echo ""
echo -e "${YELLOW}Hinweis: Bei Problemen kann das Backup unter $BACKUP_DIR verwendet werden.${NC}"
echo "Zum Wiederherstellen: cp -r $BACKUP_DIR/* $DECK_APP_DIR/"
echo ""
echo -e "${BLUE}${BOLD}Viel Erfolg mit SwissAirDry!${NC}"