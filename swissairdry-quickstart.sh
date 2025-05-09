#!/bin/bash
# SwissAirDry - Quick Start Script (Plug & Play)
# Dieses Skript bietet eine komplett automatisierte Einrichtung der SwissAirDry-Plattform

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

clear
echo -e "${BLUE}================================================${NC}"
echo -e "${BOLD}       SwissAirDry Plug & Play Setup           ${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo -e "Dieses Skript richtet SwissAirDry vollautomatisch ein."
echo -e "In wenigen Minuten ist Ihr System einsatzbereit."
echo -e "${YELLOW}Keine manuellen Eingriffe erforderlich!${NC}"
echo ""

# Prüfe Root-Rechte
if [ "$EUID" -ne 0 ]; then
  echo -e "${YELLOW}Hinweis: Für einige Aktionen werden Root-Rechte benötigt.${NC}"
  echo -e "Starte neu mit sudo..."
  exec sudo "$0" "$@"
  exit
fi

# Check for required commands
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${YELLOW}Installiere $1...${NC}"
        case $1 in
            docker)
                curl -fsSL https://get.docker.com -o get-docker.sh
                sh get-docker.sh
                usermod -aG docker $SUDO_USER
                ;;
            docker-compose)
                curl -L "https://github.com/docker/compose/releases/download/v2.15.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
                chmod +x /usr/local/bin/docker-compose
                ;;
            git)
                apt-get update
                apt-get install -y git
                ;;
            *)
                apt-get update
                apt-get install -y $1
                ;;
        esac
        
        # Check if installation succeeded
        if ! command -v $1 &> /dev/null; then
            echo -e "${RED}Fehler: $1 konnte nicht installiert werden.${NC}"
            exit 1
        fi
    fi
}

echo -e "${YELLOW}Prüfe erforderliche Programme...${NC}"
check_command docker
check_command docker-compose
check_command git
check_command curl
echo -e "${GREEN}Alle erforderlichen Programme sind verfügbar.${NC}"

# Create working directory
INSTALL_DIR="/opt/swissairdry"
echo -e "${YELLOW}Erstelle Installationsverzeichnis...${NC}"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Clone repository if needed
if [ ! -d "$INSTALL_DIR/.git" ]; then
    echo -e "${YELLOW}Lade SwissAirDry herunter...${NC}"
    git clone https://github.com/Arduinoeinsteiger/ERP.git .
else
    echo -e "${YELLOW}Aktualisiere bestehende Installation...${NC}"
    git pull
fi

# Setup environment file
echo -e "${YELLOW}Konfiguriere Umgebung...${NC}"
cp .env.example .env

# Generate secure keys
echo -e "${YELLOW}Generiere sichere Schlüssel...${NC}"
FLASK_SECRET_KEY=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
EXAPP_SECRET=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
sed -i "s/FLASK_SECRET_KEY=.*/FLASK_SECRET_KEY=$FLASK_SECRET_KEY/" .env
sed -i "s/EXAPP_SECRET=.*/EXAPP_SECRET=$EXAPP_SECRET/" .env

# Ensure requirements directory exists
echo -e "${YELLOW}Stelle sicher, dass alle Dateien vorhanden sind...${NC}"
mkdir -p backup/attached_assets
if [ ! -f backup/attached_assets/requirements.txt ]; then
    if [ -f requirements.txt ]; then
        cp requirements.txt backup/attached_assets/
    else
        cat > backup/attached_assets/requirements.txt << EOL
Flask>=2.3.3
flask-cors>=4.0.0
requests>=2.31.0
paho-mqtt>=2.2.1
python-dotenv>=1.0.0
gunicorn>=22.0.0
psycopg2-binary>=2.9.9
jinja2>=3.1.3
email-validator>=2.0.0
flask-sqlalchemy>=3.0.5
bleak>=0.21.1
EOL
    fi
fi

# Check if ports are available
check_port() {
    nc -z localhost $1 &> /dev/null
    if [ $? -eq 0 ]; then
        echo -e "${YELLOW}Port $1 wird bereits verwendet. Prüfe alternative Ports...${NC}"
        return 1
    fi
    return 0
}

# Adjust ports if needed
WEB_PORT=5000
API_PORT=8000
MQTT_PORT=1883
if ! check_port $WEB_PORT; then
    WEB_PORT=5001
    sed -i "s/- \"5000:5000\"/- \"$WEB_PORT:5000\"/" docker-compose.yml
    echo -e "${YELLOW}Web-Interface wird auf Port $WEB_PORT laufen.${NC}"
