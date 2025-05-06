#!/bin/bash
#
# SwissAirDry Sicherheits-Update Skript
#
# Dieses Skript aktualisiert die Dependencies in den requirements.txt-Dateien,
# um bekannte Sicherheitslücken zu beheben, und baut die Docker-Images neu.
#

set -e

# Farben für die Konsole
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}
===============================================
   SwissAirDry Sicherheits-Update
===============================================
${NC}"

# Prüfe, ob die notwendigen Tools installiert sind
if ! command -v sed &> /dev/null; then
    echo -e "${RED}Fehler: sed wurde nicht gefunden.${NC}"
    exit 1
fi

# Aktualisiere die Requirements-Dateien
echo -e "${BLUE}Aktualisiere Abhängigkeiten mit Sicherheitslücken...${NC}"

update_dependency() {
    local file=$1
    local old_version=$2
    local new_version=$3
    local dependency=$4
    
    if grep -q "$dependency==$old_version" "$file"; then
        sed -i "s/$dependency==$old_version/$dependency==$new_version/g" "$file"
        echo -e "${GREEN}In $file: $dependency von $old_version auf $new_version aktualisiert${NC}"
    elif grep -q "$dependency>=$old_version" "$file"; then
        sed -i "s/$dependency>=$old_version/$dependency>=$new_version/g" "$file"
        echo -e "${GREEN}In $file: $dependency von >=$old_version auf >=$new_version aktualisiert${NC}"
    elif grep -q "$dependency" "$file"; then
        echo -e "${YELLOW}In $file: $dependency ohne Versionsangabe gefunden, bitte manuell prüfen${NC}"
    else
        echo -e "${YELLOW}In $file: $dependency nicht gefunden${NC}"
    fi
}

# Liste der zu aktualisierenden requirements.txt-Dateien
files=(
    "./api/requirements.api.txt"
    "./api/requirements.simple.txt"
    "./nextcloud/requirements.txt"
    "./swissairdry/api/app/requirements.txt"
    "./swissairdry/api/requirements.txt"
    "./swissairdry/nextcloud/requirements.txt"
)

# Liste der zu aktualisierenden Abhängigkeiten
echo -e "${BLUE}Folgende Sicherheitslücken werden behoben:${NC}"
echo -e "1. python-multipart: von 0.0.6 auf 0.0.7 (behebt Denial-of-Service-Schwachstellen)"
echo -e "2. jinja2: auf 3.1.3 (behebt Sandbox-Breakout und HTML-Attribut-Injektions-Schwachstellen)"
echo -e "3. gunicorn: auf 22.0.0 (behebt HTTP Request/Response Smuggling)"
echo -e "4. pillow: auf neuere Versionen (10.0.1/10.1.0) (behebt Buffer-Overflow und Code-Ausführungs-Schwachstellen)"
echo -e "5. flask-cors: auf 4.0.0 (behebt CORS-Schwachstellen)"

# Aktualisiere die Abhängigkeiten in allen Dateien
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${BLUE}Aktualisiere $file...${NC}"
        
        # python-multipart updaten
        update_dependency "$file" "0.0.6" "0.0.7" "python-multipart"
        
        # jinja2 updaten
        update_dependency "$file" "3.1.2" "3.1.3" "jinja2"
        update_dependency "$file" "3.1.2" "3.1.3" "Jinja2"
        
        # gunicorn updaten
        update_dependency "$file" "21.2.0" "22.0.0" "gunicorn"
        update_dependency "$file" "20.1.0" "22.0.0" "gunicorn"
        
        # pillow updaten
        update_dependency "$file" "9.5.0" "10.1.0" "pillow"
        update_dependency "$file" "9.5.0" "10.1.0" "Pillow"
        update_dependency "$file" "10.0.1" "10.1.0" "pillow"
        update_dependency "$file" "10.0.1" "10.1.0" "Pillow"
        
        # flask-cors updaten
        update_dependency "$file" "3.0.10" "4.0.0" "flask-cors"
        update_dependency "$file" "3.0.10" "4.0.0" "Flask-Cors"
    else
        echo -e "${YELLOW}Datei $file nicht gefunden, überspringe...${NC}"
    fi
done

echo -e "${GREEN}Abhängigkeiten erfolgreich aktualisiert!${NC}"
echo -e "${BLUE}===============================================${NC}"

# Vorschlag für den nächsten Schritt
echo -e "${YELLOW}Nächste Schritte:${NC}"
echo -e "1. Lokales Testen:"
echo -e "   ./stop_docker.sh"
echo -e "   ./start_docker.sh"
echo -e "   (Wählen Sie 'N' bei 'Möchten Sie nur vorgefertigte Docker-Images verwenden?')"
echo -e ""
echo -e "2. Für Produktion Docker-Images neu bauen und veröffentlichen:"
echo -e "   ./build_and_publish_images.sh"
echo -e "${BLUE}===============================================${NC}"

exit 0