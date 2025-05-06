#!/bin/bash
# ------------------------------------------------------------------------------
# SwissAirDry - All-in-One Installation
# ------------------------------------------------------------------------------
# Dieses Skript startet alle Komponenten von SwissAirDry und Nextcloud
# ------------------------------------------------------------------------------

set -e

# Farben für die Ausgabe
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Banner anzeigen
echo -e "${BLUE}${BOLD}"
echo "SwissAirDry + Nextcloud - All-in-One Installation"
echo "================================================="
echo -e "${NC}"

# Prüfen, ob Docker und Docker Compose installiert sind
if ! command -v docker >/dev/null 2>&1; then
    echo -e "${RED}FEHLER: Docker ist nicht installiert.${NC}"
    echo "Bitte folgen Sie der Anleitung unter https://docs.docker.com/get-docker/"
    exit 1
fi

if ! docker compose version >/dev/null 2>&1 && ! command -v docker-compose >/dev/null 2>&1; then
    echo -e "${RED}FEHLER: Docker Compose ist nicht installiert.${NC}"
    echo "Bitte folgen Sie der Anleitung unter https://docs.docker.com/compose/install/"
    exit 1
fi

# Konfigurationsdatei prüfen und ggf. erstellen
if [ ! -f .env ]; then
    echo -e "${YELLOW}Keine .env-Datei gefunden. Erstelle Standard-Konfiguration...${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}.env-Datei aus Beispiel erstellt.${NC}"
    else
        cat > .env << 'EOF'
# SwissAirDry Konfiguration
API_PORT=5000
SIMPLE_API_PORT=5001
MQTT_PORT=1883
MQTT_WS_PORT=9001
DB_USER=postgres
DB_PASSWORD=swissairdry
DB_NAME=swissairdry

# Nextcloud Konfiguration
NEXTCLOUD_ADMIN_USER=admin
NEXTCLOUD_ADMIN_PASSWORD=admin
NEXTCLOUD_DB_NAME=nextcloud
NEXTCLOUD_DB_USER=nextcloud
NEXTCLOUD_DB_PASSWORD=nextcloud
NEXTCLOUD_TRUSTED_DOMAINS=localhost nextcloud

# ExApp Konfiguration
EXAPP_PORT=8080
EXAPP_DAEMON_PORT=8081
EXAPP_SECRET_KEY=please_change_me_in_production

# Portainer Konfiguration
PORTAINER_PORT=9000
EOF
        echo -e "${GREEN}Standard-.env-Datei erstellt.${NC}"
    fi
    echo -e "${YELLOW}Bitte überprüfen und bearbeiten Sie die .env-Datei für Ihre Umgebung.${NC}"
    echo -e "Sie können diese Installation fortsetzen oder mit STRG+C abbrechen."
    read -p "Drücken Sie EINGABE, um fortzufahren... " -r
    echo
fi

# Prüfen auf nginx-Konfigurationsverzeichnis
if [ ! -d nginx/conf.d ]; then
    echo -e "${YELLOW}Nginx-Konfigurationsverzeichnis nicht gefunden. Erstelle Verzeichnis...${NC}"
    mkdir -p nginx/conf.d
    mkdir -p nginx/ssl
    
    # Standard-Nginx-Konfiguration erstellen
    cat > nginx/conf.d/nextcloud.conf << 'EOF'
upstream nextcloud-php-handler {
    server nextcloud:9000;
}

