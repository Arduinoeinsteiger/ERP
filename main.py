"""
SwissAirDry Platform - Main Application

This is the main entry point for the SwissAirDry platform, a system for monitoring
and controlling drying devices with ESP8266/ESP32 hardware.
"""
import os
import logging
import atexit
from flask import Flask, render_template, request, redirect, url_for, jsonify
# Use existing SQLAlchemy setup from the database module

from database import engine, get_db
import models
from mqtt_handler import MQTTHandler
from device_manager import DeviceManager

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

# Disconnect MQTT handler on application shutdown
def disconnect_mqtt():
    """Disconnect MQTT client on application shutdown."""
    try:
        mqtt_handler.disconnect_sync()
        logger.info("MQTT client disconnected")
    except Exception as e:
        logger.warning(f"Error disconnecting MQTT client: {e}")

atexit.register(disconnect_mqtt)

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

# API routes can be added here or in a separate Blueprint

if __name__ == "__main__":
    # Run the Flask app
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
