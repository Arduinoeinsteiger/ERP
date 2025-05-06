"""
API endpoints for the SwissAirDry platform.
"""
import time
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from datetime import datetime

from database import get_db
import models
from device_manager import DeviceManager
from mqtt_handler import get_mqtt_handler
from ota_manager import OTAManager

router = APIRouter()
device_manager = DeviceManager(get_mqtt_handler())
ota_manager = OTAManager(get_mqtt_handler())

# ----- Pydantic Models for request/response -----

class DeviceBase(BaseModel):
    device_id: str
    name: str
    type: str
    firmware_version: Optional[str] = None
    hardware_version: Optional[str] = None

class DeviceCreate(DeviceBase):
    pass

class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    firmware_version: Optional[str] = None
    is_online: Optional[bool] = None
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None

class DeviceResponse(DeviceBase):
    id: int
    is_online: bool
    last_seen: Optional[datetime] = None
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None

    class Config:
        orm_mode = True

class SensorReadingCreate(BaseModel):
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    pressure: Optional[float] = None
    fan_speed: Optional[int] = None
    power_consumption: Optional[float] = None

class SensorReadingResponse(SensorReadingCreate):
    id: int
    device_id: int
    timestamp: datetime

    class Config:
        orm_mode = True

class DeviceConfigBase(BaseModel):
    mqtt_topic: Optional[str] = None
    update_interval: Optional[int] = None
    display_type: Optional[str] = None
    has_sensors: Optional[bool] = None
    ota_enabled: Optional[bool] = None

class DeviceConfigCreate(DeviceConfigBase):
    pass

class DeviceConfigUpdate(DeviceConfigBase):
    pass

class DeviceConfigResponse(DeviceConfigBase):
    id: int
    device_id: int

    class Config:
        orm_mode = True

class OTAUpdateCreate(BaseModel):
    version: str
    device_type: str
    description: Optional[str] = None
    url: str
    md5_hash: str
    is_active: bool = True

class OTAUpdateResponse(OTAUpdateCreate):
    id: int
    release_date: datetime

    class Config:
        orm_mode = True

# ----- Device Endpoints -----

