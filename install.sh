#!/bin/bash
# SwissAirDry Installation Script
# Dieses Skript automatisiert die Installation der SwissAirDry-Plattform

# Farbige Ausgabe
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funktionen für farbige Ausgaben
info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Prüfen ob das Skript als Root ausgeführt wird
if [ "$EUID" -ne 0 ]; then
    warning "Es wird empfohlen, dieses Skript als Root auszuführen."
    read -p "Möchten Sie trotzdem fortfahren? (j/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Jj]$ ]]; then
        exit 1
    fi
fi

# Überprüfen und installieren von Abhängigkeiten
install_dependencies() {
    info "Überprüfe und installiere Abhängigkeiten..."
    
    # Liste der zu installierenden Pakete
    packages=("python3" "python3-pip" "python3-venv" "postgresql" "postgresql-contrib" "git" "mosquitto" "mosquitto-clients" "bluetooth" "bluez" "libbluetooth-dev")
    
    # Betriebssystem erkennen
    if [ -f /etc/debian_version ]; then
        # Debian/Ubuntu
        info "Debian/Ubuntu erkannt, installiere Pakete mit apt..."
        apt update
        for pkg in "${packages[@]}"; do
            dpkg -l | grep -qw $pkg || apt install -y $pkg
        done
    elif [ -f /etc/redhat-release ]; then
        # RHEL/CentOS/Fedora
        info "RHEL/CentOS/Fedora erkannt, installiere Pakete mit dnf/yum..."
        if command -v dnf &> /dev/null; then
            dnf install -y epel-release
            for pkg in "${packages[@]}"; do
                dnf install -y $pkg
            done
        else
            yum install -y epel-release
            for pkg in "${packages[@]}"; do
                yum install -y $pkg
            done
        fi
    elif [ -f /etc/arch-release ]; then
        # Arch Linux
        info "Arch Linux erkannt, installiere Pakete mit pacman..."
        pacman -Sy --noconfirm
        for pkg in "${packages[@]}"; do
            pacman -S --noconfirm $pkg
        done
    else
        error "Nicht unterstütztes Betriebssystem! Bitte installieren Sie die Abhängigkeiten manuell."
        exit 1
    fi
    
    success "Abhängigkeiten installiert!"
}

# Repository klonen
clone_repository() {
    info "Klone das SwissAirDry-Repository..."
    if [ -d "ERP" ]; then
        warning "Verzeichnis 'ERP' existiert bereits. Möchten Sie es aktualisieren?"
        read -p "Aktualisieren (j) oder überspringen (n)? " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Jj]$ ]]; then
            cd ERP
            git pull
            cd ..
            success "Repository aktualisiert!"
        else
            info "Repository-Update übersprungen."
        fi
    else
        git clone https://github.com/Arduinoeinsteiger/ERP.git
        if [ $? -ne 0 ]; then
            error "Fehler beim Klonen des Repositories!"
            exit 1
        fi
        success "Repository erfolgreich geklont!"
    fi
}

# Python-Umgebung einrichten
setup_python_env() {
    info "Richte Python-Umgebung ein..."
    cd ERP
    
    # Virtuelle Umgebung erstellen
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        error "Fehler beim Erstellen der virtuellen Umgebung!"
        exit 1
    fi
    
    # Virtuelle Umgebung aktivieren
    source venv/bin/activate
    
    # Abhängigkeiten installieren
    pip install --upgrade pip
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        error "Fehler beim Installieren der Python-Abhängigkeiten!"
        exit 1
    fi
    
    success "Python-Umgebung eingerichtet!"
}

# Datenbank einrichten
setup_database() {
    info "Richte PostgreSQL-Datenbank ein..."
    
    # PostgreSQL-Dienst starten
    if systemctl is-active --quiet postgresql; then
        info "PostgreSQL läuft bereits."
    else
        systemctl start postgresql
        systemctl enable postgresql
    fi
    
    # Datenbank erstellen als postgres-Benutzer
    info "Erstelle Datenbank und Benutzer..."
    
    # Generiere ein zufälliges Passwort
    DB_PASSWORD=$(tr -dc 'a-zA-Z0-9' < /dev/urandom | fold -w 12 | head -n 1)
    
    # Führe Datenbank-Befehle aus
    su - postgres -c "psql -c \"CREATE DATABASE swissairdry;\""
    su - postgres -c "psql -c \"CREATE USER swissairdry WITH PASSWORD '$DB_PASSWORD';\""
    su - postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE swissairdry TO swissairdry;\""
    
    if [ $? -ne 0 ]; then
        warning "Es gab Probleme bei der Datenbankerstellung. Möglicherweise existiert die Datenbank bereits."
    else
        success "Datenbank eingerichtet!"
    fi
    
    # Erstelle .env-Datei
    info "Erstelle .env-Datei..."
    FLASK_SECRET_KEY=$(tr -dc 'a-zA-Z0-9' < /dev/urandom | fold -w 32 | head -n 1)
    
    cat > .env << EOF
DATABASE_URL=postgresql://swissairdry:$DB_PASSWORD@localhost:5432/swissairdry
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=
FLASK_SECRET_KEY=$FLASK_SECRET_KEY
EOF
    
    success ".env-Datei erstellt!"
}