server {
    listen 80;
    server_name nextcloud;

    # Add headers to serve security related headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-XSS-Protection "1; mode=block";
    add_header X-Robots-Tag none;
    add_header X-Download-Options noopen;
    add_header X-Permitted-Cross-Domain-Policies none;
    add_header Referrer-Policy no-referrer;

    root /var/www/html;

    location = /robots.txt {
        allow all;
        log_not_found off;
        access_log off;
    }

    location = /.well-known/carddav {
        return 301 $scheme://$host/remote.php/dav;
    }
    location = /.well-known/caldav {
        return 301 $scheme://$host/remote.php/dav;
    }

    # set max upload size
    client_max_body_size 512M;
    fastcgi_buffers 64 4K;

    # Enable gzip but do not remove ETag headers
    gzip on;
    gzip_vary on;
    gzip_comp_level 4;
    gzip_min_length 256;
    gzip_proxied expired no-cache no-store private no_last_modified no_etag auth;
    gzip_types application/atom+xml application/javascript application/json application/ld+json application/manifest+json application/rss+xml application/vnd.geo+json application/vnd.ms-fontobject application/x-font-ttf application/x-web-app-manifest+json application/xhtml+xml application/xml font/opentype image/bmp image/svg+xml image/x-icon text/cache-manifest text/css text/plain text/vcard text/vnd.rim.location.xloc text/vtt text/x-component text/x-cross-domain-policy;

    # Pagespeed is not supported by Nextcloud, so if your server is built
    # with the `ngx_pagespeed` module, uncomment this line to disable it.
    #pagespeed off;

    location / {
        rewrite ^ /index.php;
    }

    location ~ ^\/(?:build|tests|config|lib|3rdparty|templates|data)\/ {
        deny all;
    }
    location ~ ^\/(?:\.|autotest|occ|issue|indie|db_|console) {
        deny all;
    }

    location ~ ^\/(?:index|remote|public|cron|core\/ajax\/update|status|ocs\/v[12]|updater\/.+|oc[ms]-provider\/.+|.+\/richdocumentscode\/proxy)\.php(?:$|\/) {
        fastcgi_split_path_info ^(.+?\.php)(\/.*|)$;
        set $path_info $fastcgi_path_info;
        try_files $fastcgi_script_name =404;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        fastcgi_param PATH_INFO $path_info;
        fastcgi_param HTTPS on;
        # Avoid sending the security headers twice
        fastcgi_param modHeadersAvailable true;
        # Enable pretty urls
        fastcgi_param front_controller_active true;
        fastcgi_pass nextcloud-php-handler;
        fastcgi_intercept_errors on;
        fastcgi_request_buffering off;
    }

    location ~ ^\/(?:updater|oc[ms]-provider)(?:$|\/) {
        try_files $uri/ =404;
        index index.php;
    }

    # Adding the cache control header for js, css and map files
    # Make sure it is BELOW the PHP block
    location ~ \.(?:css|js|woff2?|svg|gif|map)$ {
        try_files $uri /index.php$request_uri;
        add_header Cache-Control "public, max-age=15778463";
        # Add headers to serve security related headers (It is intended to have those duplicated to the ones above)
        # Before enabling Strict-Transport-Security headers please read into this topic first.
        #add_header Strict-Transport-Security "max-age=15768000; includeSubDomains; preload;" always;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header X-Robots-Tag none;
        add_header X-Download-Options noopen;
        add_header X-Permitted-Cross-Domain-Policies none;
        add_header Referrer-Policy no-referrer;
        # Optional: Don't log access to assets
        access_log off;
    }

    location ~ \.(?:png|html|ttf|ico|jpg|jpeg|bcmap|mp4|webm)$ {
        try_files $uri /index.php$request_uri;
        # Optional: Don't log access to other assets
        access_log off;
    }
}
EOF

    # Konfiguration für die API
    cat > nginx/conf.d/api.conf << 'EOF'
server {
    listen 80;
    server_name api;

    location / {
        proxy_pass http://api:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name simple-api;

    location / {
        proxy_pass http://simple-api:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

    echo -e "${GREEN}Standard-Nginx-Konfiguration erstellt.${NC}"
fi

# Prüfen auf MQTT-Konfiguration
if [ ! -d mosquitto/config ]; then
    echo -e "${YELLOW}MQTT-Konfigurationsverzeichnis nicht gefunden. Erstelle Verzeichnis...${NC}"
    mkdir -p mosquitto/config
    
    # Standard-MQTT-Konfiguration erstellen
    cat > mosquitto/config/mosquitto.conf << 'EOF'
# SwissAirDry MQTT-Broker-Konfiguration

# Allgemeine Einstellungen
listener 1883
protocol mqtt

# WebSocket-Listener
listener 9001
protocol websockets

# Persistenz
persistence true
persistence_location /mosquitto/data/
persistent_client_expiration 1d

# Logging
log_dest file /mosquitto/log/mosquitto.log
log_dest stdout

# Standard-Berechtigung (Kann über Umgebungsvariablen geändert werden)
allow_anonymous true

# Weitere Einstellungen können hier ergänzt werden
EOF

    echo -e "${GREEN}Standard-MQTT-Konfiguration erstellt.${NC}"
fi

# Mit Docker-Compose starten
echo -e "${BLUE}Starte SwissAirDry + Nextcloud All-in-One...${NC}"

# Docker Compose-Befehl ermitteln
if docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

# Container starten
$DOCKER_COMPOSE -f docker-compose-all-in-one.yml up -d

# Ausgabe nach erfolgreichem Start
echo
echo -e "${GREEN}${BOLD}SwissAirDry + Nextcloud All-in-One erfolgreich gestartet!${NC}"
echo
echo -e "${BLUE}Sie können folgende Dienste erreichen:${NC}"
echo -e " * ${BOLD}Portainer (Container-Management):${NC} http://localhost:${PORTAINER_PORT:-9000}"
echo -e " * ${BOLD}Nextcloud:${NC} http://localhost:80"
echo -e " * ${BOLD}SwissAirDry API:${NC} http://localhost:${API_PORT:-5000}"
echo -e " * ${BOLD}SwissAirDry Simple API:${NC} http://localhost:${SIMPLE_API_PORT:-5001}"
echo -e " * ${BOLD}SwissAirDry ExApp:${NC} http://localhost:${EXAPP_PORT:-8080}"
echo -e " * ${BOLD}SwissAirDry ExApp Daemon:${NC} http://localhost:${EXAPP_DAEMON_PORT:-8081}"
echo -e " * ${BOLD}MQTT Broker:${NC} localhost:${MQTT_PORT:-1883} (für MQTT-Clients)"
echo -e " * ${BOLD}MQTT WebSockets:${NC} localhost:${MQTT_WS_PORT:-9001} (für Browser-Clients)"
echo
echo -e "${YELLOW}Hinweis: Der erste Start kann einige Minuten dauern, während die Container initialisiert werden.${NC}"
echo -e "${YELLOW}Sie können die Logs mit '${DOCKER_COMPOSE} -f docker-compose-all-in-one.yml logs -f' anzeigen.${NC}"
echo
echo -e "${BLUE}${BOLD}Viel Erfolg mit SwissAirDry!${NC}"