@router.get("/devices", response_model=List[DeviceResponse])
def get_devices(
    skip: int = 0, 
    limit: int = 100, 
    device_type: Optional[str] = None,
    is_online: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    Get all devices with optional filtering.
    """
    query = db.query(models.Device)
    
    if device_type:
        query = query.filter(models.Device.type == device_type)
    
    if is_online is not None:
        query = query.filter(models.Device.is_online == is_online)
        
    return query.offset(skip).limit(limit).all()

@router.post("/devices", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
def create_device(device: DeviceCreate, db: Session = Depends(get_db)):
    """
    Create a new device.
    """
    # Check if device with this ID already exists
    db_device = db.query(models.Device).filter(models.Device.device_id == device.device_id).first()
    if db_device:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Device with ID {device.device_id} already exists"
        )
    
    # Create new device instance
    db_device = models.Device(**device.dict(), is_online=False, last_seen=None)
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    
    # Create default config for the device
    default_config = models.DeviceConfig(
        device_id=db_device.id,
        mqtt_topic=f"swissairdry/{device.device_id}",
        update_interval=60,
        display_type="64px" if "esp8266" in device.type.lower() else "128px",
        has_sensors=True,
        ota_enabled=True
    )
    db.add(default_config)
    db.commit()
    
    return db_device

@router.get("/devices/{device_id}", response_model=DeviceResponse)
def get_device(device_id: str, db: Session = Depends(get_db)):
    """
    Get a specific device by its device_id.
    """
    db_device = db.query(models.Device).filter(models.Device.device_id == device_id).first()
    if not db_device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found"
        )
    return db_device

@router.put("/devices/{device_id}", response_model=DeviceResponse)
def update_device(device_id: str, device_update: DeviceUpdate, db: Session = Depends(get_db)):
    """
    Update a device.
    """
    db_device = db.query(models.Device).filter(models.Device.device_id == device_id).first()
    if not db_device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found"
        )
    
    # Update device with provided fields
    for key, value in device_update.dict(exclude_unset=True).items():
        setattr(db_device, key, value)
    
    # If device is reconnecting, update last_seen
    if device_update.is_online:
        db_device.last_seen = func.now()
    
    db.commit()
    db.refresh(db_device)
    return db_device

@router.delete("/devices/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_device(device_id: str, db: Session = Depends(get_db)):
    """
    Delete a device.
    """
    db_device = db.query(models.Device).filter(models.Device.device_id == device_id).first()
    if not db_device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found"
        )
    
    db.delete(db_device)
    db.commit()
    return None

# ----- Sensor Reading Endpoints -----

@router.post("/devices/{device_id}/readings", response_model=SensorReadingResponse)
def create_sensor_reading(
    device_id: str, 
    reading: SensorReadingCreate, 
    db: Session = Depends(get_db)
):
    """
    Add a new sensor reading for a device.
    """
    db_device = db.query(models.Device).filter(models.Device.device_id == device_id).first()
    if not db_device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found"
        )
    
    # Create the sensor reading
    db_reading = models.SensorReading(
        device_id=db_device.id,
        **reading.dict()
    )
    db.add(db_reading)
    
    # Update device online status and last_seen
    db_device.is_online = True
    db_device.last_seen = func.now()
    
    db.commit()
    db.refresh(db_reading)
    return db_reading

@router.get("/devices/{device_id}/readings", response_model=List[SensorReadingResponse])
def get_device_readings(
    device_id: str, 
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    Get sensor readings for a specific device.
    """
    db_device = db.query(models.Device).filter(models.Device.device_id == device_id).first()
    if not db_device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found"
        )
    
    readings = db.query(models.SensorReading).filter(
        models.SensorReading.device_id == db_device.id
    ).order_by(
        models.SensorReading.timestamp.desc()
    ).offset(skip).limit(limit).all()
    
    return readings

# ----- Device Configuration Endpoints -----

@router.get("/devices/{device_id}/config", response_model=DeviceConfigResponse)
def get_device_config(device_id: str, db: Session = Depends(get_db)):
    """
    Get configuration for a specific device.
    """
    db_device = db.query(models.Device).filter(models.Device.device_id == device_id).first()
    if not db_device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found"
        )
    
    config = db.query(models.DeviceConfig).filter(
        models.DeviceConfig.device_id == db_device.id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuration for device {device_id} not found"
        )
    
    return config

@router.put("/devices/{device_id}/config", response_model=DeviceConfigResponse)
def update_device_config(
    device_id: str, 
    config_update: DeviceConfigUpdate, 
    db: Session = Depends(get_db)
):
    """
    Update configuration for a specific device.
    """
    db_device = db.query(models.Device).filter(models.Device.device_id == device_id).first()
    if not db_device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found"
        )
    
    config = db.query(models.DeviceConfig).filter(
        models.DeviceConfig.device_id == db_device.id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuration for device {device_id} not found"
        )
    
    # Update configuration with provided fields
    for key, value in config_update.dict(exclude_unset=True).items():
        setattr(config, key, value)
    
    db.commit()
    db.refresh(config)
    
    # Publish updated config to the device via MQTT
    device_manager.publish_config(db_device, config)
    
    return config

# ----- OTA Update Endpoints -----

@router.post("/ota-updates", response_model=OTAUpdateResponse, status_code=status.HTTP_201_CREATED)
def create_ota_update(update: OTAUpdateCreate, db: Session = Depends(get_db)):
    """
    Create a new OTA update.
    """
    db_update = models.OTAUpdate(**update.dict())
    db.add(db_update)
    db.commit()
    db.refresh(db_update)
    return db_update

