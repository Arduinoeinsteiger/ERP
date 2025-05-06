"""
MQTT Bridge for the SwissAirDry platform.

This module bridges MQTT messages to the database for long-term storage.
"""
import os
import json
import time
import logging
import threading
from typing import Optional, Dict, Any
import paho.mqtt.client as mqtt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models import Device, SensorReading, DeviceLog
from database import Base

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Database connection
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    f"postgresql://{os.getenv('PGUSER', 'postgres')}:{os.getenv('PGPASSWORD', 'postgres')}@{os.getenv('PGHOST', 'localhost')}:{os.getenv('PGPORT', '5432')}/{os.getenv('PGDATABASE', 'swissairdry')}"
)

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Create database schema if it doesn't exist
Base.metadata.create_all(engine)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class MQTTBridge:
    """
    Bridge between MQTT and the database.
    """
    def __init__(
        self, 
        broker: str = "localhost", 
        port: int = 1883, 
        username: Optional[str] = None, 
        password: Optional[str] = None,
        client_id: str = "swissairdry-bridge"
    ):
        self.broker = broker
        self.port = port
        self.username = username
        self.password = password
        self.client_id = client_id
        self.client = None
        self.connected = False
        self.topics = [
            "swissairdry/+/telemetry",  # Sensor readings
            "swissairdry/+/status",     # Device status
            "swissairdry/+/logs",       # Device logs
            "swissairdry/discovery",    # Device discovery
        ]
        
    def connect(self) -> None:
        """
        Connect to the MQTT broker.
        """
        try:
            # Initialize MQTT client
            self.client = mqtt.Client(client_id=self.client_id)
            
            # Set up callbacks
            self.client.on_connect = self._on_connect
            self.client.on_message = self._on_message
            self.client.on_disconnect = self._on_disconnect
            
            # Set credentials if provided
            if self.username and self.password:
                self.client.username_pw_set(self.username, self.password)
            
            # Connect to broker
            self.client.connect_async(self.broker, self.port)
            
            # Start the loop in a new thread
            self.client.loop_start()
            
            logger.info(f"MQTT bridge initialized with broker {self.broker}:{self.port}")
            self.connected = True
        except Exception as e:
            logger.error(f"Could not initialize MQTT connection: {e}")
            raise
            
    def disconnect(self) -> None:
        """
        Disconnect from the MQTT broker.
        """
        if self.client:
            try:
                self.client.loop_stop()
                if self.connected:
                    self.client.disconnect()
                self.connected = False
                logger.info("Disconnected from MQTT broker")
            except Exception as e:
                logger.error(f"Error disconnecting from MQTT broker: {e}")
                self.connected = False
                
    def _on_connect(self, client, userdata, flags, rc):
        """
        Callback for when the client connects to the broker.
        """
        if rc == 0:
            self.connected = True
            logger.info("MQTT connection established")
            
            # Subscribe to topics
            for topic in self.topics:
                self.client.subscribe(topic, qos=1)
                logger.info(f"Subscribed to {topic}")
        else:
            logger.error(f"Failed to connect to MQTT broker with code: {rc}")
            
    def _on_message(self, client, userdata, msg):
        """
        Callback for when a message is received from the broker.
        """
        try:
            topic = msg.topic
            payload_str = msg.payload.decode()
            logger.debug(f"Received message on {topic}: {payload_str}")
            
            # Process message based on topic
            if "telemetry" in topic:
                self._process_telemetry(topic, payload_str)
            elif "status" in topic:
                self._process_status(topic, payload_str)
            elif "logs" in topic:
                self._process_logs(topic, payload_str)
            elif "discovery" in topic:
                self._process_discovery(topic, payload_str)
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")
            
    def _on_disconnect(self, client, userdata, rc):
        """
        Callback for when the client disconnects from the broker.
        """
        self.connected = False
        if rc != 0:
            logger.error(f"MQTT disconnected with error code: {rc}")
        else:
            logger.info("MQTT disconnected")
            
    def _process_telemetry(self, topic, payload_str):
        """
        Process telemetry data and store in database.
        """
        try:
            # Parse device ID from topic
            parts = topic.split("/")
            device_id = parts[1] if len(parts) > 1 else None
            
            if not device_id:
                logger.warning(f"Invalid topic format: {topic}")
                return
            
            # Parse payload
            try:
                data = json.loads(payload_str)
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in telemetry: {payload_str}")
                return
                
            # Create database session
            db = SessionLocal()
            try:
                # Find device
                device = db.query(Device).filter(Device.device_id == device_id).first()
                if not device:
                    logger.warning(f"Device not found: {device_id}")
                    return
                    
                # Create sensor reading
                reading = SensorReading(
                    device_id=device.id,
                    temperature=data.get("temperature"),
                    humidity=data.get("humidity"),
                    pressure=data.get("pressure"),
                    fan_speed=data.get("fan_speed"),
                    power_consumption=data.get("power"),
                )
                
                db.add(reading)
                db.commit()
                logger.debug(f"Stored telemetry for device {device_id}")
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error processing telemetry: {e}")
            
    def _process_status(self, topic, payload_str):
        """
        Process device status updates and store in database.
        """
        try:
            # Parse device ID from topic
            parts = topic.split("/")
            device_id = parts[1] if len(parts) > 1 else None
            
            if not device_id:
                logger.warning(f"Invalid topic format: {topic}")
                return
            
            # Parse payload
            try:
                data = json.loads(payload_str)
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in status: {payload_str}")
                return
                
            # Create database session
            db = SessionLocal()
            try:
                # Find device
                device = db.query(Device).filter(Device.device_id == device_id).first()
                if not device:
                    logger.warning(f"Device not found: {device_id}")
                    return
                    
                # Update device status
                device.is_online = True
                device.last_seen = func.now()
                
                if "firmware_version" in data:
                    device.firmware_version = data["firmware_version"]
                    
                if "ip_address" in data:
                    device.ip_address = data["ip_address"]
                    
                db.commit()
                logger.debug(f"Updated status for device {device_id}")
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error processing status: {e}")
            
    def _process_logs(self, topic, payload_str):
        """
        Process device logs and store in database.
        """
        try:
            # Parse device ID from topic
            parts = topic.split("/")
            device_id = parts[1] if len(parts) > 1 else None
            
            if not device_id:
                logger.warning(f"Invalid topic format: {topic}")
                return
            
            # Parse payload
            try:
                data = json.loads(payload_str)
            except json.JSONDecodeError:
                # If not JSON, treat as plain text log with level=info
                data = {
                    "level": "info",
                    "message": payload_str
                }
                
            # Create database session
            db = SessionLocal()
            try:
                # Find device
                device = db.query(Device).filter(Device.device_id == device_id).first()
                if not device:
                    logger.warning(f"Device not found: {device_id}")
                    return
                    
                # Create log entry
                log = DeviceLog(
                    device_id=device.id,
                    level=data.get("level", "info"),
                    message=data.get("message", ""),
                )
                
                db.add(log)
                db.commit()
                logger.debug(f"Stored log for device {device_id}")
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error processing log: {e}")
            
    def _process_discovery(self, topic, payload_str):
        """
        Process device discovery and register new devices.
        """
        try:
            # Parse payload
            try:
                data = json.loads(payload_str)
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in discovery: {payload_str}")
                return
                
            # Check required fields
            device_id = data.get("device_id")
            if not device_id:
                logger.warning("Missing device_id in discovery payload")
                return
                
            device_type = data.get("type")
            if not device_type:
                logger.warning("Missing type in discovery payload")
                return
                
            name = data.get("name", f"SwissAirDry {device_type}-{device_id}")
                
            # Create database session
            db = SessionLocal()
            try:
                # Check if device exists
                device = db.query(Device).filter(Device.device_id == device_id).first()
                
                if device:
                    # Update existing device
                    device.is_online = True
                    device.last_seen = func.now()
                    device.firmware_version = data.get("firmware_version", device.firmware_version)
                    device.hardware_version = data.get("hardware_version", device.hardware_version)
                    device.ip_address = data.get("ip_address", device.ip_address)
                    device.mac_address = data.get("mac_address", device.mac_address)
                    
                    logger.info(f"Updated existing device: {device_id}")
                else:
                    # Create new device
                    device = Device(
                        device_id=device_id,
                        name=name,
                        type=device_type,
                        firmware_version=data.get("firmware_version"),
                        hardware_version=data.get("hardware_version"),
                        ip_address=data.get("ip_address"),
                        mac_address=data.get("mac_address"),
                        is_online=True,
                    )
                    
                    db.add(device)
                    logger.info(f"Registered new device: {device_id}")
                    
                db.commit()
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error processing discovery: {e}")

def main():
    """
    Main entry point for the MQTT bridge.
    """
    # Get MQTT connection details from environment variables
    broker = os.getenv("MQTT_BROKER", "localhost")
    port = int(os.getenv("MQTT_PORT", 1883))
    username = os.getenv("MQTT_USERNAME", "")
    password = os.getenv("MQTT_PASSWORD", "")
    
    # Create and connect the bridge
    bridge = MQTTBridge(
        broker=broker,
        port=port,
        username=username if username else None,
        password=password if password else None,
    )
    
    try:
        bridge.connect()
        
        # Keep the main thread running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    finally:
        bridge.disconnect()
        logger.info("MQTT bridge stopped")

if __name__ == "__main__":
    main()