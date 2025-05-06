"""
BLE (Bluetooth Low Energy) Service für die SwissAirDry Plattform.

Dieser Dienst ermöglicht das Scannen und Verbinden mit SwissAirDry-Geräten über BLE.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Callable, Any
import time

import bleak
from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice

from database import get_db
import models

# Logger für BLE Service
logger = logging.getLogger("ble_service")

# SwissAirDry-spezifische UUIDs
SWISSAIRDRY_SERVICE_UUID = "8cc6d3c8-0000-4af8-a0a8-d942d46aa1c5"  # Haupt-Service UUID
DEVICE_INFO_CHAR_UUID = "8cc6d3c8-0001-4af8-a0a8-d942d46aa1c5"     # Geräteinfo-Charakteristik
SENSOR_DATA_CHAR_UUID = "8cc6d3c8-0002-4af8-a0a8-d942d46aa1c5"     # Sensordaten-Charakteristik
CONTROL_CHAR_UUID = "8cc6d3c8-0003-4af8-a0a8-d942d46aa1c5"         # Steuerungs-Charakteristik
CONFIG_CHAR_UUID = "8cc6d3c8-0004-4af8-a0a8-d942d46aa1c5"          # Konfigurations-Charakteristik

class BLEService:
    """
    Bluetooth Low Energy Service für die SwissAirDry-Plattform.
    Ermöglicht die BLE-Verbindung und -Kommunikation mit Geräten.
    """
    
    def __init__(self, scan_interval: int = 60):
        """
        Initialisiert den BLE-Service.
        
        Args:
            scan_interval: Intervall in Sekunden für den Scan nach neuen Geräten
        """
        self.scan_interval = scan_interval
        self.devices: Dict[str, BLEDevice] = {}  # Gefundene BLE-Geräte
        self.connected_devices: Dict[str, BleakClient] = {}  # Verbundene Clients
        self.running = False
        self.scan_task = None
        self._callbacks: Dict[str, List[Callable]] = {
            "device_found": [],
            "device_connected": [],
            "device_disconnected": [],
            "sensor_data": [],
        }
    
    async def start(self):
        """
        Startet den BLE-Service und den regelmäßigen Scan nach Geräten.
        """
        logger.info("BLE-Service wird gestartet")
        self.running = True
        self.scan_task = asyncio.create_task(self._scan_loop())
    
    async def stop(self):
        """
        Stoppt den BLE-Service und schließt alle Verbindungen.
        """
        logger.info("BLE-Service wird gestoppt")
        self.running = False
        
        if self.scan_task:
            self.scan_task.cancel()
            try:
                await self.scan_task
            except asyncio.CancelledError:
                pass
        
        # Alle Verbindungen trennen
        for addr, client in list(self.connected_devices.items()):
            try:
                await client.disconnect()
            except Exception as e:
                logger.error(f"Fehler beim Trennen der Verbindung zu {addr}: {e}")
        self.connected_devices.clear()
    
    def register_callback(self, event_type: str, callback: Callable):
        """
        Registriert einen Callback für einen bestimmten Ereignistyp.
        
        Args:
            event_type: Typ des Ereignisses (device_found, device_connected, usw.)
            callback: Aufzurufende Funktion
        """
        if event_type in self._callbacks:
            self._callbacks[event_type].append(callback)
    
    def unregister_callback(self, event_type: str, callback: Callable):
        """
        Entfernt einen registrierten Callback.
        
        Args:
            event_type: Typ des Ereignisses
            callback: Zu entfernende Callback-Funktion
        """
        if event_type in self._callbacks and callback in self._callbacks[event_type]:
            self._callbacks[event_type].remove(callback)
    
    async def _scan_loop(self):
        """
        Scannt kontinuierlich nach BLE-Geräten im festgelegten Intervall.
        """
        while self.running:
            try:
                await self._scan_for_devices()
            except Exception as e:
                logger.error(f"Fehler beim Scannen nach BLE-Geräten: {e}")
            
            # Warte bis zum nächsten Scan
            await asyncio.sleep(self.scan_interval)
    
    async def _scan_for_devices(self):
        """
        Führt einen Scan nach SwissAirDry-BLE-Geräten durch.
        """
        logger.debug("Scanne nach BLE-Geräten...")
        
        # Scanne spezifisch nach SwissAirDry-Service UUID
        devices = await BleakScanner.discover(
            return_adv=True,
            service_uuids=[SWISSAIRDRY_SERVICE_UUID]
        )
        
        for device, adv_data in devices.values():
            if device.address not in self.devices:
                logger.info(f"Neues SwissAirDry-Gerät gefunden: {device.name} ({device.address})")
                self.devices[device.address] = device
                
                # Callback für neue Geräte aufrufen
                for callback in self._callbacks["device_found"]:
                    callback(device)
                
                # Versuche eine Verbindung herzustellen
                asyncio.create_task(self._connect_to_device(device))
            else:
                # Gerät ist bereits bekannt, aktualisiere es
                self.devices[device.address] = device
    
    async def _connect_to_device(self, device: BLEDevice):
        """
        Stellt eine Verbindung zu einem BLE-Gerät her.
        
        Args:
            device: Das zu verbindende BLE-Gerät
        """
        if device.address in self.connected_devices:
            logger.debug(f"Bereits verbunden mit {device.name} ({device.address})")
            return
        
        logger.info(f"Verbinde mit Gerät: {device.name} ({device.address})")
        
        try:
            client = BleakClient(device)
            await client.connect()
            logger.info(f"Verbunden mit {device.name} ({device.address})")
            
            # Verbindung speichern
            self.connected_devices[device.address] = client
            
            # Callback für verbundene Geräte aufrufen
            for callback in self._callbacks["device_connected"]:
                callback(device, client)
            
            # Registriere Benachrichtigungen für Sensordaten
            await self._setup_notifications(client)
            
            # Geräteinformationen abrufen und in der Datenbank speichern
            await self._register_device_in_db(client, device)
            
            # Überwache Verbindungsstatus
            client.set_disconnected_callback(
                lambda c: self._handle_disconnect(device.address)
            )
            
        except Exception as e:
            logger.error(f"Fehler beim Verbinden mit {device.name} ({device.address}): {e}")
    
    def _handle_disconnect(self, address: str):
        """
        Behandelt Verbindungsabbrüche zu BLE-Geräten.
        
        Args:
            address: MAC-Adresse des getrennte Geräts
        """
        if address in self.connected_devices:
            device = self.devices.get(address)
            logger.info(f"Verbindung zu {device.name if device else address} getrennt")
            
            # Entferne Client aus aktiven Verbindungen
            client = self.connected_devices.pop(address, None)
            
            # Callback für getrennte Geräte aufrufen
            if device:
                for callback in self._callbacks["device_disconnected"]:
                    callback(device)
            
            # Versuche nach kurzer Verzögerung erneut zu verbinden
            if device:
                asyncio.create_task(self._reconnect_with_backoff(device))
    
    async def _reconnect_with_backoff(self, device: BLEDevice, max_attempts: int = 5):
        """
        Versucht, die Verbindung zu einem Gerät mit exponentieller Verzögerung wiederherzustellen.
        
        Args:
            device: Das wiederzuverbindende Gerät
            max_attempts: Maximale Anzahl von Wiederverbindungsversuchen
        """
        for attempt in range(1, max_attempts + 1):
            # Warte mit exponentieller Verzögerung
            delay = 2 ** attempt
            logger.info(f"Wiederverbindung zu {device.name} in {delay} Sekunden (Versuch {attempt}/{max_attempts})")
            await asyncio.sleep(delay)
            
            try:
                await self._connect_to_device(device)
                logger.info(f"Erfolgreich wiederverbunden mit {device.name}")
                return
            except Exception as e:
                logger.error(f"Wiederverbindungsversuch {attempt} zu {device.name} fehlgeschlagen: {e}")
        
        logger.warning(f"Alle Wiederverbindungsversuche zu {device.name} fehlgeschlagen")
    
    async def _setup_notifications(self, client: BleakClient):
        """
        Richtet BLE-Benachrichtigungen für Sensordaten ein.
        
        Args:
            client: Der verbundene BLE-Client
        """
        try:
            await client.start_notify(
                SENSOR_DATA_CHAR_UUID, 
                lambda _, data: self._handle_sensor_data(client.address, data)
            )
            logger.debug(f"Benachrichtigungen für Sensordaten eingerichtet bei {client.address}")
        except Exception as e:
            logger.error(f"Fehler beim Einrichten von Benachrichtigungen: {e}")
    
    def _handle_sensor_data(self, address: str, data: bytearray):
        """
        Verarbeitet empfangene Sensordaten von einem Gerät.
        
        Args:
            address: MAC-Adresse des Geräts
            data: Empfangene Datenbytes
        """
        try:
            # Datenbytes in JSON dekodieren
            json_str = data.decode('utf-8')
            sensor_data = json.loads(json_str)
            
            logger.debug(f"Sensordaten empfangen von {address}: {sensor_data}")
            
            # Callback für Sensordaten aufrufen
            for callback in self._callbacks["sensor_data"]:
                callback(address, sensor_data)
            
            # Speichere Sensordaten in der Datenbank
            asyncio.create_task(self._save_sensor_reading(address, sensor_data))
            
        except Exception as e:
            logger.error(f"Fehler beim Verarbeiten von Sensordaten von {address}: {e}")
    
    async def _register_device_in_db(self, client: BleakClient, ble_device: BLEDevice):
        """
        Registriert ein neues Gerät in der Datenbank oder aktualisiert ein bestehendes.
        
        Args:
            client: Der verbundene BLE-Client
            ble_device: Das BLE-Gerät
        """
        try:
            # Geräteinformationen abrufen
            device_info_bytes = await client.read_gatt_char(DEVICE_INFO_CHAR_UUID)
            device_info = json.loads(device_info_bytes.decode('utf-8'))
            
            # Extrahiere Geräteinformationen
            device_id = device_info.get("device_id", f"ble_{ble_device.address.replace(':', '')}")
            device_name = device_info.get("name", ble_device.name or f"SwissAirDry {device_id[-6:]}")
            device_type = device_info.get("type", "unknown")
            firmware_version = device_info.get("firmware_version")
            hardware_version = device_info.get("hardware_version")
            
            # Speichere in Datenbank
            db = next(get_db())
            try:
                # Prüfe, ob Gerät bereits existiert
                device = db.query(models.Device).filter_by(device_id=device_id).first()
                
                if device:
                    # Aktualisiere bestehendes Gerät
                    device.name = device_name
                    device.firmware_version = firmware_version
                    device.hardware_version = hardware_version
                    device.is_online = True
                    device.last_seen = time.time()
                    device.ble_address = ble_device.address
                else:
                    # Erstelle neues Gerät
                    device = models.Device(
                        device_id=device_id,
                        name=device_name,
                        type=device_type,
                        firmware_version=firmware_version,
                        hardware_version=hardware_version,
                        is_online=True,
                        last_seen=time.time(),
                        ble_address=ble_device.address
                    )
                    db.add(device)
                
                # Gerätekonfiguration
                if not device.config:
                    config = models.DeviceConfig(
                        device=device,
                        display_type=device_info.get("display_type", "none"),
                        has_sensors=True,
                        ota_enabled=True,
                        ble_enabled=True
                    )
                    db.add(config)
                
                db.commit()
                logger.info(f"Gerät in Datenbank registriert/aktualisiert: {device_name} ({device_id})")
                
            except Exception as db_error:
                db.rollback()
                logger.error(f"Datenbankfehler beim Registrieren des Geräts: {db_error}")
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Fehler beim Abrufen von Geräteinformationen: {e}")
    
    async def _save_sensor_reading(self, address: str, sensor_data: Dict[str, Any]):
        """
        Speichert Sensordaten in der Datenbank.
        
        Args:
            address: MAC-Adresse des Geräts
            sensor_data: Die empfangenen Sensordaten
        """
        db = next(get_db())
        try:
            # Finde das zugehörige Gerät
            device = db.query(models.Device).filter_by(ble_address=address).first()
            
            if not device:
                logger.warning(f"Kein Gerät mit BLE-Adresse {address} in der Datenbank gefunden")
                return
            
            # Erstelle neuen Sensordatensatz
            reading = models.SensorReading(
                device_id=device.id,
                temperature=sensor_data.get("temperature"),
                humidity=sensor_data.get("humidity"),
                pressure=sensor_data.get("pressure"),
                fan_speed=sensor_data.get("fan_speed"),
                power_consumption=sensor_data.get("power_consumption")
            )
            
            db.add(reading)
            db.commit()
            logger.debug(f"Sensordaten für Gerät {device.name} gespeichert")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Fehler beim Speichern von Sensordaten: {e}")
        finally:
            db.close()
    
    async def send_command(self, device_id: str, command: Dict[str, Any]) -> bool:
        """
        Sendet einen Befehl an ein Gerät über BLE.
        
        Args:
            device_id: Die ID des Zielgeräts
            command: Der zu sendende Befehl
            
        Returns:
            bool: Erfolg der Operation
        """
        db = next(get_db())
        try:
            # Finde das Gerät in der Datenbank
            device = db.query(models.Device).filter_by(device_id=device_id).first()
            
            if not device or not device.ble_address:
                logger.warning(f"Kein Gerät mit ID {device_id} oder BLE-Adresse gefunden")
                return False
            
            # Prüfe, ob Gerät verbunden ist
            client = self.connected_devices.get(device.ble_address)
            if not client:
                logger.warning(f"Keine aktive BLE-Verbindung zu Gerät {device.name} ({device_id})")
                return False
            
            # Befehl als JSON serialisieren
            command_json = json.dumps(command)
            command_bytes = command_json.encode('utf-8')
            
            # Befehl senden
            await client.write_gatt_char(CONTROL_CHAR_UUID, command_bytes)
            logger.info(f"Befehl an Gerät {device.name} gesendet: {command}")
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Senden des Befehls an {device_id}: {e}")
            return False
        finally:
            db.close()
    
    async def update_config(self, device_id: str, config: Dict[str, Any]) -> bool:
        """
        Aktualisiert die Konfiguration eines Geräts über BLE.
        
        Args:
            device_id: Die ID des Zielgeräts
            config: Die zu aktualisierende Konfiguration
            
        Returns:
            bool: Erfolg der Operation
        """
        db = next(get_db())
        try:
            # Finde das Gerät in der Datenbank
            device = db.query(models.Device).filter_by(device_id=device_id).first()
            
            if not device or not device.ble_address:
                logger.warning(f"Kein Gerät mit ID {device_id} oder BLE-Adresse gefunden")
                return False
            
            # Prüfe, ob Gerät verbunden ist
            client = self.connected_devices.get(device.ble_address)
            if not client:
                logger.warning(f"Keine aktive BLE-Verbindung zu Gerät {device.name} ({device_id})")
                return False
            
            # Konfiguration als JSON serialisieren
            config_json = json.dumps(config)
            config_bytes = config_json.encode('utf-8')
            
            # Konfiguration senden
            await client.write_gatt_char(CONFIG_CHAR_UUID, config_bytes)
            logger.info(f"Konfiguration für Gerät {device.name} aktualisiert")
            
            # Aktualisiere auch in der Datenbank
            device_config = db.query(models.DeviceConfig).filter_by(device_id=device.id).first()
            if device_config:
                if "update_interval" in config:
                    device_config.update_interval = config["update_interval"]
                if "display_type" in config:
                    device_config.display_type = config["display_type"]
                if "ble_enabled" in config:
                    device_config.ble_enabled = config["ble_enabled"]
                
                db.commit()
            
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Fehler beim Aktualisieren der Konfiguration für {device_id}: {e}")
            return False
        finally:
            db.close()

# Singleton-Instanz des BLE-Service
_ble_service_instance = None

def get_ble_service() -> BLEService:
    """
    Gibt die Singleton-Instanz des BLE-Service zurück.
    """
    global _ble_service_instance
    if _ble_service_instance is None:
        _ble_service_instance = BLEService()
    return _ble_service_instance