@router.get("/ota-updates", response_model=List[OTAUpdateResponse])
def get_ota_updates(
    skip: int = 0, 
    limit: int = 100, 
    device_type: Optional[str] = None,
    is_active: bool = True,
    db: Session = Depends(get_db)
):
    """
    Get all OTA updates with optional filtering.
    """
    query = db.query(models.OTAUpdate)
    
    if device_type:
        query = query.filter(models.OTAUpdate.device_type == device_type)
    
    if is_active is not None:
        query = query.filter(models.OTAUpdate.is_active == is_active)
        
    return query.order_by(models.OTAUpdate.release_date.desc()).offset(skip).limit(limit).all()

@router.get("/ota-updates/latest/{device_type}", response_model=OTAUpdateResponse)
def get_latest_ota_update(device_type: str, db: Session = Depends(get_db)):
    """
    Get the latest OTA update for a specific device type.
    """
    latest_update = db.query(models.OTAUpdate).filter(
        models.OTAUpdate.device_type == device_type,
        models.OTAUpdate.is_active == True
    ).order_by(models.OTAUpdate.release_date.desc()).first()
    
    if not latest_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active OTA updates found for device type {device_type}"
        )
    
    return latest_update

@router.post("/devices/{device_id}/trigger-update")
def trigger_device_update(device_id: str, db: Session = Depends(get_db)):
    """
    Trigger an OTA update for a specific device.
    """
    db_device = db.query(models.Device).filter(models.Device.device_id == device_id).first()
    if not db_device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found"
        )
    
    config = db.query(models.DeviceConfig).filter(
        models.DeviceConfig.device_id == db_device.id
    ).first()
    
    if not config or not config.ota_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OTA updates not enabled for device {device_id}"
        )
    
    # Get the latest OTA update for this device type
    latest_update = db.query(models.OTAUpdate).filter(
        models.OTAUpdate.device_type == db_device.type,
        models.OTAUpdate.is_active == True
    ).order_by(models.OTAUpdate.release_date.desc()).first()
    
    if not latest_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active OTA updates found for device type {db_device.type}"
        )
    
    # Check if device already has the latest version
    if db_device.firmware_version == latest_update.version:
        return {"message": f"Device {device_id} is already on the latest version {latest_update.version}"}
    
    # Trigger the update via OTA manager
    result = ota_manager.trigger_update(db_device, latest_update)
    
    return {"message": f"OTA update to version {latest_update.version} triggered for device {device_id}"}

# ----- Status and Control Endpoints -----

@router.post("/devices/{device_id}/control/power")
def control_device_power(device_id: str, state: bool, db: Session = Depends(get_db)):
    """
    Turn a device on or off.
    """
    db_device = db.query(models.Device).filter(models.Device.device_id == device_id).first()
    if not db_device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found"
        )
    
    # Send power control command to device
    result = device_manager.control_power(db_device, state)
    
    return {"message": f"Power {'on' if state else 'off'} command sent to device {device_id}"}

@router.post("/devices/{device_id}/control/fan")
def control_device_fan(device_id: str, speed: int, db: Session = Depends(get_db)):
    """
    Set the fan speed of a device.
    """
    if speed < 0 or speed > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fan speed must be between 0 and 100"
        )
    
    db_device = db.query(models.Device).filter(models.Device.device_id == device_id).first()
    if not db_device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found"
        )
    
    # Send fan control command to device
    result = device_manager.control_fan(db_device, speed)
    
    return {"message": f"Fan speed set to {speed}% for device {device_id}"}

@router.get("/system/status")
def get_system_status(db: Session = Depends(get_db)):
    """
    Get overall system status.
    """
    total_devices = db.query(func.count(models.Device.id)).scalar()
    online_devices = db.query(func.count(models.Device.id)).filter(models.Device.is_online == True).scalar()
    latest_readings = db.query(models.SensorReading).order_by(models.SensorReading.timestamp.desc()).limit(10).all()
    
    return {
        "total_devices": total_devices,
        "online_devices": online_devices,
        "offline_devices": total_devices - online_devices,
        "system_time": datetime.now(),
        "uptime": time.time()  # This would be replaced with actual system uptime
    }
