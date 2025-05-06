#!/usr/bin/env python3
"""
SwissAirDry Einfacher HTTP Server

Ein minimaler HTTP-Server für SwissAirDry ohne externe Abhängigkeiten.
"""

import os
import json
import logging
import http.server
import socketserver
from urllib.parse import urlparse
from datetime import datetime

# Konfiguration
HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
PORT = int(os.environ.get('SERVER_PORT', 5003))

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('simple_http_server')

# Einfache Beispieldaten
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
    }
}

class SimpleRequestHandler(http.server.BaseHTTPRequestHandler):
    """
    Einfacher HTTP-Request-Handler für SwissAirDry.
    """
    
    def _set_headers(self, status_code=200, content_type='application/json'):
        """
        Setzt die HTTP-Header für die Antwort.
        """
        self.send_response(status_code)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
    
    def _send_json_response(self, data, status_code=200):
        """
        Sendet eine JSON-Antwort.
        """
        self._set_headers(status_code)
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def _send_html_response(self, html, status_code=200):
        """
        Sendet eine HTML-Antwort.
        """
        self._set_headers(status_code, 'text/html; charset=utf-8')
        self.wfile.write(html.encode('utf-8'))
    
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
        
        # Einfache API-Endpunkte
        if path == '/health':
            self._send_json_response({
                "status": "ok",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0.0"
            })
        elif path == '/api/devices':
            self._send_json_response(list(devices.values()))
        elif path.startswith('/api/devices/'):
            device_id = path.split('/')[-1]
            if device_id in devices:
                self._send_json_response(devices[device_id])
            else:
                self._send_json_response({"error": "Gerät nicht gefunden"}, 404)
        else:
            # Standardseite
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>SwissAirDry Einfacher Server</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        margin: 40px;
                        line-height: 1.6;
                    }
                    h1 {
                        color: #0066cc;
                    }
                    .endpoint {
                        background-color: #f5f5f5;
                        padding: 10px;
                        margin-bottom: 10px;
                        border-left: 3px solid #0066cc;
                    }
                </style>
            </head>
            <body>
                <h1>SwissAirDry API Server</h1>
                <p>Einfacher HTTP-Server für SwissAirDry.</p>
                
                <h2>Verfügbare Endpunkte:</h2>
                <div class="endpoint">
                    <a href="/health">/health</a> - Server Status
                </div>
                <div class="endpoint">
                    <a href="/api/devices">/api/devices</a> - Liste aller Geräte
                </div>
                <div class="endpoint">
                    <a href="/api/devices/1">/api/devices/1</a> - Gerätedetails
                </div>
                
                <p>
                    <strong>SwissAirDry Projekt - Version 1.0.0</strong><br>
                    &copy; 2025 SwissAirDry
                </p>
            </body>
            </html>
            """
            self._send_html_response(html)

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    """
    Threaded HTTP Server für gleichzeitige Verbindungen.
    """
    daemon_threads = True

def run_server():
    """
    Startet den HTTP-Server.
    """
    server = ThreadedHTTPServer((HOST, PORT), SimpleRequestHandler)
    
    print(f"SwissAirDry Einfacher HTTP-Server startet auf Port {PORT}...")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer wird beendet...")
    finally:
        server.server_close()
        print("Server gestoppt.")

if __name__ == "__main__":
    run_server()