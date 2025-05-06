#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SwissAirDry ExApp Daemon
------------------------

Dieser Daemon stellt die Verbindung zwischen der Nextcloud ExApp und dem SwissAirDry API-Server her.
Er dient als Middleware zwischen Nextcloud und der SwissAirDry API mit integrierter Deck-Unterstützung.
"""

import os
import sys
import logging
import json
import signal
import time
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from functools import wraps

import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import paho.mqtt.client as mqtt

# SwissAirDry Integration importieren - erfordert, dass die Integration verfügbar ist
# Wir importieren dynamisch, um einen Fehler zu vermeiden, wenn es nicht verfügbar ist
try:
    from swissairdry.integration.deck import DeckAPIClient, SwissAirDryDeckIntegration, DeckAPIException
    DECK_AVAILABLE = True
except ImportError:
    # Mock-Implementation für die Typüberprüfung
    class DeckAPIClient:
        pass
    
    class SwissAirDryDeckIntegration:
        def __init__(self, *args, **kwargs):
            pass

    class DeckAPIException(Exception):
        pass
    
    DECK_AVAILABLE = False

# Konfiguration aus Umgebungsvariablen
APP_ID = os.environ.get('APP_ID', 'swissairdry')
APP_VERSION = os.environ.get('APP_VERSION', '1.0.0')
APP_HOST = os.environ.get('APP_HOST', '0.0.0.0')
APP_PORT = int(os.environ.get('APP_PORT', 8081))
APP_SECRET = os.environ.get('APP_SECRET', 'change_me_in_production')
NEXTCLOUD_URL = os.environ.get('NEXTCLOUD_URL', '')
NEXTCLOUD_USER = os.environ.get('NEXTCLOUD_USER', '')
NEXTCLOUD_PASSWORD = os.environ.get('NEXTCLOUD_PASSWORD', '')
API_URL = os.environ.get('API_URL', '')
SIMPLE_API_URL = os.environ.get('SIMPLE_API_URL', '')
MQTT_BROKER = os.environ.get('MQTT_BROKER', '')
MQTT_PORT = int(os.environ.get('MQTT_PORT', 1883))
MQTT_WS_PORT = int(os.environ.get('MQTT_WS_PORT', 9001))
MQTT_USERNAME = os.environ.get('MQTT_USERNAME', '')
MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD', '')
MQTT_CLIENT_ID = f'exapp-{APP_ID}-daemon'
MQTT_TOPIC_PREFIX = os.environ.get('MQTT_TOPIC_PREFIX', 'swissairdry')

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('exapp_daemon')

# Flask-App initialisieren
app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = APP_SECRET
CORS(app)

# MQTT-Client initialisieren
mqtt_client = None

# Deck-Integration
deck_integration: Optional[SwissAirDryDeckIntegration] = None
deck_initialized = False


def async_route(route_function):
    """Decorator für asynchrone Flask-Routen"""
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # Kein Event-Loop im aktuellen Thread, erstelle einen neuen
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Führe die asynchrone Funktion aus und warte auf das Ergebnis
        result = loop.run_until_complete(route_function(*args, **kwargs))
        return result
    
    return wrapper


def setup_mqtt():
    """MQTT-Client einrichten und verbinden"""
    global mqtt_client
    try:
        mqtt_client = mqtt.Client(client_id=MQTT_CLIENT_ID)
        
        # Authentifizierung, falls konfiguriert
        if MQTT_USERNAME and MQTT_PASSWORD:
            mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        
        # Callbacks registrieren
        mqtt_client.on_connect = on_mqtt_connect
        mqtt_client.on_message = on_mqtt_message
        mqtt_client.on_disconnect = on_mqtt_disconnect
        
        # Verbindung herstellen
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_start()
        logger.info(f"MQTT-Client gestartet und verbunden mit {MQTT_BROKER}:{MQTT_PORT}")
        return True
    except Exception as e:
        logger.error(f"Fehler beim Starten des MQTT-Clients: {e}")
        return False


def setup_deck_integration():
    """Initialisiert die Deck-Integration, falls konfiguriert"""
    global deck_integration, deck_initialized
    
    if not DECK_AVAILABLE:
        logger.warning("Deck-Integration nicht verfügbar. Stelle sicher, dass swissairdry.integration.deck importiert werden kann.")
        return False
    
    if not NEXTCLOUD_URL or not NEXTCLOUD_USER or not NEXTCLOUD_PASSWORD:
        logger.warning("Nextcloud-Konfiguration unvollständig. Deck-Integration ist deaktiviert.")
        return False
    
    try:
        # Deck-Integration initialisieren
        deck_integration = SwissAirDryDeckIntegration(
            NEXTCLOUD_URL, 
            NEXTCLOUD_USER, 
            NEXTCLOUD_PASSWORD,
            board_name="SwissAirDry ExApp"
        )
        
        # Event-Loop für die asynchrone Initialisierung
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        deck_initialized = loop.run_until_complete(deck_integration.initialize())
        
        if deck_initialized:
            logger.info("Deck-Integration erfolgreich initialisiert")
        else:
            logger.error("Deck-Integration konnte nicht initialisiert werden")
        
        return deck_initialized
    except Exception as e:
        logger.error(f"Fehler bei der Initialisierung der Deck-Integration: {e}")
        return False


def on_mqtt_connect(client, userdata, flags, rc):
    """Callback bei erfolgreicher MQTT-Verbindung"""
    if rc == 0:
        logger.info("Verbunden mit MQTT-Broker")
        # Auf relevante Topics subscriben
        client.subscribe(f"{MQTT_TOPIC_PREFIX}/+/status")
        client.subscribe(f"{MQTT_TOPIC_PREFIX}/+/alarm")
        client.subscribe(f"{MQTT_TOPIC_PREFIX}/+/data")
        client.subscribe(f"{MQTT_TOPIC_PREFIX}/exapp/+")
    else:
        logger.error(f"Verbindung zum MQTT-Broker fehlgeschlagen mit Code {rc}")


def on_mqtt_message(client, userdata, msg):
    """Callback bei eingehender MQTT-Nachricht"""
    try:
        topic = msg.topic
        payload = msg.payload.decode('utf-8')
        logger.debug(f"MQTT-Nachricht empfangen: {topic} - {payload}")
        
        # Überprüfe auf Alarme für die Deck-Integration
        if DECK_AVAILABLE and deck_initialized and deck_integration and "/alarm" in topic:
            try:
                parts = topic.split('/')
                if len(parts) >= 2:
                    device_id = parts[-2]  # Der Teil vor "/alarm"
                    
                    # Parse JSON payload
                    alarm_data = json.loads(payload)
                    alarm_type = alarm_data.get('type', 'Unbekannt')
                    alarm_description = alarm_data.get('description', 'Keine Details verfügbar')
                    
                    # Erstelle Event-Loop für die asynchrone Funktion
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    # Erstelle Alarm-Karte in Deck
                    success = loop.run_until_complete(
                        deck_integration.create_alarm_card(
                            device_id=device_id,
                            alarm_type=alarm_type,
                            description=alarm_description
                        )
                    )
                    
                    if success:
                        logger.info(f"Alarm-Karte für {device_id} erstellt: {alarm_type}")
                    else:
                        logger.error(f"Fehler beim Erstellen der Alarm-Karte für {device_id}")
            except Exception as e:
                logger.error(f"Fehler bei der Verarbeitung der Alarm-Nachricht: {e}")
        
    except Exception as e:
        logger.error(f"Fehler bei der Verarbeitung der MQTT-Nachricht: {e}")


def on_mqtt_disconnect(client, userdata, rc):
    """Callback bei MQTT-Verbindungsabbruch"""
    if rc != 0:
        logger.warning(f"Unerwartete Trennung vom MQTT-Broker. Versuche erneute Verbindung...")
        try:
            client.reconnect()
        except Exception as e:
            logger.error(f"Reconnect-Fehler: {e}")


# API Routes

@app.route('/')
def index():
    """ExApp-Startseite"""
    return jsonify({
        'app': APP_ID,
        'version': APP_VERSION,
        'status': 'running',
        'api_url': API_URL,
        'simple_api_url': SIMPLE_API_URL,
        'nextcloud_url': NEXTCLOUD_URL,
        'deck_integration': {
            'available': DECK_AVAILABLE,
            'initialized': deck_initialized
        }
    })


@app.route('/status')
def status():
    """Statusprüfung für Healthchecks"""
    return jsonify({
        'status': 'ok',
        'mqtt': mqtt_client is not None,
        'deck': deck_initialized
    })


@app.route('/api/proxy', methods=['GET', 'POST', 'PUT', 'DELETE'])
def api_proxy():
    """Proxy-Endpunkt für API-Anfragen"""
    if not API_URL:
        return jsonify({'error': 'API_URL nicht konfiguriert'}), 500
    
    try:
        # Ziel-URL konstruieren
        path = request.args.get('path', '')
        url = f"{API_URL}/{path.lstrip('/')}"
        
        # Anfrage an API weiterleiten
        headers = {k: v for k, v in request.headers.items() if k.lower() not in ['host', 'content-length']}
        resp = requests.request(
            method=request.method,
            url=url,
            headers=headers,
            params=request.args,
            json=request.json if request.is_json else None,
            data=request.form if request.form else request.data,
            cookies=request.cookies,
            allow_redirects=False
        )
        
        # Antwort zurückgeben
        response_headers = {k: v for k, v in resp.headers.items() if k.lower() not in ['content-encoding', 'transfer-encoding']}
        return (resp.content, resp.status_code, response_headers)
    except Exception as e:
        logger.error(f"Proxy-Fehler: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/mqtt/publish', methods=['POST'])
def mqtt_publish():
    """Endpunkt zum Veröffentlichen von MQTT-Nachrichten"""
    global mqtt_client
    if not mqtt_client:
        return jsonify({'error': 'MQTT-Client nicht verbunden'}), 500
    
    try:
        data = request.json
        if not data or 'topic' not in data or 'payload' not in data:
            return jsonify({'error': 'Ungültige Anfrage, topic und payload erforderlich'}), 400
        
        topic = data['topic']
        payload = data['payload']
        qos = data.get('qos', 0)
        retain = data.get('retain', False)
        
        # Topic-Präfix hinzufügen, falls nicht vorhanden
        if not topic.startswith(f"{MQTT_TOPIC_PREFIX}/"):
            topic = f"{MQTT_TOPIC_PREFIX}/{topic}"
        
        # Nachricht veröffentlichen
        result = mqtt_client.publish(topic, json.dumps(payload), qos=qos, retain=retain)
        if result.rc != 0:
            return jsonify({'error': f'MQTT-Fehler {result.rc}'}), 500
        
        return jsonify({'success': True, 'topic': topic})
    except Exception as e:
        logger.error(f"MQTT-Publish-Fehler: {e}")
        return jsonify({'error': str(e)}), 500


# Deck-Integration Routes

@app.route('/deck/status')
def deck_status():
    """Status der Deck-Integration"""
    if not DECK_AVAILABLE:
        return jsonify({'error': 'Deck-Integration nicht verfügbar'}), 501
    
    if not deck_initialized or not deck_integration:
        return jsonify({'error': 'Deck-Integration nicht initialisiert'}), 503
    
    return jsonify({
        'status': 'ok',
        'initialized': deck_initialized,
        'board_id': getattr(deck_integration, 'board_id', None),
        'stacks': getattr(deck_integration, 'stacks', {})
    })


@app.route('/deck/boards')
@async_route
async def get_boards():
    """Holt alle verfügbaren Boards von Deck"""
    if not DECK_AVAILABLE:
        return jsonify({'error': 'Deck-Integration nicht verfügbar'}), 501
    
    if not deck_initialized or not deck_integration:
        return jsonify({'error': 'Deck-Integration nicht initialisiert'}), 503
    
    try:
        # Alle Boards abrufen
        boards = deck_integration.client.get_boards()
        return jsonify({
            'success': True,
            'boards': boards
        })
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Boards: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/deck/jobs', methods=['POST'])
@async_route
async def create_job_board():
    """Erstellt ein neues Job-Board in Deck"""
    if not DECK_AVAILABLE:
        return jsonify({'error': 'Deck-Integration nicht verfügbar'}), 501
    
    if not deck_initialized or not deck_integration:
        return jsonify({'error': 'Deck-Integration nicht initialisiert'}), 503
    
    try:
        data = request.json
        if not data or 'job_id' not in data or 'title' not in data:
            return jsonify({'error': 'Ungültige Anfrage, job_id und title erforderlich'}), 400
        
        job_id = data['job_id']
        title = data['title']
        description = data.get('description', '')
        status = data.get('status', 'Aktiv')
        details = data.get('details', {})
        
        # Job-Karte erstellen
        success = await deck_integration.create_job_card(job_id, title, description, status, details)
        
        if success:
            return jsonify({
                'success': True,
                'message': f"Job-Board für {job_id} erfolgreich erstellt"
            })
        else:
            return jsonify({
                'success': False,
                'message': f"Fehler beim Erstellen des Job-Boards für {job_id}"
            }), 500
            
    except Exception as e:
        logger.error(f"Fehler beim Erstellen des Job-Boards: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/deck/alarms', methods=['POST'])
@async_route
async def create_alarm():
    """Erstellt eine Alarm-Karte in Deck"""
    if not DECK_AVAILABLE:
        return jsonify({'error': 'Deck-Integration nicht verfügbar'}), 501
    
    if not deck_initialized or not deck_integration:
        return jsonify({'error': 'Deck-Integration nicht initialisiert'}), 503
    
    try:
        data = request.json
        if not data or 'device_id' not in data or 'alarm_type' not in data:
            return jsonify({'error': 'Ungültige Anfrage, device_id und alarm_type erforderlich'}), 400
        
        device_id = data['device_id']
        alarm_type = data['alarm_type']
        description = data.get('description', '')
        timestamp = datetime.now()
        
        # Alarm-Karte erstellen
        success = await deck_integration.create_alarm_card(device_id, alarm_type, description, timestamp)
        
        if success:
            return jsonify({
                'success': True,
                'message': f"Alarm-Karte für {device_id} erfolgreich erstellt"
            })
        else:
            return jsonify({
                'success': False,
                'message': f"Fehler beim Erstellen der Alarm-Karte für {device_id}"
            }), 500
            
    except Exception as e:
        logger.error(f"Fehler beim Erstellen der Alarm-Karte: {e}")
        return jsonify({'error': str(e)}), 500


def signal_handler(sig, frame):
    """Signal-Handler für sauberes Herunterfahren"""
    logger.info("Daemon wird heruntergefahren...")
    if mqtt_client:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
    sys.exit(0)


if __name__ == '__main__':
    # Signal-Handler registrieren
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # MQTT-Client starten, wenn konfiguriert
    mqtt_connected = False
    if MQTT_BROKER:
        mqtt_connected = setup_mqtt()
    else:
        logger.warning("MQTT_BROKER nicht konfiguriert, MQTT-Funktionalität deaktiviert")
    
    # Deck-Integration starten, wenn verfügbar
    if DECK_AVAILABLE:
        setup_deck_integration()
    
    # Server starten
    logger.info(f"ExApp-Daemon wird gestartet auf {APP_HOST}:{APP_PORT}")
    app.run(host=APP_HOST, port=APP_PORT, debug=False)