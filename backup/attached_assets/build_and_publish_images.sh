#!/bin/bash
#
# SwissAirDry Docker Image Build und Publish Skript
#
# Dieses Skript baut Docker-Images und veröffentlicht sie in einer Container-Registry
# Standard: GitHub Container Registry (ghcr.io)
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
   SwissAirDry Docker Image Builder
===============================================
${NC}"

# Prüfe, ob docker installiert ist
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Fehler: Docker wurde nicht gefunden.${NC}"
    echo "Bitte installieren Sie Docker:"
    echo "https://docs.docker.com/engine/install/"
    exit 1
fi

# Prüfe, ob Docker läuft
echo -e "${BLUE}Prüfe, ob Docker läuft...${NC}"
if ! docker info &> /dev/null; then
    echo -e "${RED}Docker scheint nicht zu laufen. Bitte starten Sie den Docker-Dienst.${NC}"
    exit 1
fi

# Konfiguration laden
echo -e "${BLUE}Konfiguration laden...${NC}"
if [ -f .env ]; then
    source .env
else
    if [ -f .env.example ]; then
        cp .env.example .env
        source .env
        echo -e "${YELLOW}Keine .env Datei gefunden. .env.example kopiert.${NC}"
    else
        echo -e "${RED}Keine .env oder .env.example Datei gefunden.${NC}"
        exit 1
    fi
fi

# GitHub-Benutzername abfragen, falls nicht gesetzt
if [ -z "$GITHUB_USERNAME" ]; then
    read -p "GitHub-Benutzername: " GITHUB_USERNAME
    echo "GITHUB_USERNAME=$GITHUB_USERNAME" >> .env
    echo -e "${YELLOW}GitHub-Benutzername in .env gespeichert.${NC}"
fi

# Personal Access Token für GitHub abfragen, falls nicht gesetzt
if [ -z "$GITHUB_TOKEN" ]; then
    echo -e "${YELLOW}GitHub Personal Access Token (mit packages:write-Berechtigung) wird benötigt.${NC}"
    echo -e "${YELLOW}Erstellen Sie einen Token unter: https://github.com/settings/tokens${NC}"
    read -s -p "GitHub Personal Access Token: " GITHUB_TOKEN
    echo
    echo "GITHUB_TOKEN=$GITHUB_TOKEN" >> .env
    echo -e "${YELLOW}GitHub-Token in .env gespeichert.${NC}"
fi

# Registry-URL und Tag setzen
REGISTRY_URL=${REGISTRY_URL:-ghcr.io/${GITHUB_USERNAME}}
IMAGE_TAG=${IMAGE_TAG:-latest}

echo -e "${BLUE}Verwende Registry: ${REGISTRY_URL}${NC}"
echo -e "${BLUE}Verwende Tag: ${IMAGE_TAG}${NC}"

# Bei der Registry anmelden
echo -e "${BLUE}Bei der Registry anmelden...${NC}"
echo "$GITHUB_TOKEN" | docker login ghcr.io -u "$GITHUB_USERNAME" --password-stdin

# Liste der zu bauenden Images
images=(
    "api:swissairdry-api"
    "api:swissairdry-simple-api:Dockerfile.simple"
    "nextcloud:swissairdry-exapp:Dockerfile.exapp"
    "nextcloud:swissairdry-exapp-daemon:Dockerfile.daemon"
    "mqtt-config:swissairdry-mqtt-config"
)

# Images bauen und veröffentlichen
for img in "${images[@]}"; do
    # Image-Informationen aufteilen
    IFS=':' read -r context image_name dockerfile <<< "$img"
    
    if [ -z "$dockerfile" ]; then
        dockerfile="Dockerfile"
    fi
    
    echo -e "${BLUE}Baue Image: ${image_name}...${NC}"
    
    # Image bauen
    docker build -t "${REGISTRY_URL}/${image_name}:${IMAGE_TAG}" \
        -f "${context}/${dockerfile}" \
        "${context}"
    
    # Image veröffentlichen
    echo -e "${BLUE}Veröffentliche Image: ${image_name}...${NC}"
    docker push "${REGISTRY_URL}/${image_name}:${IMAGE_TAG}"
    
    echo -e "${GREEN}Image ${image_name}:${IMAGE_TAG} erfolgreich veröffentlicht!${NC}"
done

echo -e "${GREEN}Alle Images wurden erfolgreich gebaut und veröffentlicht!${NC}"
echo -e "${BLUE}Pull-Befehl für Images:${NC}"
echo -e "docker pull ${REGISTRY_URL}/swissairdry-api:${IMAGE_TAG}"
echo -e "docker pull ${REGISTRY_URL}/swissairdry-simple-api:${IMAGE_TAG}"
echo -e "docker pull ${REGISTRY_URL}/swissairdry-exapp:${IMAGE_TAG}"
echo -e "docker pull ${REGISTRY_URL}/swissairdry-exapp-daemon:${IMAGE_TAG}"
echo -e "docker pull ${REGISTRY_URL}/swissairdry-mqtt-config:${IMAGE_TAG}"

echo -e "${BLUE}===============================================${NC}"
echo -e "${GREEN}Docker-Images erfolgreich veröffentlicht unter:${NC}"
echo -e "${BLUE}${REGISTRY_URL}${NC}"
echo -e "${BLUE}===============================================${NC}"
echo -e "In der .env-Datei können Sie die Registry-URL und den Tag anpassen:"
echo -e "REGISTRY_URL=${REGISTRY_URL}"
echo -e "IMAGE_TAG=${IMAGE_TAG}"
echo -e "${BLUE}===============================================${NC}"

exit 0