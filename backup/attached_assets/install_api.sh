#!/bin/bash
#
# SwissAirDry API Installationsskript
# Dieses Skript installiert nur die API-Komponente des SwissAirDry-Systems
#

set -e  # Bei Fehlern abbrechen

echo "
===============================================
   SwissAirDry API Installationsskript
===============================================
"

# Arbeitsverzeichnis erstellen, falls nicht vorhanden
INSTALL_DIR="$HOME/swissairdry"
API_DIR="$INSTALL_DIR/api"

echo "[1/6] Arbeitsverzeichnis wird vorbereitet..."
mkdir -p "$API_DIR"
mkdir -p "$API_DIR/app"
mkdir -p "$API_DIR/logs"

# Aktuelle Position merken
CURRENT_DIR=$(pwd)

# Abhängigkeiten prüfen und installieren
echo "[2/6] Python-Abhängigkeiten werden installiert..."
pip install fastapi uvicorn sqlalchemy pydantic psycopg2-binary python-dotenv paho-mqtt python-multipart jinja2 --no-cache-dir

# Environment-Variablen
echo "[3/6] Environment-Konfiguration wird erstellt..."
cat > "$INSTALL_DIR/.env" << 'EOL'
# SwissAirDry API Konfiguration
API_HOST=0.0.0.0
API_PORT=5000
API_DEBUG=true
API_RELOAD=true
API_WORKERS=1
API_TITLE="SwissAirDry API"
API_DESCRIPTION="REST API für das SwissAirDry Trocknungsgeräte-Management-System"
API_VERSION="1.0.0"

# Datenbank-Konfiguration
DB_ENGINE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=swissairdry
DB_NAME=swissairdry

# MQTT-Konfiguration
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_CLIENT_ID=swissairdry-api
MQTT_USERNAME=
MQTT_PASSWORD=
MQTT_USE_SSL=false
MQTT_QOS=1
MQTT_RETAIN=true
MQTT_TOPIC_PREFIX=swissairdry
EOL

