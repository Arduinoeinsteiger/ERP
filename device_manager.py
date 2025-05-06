"""
Device Manager for the SwissAirDry platform.

This module handles device management operations including
device discovery, control, and status updates.
"""
import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

import models
from mqtt_handler import MQTTHandler

# Configure logging
logger = logging.getLogger(__name__)

class DeviceManager:
    """
    Manages SwissAirDry devices connected to the platform.
    """
    
    def __init__(self, mqtt_handler: MQTTHandler):
        """
        Initialize DeviceManager with MQTT handler.
        """
        self.mqtt = mqtt_handler
        
        # Register callbacks for device topics
        self.mqtt.register_callback("swissairdry/+/status", self._handle_status_update)
        self.mqtt.register_callback("swissairdry/+/telemetry", self._handle_telemetry)
        self.mqtt.register_callback("swissairdry/+/discovery", self._handle_discovery)
        self.mqtt.register_callback("swissairdry/+/log", self._handle_device_log)
        
        # Subscribe to necessary topics - use synchronous method now
        try:
            self.mqtt.subscribe_sync("swissairdry/#")
        except Exception as e:
            logger.warning(f"Could not subscribe to MQTT topics: {e}")
            # Non-critical, the application will continue without MQTT initially
        
        logger.info("DeviceManager initialized")
    
    def control_power(self, device: models.Device, state: bool) -> bool:
        """
        Control the power state of a device.
        
        Args:
            device: The device to control
            state: True for on, False for off
            
        Returns:
            bool: Success status
        """
        if not device:
            logger.error("Cannot control power: Device is None")
            return False
        
        topic = f"swissairdry/{device.device_id}/control"
        payload = {
            "power": state,
            "timestamp": datetime.now().isoformat()
        }
        
        # Use synchronous method
        self.mqtt.publish_sync(topic, payload)
        logger.info(f"Power control command sent to {device.device_id}: {'ON' if state else 'OFF'}")
        return True
    
    def control_fan(self, device: models.Device, speed: int) -> bool:
        """
        Control the fan speed of a device.
        
        Args:
            device: The device to control
            speed: Fan speed (0-100%)
            
        Returns:
            bool: Success status
        """
        if not device:
            logger.error("Cannot control fan: Device is None")
            return False
        
        topic = f"swissairdry/{device.device_id}/control"
        payload = {
            "fan_speed": speed,
            "timestamp": datetime.now().isoformat()
        }
        
        # Use synchronous method
        self.mqtt.publish_sync(topic, payload)
        logger.info(f"Fan control command sent to {device.device_id}: {speed}%")
        return True
    
    def publish_config(self, device: models.Device, config: models.DeviceConfig) -> bool:
        """
        Publish configuration to a device.
        
        Args:
            device: The target device
            config: Device configuration
            
        Returns:
            bool: Success status
        """
        if not device or not config:
            logger.error("Cannot publish config: Device or config is None")
            return False
        
        topic = f"swissairdry/{device.device_id}/config"
        payload = {
            "update_interval": config.update_interval,
            "display_type": config.display_type,
            "has_sensors": config.has_sensors,
            "ota_enabled": config.ota_enabled,
            "timestamp": datetime.now().isoformat()
        }
        
        # Use synchronous method
        self.mqtt.publish_sync(topic, payload, retain=True)
        logger.info(f"Configuration published to {device.device_id}")
        return True
    
    def request_status(self, device: models.Device) -> bool:
        """
        Request a status update from a device.
        
        Args:
            device: The device to query
            
        Returns:
            bool: Success status
        """
        if not device:
            logger.error("Cannot request status: Device is None")
            return False
        
        topic = f"swissairdry/{device.device_id}/command"
        payload = {
            "action": "status_update",
            "timestamp": datetime.now().isoformat()
        }
        
        # Use synchronous method
        self.mqtt.publish_sync(topic, payload)
        logger.info(f"Status update requested from {device.device_id}")
        return True
    
    def _handle_status_update(self, topic: str, payload: Any) -> None:
        """
        Handle status updates from devices.
        """
        try:
            # Extract device_id from topic
            parts = topic.split('/')
            if len(parts) < 3:
                logger.error(f"Invalid topic format: {topic}")
                return
            
            device_id = parts[1]
            logger.debug(f"Status update from {device_id}: {payload}")
            
            # This would update the device status in the database
            # In a real implementation, this would use a database session
            # and update the device record
            
            # For this example, we'll just log the status
            if isinstance(payload, dict):
                if 'online' in payload:
                    logger.info(f"Device {device_id} is {'online' if payload['online'] else 'offline'}")
                if 'firmware_version' in payload:
                    logger.info(f"Device {device_id} firmware version: {payload['firmware_version']}")
        except Exception as e:
            logger.error(f"Error handling status update: {e}")
    
    def _handle_telemetry(self, topic: str, payload: Any) -> None:
        """
        Handle telemetry data from devices.
        """
        try:
            # Extract device_id from topic
            parts = topic.split('/')
            if len(parts) < 3:
                logger.error(f"Invalid topic format: {topic}")
                return
            
            device_id = parts[1]
            logger.debug(f"Telemetry from {device_id}: {payload}")
            
            # This would update the device telemetry in the database
            # In a real implementation, this would use a database session
            # and add a new sensor reading record
            
            # For this example, we'll just log the telemetry
            if isinstance(payload, dict):
                if 'temperature' in payload:
                    logger.info(f"Device {device_id} temperature: {payload['temperature']}°C")
                if 'humidity' in payload:
                    logger.info(f"Device {device_id} humidity: {payload['humidity']}%")
        except Exception as e:
            logger.error(f"Error handling telemetry: {e}")
    
    def _handle_discovery(self, topic: str, payload: Any) -> None:
        """
        Handle device discovery messages.
        """
        try:
            # Extract device_id from topic
            parts = topic.split('/')
            if len(parts) < 3:
                logger.error(f"Invalid topic format: {topic}")
                return
            
            device_id = parts[1]
            logger.info(f"Discovery message from {device_id}: {payload}")
            
            # This would register or update the device in the database
            # In a real implementation, this would use a database session
            
            # For this example, we'll just log the discovery
            if isinstance(payload, dict):
                device_type = payload.get('type', 'unknown')
                firmware = payload.get('firmware_version', 'unknown')
                logger.info(f"Device discovered: {device_id}, type: {device_type}, firmware: {firmware}")
                
                # Send a welcome message back to the device
                welcome_topic = f"swissairdry/{device_id}/welcome"
                welcome_payload = {
                    "message": "Welcome to SwissAirDry!",
                    "server_time": datetime.now().isoformat()
                }
                self.mqtt.publish_sync(welcome_topic, welcome_payload)
        except Exception as e:
            logger.error(f"Error handling discovery: {e}")
    
    def _handle_device_log(self, topic: str, payload: Any) -> None:
        """
        Handle log messages from devices.
        """
        try:
            # Extract device_id from topic
            parts = topic.split('/')
            if len(parts) < 3:
                logger.error(f"Invalid topic format: {topic}")
                return
            
            device_id = parts[1]
            
            # This would add the log to the database
            # In a real implementation, this would use a database session
            
            # For this example, we'll just log the message
            if isinstance(payload, dict):
                level = payload.get('level', 'info').upper()
                message = payload.get('message', '')
                logger.info(f"Device {device_id} [{level}]: {message}")
        except Exception as e:
            logger.error(f"Error handling device log: {e}")
