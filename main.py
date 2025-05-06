"""
SwissAirDry Platform - Main Application

This is the main entry point for the SwissAirDry platform, a system for monitoring
and controlling drying devices with ESP8266/ESP32 hardware via MQTT and BLE.
"""
import os
import logging
import atexit
import asyncio
import threading
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify
# Use existing SQLAlchemy setup from the database module

from database import engine, get_db
import models
from mqtt_handler import MQTTHandler
from device_manager import DeviceManager
from ble_service import get_ble_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "swissairdry-secret-key"

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize MQTT handler
mqtt_handler = MQTTHandler(
    broker=os.getenv("MQTT_BROKER", "localhost"),
    port=int(os.getenv("MQTT_PORT", 1883)),
    username=os.getenv("MQTT_USERNAME", ""),
    password=os.getenv("MQTT_PASSWORD", ""),
)

# Initialize device manager
device_manager = DeviceManager(mqtt_handler)

# Connect MQTT handler
def connect_mqtt():
    """Start MQTT client on first request."""
    try:
        mqtt_handler.connect_sync()
        logger.info("MQTT client initialized")
    except Exception as e:
        logger.warning(f"MQTT connection failed: {e}")
        logger.info("Application will run without MQTT connectivity")

# Register connect_mqtt to run on app startup
with app.app_context():
    connect_mqtt()

# Initialize BLE service asynchronously 
async def initialize_ble():
    """Starte den BLE-Service."""
    try:
        await device_manager.initialize_ble()
        logger.info("BLE-Service initialisiert")
    except Exception as e:
        logger.warning(f"Fehler bei der BLE-Initialisierung: {e}")
        logger.info("Anwendung wird ohne BLE-Unterstützung ausgeführt")