# API-Dateien kopieren
echo "[4/6] API-Dateien werden kopiert..."
if [ -d "$CURRENT_DIR/swissairdry/api" ]; then
    cp -r "$CURRENT_DIR/swissairdry/api"/* "$API_DIR/"
    echo "Dateien aus '$CURRENT_DIR/swissairdry/api' kopiert."
else
    echo "WARNUNG: Verzeichnis '$CURRENT_DIR/swissairdry/api' nicht gefunden. Erstelle minimale API-Konfiguration."
    
    # Hauptanwendungsdatei erstellen
    cat > "$API_DIR/app/run2.py" << 'EOL'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SwissAirDry API Server

Eine REST API für das SwissAirDry Trocknungsgeräte-Management-System.
"""

import os
import uvicorn
from dotenv import load_dotenv
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Lade Umgebungsvariablen aus .env-Datei
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# API-Konfiguration aus Umgebungsvariablen
HOST = os.getenv("API_HOST", "0.0.0.0")
PORT = int(os.getenv("API_PORT", "5000"))
DEBUG = os.getenv("API_DEBUG", "true").lower() == "true"
RELOAD = os.getenv("API_RELOAD", "true").lower() == "true"
WORKERS = int(os.getenv("API_WORKERS", "1"))
TITLE = os.getenv("API_TITLE", "SwissAirDry API")
DESCRIPTION = os.getenv("API_DESCRIPTION", "REST API für das SwissAirDry Trocknungsgeräte-Management-System")
VERSION = os.getenv("API_VERSION", "1.0.0")

# FastAPI-App initialisieren
app = FastAPI(
    title=TITLE,
    description=DESCRIPTION,
    version=VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Templates für HTML-Rendering
templates_dir = Path(__file__).resolve().parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

# Statische Dateien
static_dir = Path(__file__).resolve().parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Root-Route
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    # Einfache HTML-Antwort
    return """
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SwissAirDry API</title>
        <style>
            :root {
                --primary-color: #0066cc;
                --secondary-color: #004999;
                --accent-color: #ff6600;
                --light-color: #f5f9ff;
                --dark-color: #333;
                --success-color: #28a745;
                --warning-color: #ffc107;
                --danger-color: #dc3545;
                --gray-color: #6c757d;
                --light-gray: #e9ecef;
            }

            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }

            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: var(--dark-color);
                background-color: #f8f9fa;
            }

            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }

            /* Header */
            header {
                text-align: center;
                margin-bottom: 40px;
                padding: 30px 0;
                background-color: var(--light-color);
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }

            header h1 {
                color: var(--primary-color);
                font-size: 2.5rem;
                margin-bottom: 10px;
            }

            .subtitle {
                font-size: 1.2rem;
                color: var(--gray-color);
            }

            /* Cards */
            .info-card {
                background-color: white;
                border-radius: 8px;
                padding: 25px;
                margin-bottom: 30px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }

            .info-card h2 {
                color: var(--primary-color);
                margin-bottom: 15px;
                border-bottom: 2px solid var(--light-gray);
                padding-bottom: 10px;
            }

            .info-card p {
                margin-bottom: 15px;
            }

            /* API Endpoints */
            .api-section {
                margin-bottom: 30px;
            }

            .api-section h2 {
                color: var(--primary-color);
                margin-bottom: 20px;
                text-align: center;
            }

            .endpoints {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 20px;
            }

            .endpoint {
                background-color: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }

            .endpoint h3 {
                color: var(--secondary-color);
                margin-bottom: 15px;
                border-bottom: 1px solid var(--light-gray);
                padding-bottom: 8px;
            }

            .endpoint ul {
                list-style-type: none;
            }

            .endpoint li {
                margin-bottom: 10px;
                padding-left: 10px;
                border-left: 3px solid var(--light-gray);
            }

            .endpoint li:hover {
                border-left-color: var(--accent-color);
            }

            .method {
                display: inline-block;
                padding: 2px 6px;
                margin-right: 8px;
                background-color: var(--primary-color);
                color: white;
                border-radius: 4px;
                font-size: 0.8rem;
                font-weight: bold;
            }

            /* Buttons */
            .button {
                display: inline-block;
                padding: 10px 20px;
                margin: 10px 5px;
                background-color: var(--primary-color);
                color: white;
                text-decoration: none;
                border-radius: 4px;
                transition: background-color 0.3s;
            }

            .button:hover {
                background-color: var(--secondary-color);
            }

            /* Footer */
            footer {
                text-align: center;
                margin-top: 50px;
                padding: 20px 0;
                color: var(--gray-color);
                font-size: 0.9rem;
            }

            footer a {
                color: var(--primary-color);
                text-decoration: none;
            }

            footer a:hover {
                text-decoration: underline;
            }

            @media (max-width: 768px) {
                .container {
                    padding: 10px;
                }
                
                header {
                    padding: 20px 0;
                }
                
                header h1 {
                    font-size: 2rem;
                }
                
                .endpoints {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>SwissAirDry API</h1>
                <p class="subtitle">REST-API für das SwissAirDry Trocknungsgeräte-Management-System</p>
            </header>
            
            <section class="info-card">
                <h2>Über die API</h2>
                <p>Die SwissAirDry API bietet eine Schnittstelle zur Steuerung und Überwachung von Trocknungsgeräten, Verwaltung von Kundeninformationen, Auftragsmanagement und Sensordaten-Tracking.</p>
                <p>Diese API unterstützt IoT-Geräte, mobile Apps und Web-Anwendungen des SwissAirDry-Ökosystems.</p>
            </section>
            
            <section class="api-section">
                <h2>API-Endpunkte</h2>
                <div class="endpoints">
                    <div class="endpoint">
                        <h3>Geräte-API</h3>
                        <ul>
                            <li><span class="method">GET</span> /api/devices - Liste aller Geräte</li>
                            <li><span class="method">POST</span> /api/devices - Neues Gerät erstellen</li>
                            <li><span class="method">GET</span> /api/devices/{device_id} - Gerätdetails abrufen</li>
                            <li><span class="method">PUT</span> /api/devices/{device_id} - Gerät aktualisieren</li>
                            <li><span class="method">DELETE</span> /api/devices/{device_id} - Gerät löschen</li>
                        </ul>
                    </div>
                    
                    <div class="endpoint">
                        <h3>Sensordaten-API</h3>
                        <ul>
                            <li><span class="method">POST</span> /api/device/{device_id}/data - Sensordaten senden</li>
                            <li><span class="method">GET</span> /api/device/{device_id}/data - Sensordaten abrufen</li>
                        </ul>
                    </div>
                    
                    <div class="endpoint">
                        <h3>Kunden-API</h3>
                        <ul>
                            <li><span class="method">GET</span> /api/customers - Liste aller Kunden</li>
                            <li><span class="method">POST</span> /api/customers - Neuen Kunden erstellen</li>
                            <li><span class="method">GET</span> /api/customers/{customer_id} - Kundendetails abrufen</li>
                        </ul>
                    </div>
                    
                    <div class="endpoint">
                        <h3>Auftrags-API</h3>
                        <ul>
                            <li><span class="method">GET</span> /api/jobs - Liste aller Aufträge</li>
                            <li><span class="method">POST</span> /api/jobs - Neuen Auftrag erstellen</li>
                            <li><span class="method">GET</span> /api/jobs/{job_id} - Auftragsdetails abrufen</li>
                        </ul>
                    </div>
                </div>
            </section>
            
            <section class="info-card">
                <h2>Dokumentation</h2>
                <p>Die vollständige API-Dokumentation finden Sie unter:</p>
                <a href="/docs" class="button">OpenAPI-Dokumentation</a>
                <a href="/redoc" class="button">ReDoc-Dokumentation</a>
            </section>
            
            <footer>
                <p>&copy; 2023-2025 Swiss Air Dry Team</p>
                <p><a href="/admin">Admin-Bereich</a> | <a href="/health">Status</a></p>
            </footer>
        </div>
    </body>
    </html>
    """

# Gesundheitscheck-Route
@app.get("/health")
async def health():
    return {"status": "ok", "version": VERSION}

# Administrationsbereich
@app.get("/admin", response_class=HTMLResponse)
async def admin(request: Request):
    # Einfache Admin-Seite
    return """
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SwissAirDry API - Admin</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background-color: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h1 {
                color: #0066cc;
            }
            .info-box {
                background-color: #e9f5ff;
                border-left: 4px solid #0066cc;
                padding: 15px;
                margin: 15px 0;
                border-radius: 4px;
            }
            .back {
                margin-top: 20px;
                display: inline-block;
                padding: 8px 16px;
                background-color: #0066cc;
                color: white;
                text-decoration: none;
                border-radius: 4px;
            }
            .back:hover {
                background-color: #004999;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>SwissAirDry API - Administration</h1>
            <div class="info-box">
                <p>Hier wird die Admin-Oberfläche für die SwissAirDry API implementiert.</p>
                <p>Funktionen in Entwicklung:</p>
                <ul>
                    <li>Gerätemanagement</li>
                    <li>Benutzerverwaltung</li>
                    <li>Systemkonfiguration</li>
                    <li>Protokolle und Überwachung</li>
                </ul>
            </div>
            <a href="/" class="back">Zurück zur Hauptseite</a>
        </div>
    </body>
    </html>
    """

# API-Routen und MQTT-Integration hier ergänzen...


# Server starten, wenn direkt ausgeführt
if __name__ == "__main__":
    print(f"SwissAirDry API startet auf {HOST}:{PORT}")
    uvicorn.run(
        "run2:app", 
        host=HOST, 
        port=PORT, 
        reload=RELOAD,
        workers=WORKERS
    )
EOL

    # Simple API-Datei erstellen
    mkdir -p "$API_DIR"
    cat > "$API_DIR/start_simple.py" << 'EOL'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SwissAirDry Simple API Server

Eine vereinfachte API für das SwissAirDry System, 
optimiert für IoT-Geräte und einfache Integrationen.
"""

import os
import sys
import json
import paho.mqtt.client as mqtt
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from dotenv import load_dotenv
from pathlib import Path

# Lade Umgebungsvariablen aus .env-Datei
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# API-Konfiguration aus Umgebungsvariablen
HOST = os.getenv("API_HOST", "0.0.0.0")
PORT = 5001  # Anderer Port als die Haupt-API
DEBUG = os.getenv("API_DEBUG", "true").lower() == "true"

# MQTT-Konfiguration
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_CLIENT_ID = os.getenv("MQTT_CLIENT_ID", "swissairdry-simple-api")
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")
MQTT_USE_SSL = os.getenv("MQTT_USE_SSL", "false").lower() == "true"
MQTT_QOS = int(os.getenv("MQTT_QOS", "1"))
MQTT_TOPIC_PREFIX = os.getenv("MQTT_TOPIC_PREFIX", "swissairdry")

# Flask-App initialisieren
app = Flask(__name__)
CORS(app)  # Cross-Origin Resource Sharing aktivieren

# MQTT-Client initialisieren
client = mqtt.Client(client_id=MQTT_CLIENT_ID)

if MQTT_USERNAME and MQTT_PASSWORD:
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

# MQTT-Callback-Funktionen
def on_connect(client, userdata, flags, rc):
    """Bei erfolgreicher Verbindung zum MQTT-Broker aufgerufen."""
    print(f"Mit MQTT-Broker verbunden. Ergebnis-Code: {rc}")
    # Alle Topics abonnieren
    client.subscribe(f"{MQTT_TOPIC_PREFIX}/#")

def on_message(client, userdata, msg):
    """Bei einer eingehenden MQTT-Nachricht aufgerufen."""
    topic = msg.topic
    payload = msg.payload.decode()
    print(f"MQTT-Nachricht empfangen: {topic}")
    try:
        # Payload als JSON parsen, falls möglich
        data = json.loads(payload)
        # Hier kann die Datenverarbeitung erfolgen
    except json.JSONDecodeError:
        # Falls kein gültiges JSON, als Zeichenkette behandeln
        data = payload

def on_disconnect(client, userdata, rc):
    """Bei Verbindungsabbruch zum MQTT-Broker aufgerufen."""
    if rc != 0:
        print(f"Unerwartete Trennung vom MQTT-Broker. Code: {rc}")

# MQTT-Callbacks registrieren
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

# MQTT-Verbindung herstellen
try:
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()  # Starte MQTT-Loop im Hintergrund
except Exception as e:
    print(f"Fehler bei MQTT-Verbindung: {e}")

# API-Routen
@app.route('/')
def home():
    """Homepage der Simple API."""
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SwissAirDry API</title>
        <style>
            :root {
                --primary-color: #0066cc;
                --secondary-color: #004999;
                --accent-color: #ff6600;
                --light-color: #f5f9ff;
                --dark-color: #333;
                --success-color: #28a745;
                --warning-color: #ffc107;
                --danger-color: #dc3545;
                --gray-color: #6c757d;
                --light-gray: #e9ecef;
            }

            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }

            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: var(--dark-color);
                background-color: #f8f9fa;
            }

            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }

            /* Header */
            header {
                text-align: center;
                margin-bottom: 40px;
                padding: 30px 0;
                background-color: var(--light-color);
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }

            header h1 {
                color: var(--primary-color);
                font-size: 2.5rem;
                margin-bottom: 10px;
            }

            .subtitle {
                font-size: 1.2rem;
                color: var(--gray-color);
            }

            /* Cards */
            .info-card {
                background-color: white;
                border-radius: 8px;
                padding: 25px;
                margin-bottom: 30px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }

            .info-card h2 {
                color: var(--primary-color);
                margin-bottom: 15px;
                border-bottom: 2px solid var(--light-gray);
                padding-bottom: 10px;
            }

            .info-card p {
                margin-bottom: 15px;
            }

            /* API Endpoints */
            .api-section {
                margin-bottom: 30px;
            }

            .api-section h2 {
                color: var(--primary-color);
                margin-bottom: 20px;
                text-align: center;
            }

            .endpoints {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 20px;
            }

            .endpoint {
                background-color: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }

            .endpoint h3 {
                color: var(--secondary-color);
                margin-bottom: 15px;
                border-bottom: 1px solid var(--light-gray);
                padding-bottom: 8px;
            }

            .endpoint ul {
                list-style-type: none;
            }

            .endpoint li {
                margin-bottom: 10px;
                padding-left: 10px;
                border-left: 3px solid var(--light-gray);
            }

            .endpoint li:hover {
                border-left-color: var(--accent-color);
            }

            .method {
                display: inline-block;
                padding: 2px 6px;
                margin-right: 8px;
                background-color: var(--primary-color);
                color: white;
                border-radius: 4px;
                font-size: 0.8rem;
                font-weight: bold;
            }

            /* Buttons */
            .button {
                display: inline-block;
                padding: 10px 20px;
                margin: 10px 5px;
                background-color: var(--primary-color);
                color: white;
                text-decoration: none;
                border-radius: 4px;
                transition: background-color 0.3s;
            }

            .button:hover {
                background-color: var(--secondary-color);
            }

            /* Footer */
            footer {
                text-align: center;
                margin-top: 50px;
                padding: 20px 0;
                color: var(--gray-color);
                font-size: 0.9rem;
            }

            footer a {
                color: var(--primary-color);
                text-decoration: none;
            }

            footer a:hover {
                text-decoration: underline;
            }

            @media (max-width: 768px) {
                .container {
                    padding: 10px;
                }
                
                header {
                    padding: 20px 0;
                }
                
                header h1 {
                    font-size: 2rem;
                }
                
                .endpoints {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>SwissAirDry API</h1>
                <p class="subtitle">REST-API für das SwissAirDry Trocknungsgeräte-Management-System</p>
            </header>
            
            <section class="info-card">
                <h2>Über die API</h2>
                <p>Die SwissAirDry API bietet eine Schnittstelle zur Steuerung und Überwachung von Trocknungsgeräten, Verwaltung von Kundeninformationen, Auftragsmanagement und Sensordaten-Tracking.</p>
                <p>Diese API unterstützt IoT-Geräte, mobile Apps und Web-Anwendungen des SwissAirDry-Ökosystems.</p>
            </section>
            
            <section class="api-section">
                <h2>API-Endpunkte</h2>
                <div class="endpoints">
                    <div class="endpoint">
                        <h3>Geräte-API</h3>
                        <ul>
                            <li><span class="method">GET</span> /api/devices - Liste aller Geräte</li>
                            <li><span class="method">POST</span> /api/devices - Neues Gerät erstellen</li>
                            <li><span class="method">GET</span> /api/devices/{device_id} - Gerätdetails abrufen</li>
                            <li><span class="method">PUT</span> /api/devices/{device_id} - Gerät aktualisieren</li>
                            <li><span class="method">DELETE</span> /api/devices/{device_id} - Gerät löschen</li>
                        </ul>
                    </div>
                    
                    <div class="endpoint">
                        <h3>Sensordaten-API</h3>
                        <ul>
                            <li><span class="method">POST</span> /api/device/{device_id}/data - Sensordaten senden</li>
                            <li><span class="method">GET</span> /api/device/{device_id}/data - Sensordaten abrufen</li>
                        </ul>
                    </div>
                    
                    <div class="endpoint">
                        <h3>Kunden-API</h3>
                        <ul>
                            <li><span class="method">GET</span> /api/customers - Liste aller Kunden</li>
                            <li><span class="method">POST</span> /api/customers - Neuen Kunden erstellen</li>
                            <li><span class="method">GET</span> /api/customers/{customer_id} - Kundendetails abrufen</li>
                        </ul>
                    </div>
                    
                    <div class="endpoint">
                        <h3>Auftrags-API</h3>
                        <ul>
                            <li><span class="method">GET</span> /api/jobs - Liste aller Aufträge</li>
                            <li><span class="method">POST</span> /api/jobs - Neuen Auftrag erstellen</li>
                            <li><span class="method">GET</span> /api/jobs/{job_id} - Auftragsdetails abrufen</li>
                        </ul>
                    </div>
                </div>
            </section>
            
            <section class="info-card">
                <h2>Dokumentation</h2>
                <p>Die vollständige API-Dokumentation finden Sie unter:</p>
                <a href="/docs" class="button">OpenAPI-Dokumentation</a>
                <a href="/redoc" class="button">ReDoc-Dokumentation</a>
            </section>
            
            <footer>
                <p>&copy; 2023-2025 Swiss Air Dry Team</p>
                <p><a href="/admin">Admin-Bereich</a> | <a href="/health">Status</a></p>
            </footer>
        </div>
    </body>
    </html>
    """)

@app.route('/api/devices', methods=['GET'])
def get_devices():
    """Liste aller Geräte abrufen."""
    # In einer echten Anwendung würden hier Daten aus einer Datenbank abgerufen
    devices = [
        {"id": "device-001", "name": "Trocknungsgerät 1", "status": "active", "type": "dehumidifier"},
        {"id": "device-002", "name": "Trocknungsgerät 2", "status": "inactive", "type": "dehumidifier"},
        {"id": "device-003", "name": "Ventilator 1", "status": "active", "type": "fan"}
    ]
    return jsonify(devices)

@app.route('/api/devices/<device_id>', methods=['GET'])
def get_device(device_id):
    """Details zu einem bestimmten Gerät abrufen."""
    # Beispiel für Gerätedetails
    device = {
        "id": device_id,
        "name": f"Gerät {device_id}",
        "status": "active",
        "type": "dehumidifier",
        "location": "Baustelle A",
        "current_readings": {
            "temperature": 22.5,
            "humidity": 65.8,
            "power": 420.5
        }
    }
    return jsonify(device)

@app.route('/api/device/<device_id>/data', methods=['POST'])
def post_device_data(device_id):
    """Sensordaten von einem Gerät empfangen und verarbeiten."""
    data = request.json
    if not data:
        return jsonify({"error": "Keine Daten empfangen"}), 400
    
    # Daten über MQTT veröffentlichen
    try:
        mqtt_topic = f"{MQTT_TOPIC_PREFIX}/device/{device_id}/data"
        result = client.publish(
            topic=mqtt_topic,
            payload=json.dumps(data),
            qos=MQTT_QOS,
            retain=False
        )
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            return jsonify({"success": True, "message": "Daten empfangen und veröffentlicht"})
        else:
            return jsonify({"success": False, "message": "Fehler beim Veröffentlichen via MQTT"}), 500
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/device/<device_id>/control', methods=['POST'])
def control_device(device_id):
    """Steuerungsbefehle an ein Gerät senden."""
    data = request.json
    if not data or 'command' not in data:
        return jsonify({"error": "Kein gültiger Steuerungsbefehl"}), 400
    
    command = data['command']
    params = data.get('params', {})
    
    # Befehl über MQTT veröffentlichen
    try:
        mqtt_topic = f"{MQTT_TOPIC_PREFIX}/device/{device_id}/command"
        message = {
            "command": command,
            "params": params,
            "timestamp": int(time.time())
        }
        
        result = client.publish(
            topic=mqtt_topic,
            payload=json.dumps(message),
            qos=MQTT_QOS,
            retain=False
        )
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            return jsonify({"success": True, "message": f"Befehl '{command}' gesendet"})
        else:
            return jsonify({"success": False, "message": "Fehler beim Senden des Befehls"}), 500
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/health')
def health():
    """API-Gesundheitscheck."""
    mqtt_connected = client.is_connected()
    return jsonify({
        "status": "ok",
        "mqtt_connected": mqtt_connected,
        "mqtt_broker": MQTT_BROKER,
        "mqtt_port": MQTT_PORT
    })

# Server starten
if __name__ == "__main__":
    print(f"SwissAirDry Simple API wird gestartet auf {HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=DEBUG)
EOL

    # MQTT Integration erstellen
    mkdir -p "$API_DIR/app/mqtt"
    cat > "$API_DIR/app/mqtt_client.py" << 'EOL'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SwissAirDry MQTT Client

Modul zur Kommunikation mit MQTT-Brokern für das SwissAirDry-System.
"""

import os
import json
import time
import ssl
import paho.mqtt.client as mqtt
import logging
from threading import Thread
from typing import Dict, Any, Optional, Callable

# Logger konfigurieren
logger = logging.getLogger("swissairdry.mqtt")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(ch)

class MQTTClient:
    """MQTT-Client für SwissAirDry."""
    
    def __init__(
        self,
        broker_host: str,
        broker_port: int = 1883,
        client_id: str = "swissairdry-api",
        username: Optional[str] = None,
        password: Optional[str] = None,
        use_ssl: bool = False,
        ca_cert: Optional[str] = None,
        topic_prefix: str = "swissairdry",
        clean_session: bool = True,
        qos: int = 1,
        on_message_callback: Optional[Callable] = None
    ):
        """
        Initialisieren des MQTT-Clients.
        
        Args:
            broker_host: Hostname des MQTT-Brokers
            broker_port: Port des MQTT-Brokers (Standard: 1883)
            client_id: Client-ID für MQTT (Standard: "swissairdry-api")
            username: Benutzername für die Authentifizierung (Optional)
            password: Passwort für die Authentifizierung (Optional)
            use_ssl: TLS/SSL für die Verbindung verwenden (Standard: False)
            ca_cert: CA-Zertifikat für TLS/SSL (Optional)
            topic_prefix: Präfix für MQTT-Topics (Standard: "swissairdry")
            clean_session: Sitzung bereinigen (Standard: True)
            qos: Quality of Service Level (Standard: 1)
            on_message_callback: Callback-Funktion für eingehende Nachrichten
        """
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client_id = client_id
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.ca_cert = ca_cert
        self.topic_prefix = topic_prefix
        self.clean_session = clean_session
        self.qos = qos
        self.connected = False
        self.on_message_callback = on_message_callback
        
        # Client initialisieren
        self.client = mqtt.Client(client_id=client_id, clean_session=clean_session)
        
        # Callbacks einrichten
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        
        # Authentifizierung, falls angegeben
        if username and password:
            self.client.username_pw_set(username, password)
        
        # TLS/SSL konfigurieren, falls aktiviert
        if use_ssl:
            if ca_cert:
                self.client.tls_set(
                    ca_certs=ca_cert,
                    cert_reqs=ssl.CERT_REQUIRED,
                    tls_version=ssl.PROTOCOL_TLSv1_2
                )
            else:
                self.client.tls_set(
                    cert_reqs=ssl.CERT_NONE,
                    tls_version=ssl.PROTOCOL_TLSv1_2
                )
                self.client.tls_insecure_set(True)
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback bei erfolgreicher Verbindung."""
        if rc == 0:
            logger.info(f"Mit MQTT-Broker {self.broker_host}:{self.broker_port} verbunden")
            self.connected = True
            # Abonniere alle Themen unter dem Topic-Präfix
            self.client.subscribe(f"{self.topic_prefix}/#", self.qos)
            logger.info(f"Themen unter {self.topic_prefix}/# abonniert")
        else:
            logger.error(f"Verbindung zum MQTT-Broker fehlgeschlagen. Fehlercode: {rc}")
            self.connected = False
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback bei Verbindungsabbruch."""
        logger.warning(f"Verbindung zum MQTT-Broker getrennt. Grund: {rc}")
        self.connected = False
        if rc != 0:
            logger.info("Versuche, die Verbindung wiederherzustellen...")
            self._reconnect()
    
    def _on_message(self, client, userdata, msg):
        """Callback bei eingehender Nachricht."""
        topic = msg.topic
        payload = msg.payload.decode()
        logger.debug(f"Nachricht empfangen: {topic} => {payload}")
        
        try:
            # Versuchen, die Nachricht als JSON zu parsen
            payload_json = json.loads(payload)
            if self.on_message_callback:
                self.on_message_callback(topic, payload_json)
        except json.JSONDecodeError:
            # Wenn nicht JSON, dann als String behandeln
            if self.on_message_callback:
                self.on_message_callback(topic, payload)
    
    def _reconnect(self):
        """Versucht, die Verbindung wiederherzustellen."""
        try:
            self.client.reconnect()
        except Exception as e:
            logger.error(f"Wiederverbindung fehlgeschlagen: {e}")
    
    def connect(self, retry_interval: int = 5, max_retries: int = -1) -> bool:
        """
        Verbindung zum MQTT-Broker herstellen.
        
        Args:
            retry_interval: Zeit in Sekunden zwischen Wiederholungsversuchen
            max_retries: Maximale Anzahl an Wiederholungsversuchen (-1 für unendliche Versuche)
        
        Returns:
            bool: True bei erfolgreicher Verbindung, False sonst
        """
        retries = 0
        
        while not self.connected and (max_retries == -1 or retries < max_retries):
            try:
                logger.info(f"Verbinde mit MQTT-Broker {self.broker_host}:{self.broker_port}...")
                self.client.connect(self.broker_host, self.broker_port, 60)
                self.client.loop_start()
                
                # Kurz warten und prüfen, ob die Verbindung hergestellt wurde
                time.sleep(1)
                if self.connected:
                    return True
                
                retries += 1
                if max_retries > 0:
                    logger.warning(f"Verbindungsversuch {retries}/{max_retries} fehlgeschlagen")
                else:
                    logger.warning(f"Verbindungsversuch {retries} fehlgeschlagen")
                
                time.sleep(retry_interval)
            except Exception as e:
                logger.error(f"Fehler beim Verbinden: {e}")
                retries += 1
                time.sleep(retry_interval)
        
        return self.connected
    
    def disconnect(self):
        """Verbindung zum MQTT-Broker trennen."""
        try:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
            logger.info("Verbindung zum MQTT-Broker getrennt")
        except Exception as e:
            logger.error(f"Fehler beim Trennen der Verbindung: {e}")
    
    def publish(self, topic: str, payload: Any, retain: bool = False) -> bool:
        """
        Nachricht an ein MQTT-Topic veröffentlichen.
        
        Args:
            topic: MQTT-Topic ohne Präfix
            payload: Nachricht (wird automatisch nach JSON konvertiert, wenn es ein Dict ist)
            retain: Flag, ob die Nachricht beibehalten werden soll (Standard: False)
        
        Returns:
            bool: True bei erfolgreicher Veröffentlichung, False sonst
        """
        if not self.connected:
            logger.warning("Nicht mit MQTT-Broker verbunden, kann nicht veröffentlichen")
            return False
        
        full_topic = f"{self.topic_prefix}/{topic}"
        
        try:
            if isinstance(payload, dict):
                payload_str = json.dumps(payload)
            elif not isinstance(payload, str):
                payload_str = str(payload)
            else:
                payload_str = payload
            
            result = self.client.publish(full_topic, payload_str, self.qos, retain)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.debug(f"Veröffentlicht an {full_topic}: {payload_str}")
                return True
            else:
                logger.error(f"Fehler beim Veröffentlichen an {full_topic}: {result.rc}")
                return False
        except Exception as e:
            logger.error(f"Ausnahme beim Veröffentlichen an {full_topic}: {e}")
            return False
    
    def subscribe(self, topic: str) -> bool:
        """
        Ein MQTT-Topic abonnieren.
        
        Args:
            topic: MQTT-Topic ohne Präfix
        
        Returns:
            bool: True bei erfolgreichem Abonnement, False sonst
        """
        if not self.connected:
            logger.warning("Nicht mit MQTT-Broker verbunden, kann nicht abonnieren")
            return False
        
        full_topic = f"{self.topic_prefix}/{topic}"
        
        try:
            result = self.client.subscribe(full_topic, self.qos)
            if result[0] == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Thema abonniert: {full_topic}")
                return True
            else:
                logger.error(f"Fehler beim Abonnieren von {full_topic}: {result[0]}")
                return False
        except Exception as e:
            logger.error(f"Ausnahme beim Abonnieren von {full_topic}: {e}")
            return False
    
    def unsubscribe(self, topic: str) -> bool:
        """
        Abonnement eines MQTT-Topics kündigen.
        
        Args:
            topic: MQTT-Topic ohne Präfix
        
        Returns:
            bool: True bei erfolgreicher Kündigung, False sonst
        """
        if not self.connected:
            logger.warning("Nicht mit MQTT-Broker verbunden, kann nicht kündigen")
            return False
        
        full_topic = f"{self.topic_prefix}/{topic}"
        
        try:
            result = self.client.unsubscribe(full_topic)
            if result[0] == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Abonnement gekündigt: {full_topic}")
                return True
            else:
                logger.error(f"Fehler beim Kündigen von {full_topic}: {result[0]}")
                return False
        except Exception as e:
            logger.error(f"Ausnahme beim Kündigen von {full_topic}: {e}")
            return False
    
    def is_connected(self) -> bool:
        """
        Prüfen, ob der Client mit dem Broker verbunden ist.
        
        Returns:
            bool: True, wenn verbunden, sonst False
        """
        return self.connected

# Singleton-Instanz für die Anwendung
_mqtt_client_instance = None

def get_mqtt_client(config: Optional[Dict[str, Any]] = None) -> MQTTClient:
    """
    Gibt eine Singleton-Instanz des MQTT-Clients zurück.
    
    Args:
        config: Konfigurationsobjekt (Optional)
    
    Returns:
        MQTTClient: Eine Instanz des MQTT-Clients
    """
    global _mqtt_client_instance
    
    if _mqtt_client_instance is None:
        if config is None:
            # Standardkonfiguration aus Umgebungsvariablen
            config = {
                "broker_host": os.environ.get("MQTT_BROKER", "localhost"),
                "broker_port": int(os.environ.get("MQTT_PORT", "1883")),
                "client_id": os.environ.get("MQTT_CLIENT_ID", "swissairdry-api"),
                "username": os.environ.get("MQTT_USERNAME", ""),
                "password": os.environ.get("MQTT_PASSWORD", ""),
                "use_ssl": os.environ.get("MQTT_USE_SSL", "false").lower() == "true",
                "topic_prefix": os.environ.get("MQTT_TOPIC_PREFIX", "swissairdry"),
                "qos": int(os.environ.get("MQTT_QOS", "1"))
            }
        
        # Leere Strings als None behandeln
        if config.get("username") == "":
            config["username"] = None
        if config.get("password") == "":
            config["password"] = None
        
        _mqtt_client_instance = MQTTClient(
            broker_host=config["broker_host"],
            broker_port=config["broker_port"],
            client_id=config["client_id"],
            username=config["username"],
            password=config["password"],
            use_ssl=config["use_ssl"],
            topic_prefix=config["topic_prefix"],
            qos=config["qos"]
        )
    
    return _mqtt_client_instance

# Beispielcode für die Verwendung
if __name__ == "__main__":
    # Konfiguriere Logging
    logging.basicConfig(level=logging.INFO)
    
    # Callback-Funktion für eingehende Nachrichten
    def on_message(topic, payload):
        print(f"Nachricht empfangen: {topic} => {payload}")
    
    # Client erstellen und verbinden
    mqtt_client = MQTTClient(
        broker_host="localhost",
        broker_port=1883,
        client_id="swissairdry-mqtt-test",
        on_message_callback=on_message
    )
    
    if mqtt_client.connect():
        print("Mit MQTT-Broker verbunden")
        
        # Nachrichten veröffentlichen
        mqtt_client.publish("test/hello", {"message": "Hallo MQTT!", "timestamp": time.time()})
        
        # Warten und Verbindung halten
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Programm beendet")
        finally:
            mqtt_client.disconnect()
    else:
        print("Verbindung zum MQTT-Broker fehlgeschlagen")
EOL

fi

# Startup-Skript erstellen
echo "[5/6] Startup-Skript wird erstellt..."
cat > "$INSTALL_DIR/start_api.sh" << 'EOL'
#!/bin/bash

# SwissAirDry API-Startskript
echo "SwissAirDry API wird gestartet..."

# Zum Installationsverzeichnis wechseln
cd "$(dirname "$0")"

# Umgebungsvariablen laden
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

# Haupt-API starten
echo "Starte Haupt-API auf Port $API_PORT..."
cd api/app
python run2.py >> ../../logs/api.log 2>&1 &
echo $! > ../../api.pid
cd ../..

# Warten, bis der Port geöffnet ist
echo "Warte, bis API bereit ist..."
sleep 3

echo "SwissAirDry API läuft auf http://$API_HOST:$API_PORT"
echo "Logs: $INSTALL_DIR/logs/api.log"
echo "PID: $(cat api.pid)"

echo "API erfolgreich gestartet!"
EOL

chmod +x "$INSTALL_DIR/start_api.sh"

# Simple API Startup-Skript
cat > "$INSTALL_DIR/start_simple_api.sh" << 'EOL'
#!/bin/bash

# SwissAirDry Simple API-Startskript
echo "SwissAirDry Simple API wird gestartet..."

# Zum Installationsverzeichnis wechseln
cd "$(dirname "$0")"

# Umgebungsvariablen laden
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

# Simple API starten
echo "Starte Simple API auf Port 5001..."
cd api
python start_simple.py >> ../logs/simple_api.log 2>&1 &
echo $! > ../simple_api.pid
cd ..

# Warten, bis der Port geöffnet ist
echo "Warte, bis Simple API bereit ist..."
sleep 3

echo "SwissAirDry Simple API läuft auf http://$API_HOST:5001"
echo "Logs: $INSTALL_DIR/logs/simple_api.log"
echo "PID: $(cat simple_api.pid)"

echo "Simple API erfolgreich gestartet!"
EOL

chmod +x "$INSTALL_DIR/start_simple_api.sh"

# Stop-Skript erstellen
cat > "$INSTALL_DIR/stop_api.sh" << 'EOL'
#!/bin/bash

# SwissAirDry API-Stoppskript
echo "SwissAirDry API wird gestoppt..."

# Zum Installationsverzeichnis wechseln
cd "$(dirname "$0")"

# Haupt-API stoppen
if [ -f api.pid ]; then
  PID=$(cat api.pid)
  if ps -p $PID > /dev/null; then
    echo "Beende API-Prozess (PID: $PID)..."
    kill $PID
    rm api.pid
  else
    echo "API-Prozess ist nicht mehr aktiv."
    rm api.pid
  fi
else
  echo "Keine API-PID-Datei gefunden."
fi

# Simple API stoppen
if [ -f simple_api.pid ]; then
  PID=$(cat simple_api.pid)
  if ps -p $PID > /dev/null; then
    echo "Beende Simple API-Prozess (PID: $PID)..."
    kill $PID
    rm simple_api.pid
  else
    echo "Simple API-Prozess ist nicht mehr aktiv."
    rm simple_api.pid
  fi
else
  echo "Keine Simple API-PID-Datei gefunden."
fi

echo "SwissAirDry API gestoppt!"
EOL

chmod +x "$INSTALL_DIR/stop_api.sh"

echo "[6/6] Installation abgeschlossen!"
echo ""
echo "Die SwissAirDry API wurde in $INSTALL_DIR installiert."
echo ""
echo "Um die API zu starten, führen Sie folgende Befehle aus:"
echo "   $INSTALL_DIR/start_api.sh"
echo "   $INSTALL_DIR/start_simple_api.sh"
echo ""
echo "Um die API zu stoppen, führen Sie folgenden Befehl aus:"
echo "   $INSTALL_DIR/stop_api.sh"
echo ""
echo "API-Dokumentation ist verfügbar unter:"
echo "   http://localhost:5000/docs"
echo ""