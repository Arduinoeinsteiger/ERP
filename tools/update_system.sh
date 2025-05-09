#!/bin/bash
# SwissAirDry - System Update Tool
# Dieses Skript aktualisiert das SwissAirDry-System auf die neueste Version

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}       SwissAirDry System Update          ${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

check_command() {
    command -v $1 >/dev/null 2>&1 || { 
        echo -e "${RED}Error: $1 is required but not installed.${NC}" 
        echo "Please install $1 and try again."
        exit 1
    }
}

echo -e "${YELLOW}Checking for required commands...${NC}"
check_command git
check_command docker
check_command docker-compose
echo -e "${GREEN}All required commands are available.${NC}"
echo ""

# Backup existing requirements.txt
echo -e "${YELLOW}Creating backup of requirements files...${NC}"
if [ -f "backup/attached_assets/requirements.txt" ]; then
    cp backup/attached_assets/requirements.txt backup/attached_assets/requirements.txt.bak.$(date +"%Y%m%d%H%M%S")
    echo -e "${GREEN}Backup created.${NC}"
fi

if [ -f "nextcloud/apps/swissairdry/daemon/requirements.txt" ]; then
    cp nextcloud/apps/swissairdry/daemon/requirements.txt nextcloud/apps/swissairdry/daemon/requirements.txt.bak.$(date +"%Y%m%d%H%M%S")
    echo -e "${GREEN}Backup created.${NC}"
fi

# Pull latest changes
echo -e "${YELLOW}Pulling latest changes from repository...${NC}"
git pull
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to pull latest changes.${NC}"
    echo "Please resolve any conflicts and try again."
    exit 1
fi
echo -e "${GREEN}Successfully pulled latest changes.${NC}"
echo ""

# Check for requirements.txt changes
echo -e "${YELLOW}Checking for changes in requirements.txt...${NC}"
REQUIREMENTS_CHANGED=0
if [ -f "backup/attached_assets/requirements.txt.bak."* ]; then
    LATEST_BACKUP=$(ls -t backup/attached_assets/requirements.txt.bak.* | head -1)
    if ! diff -q "$LATEST_BACKUP" "backup/attached_assets/requirements.txt" > /dev/null; then
        echo -e "${YELLOW}Changes detected in requirements.txt.${NC}"
        echo "Diff between backup and current:"
        diff "$LATEST_BACKUP" "backup/attached_assets/requirements.txt"
        REQUIREMENTS_CHANGED=1
    else
        echo -e "${GREEN}No changes detected in requirements.txt.${NC}"
    fi
fi
echo ""

# Check for paho-mqtt version
echo -e "${YELLOW}Checking paho-mqtt version...${NC}"
if grep -q "paho-mqtt==2.1.0" backup/attached_assets/requirements.txt; then
    echo -e "${GREEN}paho-mqtt version is correct (2.1.0).${NC}"
else
    echo -e "${RED}Warning: paho-mqtt version may not be correct!${NC}"
    echo "Current version in requirements.txt:"
    grep "paho-mqtt" backup/attached_assets/requirements.txt || echo "Not found!"
    echo ""
    echo -e "${YELLOW}Do you want to fix the paho-mqtt version to 2.1.0? (y/N)${NC}"
    read -p "> " fix_mqtt
    if [[ $fix_mqtt =~ ^[Yy]$ ]]; then
        if grep -q "paho-mqtt" backup/attached_assets/requirements.txt; then
            sed -i 's/paho-mqtt.*/paho-mqtt==2.1.0/' backup/attached_assets/requirements.txt
        else
            echo "paho-mqtt==2.1.0" >> backup/attached_assets/requirements.txt
        fi
        if grep -q "paho-mqtt" nextcloud/apps/swissairdry/daemon/requirements.txt; then
            sed -i 's/paho-mqtt.*/paho-mqtt==2.1.0/' nextcloud/apps/swissairdry/daemon/requirements.txt
        else
            echo "paho-mqtt==2.1.0" >> nextcloud/apps/swissairdry/daemon/requirements.txt
        fi
        echo -e "${GREEN}paho-mqtt version fixed.${NC}"
        REQUIREMENTS_CHANGED=1
    fi
fi
echo ""

# Rebuild and restart services if needed
if [ $REQUIREMENTS_CHANGED -eq 1 ]; then
    echo -e "${YELLOW}Requirements have changed. Would you like to rebuild containers? (y/N)${NC}"
    read -p "> " rebuild
    if [[ $rebuild =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Rebuilding containers...${NC}"
        docker-compose build --no-cache
        if [ $? -ne 0 ]; then
            echo -e "${RED}Error: Failed to rebuild containers.${NC}"
            exit 1
        fi
        echo -e "${GREEN}Successfully rebuilt containers.${NC}"
        
        echo -e "${YELLOW}Restarting services...${NC}"
        docker-compose up -d
        if [ $? -ne 0 ]; then
            echo -e "${RED}Error: Failed to restart services.${NC}"
            exit 1
        fi
        echo -e "${GREEN}Successfully restarted services.${NC}"
    else
        echo -e "${YELLOW}Skipping rebuild. You'll need to rebuild manually later.${NC}"
    fi
else
    echo -e "${YELLOW}Would you like to restart services? (y/N)${NC}"
    read -p "> " restart
    if [[ $restart =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Restarting services...${NC}"
        docker-compose up -d
        if [ $? -ne 0 ]; then
            echo -e "${RED}Error: Failed to restart services.${NC}"
            exit 1
        fi
        echo -e "${GREEN}Successfully restarted services.${NC}"
    fi
fi
echo ""

# Generate installation report
echo -e "${YELLOW}Generating installation report...${NC}"
if [ -f "tools/generate_install_report.sh" ]; then
    ./tools/generate_install_report.sh
else
    echo -e "${RED}Warning: Installation report generator not found.${NC}"
fi
echo ""

echo -e "${BLUE}============================================${NC}"
echo -e "${GREEN}SwissAirDry System Update Complete!${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""