#!/bin/bash
#
# SwissAirDry Docker Stack Stoppskript
#

# Farben für die Konsole
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}
===============================================
   SwissAirDry Docker Stack Stoppskript
===============================================
${NC}"

# Prüfe, ob docker-compose installiert ist
if ! command -v docker-compose &> /dev/null && ! command -v docker &> /dev/null; then
    echo -e "${RED}Fehler: Weder docker-compose noch docker wurden gefunden.${NC}"
    echo "Bitte installieren Sie Docker und Docker Compose:"
    echo "https://docs.docker.com/engine/install/"
    exit 1
fi

# Prüfe, ob Docker läuft
if ! docker info &> /dev/null; then
    echo -e "${RED}Docker scheint nicht zu laufen. Bitte starten Sie den Docker-Dienst.${NC}"
    exit 1
fi

# Optionen für das Stoppen abfragen
read -p "Möchten Sie auch die Datenvolumes löschen? [y/N] " delete_volumes
read -p "Möchten Sie ungenutzte Docker-Images löschen? [y/N] " delete_images

# Container stoppen
echo -e "${BLUE}Stoppe Docker Compose Stack...${NC}"
docker-compose down $([ "$delete_volumes" = "y" ] || [ "$delete_volumes" = "Y" ] && echo "-v")

# Bilder löschen, falls gewünscht
if [ "$delete_images" = "y" ] || [ "$delete_images" = "Y" ]; then
    echo -e "${BLUE}Lösche ungenutzte Docker-Images...${NC}"
    docker image prune -af
fi

echo -e "${GREEN}SwissAirDry Docker Stack wurde gestoppt!${NC}"

exit 0