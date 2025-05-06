"""
Device Manager for the SwissAirDry platform.

This module handles device management operations including
device discovery, control, and status updates via MQTT and BLE.
"""
import logging
import json
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta 
from sqlalchemy.orm import Session

import models
from mqtt_handler import MQTTHandler
from ble_service import get_ble_service, BLEService
from database import get_db

# Configure logging
logger = logging.getLogger(__name__)

class DeviceManager:
    """
    Manages SwissAirDry devices connected to the platform.
    """
    
    # === BLE Callback-Handler ===
    
    def _handle_ble_device_found(self, device):
        """
        Callback für neu gefundene BLE-Geräte.
        """
        logger.info(f"BLE-Gerät gefunden: {device.name} ({device.address})")
        
        # Weitere Gerätedetails werden automatisch vom BLE-Service verarbeitet
        # und in der Datenbank gespeichert
        
    def _handle_ble_device_connected(self, device, client):
        """
        Callback für verbundene BLE-Geräte.
        """
        logger.info(f"BLE-Gerät verbunden: {device.name} ({device.address})")
        
        # Aktualisiere Verbindungsstatus in der Datenbank
        db = next(get_db())
        try:
            db_device = db.query(models.Device).filter_by(ble_address=device.address).first()
            if db_device:
                db_device.ble_connected = True
                db_device.is_online = True
                db_device.last_seen = datetime.now()
                db.commit()
                logger.debug(f"BLE-Verbindungsstatus für {db_device.name} aktualisiert")
        except Exception as e:
            db.rollback()
            logger.error(f"Fehler beim Aktualisieren des BLE-Verbindungsstatus: {e}")
        finally:
            db.close()
            
    def _handle_ble_device_disconnected(self, device):
        """
        Callback für getrennte BLE-Geräte.
        """
        logger.info(f"BLE-Gerät getrennt: {device.name} ({device.address})")
        
        # Aktualisiere Verbindungsstatus in der Datenbank
        db = next(get_db())
        try:
            db_device = db.query(models.Device).filter_by(ble_address=device.address).first()
            if db_device:
                db_device.ble_connected = False
                db.commit()
                logger.debug(f"BLE-Verbindungsstatus für {db_device.name} aktualisiert")
        except Exception as e:
            db.rollback()
            logger.error(f"Fehler beim Aktualisieren des BLE-Verbindungsstatus: {e}")
        finally:
            db.close()
            
    def _handle_ble_sensor_data(self, address: str, sensor_data: Dict[str, Any]):
        """
        Callback für Sensordaten von BLE-Geräten.
        """
        logger.info(f"BLE-Sensordaten von {address}: {sensor_data}")
        
        # Die Daten werden bereits vom BLE-Service in der Datenbank gespeichert,
        # wir müssen hier nichts zusätzlich tun.
    
    def __init__(self, mqtt_handler: MQTTHandler):
        """
        Initialize DeviceManager with MQTT handler.
        """
        self.mqtt = mqtt_handler
        self.ble_service = get_ble_service()
        self.ble_initialized = False
        
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
            
        # Register BLE callbacks
        self.ble_service.register_callback("device_found", self._handle_ble_device_found)
        self.ble_service.register_callback("device_connected", self._handle_ble_device_connected)
        self.ble_service.register_callback("device_disconnected", self._handle_ble_device_disconnected)
        self.ble_service.register_callback("sensor_data", self._handle_ble_sensor_data)
        
        logger.info("DeviceManager initialized")
        
    async def initialize_ble(self):
        """
        Initialisiert den BLE-Service asynchron.
        """
        if not self.ble_initialized:
            try:
                await self.ble_service.start()
                self.ble_initialized = True
                logger.info("BLE-Service gestartet")
            except Exception as e:
                logger.error(f"Fehler beim Starten des BLE-Service: {e}")
                
    async def shutdown_ble(self):
        """
        Stoppt den BLE-Service.
        """
        if self.ble_initialized:
            try:
                await self.ble_service.stop()
                self.ble_initialized = False
                logger.info("BLE-Service gestoppt")
            except Exception as e:
                logger.error(f"Fehler beim Stoppen des BLE-Service: {e}")
    
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
            
    # === BLE Callback-Handler ===
    
    def _handle_ble_device_found(self, device):
        """
        Callback für neu gefundene BLE-Geräte.
        """
        logger.info(f"BLE-Gerät gefunden: {device.name} ({device.address})")
        
        # Weitere Gerätedetails werden automatisch vom BLE-Service verarbeitet
        # und in der Datenbank gespeichert
        
    def _handle_ble_device_connected(self, device, client):
        """
        Callback für verbundene BLE-Geräte.
        """
        logger.info(f"BLE-Gerät verbunden: {device.name} ({device.address})")
        
        # Aktualisiere Verbindungsstatus in der Datenbank
        db = next(get_db())
        try:
            db_device = db.query(models.Device).filter_by(ble_address=device.address).first()
            if db_device:
                db_device.ble_connected = True
                db_device.is_online = True
                db_device.last_seen = datetime.now()
                db.commit()
                logger.debug(f"BLE-Verbindungsstatus für {db_device.name} aktualisiert")
        except Exception as e:
            db.rollback()
            logger.error(f"Fehler beim Aktualisieren des BLE-Verbindungsstatus: {e}")
        finally:
            db.close()
            
    def _handle_ble_device_disconnected(self, device):
        """
        Callback für getrennte BLE-Geräte.
        """
        logger.info(f"BLE-Gerät getrennt: {device.name} ({device.address})")
        
        # Aktualisiere Verbindungsstatus in der Datenbank
        db = next(get_db())
        try:
            db_device = db.query(models.Device).filter_by(ble_address=device.address).first()
            if db_device:
                db_device.ble_connected = False
                db.commit()
                logger.debug(f"BLE-Verbindungsstatus für {db_device.name} aktualisiert")
        except Exception as e:
            db.rollback()
            logger.error(f"Fehler beim Aktualisieren des BLE-Verbindungsstatus: {e}")
        finally:
            db.close()
            
    def _handle_ble_sensor_data(self, address: str, sensor_data: Dict[str, Any]):
        """
        Callback für Sensordaten von BLE-Geräten.
        """
        logger.info(f"BLE-Sensordaten von {address}: {sensor_data}")
        
        # Die Daten werden bereits vom BLE-Service in der Datenbank gespeichert,
        # wir müssen hier nichts zusätzlich tun.
        
    # === BLE-spezifische Methoden ===
    
    async def control_power_ble(self, device: models.Device, state: bool) -> bool:
        """
        Steuert den Ein/Aus-Zustand eines Geräts über BLE.
        
        Args:
            device: Das zu steuernde Gerät
            state: True für Ein, False für Aus
            
        Returns:
            bool: Erfolgsstatus
        """
        if not device or not device.ble_address:
            logger.error("BLE-Steuerung nicht möglich: Kein Gerät oder BLE-Adresse")
            return False
            
        command = {
            "power": state,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            result = await self.ble_service.send_command(device.device_id, command)
            logger.info(f"BLE-Befehl an {device.name} gesendet: Power {'ON' if state else 'OFF'}")
            return result
        except Exception as e:
            logger.error(f"Fehler beim Senden des BLE-Power-Befehls: {e}")
            return False
            
    async def control_fan_ble(self, device: models.Device, speed: int) -> bool:
        """
        Steuert die Lüftergeschwindigkeit eines Geräts über BLE.
        
        Args:
            device: Das zu steuernde Gerät
            speed: Lüftergeschwindigkeit (0-100%)
            
        Returns:
            bool: Erfolgsstatus
        """
        if not device or not device.ble_address:
            logger.error("BLE-Steuerung nicht möglich: Kein Gerät oder BLE-Adresse")
            return False
            
        command = {
            "fan_speed": speed,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            result = await self.ble_service.send_command(device.device_id, command)
            logger.info(f"BLE-Befehl an {device.name} gesendet: Fan Speed {speed}%")
            return result
        except Exception as e:
            logger.error(f"Fehler beim Senden des BLE-Fan-Befehls: {e}")
            return False
            
    async def update_config_ble(self, device: models.Device, config: models.DeviceConfig) -> bool:
        """
        Aktualisiert die Konfiguration eines Geräts über BLE.
        
        Args:
            device: Das Zielgerät
            config: Die Gerätekonfiguration
            
        Returns:
            bool: Erfolgsstatus
        """
        if not device or not device.ble_address or not config:
            logger.error("BLE-Konfiguration nicht möglich: Kein Gerät, BLE-Adresse oder Konfiguration")
            return False
            
        config_data = {
            "update_interval": config.update_interval,
            "display_type": config.display_type,
            "has_sensors": config.has_sensors,
            "ota_enabled": config.ota_enabled,
            "ble_enabled": config.ble_enabled,
            "ble_advertise": config.ble_advertise,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            result = await self.ble_service.update_config(device.device_id, config_data)
            logger.info(f"BLE-Konfiguration an {device.name} gesendet")
            return result
        except Exception as e:
            logger.error(f"Fehler beim Senden der BLE-Konfiguration: {e}")
            return False
            
    async def get_ble_devices(self) -> List[models.Device]:
        """
        Gibt eine Liste aller Geräte mit BLE-Unterstützung zurück.
        
        Returns:
            List[models.Device]: Liste der BLE-Geräte
        """
        db = next(get_db())
        try:
            devices = db.query(models.Device).filter(models.Device.ble_address.isnot(None)).all()
            return devices
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der BLE-Geräte: {e}")
            return []
        finally:
            db.close()
            
    async def assign_task_to_device(self, device_id: str, task_id: int, start_time: Optional[datetime] = None) -> bool:
        """
        Weist einem Gerät eine Aufgabe zu und konfiguriert es entsprechend.
        
        Args:
            device_id: ID des Zielgeräts
            task_id: ID der zuzuweisenden Aufgabe
            start_time: Optionaler Startzeitpunkt (Standard: jetzt)
            
        Returns:
            bool: Erfolgsstatus
        """
        db = next(get_db())
        try:
            # Gerät und Aufgabe abrufen
            device = db.query(models.Device).filter_by(device_id=device_id).first()
            task = db.query(models.Task).filter_by(id=task_id).first()
            
            if not device or not task:
                logger.error(f"Gerät {device_id} oder Aufgabe {task_id} nicht gefunden")
                return False
                
            # Startzeit festlegen
            if not start_time:
                start_time = datetime.now()
                
            # Endzeit berechnen
            end_time = start_time + timedelta(minutes=task.duration_minutes)
            
            # Neue Aufgabenzuweisung erstellen
            assignment = models.TaskAssignment(
                device_id=device.id,
                task_id=task.id,
                start_time=start_time,
                end_time=end_time,
                status="scheduled",
                notes=f"Automatisch zugewiesen am {datetime.now().isoformat()}"
            )
            
            db.add(assignment)
            db.commit()
            
            # Aufgabenparameter an das Gerät senden
            task_command = {
                "action": "start_task",
                "task_id": task.id,
                "name": task.name,
                "duration": task.duration_minutes,
                "fan_speed": task.fan_speed,
                "timestamp": datetime.now().isoformat()
            }
            
            if task.target_temperature:
                task_command["target_temperature"] = task.target_temperature
                
            if task.target_humidity:
                task_command["target_humidity"] = task.target_humidity
            
            # Über BLE oder MQTT senden, je nach Verfügbarkeit
            success = False
            
            if device.ble_address and self.ble_initialized:
                try:
                    success = await self.ble_service.send_command(device.device_id, task_command)
                except Exception as e:
                    logger.error(f"Fehler beim Senden der Aufgabe über BLE: {e}")
            
            if not success:
                # Fallback auf MQTT
                topic = f"swissairdry/{device.device_id}/task"
                self.mqtt.publish_sync(topic, task_command)
                success = True
                
            logger.info(f"Aufgabe {task.name} wurde Gerät {device.name} zugewiesen")
            return success
            
        except Exception as e:
            db.rollback()
            logger.error(f"Fehler bei der Aufgabenzuweisung: {e}")
            return False
        finally:
            db.close()