# Schedule BLE service initialization
def start_ble_service():
    """Starte den BLE-Service in einem asynchronen Context."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(initialize_ble())
    except Exception as e:
        logger.error(f"Fehler beim Starten des BLE-Service: {e}")
    finally:
        loop.close()

# Start BLE service in a separate thread to not block the main thread
ble_thread = threading.Thread(target=start_ble_service, daemon=True)
ble_thread.start()

# Shutdown handlers
def disconnect_mqtt():
    """Disconnect MQTT client on application shutdown."""
    try:
        mqtt_handler.disconnect_sync()
        logger.info("MQTT client disconnected")
    except Exception as e:
        logger.warning(f"Error disconnecting MQTT client: {e}")

async def shutdown_ble():
    """Stoppe den BLE-Service."""
    try:
        await device_manager.shutdown_ble()
        logger.info("BLE-Service gestoppt")
    except Exception as e:
        logger.warning(f"Fehler beim Stoppen des BLE-Service: {e}")

def shutdown_all():
    """Fahre alle Services herunter."""
    disconnect_mqtt()
    
    # Für BLE brauchen wir einen Event-Loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(shutdown_ble())
    except Exception as e:
        logger.error(f"Fehler beim Herunterfahren des BLE-Service: {e}")
    finally:
        loop.close()

atexit.register(shutdown_all)

# Main dashboard route
@app.route("/")
def root():
    """Render the main dashboard."""
    db = next(get_db())
    try:
        devices = db.query(models.Device).all()
        return render_template("index.html", devices=devices)
    finally:
        db.close()

# Devices management page
@app.route("/devices")
def devices_page():
    """Render the devices management page."""
    db = next(get_db())
    try:
        devices = db.query(models.Device).all()
        return render_template("devices.html", devices=devices)
    finally:
        db.close()

# System status page
@app.route("/status")
def status_page():
    """Render the system status page."""
    db = next(get_db())
    try:
        devices = db.query(models.Device).all()
        device_count = len(devices)
        online_count = sum(1 for device in devices if device.is_online)
        
        return render_template(
            "status.html", 
            device_count=device_count,
            online_count=online_count,
            offline_count=device_count - online_count
        )
    finally:
        db.close()

# Settings page
@app.route("/settings")
def settings_page():
    """Render the settings page."""
    return render_template("settings.html")

# BLE-spezifische Routen
@app.route("/api/ble/devices")
def get_ble_devices_api():
    """Liste aller BLE-Geräte abrufen."""
    db = next(get_db())
    try:
        devices = db.query(models.Device).filter(models.Device.ble_address.isnot(None)).all()
        
        # Konvertiere Geräte in JSON-Objekte
        devices_json = []
        for device in devices:
            devices_json.append({
                "id": device.id,
                "device_id": device.device_id,
                "name": device.name,
                "type": device.type,
                "firmware_version": device.firmware_version,
                "ble_address": device.ble_address,
                "ble_connected": device.ble_connected,
                "ble_rssi": device.ble_rssi,
                "is_online": device.is_online,
                "last_seen": device.last_seen.isoformat() if device.last_seen else None
            })
        
        return jsonify({"success": True, "devices": devices_json})
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der BLE-Geräte: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()

@app.route("/api/ble/device/<device_id>/power", methods=["POST"])
def control_ble_power_api(device_id):
    """Steuere den Power-Status eines Geräts über BLE."""
    data = request.json
    if not data or "state" not in data:
        return jsonify({"success": False, "error": "Parameter 'state' fehlt"}), 400
    
    state = bool(data["state"])
    
    db = next(get_db())
    try:
        device = db.query(models.Device).filter_by(device_id=device_id).first()
        if not device:
            return jsonify({"success": False, "error": f"Gerät mit ID {device_id} nicht gefunden"}), 404
        
        # Führe asynchrone Operation in eigenem Thread aus
        loop = asyncio.new_event_loop()
        result = False
        
        def execute_ble_control():
            nonlocal result
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(device_manager.control_power_ble(device, state))
            finally:
                loop.close()
        
        thread = threading.Thread(target=execute_ble_control)
        thread.start()
        thread.join(timeout=5)  # Warte maximal 5 Sekunden
        
        if result:
            return jsonify({"success": True, "message": f"Power-Befehl ({state}) erfolgreich gesendet"})
        else:
            return jsonify({"success": False, "error": "Befehl konnte nicht ausgeführt werden"}), 500
            
    except Exception as e:
        logger.error(f"Fehler bei BLE-Steuerung: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()

@app.route("/api/ble/device/<device_id>/fan", methods=["POST"])
def control_ble_fan_api(device_id):
    """Steuere die Lüftergeschwindigkeit eines Geräts über BLE."""
    data = request.json
    if not data or "speed" not in data:
        return jsonify({"success": False, "error": "Parameter 'speed' fehlt"}), 400
    
    speed = int(data["speed"])
    if speed < 0 or speed > 100:
        return jsonify({"success": False, "error": "Fan-Speed muss zwischen 0 und 100 liegen"}), 400
    
    db = next(get_db())
    try:
        device = db.query(models.Device).filter_by(device_id=device_id).first()
        if not device:
            return jsonify({"success": False, "error": f"Gerät mit ID {device_id} nicht gefunden"}), 404
        
        # Führe asynchrone Operation in eigenem Thread aus
        loop = asyncio.new_event_loop()
        result = False
        
        def execute_ble_control():
            nonlocal result
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(device_manager.control_fan_ble(device, speed))
            finally:
                loop.close()
        
        thread = threading.Thread(target=execute_ble_control)
        thread.start()
        thread.join(timeout=5)  # Warte maximal 5 Sekunden
        
        if result:
            return jsonify({"success": True, "message": f"Fan-Speed-Befehl ({speed}%) erfolgreich gesendet"})
        else:
            return jsonify({"success": False, "error": "Befehl konnte nicht ausgeführt werden"}), 500
            
    except Exception as e:
        logger.error(f"Fehler bei BLE-Steuerung: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()
        
@app.route("/api/ble/device/<device_id>/assign_task", methods=["POST"])
def assign_task_api(device_id):
    """Weise einem Gerät eine Aufgabe zu."""
    data = request.json
    if not data or "task_id" not in data:
        return jsonify({"success": False, "error": "Parameter 'task_id' fehlt"}), 400
    
    task_id = int(data["task_id"])
    start_time = None
    if "start_time" in data and data["start_time"]:
        try:
            start_time = datetime.fromisoformat(data["start_time"])
        except ValueError:
            return jsonify({"success": False, "error": "Ungültiges Datumsformat für 'start_time'"}), 400
    
    # Führe asynchrone Operation in eigenem Thread aus
    loop = asyncio.new_event_loop()
    result = False
    
    def execute_assign_task():
        nonlocal result
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(device_manager.assign_task_to_device(device_id, task_id, start_time))
        finally:
            loop.close()
    
    thread = threading.Thread(target=execute_assign_task)
    thread.start()
    thread.join(timeout=10)  # Warte maximal 10 Sekunden
    
    if result:
        return jsonify({"success": True, "message": f"Aufgabe {task_id} erfolgreich zugewiesen"})
    else:
        return jsonify({"success": False, "error": "Aufgabe konnte nicht zugewiesen werden"}), 500

# API routes can be added here or in a separate Blueprint

if __name__ == "__main__":
    # Run the Flask app
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
