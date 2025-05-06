#!/usr/bin/env python3
"""
SwissAirDry Minimal HTTP Server

Ein einfacher HTTP-Server mit grundlegenden API-Endpunkten für SwissAirDry,
einschließlich eines QR-Code-Generators. Dieser Server hat minimale externe
Abhängigkeiten und kann als eigenständiger Service laufen.

@author Swiss Air Dry Team <info@swissairdry.com>
@copyright 2023-2025 Swiss Air Dry Team
"""

import os
import json
import logging
import time
import socket
import mimetypes
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
from http import HTTPStatus
from datetime import datetime
import io
import base64
import threading
from typing import Dict, Any, List, Optional, Callable, Tuple, Union

# Versuche, QR-Code-Abhängigkeiten zu importieren
try:
    import qrcode
    from qrcode.constants import ERROR_CORRECT_H
    has_qrcode = True
except ImportError:
    has_qrcode = False
    print("QR-Code-Bibliothek nicht gefunden. QR-Code-Funktionalität deaktiviert.")

# Versuche, PIL (für Bildverarbeitung) zu importieren
try:
    from PIL import Image, ImageDraw, ImageFont
    has_pil = True
except ImportError:
    has_pil = False
    print("PIL nicht gefunden. Erweiterte Bildverarbeitungsfunktionen deaktiviert.")

# Konfiguration
HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
PORT = int(os.environ.get('SERVER_PORT', 5003))
DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'

# Logging konfigurieren
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('minimal_http_server')

# Globale Daten (in einer echten Anwendung würde das in einer Datenbank gespeichert)
devices = {
    "1": {
        "id": "1",
        "name": "SwissAirDry Pro 2000",
        "type": "dehumidifier",
        "status": "online",
        "humidity": 65,
        "temperature": 22.5,
        "last_update": "2025-05-01T10:30:00Z"
    },
    "2": {
        "id": "2",
        "name": "SwissAirDry Mini",
        "type": "dehumidifier",
        "status": "offline",
        "humidity": None,
        "temperature": None,
        "last_update": "2025-04-30T18:45:00Z"
    },
    "3": {
        "id": "3",
        "name": "SwissAirDry Heater 500",
        "type": "heater",
        "status": "online",
        "humidity": None,
        "temperature": 28.3,
        "last_update": "2025-05-01T09:15:00Z"
    }
}

# Standard-QR-Code-Größe und Titel
DEFAULT_QR_SIZE = 200
DEFAULT_QR_TITLE = "SwissAirDry QR-Code"


