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
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
# Use existing SQLAlchemy setup from the database module

from database import engine, get_db
import models
from mqtt_handler import MQTTHandler
from device_manager import DeviceManager
from ble_service import get_ble_service
from cloudflare_manager import get_cloudflare_manager
import domain_manager

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

# BLE devices page
@app.route("/ble-devices")
def ble_devices_page():
    """Render the BLE devices page."""
    db = next(get_db())
    try:
        tasks = db.query(models.Task).filter_by(is_active=True).all()
        return render_template("ble_devices.html", tasks=tasks)
    finally:
        db.close()

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

# Domain Management Routes
@app.route("/domains")
def domains_page():
    """Render the domain management page."""
    db = next(get_db())
    try:
        # Get domain status
        status = domain_manager.get_domain_status(db)
        
        # Prepare template variables
        cloudflare_connected = status.get("cloudflare_connected", False)
        zones = status.get("zones", [])
        service_mappings = status.get("service_mappings", {})
        public_ip = status.get("public_ip", "")
        
        return render_template(
            "domains.html",
            cloudflare_connected=cloudflare_connected,
            zones=zones,
            service_mappings=service_mappings,
            public_ip=public_ip
        )
    except Exception as e:
        logger.error(f"Error rendering domains page: {e}")
        flash(f"Fehler beim Laden der Domain-Verwaltung: {str(e)}", "danger")
        return redirect(url_for("root"))
    finally:
        db.close()

@app.route("/domains/connect")
def domains_connect_cloudflare():
    """Connect to Cloudflare to manage domains."""
    cf_manager = get_cloudflare_manager()
    
    # Check if token is already validated
    if cf_manager.verify_token():
        flash("Bereits mit Cloudflare verbunden.", "info")
        return redirect(url_for("domains_page"))
    
    # If no environment variable is set, we'll need to ask the user to provide it
    if not os.environ.get("CLOUDFLARE_API_TOKEN"):
        flash(
            "Bitte geben Sie Ihr Cloudflare API-Token an. "
            "Dieses können Sie in Ihrem Cloudflare-Dashboard unter 'My Profile > API Tokens' erstellen.", 
            "warning"
        )
        # Here we'd normally show a form to enter the token
        # For this example, we'll redirect to settings page
        return redirect(url_for("settings_page"))
    
    # Try to verify the token
    if cf_manager.verify_token():
        flash("Erfolgreich mit Cloudflare verbunden!", "success")
    else:
        flash("Verbindung zu Cloudflare fehlgeschlagen. Bitte prüfen Sie Ihr API-Token.", "danger")
    
    return redirect(url_for("domains_page"))

@app.route("/domains/import")
def domains_import():
    """Import domains from Cloudflare."""
    db = next(get_db())
    try:
        # Import domains from Cloudflare
        zone_count, record_count, errors = domain_manager.import_cloudflare_domains(db)
        
        if errors:
            for error in errors:
                flash(f"Fehler: {error}", "danger")
        
        if zone_count > 0 or record_count > 0:
            flash(f"{zone_count} Domains und {record_count} DNS-Einträge erfolgreich importiert.", "success")
        else:
            flash("Keine neuen Domains gefunden oder importiert.", "info")
        
        return redirect(url_for("domains_page"))
    except Exception as e:
        logger.error(f"Error importing domains: {e}")
        flash(f"Fehler beim Importieren der Domains: {str(e)}", "danger")
        return redirect(url_for("domains_page"))
    finally:
        db.close()

@app.route("/domains/view/<int:zone_id>")
def domains_view(zone_id):
    """View detailed information about a domain zone."""
    db = next(get_db())
    try:
        zone = db.query(models.DomainZone).filter_by(id=zone_id).first()
        if not zone:
            flash(f"Domain mit ID {zone_id} nicht gefunden.", "danger")
            return redirect(url_for("domains_page"))
        
        dns_records = db.query(models.DNSRecord).filter_by(zone_id=zone.id).all()
        service_mappings = db.query(models.DomainServiceMapping).filter_by(zone_id=zone.id).all()
        
        return render_template(
            "domain_details.html",
            zone=zone,
            dns_records=dns_records,
            service_mappings=service_mappings
        )
    except Exception as e:
        logger.error(f"Error viewing domain details: {e}")
        flash(f"Fehler beim Laden der Domain-Details: {str(e)}", "danger")
        return redirect(url_for("domains_page"))
    finally:
        db.close()

@app.route("/domains/dns/<int:zone_id>")
def domains_dns_records(zone_id):
    """View DNS records for a domain zone."""
    db = next(get_db())
    try:
        zone = db.query(models.DomainZone).filter_by(id=zone_id).first()
        if not zone:
            flash(f"Domain mit ID {zone_id} nicht gefunden.", "danger")
            return redirect(url_for("domains_page"))
        
        dns_records = db.query(models.DNSRecord).filter_by(zone_id=zone.id).all()
        
        return render_template(
            "domain_dns.html",
            zone=zone,
            dns_records=dns_records
        )
    except Exception as e:
        logger.error(f"Error viewing DNS records: {e}")
        flash(f"Fehler beim Laden der DNS-Einträge: {str(e)}", "danger")
        return redirect(url_for("domains_page"))
    finally:
        db.close()