fi

if ! check_port $API_PORT; then
    API_PORT=8001
    sed -i "s/- \"8000:8000\"/- \"$API_PORT:8000\"/" docker-compose.yml
    echo -e "${YELLOW}API wird auf Port $API_PORT laufen.${NC}"
fi

if ! check_port $MQTT_PORT; then
    MQTT_PORT=1884
    sed -i "s/- \"1883:1883\"/- \"$MQTT_PORT:1883\"/" docker-compose.yml
    echo -e "${YELLOW}MQTT-Broker wird auf Port $MQTT_PORT laufen.${NC}"
fi

# Start containers
echo -e "${YELLOW}Starte SwissAirDry-Container...${NC}"
docker-compose build && docker-compose up -d

# Check if startup was successful
if [ $? -eq 0 ]; then
    # Create symbolic link for easy access
    ln -sf "$INSTALL_DIR/swissairdry-control.sh" /usr/local/bin/swissairdry
    
    # Create control script
    cat > "$INSTALL_DIR/swissairdry-control.sh" << EOL
#!/bin/bash
# SwissAirDry Control Script

cd "$INSTALL_DIR"

case "\$1" in
    start)
        docker-compose up -d
        ;;
    stop)
        docker-compose down
        ;;
    restart)
        docker-compose restart
        ;;
    status)
        docker-compose ps
        ;;
    logs)
        docker-compose logs -f
        ;;
    update)
        git pull
        docker-compose build
        docker-compose up -d
        ;;
    *)
        echo "Verwendung: swissairdry {start|stop|restart|status|logs|update}"
        exit 1
esac
EOL
    chmod +x "$INSTALL_DIR/swissairdry-control.sh"
    
    # Wait for services to start
    echo -e "${YELLOW}Warte, bis alle Dienste gestartet sind...${NC}"
    sleep 10
    
    # Get local IP
    IP_ADDR=$(hostname -I | awk '{print $1}')
    
    echo -e "${BLUE}================================================${NC}"
    echo -e "${GREEN}SwissAirDry wurde erfolgreich installiert!${NC}"
    echo -e "${BLUE}================================================${NC}"
    echo ""
    echo -e "Zugriff auf das Web-Interface:"
    echo -e "  ${BOLD}http://$IP_ADDR:$WEB_PORT${NC}"
    echo ""
    echo -e "MQTT-Broker ist erreichbar unter:"
    echo -e "  ${BOLD}$IP_ADDR:$MQTT_PORT${NC}"
    echo ""
    echo -e "Verwenden Sie folgende Befehle zur Steuerung:"
    echo -e "  ${YELLOW}swissairdry start${NC}    - Startet alle Dienste"
    echo -e "  ${YELLOW}swissairdry stop${NC}     - Stoppt alle Dienste"
    echo -e "  ${YELLOW}swissairdry restart${NC}  - Startet alle Dienste neu"
    echo -e "  ${YELLOW}swissairdry status${NC}   - Zeigt den Status aller Dienste"
    echo -e "  ${YELLOW}swissairdry logs${NC}     - Zeigt die Logs aller Dienste"
    echo -e "  ${YELLOW}swissairdry update${NC}   - Aktualisiert auf die neueste Version"
    echo ""
    
    # Check for Bluetooth capability
    if [ -e /dev/hci0 ] || hciconfig -a 2>/dev/null | grep -q "hci0"; then
        echo -e "${GREEN}Bluetooth-Hardware erkannt. BLE-Funktionalität ist verfügbar.${NC}"
    else
        echo -e "${YELLOW}Keine Bluetooth-Hardware erkannt. BLE-Funktionalität ist eingeschränkt.${NC}"
        echo -e "Falls Sie BLE-Funktionalität benötigen, stellen Sie sicher, dass Bluetooth aktiviert ist."
    fi
    
    echo ""
    echo -e "${BLUE}Für weitere Informationen besuchen Sie die Dokumentation:${NC}"
    echo -e "  ${BOLD}$INSTALL_DIR/docs/${NC}"
    echo ""
else
    echo -e "${RED}Fehler beim Starten der Container. Bitte prüfen Sie die Logs.${NC}"
    docker-compose logs
    exit 1
fi