# MQTT-Broker einrichten
setup_mqtt() {
    info "Richte MQTT-Broker ein..."
    
    # Überprüfen, ob Mosquitto bereits läuft
    if systemctl is-active --quiet mosquitto; then
        info "Mosquitto läuft bereits."
    else
        systemctl start mosquitto
        systemctl enable mosquitto
    fi
    
    # Einfache Konfiguration
    cat > /etc/mosquitto/conf.d/swissairdry.conf << EOF
# SwissAirDry MQTT-Konfiguration
listener 1883
allow_anonymous true
EOF
    
    # Mosquitto neu starten
    systemctl restart mosquitto
    
    success "MQTT-Broker eingerichtet!"
}

# Bluetooth-Dienst einrichten
setup_bluetooth() {
    info "Richte Bluetooth-Dienst ein..."
    
    # Überprüfen, ob Bluetooth bereits läuft
    if systemctl is-active --quiet bluetooth; then
        info "Bluetooth-Dienst läuft bereits."
    else
        systemctl start bluetooth
        systemctl enable bluetooth
    fi
    
    # Benutzer zur bluetooth-Gruppe hinzufügen
    if [ "$SUDO_USER" ]; then
        usermod -a -G bluetooth $SUDO_USER
        success "Benutzer $SUDO_USER zur bluetooth-Gruppe hinzugefügt!"
    else
        warning "Konnte keinen Benutzer zur bluetooth-Gruppe hinzufügen. Bitte führen Sie 'usermod -a -G bluetooth BENUTZERNAME' manuell aus."
    fi
    
    success "Bluetooth-Dienst eingerichtet!"
}

# Systemd-Service für SwissAirDry erstellen
create_service() {
    info "Erstelle Systemd-Service für SwissAirDry..."
    
    # Absoluten Pfad zum Projektverzeichnis ermitteln
    INSTALL_DIR=$(pwd)
    
    # Service-Datei erstellen
    cat > /etc/systemd/system/swissairdry.service << EOF
[Unit]
Description=SwissAirDry Platform
After=network.target postgresql.service mosquitto.service bluetooth.service
Requires=postgresql.service

[Service]
ExecStart=$INSTALL_DIR/venv/bin/gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
WorkingDirectory=$INSTALL_DIR
User=$SUDO_USER
Group=$SUDO_USER
Restart=on-failure
Environment="PATH=$INSTALL_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=$INSTALL_DIR/.env

[Install]
WantedBy=multi-user.target
EOF
    
    # Systemd neu laden
    systemctl daemon-reload
    
    # Service aktivieren und starten
    systemctl enable swissairdry.service
    systemctl start swissairdry.service
    
    success "Systemd-Service für SwissAirDry erstellt und gestartet!"
}

# Hauptinstallationsroutine
main() {
    echo "================================================================="
    echo "        SwissAirDry Platform - Installationsprogramm             "
    echo "================================================================="
    echo
    
    # Frage, ob die Installation fortgesetzt werden soll
    read -p "Möchten Sie mit der Installation fortfahren? (j/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Jj]$ ]]; then
        exit 1
    fi
    
    # Installation der Abhängigkeiten
    install_dependencies
    
    # Repository klonen
    clone_repository
    
    # Python-Umgebung einrichten
    setup_python_env
    
    # Datenbank einrichten
    setup_database
    
    # MQTT-Broker einrichten
    setup_mqtt
    
    # Bluetooth-Dienst einrichten
    setup_bluetooth
    
    # Frage, ob ein Systemd-Service erstellt werden soll
    read -p "Möchten Sie einen Systemd-Service für SwissAirDry erstellen? (j/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Jj]$ ]]; then
        create_service
    fi
    
    echo
    echo "================================================================="
    echo "      SwissAirDry Platform wurde erfolgreich installiert!        "
    echo "================================================================="
    echo
    echo "Die Anwendung ist unter http://localhost:5000 erreichbar."
    echo
    echo "Um die Anwendung manuell zu starten, führen Sie folgende Befehle aus:"
    echo "  cd ERP"
    echo "  source venv/bin/activate"
    echo "  python main.py"
    echo
    echo "Wenn Sie den Systemd-Service eingerichtet haben, können Sie ihn"
    echo "mit folgenden Befehlen verwalten:"
    echo "  systemctl start swissairdry   # Starten"
    echo "  systemctl stop swissairdry    # Stoppen"
    echo "  systemctl restart swissairdry # Neustarten"
    echo "  systemctl status swissairdry  # Status anzeigen"
    echo
}

# Starte die Installation
main