@app.route("/domains/configure-services/<int:zone_id>", methods=["GET", "POST"])
def domains_configure_services(zone_id):
    """Configure services for a domain zone."""
    db = next(get_db())
    try:
        zone = db.query(models.DomainZone).filter_by(id=zone_id).first()
        if not zone:
            flash(f"Domain mit ID {zone_id} nicht gefunden.", "danger")
            return redirect(url_for("domains_page"))
        
        if request.method == "POST":
            # Get IP address from form or auto-detect
            ip_address = request.form.get("ip_address")
            if not ip_address:
                ip_address = domain_manager.get_public_ip()
                if not ip_address:
                    flash("Fehler: IP-Adresse konnte nicht automatisch erkannt werden.", "danger")
                    return redirect(request.url)
            
            # Set up service domains
            services_count, errors = domain_manager.setup_service_domains(
                zone_id=zone.id,
                domain=zone.name,
                ip_address=ip_address,
                db=db
            )
            
            if errors:
                for error in errors:
                    flash(f"Fehler: {error}", "danger")
            
            if services_count > 0:
                flash(f"{services_count} Dienste erfolgreich konfiguriert.", "success")
            else:
                flash("Keine Dienste konfiguriert.", "info")
            
            return redirect(url_for("domains_page"))
        
        # GET request: show configuration form
        available_services = domain_manager.get_available_services()
        public_ip = domain_manager.get_public_ip()
        
        return render_template(
            "domain_configure_services.html",
            zone=zone,
            available_services=available_services,
            public_ip=public_ip
        )
    except Exception as e:
        logger.error(f"Error configuring services: {e}")
        flash(f"Fehler bei der Dienst-Konfiguration: {str(e)}", "danger")
        return redirect(url_for("domains_page"))
    finally:
        db.close()

@app.route("/domains/delete/<int:zone_id>", methods=["POST"])
def domains_delete(zone_id):
    """Delete a domain zone from the database."""
    db = next(get_db())
    try:
        zone = db.query(models.DomainZone).filter_by(id=zone_id).first()
        if not zone:
            flash(f"Domain mit ID {zone_id} nicht gefunden.", "danger")
            return redirect(url_for("domains_page"))
        
        # Note: We're only removing from our database, not from Cloudflare
        db.delete(zone)
        db.commit()
        
        flash(f"Domain '{zone.name}' erfolgreich entfernt.", "success")
        return redirect(url_for("domains_page"))
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting domain: {e}")
        flash(f"Fehler beim Löschen der Domain: {str(e)}", "danger")
        return redirect(url_for("domains_page"))
    finally:
        db.close()

@app.route("/domains/delete-mapping", methods=["POST"])
def domains_delete_mapping():
    """Delete a service mapping."""
    service_name = request.args.get("service")
    zone_name = request.args.get("zone")
    
    if not service_name or not zone_name:
        flash("Fehler: Service-Name und Domain-Name sind erforderlich.", "danger")
        return redirect(url_for("domains_page"))
    
    db = next(get_db())
    try:
        zone = db.query(models.DomainZone).filter_by(name=zone_name).first()
        if not zone:
            flash(f"Domain '{zone_name}' nicht gefunden.", "danger")
            return redirect(url_for("domains_page"))
        
        mapping = db.query(models.DomainServiceMapping).filter_by(
            zone_id=zone.id,
            service_name=service_name
        ).first()
        
        if not mapping:
            flash(f"Mapping für Service '{service_name}' auf Domain '{zone_name}' nicht gefunden.", "danger")
            return redirect(url_for("domains_page"))
        
        db.delete(mapping)
        db.commit()
        
        flash(f"Mapping für Service '{service_name}' auf Domain '{zone_name}' erfolgreich entfernt.", "success")
        return redirect(url_for("domains_page"))
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting mapping: {e}")
        flash(f"Fehler beim Löschen des Mappings: {str(e)}", "danger")
        return redirect(url_for("domains_page"))
    finally:
        db.close()

@app.route("/domains/edit-mapping/<service>/<zone_name>", methods=["GET", "POST"])
def domains_edit_mapping(service, zone_name):
    """Edit a service mapping."""
    db = next(get_db())
    try:
        zone = db.query(models.DomainZone).filter_by(name=zone_name).first()
        if not zone:
            flash(f"Domain '{zone_name}' nicht gefunden.", "danger")
            return redirect(url_for("domains_page"))
        
        mapping = db.query(models.DomainServiceMapping).filter_by(
            zone_id=zone.id,
            service_name=service
        ).first()
        
        if not mapping:
            flash(f"Mapping für Service '{service}' auf Domain '{zone_name}' nicht gefunden.", "danger")
            return redirect(url_for("domains_page"))
        
        if request.method == "POST":
            # Update mapping
            subdomain = request.form.get("subdomain")
            https_enabled = request.form.get("https_enabled") == "on"
            notes = request.form.get("notes")
            
            mapping.subdomain = subdomain
            mapping.https_enabled = https_enabled
            mapping.notes = notes
            mapping.updated_at = datetime.now()
            
            db.commit()
            
            flash(f"Mapping für Service '{service}' erfolgreich aktualisiert.", "success")
            return redirect(url_for("domains_page"))
        
        # GET request: show edit form
        return render_template(
            "domain_edit_mapping.html",
            mapping=mapping,
            zone=zone,
            service=service
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error editing mapping: {e}")
        flash(f"Fehler beim Bearbeiten des Mappings: {str(e)}", "danger")
        return redirect(url_for("domains_page"))
    finally:
        db.close()

# API routes can be added here or in a separate Blueprint

if __name__ == "__main__":
    # Run the Flask app
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
