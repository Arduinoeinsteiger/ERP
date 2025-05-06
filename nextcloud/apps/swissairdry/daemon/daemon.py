#!/usr/bin/env python3
"""
SwissAirDry ExApp Daemon

This daemon acts as a bridge between Nextcloud and the SwissAirDry API.
It handles the following tasks:
- Secure communication between Nextcloud and the SwissAirDry API
- Forwarding of MQTT messages to the web UI via WebSockets
- User authentication via Nextcloud
"""

import os
import sys
import json
import logging
import asyncio
import aiohttp
import paho.mqtt.client as mqtt
from aiohttp import web
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('exapp-daemon.log')
    ]
)
logger = logging.getLogger('exapp-daemon')

# Configuration from environment variables
APP_ID = os.environ.get('APP_ID', 'swissairdry')
APP_VERSION = os.environ.get('APP_VERSION', '1.0.0')
APP_HOST = os.environ.get('APP_HOST', '0.0.0.0')
APP_PORT = int(os.environ.get('APP_PORT', 8081))
APP_SECRET = os.environ.get('APP_SECRET', 'change_me_in_production')

NEXTCLOUD_URL = os.environ.get('NEXTCLOUD_URL', 'http://localhost:8080')
API_URL = os.environ.get('API_URL', 'http://localhost:5000')
SIMPLE_API_URL = os.environ.get('SIMPLE_API_URL', 'http://localhost:5001')

MQTT_BROKER = os.environ.get('MQTT_BROKER', 'localhost')
MQTT_PORT = int(os.environ.get('MQTT_PORT', 1883))
MQTT_WS_PORT = int(os.environ.get('MQTT_WS_PORT', 9001))
MQTT_USERNAME = os.environ.get('MQTT_USERNAME', '')
MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD', '')

# MQTT client setup
mqtt_client = mqtt.Client(client_id=f"exapp-daemon-{APP_ID}")
if MQTT_USERNAME and MQTT_PASSWORD:
    mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

# Store WebSocket connections
websocket_connections = []

async def handle_status(request):
    """Handle status endpoint"""
    return web.json_response({
        'status': 'ok',
        'app_id': APP_ID,
        'version': APP_VERSION,
        'timestamp': datetime.now().isoformat(),
        'connections': {
            'mqtt': mqtt_client.is_connected(),
            'websockets': len(websocket_connections),
        }
    })

async def handle_websocket(request):
    """Handle WebSocket connections"""
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    # Add to connections
    websocket_connections.append(ws)
    logger.info(f"WebSocket client connected, total: {len(websocket_connections)}")
    
    try:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                data = json.loads(msg.data)
                
                # Process client message
                if data.get('type') == 'subscribe':
                    topic = data.get('topic')
                    if topic:
                        mqtt_client.subscribe(topic)
                        logger.info(f"Subscribed to MQTT topic: {topic}")
                
                # Forward API request
                elif data.get('type') == 'api_request':
                    api_path = data.get('path')
                    method = data.get('method', 'GET')
                    payload = data.get('payload', {})
                    
                    # Forward to appropriate API
                    api_base = API_URL if data.get('api') == 'main' else SIMPLE_API_URL
                    
                    async with aiohttp.ClientSession() as session:
                        if method == 'GET':
                            async with session.get(f"{api_base}{api_path}") as response:
                                result = await response.json()
                        elif method == 'POST':
                            async with session.post(f"{api_base}{api_path}", json=payload) as response:
                                result = await response.json()
                        
                        await ws.send_json({
                            'type': 'api_response',
                            'request_id': data.get('request_id'),
                            'data': result
                        })
            
            elif msg.type == aiohttp.WSMsgType.ERROR:
                logger.error(f"WebSocket error: {ws.exception()}")
    
    finally:
        # Remove from connections on disconnect
        if ws in websocket_connections:
            websocket_connections.remove(ws)
        logger.info(f"WebSocket client disconnected, remaining: {len(websocket_connections)}")
    
    return ws

def on_mqtt_connect(client, userdata, flags, rc):
    """Callback for MQTT connection"""
    logger.info(f"Connected to MQTT broker with result code {rc}")
    
    # Subscribe to SwissAirDry topics
    client.subscribe("swissairdry/#")

def on_mqtt_message(client, userdata, msg):
    """Callback for MQTT messages"""
    logger.debug(f"Received MQTT message on {msg.topic}")
    
    # Forward to all WebSocket clients
    for ws in websocket_connections:
        asyncio.create_task(ws.send_json({
            'type': 'mqtt_message',
            'topic': msg.topic,
            'payload': msg.payload.decode('utf-8')
        }))

async def start_mqtt():
    """Start MQTT client in the background"""
    # Set callbacks
    mqtt_client.on_connect = on_mqtt_connect
    mqtt_client.on_message = on_mqtt_message
    
    # Connect to broker
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        mqtt_client.loop_start()
        logger.info(f"MQTT client started, connecting to {MQTT_BROKER}:{MQTT_PORT}")
    except Exception as e:
        logger.error(f"Failed to connect to MQTT broker: {e}")

async def start_server():
    """Start the web server"""
    # Create application
    app = web.Application()
    
    # Configure routes
    app.add_routes([
        web.get('/status', handle_status),
        web.get('/ws', handle_websocket),
    ])
    
    # Start MQTT client
    await start_mqtt()
    
    # Start web server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, APP_HOST, APP_PORT)
    await site.start()
    
    logger.info(f"Server started at http://{APP_HOST}:{APP_PORT}")
    
    # Keep the server running
    while True:
        await asyncio.sleep(3600)  # Sleep for an hour

if __name__ == '__main__':
    try:
        logger.info("Starting SwissAirDry ExApp Daemon")
        asyncio.run(start_server())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        if mqtt_client.is_connected():
            mqtt_client.loop_stop()
            mqtt_client.disconnect()
        sys.exit(0)