class SwissAirDryRequestHandler(http.server.BaseHTTPRequestHandler):
    """
    HTTP-Request-Handler für den SwissAirDry HTTP-Server.
    """
    
    def _set_headers(self, status_code=200, content_type='application/json'):
        """
        Setzt die HTTP-Header für die Antwort.
        
        Args:
            status_code: HTTP-Statuscode
            content_type: Content-Type-Header
        """
        self.send_response(status_code)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _send_json_response(self, data, status_code=200):
        """
        Sendet eine JSON-Antwort.
        
        Args:
            data: Zu sendende Daten
            status_code: HTTP-Statuscode
        """
        self._set_headers(status_code)
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def _send_text_response(self, text, status_code=200):
        """
        Sendet eine Textantwort.
        
        Args:
            text: Zu sendender Text
            status_code: HTTP-Statuscode
        """
        self._set_headers(status_code, 'text/plain; charset=utf-8')
        self.wfile.write(text.encode('utf-8'))
    
    def _send_html_response(self, html, status_code=200):
        """
        Sendet eine HTML-Antwort.
        
        Args:
            html: Zu sendender HTML-Code
            status_code: HTTP-Statuscode
        """
        self._set_headers(status_code, 'text/html; charset=utf-8')
        self.wfile.write(html.encode('utf-8'))
    
    def _send_image_response(self, image_data, content_type='image/png', status_code=200):
        """
        Sendet eine Bildantwort.
        
        Args:
            image_data: Binärdaten des Bildes
            content_type: MIME-Typ des Bildes
            status_code: HTTP-Statuscode
        """
        self._set_headers(status_code, content_type)
        self.wfile.write(image_data)
    
    def do_OPTIONS(self):
        """
        Behandelt OPTIONS-Anfragen (für CORS).
        """
        self._set_headers()
    
    def do_GET(self):
        """
        Behandelt GET-Anfragen.
        """
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)
        
        # API-Endpunkte
        if path == '/health':
            self._handle_health()
        elif path == '/api/devices':
            self._handle_get_devices()
        elif path.startswith('/api/devices/'):
            device_id = path.split('/')[-1]
            self._handle_get_device(device_id)
        elif path == '/qrcode':
            self._handle_qrcode_generator(query_params)
        elif path == '/api/qrcode':
            self._handle_qrcode_api(query_params)
        else:
            # Allgemeiner Endpunkt für Anfragen, die keinem spezifischen Endpunkt entsprechen
            self._handle_default()
    
    def do_POST(self):
        """
        Behandelt POST-Anfragen.
        """
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        try:
            body = json.loads(post_data) if content_length > 0 else {}
        except json.JSONDecodeError:
            self._send_json_response({"error": "Ungültiges JSON"}, 400)
            return
        
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        # API-Endpunkte
        if path == '/api/devices':
            self._handle_create_device(body)
        elif path.startswith('/api/devices/') and path.endswith('/update'):
            device_id = path.split('/')[-2]
            self._handle_update_device(device_id, body)
        else:
            self._send_json_response({"error": "Endpunkt nicht gefunden"}, 404)
    
    def _handle_health(self):
        """
        Behandelt den Health-Check-Endpunkt.
        """
        self._send_json_response({
            "status": "ok",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "features": {
                "qrcode": has_qrcode,
                "image_processing": has_pil
            }
        })
    
    def _handle_get_devices(self):
        """
        Behandelt den Endpunkt zum Abrufen aller Geräte.
        """
        self._send_json_response(list(devices.values()))
    
    def _handle_get_device(self, device_id):
        """
        Behandelt den Endpunkt zum Abrufen eines einzelnen Geräts.
        
        Args:
            device_id: ID des Geräts
        """
        if device_id in devices:
            self._send_json_response(devices[device_id])
        else:
            self._send_json_response({"error": "Gerät nicht gefunden"}, 404)
    
    def _handle_create_device(self, body):
        """
        Behandelt den Endpunkt zum Erstellen eines neuen Geräts.
        
        Args:
            body: Gerätedaten
        """
        # Grundlegende Validierung
        if not body.get('name'):
            self._send_json_response({"error": "Name ist erforderlich"}, 400)
            return
        
        # Neue ID generieren
        new_id = str(max([int(k) for k in devices.keys()], default=0) + 1)
        
        # Neues Gerät erstellen
        new_device = {
            "id": new_id,
            "name": body.get('name'),
            "type": body.get('type', 'dehumidifier'),
            "status": "offline",
            "humidity": None,
            "temperature": None,
            "last_update": datetime.utcnow().isoformat()
        }
        
        # Optionale Felder hinzufügen, falls vorhanden
        for field in ['humidity', 'temperature', 'status']:
            if field in body:
                new_device[field] = body[field]
        
        # Gerät speichern
        devices[new_id] = new_device
        
        # Antwort senden
        self._send_json_response(new_device, 201)
    
    def _handle_update_device(self, device_id, body):
        """
        Behandelt den Endpunkt zum Aktualisieren eines Geräts.
        
        Args:
            device_id: ID des zu aktualisierenden Geräts
            body: Aktualisierte Gerätedaten
        """
        if device_id not in devices:
            self._send_json_response({"error": "Gerät nicht gefunden"}, 404)
            return
        
        # Gerät aktualisieren
        for field in ['name', 'type', 'status', 'humidity', 'temperature']:
            if field in body:
                devices[device_id][field] = body[field]
        
        # Zeitstempel aktualisieren
        devices[device_id]['last_update'] = datetime.utcnow().isoformat()
        
        # Antwort senden
        self._send_json_response(devices[device_id])
    
    def _handle_default(self):
        """
        Behandelt Standard-Anfragen, die keinem spezifischen Endpunkt entsprechen.
        """
        # Einfache HTML-Seite mit Links zu verfügbaren Endpunkten
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>SwissAirDry API Server</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 40px;
                    line-height: 1.6;
                }
                h1 {
                    color: #333;
                    border-bottom: 1px solid #ccc;
                    padding-bottom: 10px;
                }
                ul {
                    margin-bottom: 30px;
                }
                a {
                    color: #0066cc;
                    text-decoration: none;
                }
                a:hover {
                    text-decoration: underline;
                }
                .endpoint {
                    background-color: #f5f5f5;
                    padding: 10px;
                    border-left: 3px solid #0066cc;
                    margin-bottom: 10px;
                }
                .method {
                    font-weight: bold;
                    margin-right: 10px;
                }
                .get { color: green; }
                .post { color: orange; }
                footer {
                    margin-top: 50px;
                    border-top: 1px solid #ccc;
                    padding-top: 20px;
                    font-size: 0.8em;
                    color: #666;
                }
            </style>
        </head>
        <body>
            <h1>SwissAirDry API Server</h1>
            <p>Willkommen beim SwissAirDry API Server. Folgende Endpunkte sind verfügbar:</p>
            
            <h2>API-Endpunkte:</h2>
            <div class="endpoint">
                <span class="method get">GET</span>
                <a href="/health">/health</a> - Health-Check-Endpunkt
            </div>
            <div class="endpoint">
                <span class="method get">GET</span>
                <a href="/api/devices">/api/devices</a> - Liste aller Geräte abrufen
            </div>
            <div class="endpoint">
                <span class="method get">GET</span>
                <a href="/api/devices/1">/api/devices/{id}</a> - Details eines bestimmten Geräts abrufen
            </div>
            <div class="endpoint">
                <span class="method post">POST</span>
                /api/devices - Neues Gerät erstellen
            </div>
            <div class="endpoint">
                <span class="method post">POST</span>
                /api/devices/{id}/update - Gerät aktualisieren
            </div>
            
            <h2>QR-Code-Generator:</h2>
            <div class="endpoint">
                <span class="method get">GET</span>
                <a href="/qrcode">/qrcode</a> - QR-Code-Generator-Webseite
            </div>
            <div class="endpoint">
                <span class="method get">GET</span>
                <a href="/api/qrcode?content=SwissAirDry">/api/qrcode</a> - QR-Code als Bild generieren
            </div>
            
            <footer>
                &copy; 2025 SwissAirDry - Minimal HTTP Server v1.0.0
            </footer>
        </body>
        </html>
        """
        self._send_html_response(html)
    
    def _handle_qrcode_generator(self, query_params):
        """
        Behandelt den QR-Code-Generator-Webendpunkt.
        
        Args:
            query_params: URL-Abfrageparameter
        """
        if not has_qrcode:
            self._send_html_response(
                "<h1>Fehler</h1><p>QR-Code-Funktionalität nicht verfügbar. "
                "Bitte installieren Sie das Paket 'qrcode'.</p>", 
                500
            )
            return
        
        # HTML-Seite mit QR-Code-Generator
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>SwissAirDry QR-Code-Generator</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {
                    font-family: Arial, sans-serif;
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
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                }
                h1 {
                    color: #333;
                    text-align: center;
                    margin-bottom: 30px;
                }
                form {
                    margin-bottom: 30px;
                }
                label {
                    display: block;
                    margin-bottom: 8px;
                    font-weight: bold;
                }
                input, textarea, select {
                    width: 100%;
                    padding: 10px;
                    margin-bottom: 20px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    box-sizing: border-box;
                }
                textarea {
                    height: 100px;
                    resize: vertical;
                }
                button {
                    background-color: #0066cc;
                    color: white;
                    border: none;
                    padding: 12px 20px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 16px;
                    display: block;
                    width: 100%;
                }
                button:hover {
                    background-color: #0052a3;
                }
                .qrcode-container {
                    text-align: center;
                    margin-top: 30px;
                    padding: 20px;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    background-color: #f9f9f9;
                }
                .qrcode-image {
                    max-width: 100%;
                    margin-bottom: 15px;
                }
                .template-container {
                    margin-top: 20px;
                    padding: 15px;
                    background-color: #f0f8ff;
                    border-radius: 4px;
                }
                .template-heading {
                    margin-top: 0;
                    font-size: 18px;
                    color: #0066cc;
                }
                .template-button {
                    background-color: #4CAF50;
                    margin-bottom: 10px;
                }
                footer {
                    margin-top: 50px;
                    text-align: center;
                    color: #666;
                    font-size: 14px;
                }
                .download-button {
                    background-color: #28a745;
                    margin-top: 15px;
                }
                .hidden {
                    display: none;
                }
                .tab-container {
                    margin-bottom: 20px;
                }
                .tab {
                    display: inline-block;
                    padding: 10px 20px;
                    background-color: #eee;
                    cursor: pointer;
                    border-radius: 4px 4px 0 0;
                    border: 1px solid #ddd;
                    margin-right: 5px;
                }
                .tab.active {
                    background-color: white;
                    border-bottom: 1px solid white;
                }
                .tab-content {
                    border: 1px solid #ddd;
                    padding: 20px;
                    border-radius: 0 4px 4px 4px;
                    background-color: white;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>SwissAirDry QR-Code-Generator</h1>
                
                <div class="tab-container">
                    <div class="tab active" onclick="switchTab('custom')">Benutzerdefiniert</div>
                    <div class="tab" onclick="switchTab('wifi')">WLAN-Konfiguration</div>
                    <div class="tab" onclick="switchTab('device')">Gerät-Setup</div>
                </div>
                
                <div id="custom-tab" class="tab-content">
                    <form id="qrform" onsubmit="generateQRCode(); return false;">
                        <label for="content">QR-Code-Inhalt:</label>
                        <textarea id="content" name="content" placeholder="Hier den Text eingeben, der im QR-Code codiert werden soll..." required></textarea>
                        
                        <label for="size">Größe (px):</label>
                        <input type="number" id="size" name="size" value="200" min="50" max="500">
                        
                        <label for="title">Titel:</label>
                        <input type="text" id="title" name="title" value="SwissAirDry QR-Code" placeholder="Titel des QR-Codes">
                        
                        <button type="submit">QR-Code generieren</button>
                    </form>
                </div>
                
                <div id="wifi-tab" class="tab-content hidden">
                    <form id="wifiform" onsubmit="generateWifiQR(); return false;">
                        <label for="ssid">WLAN-Name (SSID):</label>
                        <input type="text" id="ssid" name="ssid" placeholder="Name des WLAN-Netzwerks" required>
                        
                        <label for="password">WLAN-Passwort:</label>
                        <input type="password" id="password" name="password" placeholder="WLAN-Passwort">
                        
                        <label for="encryption">Verschlüsselungstyp:</label>
                        <select id="encryption" name="encryption">
                            <option value="WPA">WPA/WPA2/WPA3</option>
                            <option value="WEP">WEP</option>
                            <option value="nopass">Kein Passwort</option>
                        </select>
                        
                        <label for="hidden">Verstecktes Netzwerk:</label>
                        <select id="hidden" name="hidden">
                            <option value="false">Nein</option>
                            <option value="true">Ja</option>
                        </select>
                        
                        <button type="submit" class="template-button">WLAN-QR-Code generieren</button>
                    </form>
                </div>
                
                <div id="device-tab" class="tab-content hidden">
                    <form id="deviceform" onsubmit="generateDeviceQR(); return false;">
                        <label for="device_id">Geräte-ID:</label>
                        <input type="text" id="device_id" name="device_id" placeholder="ID des Geräts" required>
                        
                        <label for="mqtt_server">MQTT-Server:</label>
                        <input type="text" id="mqtt_server" name="mqtt_server" placeholder="mqtt.beispiel.com" required>
                        
                        <label for="mqtt_port">MQTT-Port:</label>
                        <input type="number" id="mqtt_port" name="mqtt_port" value="1883" required>
                        
                        <label for="mqtt_user">MQTT-Benutzername (optional):</label>
                        <input type="text" id="mqtt_user" name="mqtt_user" placeholder="Benutzername">
                        
                        <label for="mqtt_password">MQTT-Passwort (optional):</label>
                        <input type="password" id="mqtt_password" name="mqtt_password" placeholder="Passwort">
                        
                        <button type="submit" class="template-button">Geräte-Setup-QR-Code generieren</button>
                    </form>
                </div>
                
                <div id="qrcode-result" class="qrcode-container hidden">
                    <h2 id="result-title">Generierter QR-Code</h2>
                    <img id="qrcode-img" class="qrcode-image" src="" alt="QR-Code">
                    <p id="qrcode-content"></p>
                    <button onclick="downloadQRCode()" class="download-button">QR-Code herunterladen</button>
                </div>
                
                <footer>
                    &copy; 2025 SwissAirDry - QR-Code-Generator v1.0.0
                </footer>
            </div>
            
            <script>
                function switchTab(tabName) {
                    // Alle Tabs ausblenden
                    document.querySelectorAll('.tab-content').forEach(tab => {
                        tab.classList.add('hidden');
                    });
                    
                    // Alle Tab-Buttons deaktivieren
                    document.querySelectorAll('.tab').forEach(tab => {
                        tab.classList.remove('active');
                    });
                    
                    // Gewählten Tab anzeigen
                    document.getElementById(tabName + '-tab').classList.remove('hidden');
                    
                    // Gewählten Tab-Button aktivieren
                    event.target.classList.add('active');
                }
                
                function generateQRCode() {
                    const content = document.getElementById('content').value;
                    const size = document.getElementById('size').value;
                    const title = document.getElementById('title').value;
                    
                    if (!content) {
                        alert('Bitte geben Sie einen Inhalt für den QR-Code ein.');
                        return;
                    }
                    
                    // QR-Code generieren
                    const url = `/api/qrcode?content=${encodeURIComponent(content)}&size=${size}&title=${encodeURIComponent(title)}`;
                    
                    // QR-Code anzeigen
                    document.getElementById('qrcode-img').src = url;
                    document.getElementById('result-title').textContent = title || 'Generierter QR-Code';
                    document.getElementById('qrcode-content').textContent = `Inhalt: ${content}`;
                    document.getElementById('qrcode-result').classList.remove('hidden');
                }
                
                function generateWifiQR() {
                    const ssid = document.getElementById('ssid').value;
                    const password = document.getElementById('password').value;
                    const encryption = document.getElementById('encryption').value;
                    const hidden = document.getElementById('hidden').value;
                    
                    if (!ssid) {
                        alert('Bitte geben Sie einen WLAN-Namen (SSID) ein.');
                        return;
                    }
                    
                    // WIFI-QR-Code-Format gemäß Standard
                    let wifiString = `WIFI:S:${ssid};`;
                    
                    // Passwort hinzufügen, wenn Verschlüsselung nicht "nopass" ist
                    if (encryption !== 'nopass' && password) {
                        wifiString += `P:${password};`;
                    }
                    
                    // Verschlüsselungstyp hinzufügen
                    wifiString += `T:${encryption};`;
                    
                    // Hidden-Flag hinzufügen, wenn das Netzwerk versteckt ist
                    if (hidden === 'true') {
                        wifiString += 'H:true;';
                    }
                    
                    // Abschließendes Semikolon hinzufügen
                    wifiString += ';';
                    
                    // QR-Code generieren
                    const url = `/api/qrcode?content=${encodeURIComponent(wifiString)}&title=${encodeURIComponent('WLAN-Konfiguration')}`;
                    
                    // QR-Code anzeigen
                    document.getElementById('qrcode-img').src = url;
                    document.getElementById('result-title').textContent = 'WLAN-Konfiguration';
                    document.getElementById('qrcode-content').textContent = `WLAN: ${ssid}`;
                    document.getElementById('qrcode-result').classList.remove('hidden');
                }
                
                function generateDeviceQR() {
                    const deviceId = document.getElementById('device_id').value;
                    const mqttServer = document.getElementById('mqtt_server').value;
                    const mqttPort = document.getElementById('mqtt_port').value;
                    const mqttUser = document.getElementById('mqtt_user').value;
                    const mqttPassword = document.getElementById('mqtt_password').value;
                    
                    if (!deviceId || !mqttServer) {
                        alert('Bitte geben Sie eine Geräte-ID und einen MQTT-Server an.');
                        return;
                    }
                    
                    // JSON-Objekt für die Gerätekonfiguration erstellen
                    const deviceConfig = {
                        device_id: deviceId,
                        mqtt: {
                            server: mqttServer,
                            port: parseInt(mqttPort),
                            user: mqttUser,
                            password: mqttPassword
                        },
                        created: new Date().toISOString()
                    };
                    
                    // QR-Code generieren
                    const url = `/api/qrcode?content=${encodeURIComponent(JSON.stringify(deviceConfig))}&title=${encodeURIComponent('Geräte-Setup')}`;
                    
                    // QR-Code anzeigen
                    document.getElementById('qrcode-img').src = url;
                    document.getElementById('result-title').textContent = 'Geräte-Setup';
                    document.getElementById('qrcode-content').textContent = `Gerät: ${deviceId}, MQTT: ${mqttServer}:${mqttPort}`;
                    document.getElementById('qrcode-result').classList.remove('hidden');
                }
                
                function downloadQRCode() {
                    const img = document.getElementById('qrcode-img');
                    const title = document.getElementById('result-title').textContent;
                    
                    // Erstelle einen temporären Link zum Herunterladen
                    const a = document.createElement('a');
                    a.href = img.src;
                    a.download = `${title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.png`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                }
            </script>
        </body>
        </html>
        """
        self._send_html_response(html)
    
    def _handle_qrcode_api(self, query_params):
        """
        Behandelt den QR-Code-API-Endpunkt.
        
        Args:
            query_params: URL-Abfrageparameter
        """
        if not has_qrcode:
            self._send_json_response({"error": "QR-Code-Funktionalität nicht verfügbar"}, 500)
            return
        
        # Parameter auslesen
        content = query_params.get('content', [''])[0]
        size = int(query_params.get('size', [DEFAULT_QR_SIZE])[0])
        title = query_params.get('title', [DEFAULT_QR_TITLE])[0]
        
        if not content:
            self._send_json_response({"error": "Parameter 'content' ist erforderlich"}, 400)
            return
        
        # Größenbeschränkung
        if size < 50 or size > 1000:
            self._send_json_response({"error": "Größe muss zwischen 50 und 1000 liegen"}, 400)
            return
        
        # QR-Code generieren
        qr = qrcode.QRCode(
            version=1,
            error_correction=ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(content)
        qr.make(fit=True)
        
        # QR-Code als Bild erstellen
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Wenn PIL verfügbar ist, Titel hinzufügen
        if has_pil and title:
            # Bild mit Rand erstellen
            original_size = img.pixel_size
            new_size = (original_size, original_size + 40)  # 40px Platz für den Titel
            
            # Neues Bild mit weißem Hintergrund erstellen
            combined = Image.new('RGB', new_size, color='white')
            
            # QR-Code in das neue Bild einfügen
            combined.paste(img, (0, 0))
            
            # Zeichnungsobjekt erstellen
            draw = ImageDraw.Draw(combined)
            
            # Schriftart und -größe festlegen (Standardschrift verwenden)
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except IOError:
                font = ImageFont.load_default()
            
            # Text zentriert unter den QR-Code zeichnen
            text_width = font.getbbox(title)[2] if hasattr(font, 'getbbox') else font.getlength(title)
            text_position = ((original_size - text_width) // 2, original_size + 10)
            draw.text(text_position, title, fill='black', font=font)
            
            # Bild auf die gewünschte Größe skalieren
            img = combined.resize((size, int(size * new_size[1] / new_size[0])))
        else:
            # Ohne Titel einfach auf die gewünschte Größe skalieren
            if has_pil:
                img = img.resize((size, size))
        
        # Bild in einen Puffer schreiben
        img_buffer = io.BytesIO()
        img.save(img_buffer, format="PNG")
        img_buffer.seek(0)
        
        # Bild senden
        self._send_image_response(img_buffer.read(), 'image/png')


class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    """
    Threaded HTTP Server für gleichzeitige Verbindungen.
    """
    daemon_threads = True


def run_server():
    """
    Startet den HTTP-Server.
    """
    server = ThreadedHTTPServer((HOST, PORT), SwissAirDryRequestHandler)
    
    print(f"SwissAirDry Minimal HTTP Server startet auf Port {PORT}...")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer wird beendet...")
    finally:
        server.server_close()
        print("Server gestoppt.")


if __name__ == "__main__":
    run_server()