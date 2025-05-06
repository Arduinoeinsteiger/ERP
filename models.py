"""
Database models for the SwissAirDry platform.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Device(Base):
    """
    Device model representing physical SwissAirDry hardware units.
    """
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)  # esp8266, esp32c6, etc.
    firmware_version = Column(String(20))
    hardware_version = Column(String(20))
    ip_address = Column(String(15))
    mac_address = Column(String(17))
    is_online = Column(Boolean, default=False)
    last_seen = Column(DateTime)
    
    # Relationships
    readings = relationship("SensorReading", back_populates="device", cascade="all, delete")
    logs = relationship("DeviceLog", back_populates="device", cascade="all, delete")
    config = relationship("DeviceConfig", uselist=False, back_populates="device", cascade="all, delete")

class SensorReading(Base):
    """
    SensorReading model for storing device measurements.
    """
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id", ondelete="CASCADE"))
    timestamp = Column(DateTime, default=func.now(), nullable=False)
    temperature = Column(Float)
    humidity = Column(Float)
    pressure = Column(Float)
    fan_speed = Column(Integer)
    power_consumption = Column(Float)
    
    # Relationships
    device = relationship("Device", back_populates="readings")

class DeviceLog(Base):
    """
    DeviceLog model for logging device events.
    """
    __tablename__ = "device_logs"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id", ondelete="CASCADE"))
    timestamp = Column(DateTime, default=func.now(), nullable=False)
    level = Column(String(10), nullable=False)  # info, warning, error
    message = Column(Text, nullable=False)
    
    # Relationships
    device = relationship("Device", back_populates="logs")

class DeviceConfig(Base):
    """
    DeviceConfig model for storing device configuration.
    """
    __tablename__ = "device_configs"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id", ondelete="CASCADE"), unique=True)
    mqtt_topic = Column(String(100))
    update_interval = Column(Integer, default=60)  # Seconds
    display_type = Column(String(20))  # 64px, 128px, none
    has_sensors = Column(Boolean, default=True)
    ota_enabled = Column(Boolean, default=True)
    
    # Relationships
    device = relationship("Device", back_populates="config")

class OTAUpdate(Base):
    """
    OTAUpdate model for managing over-the-air firmware updates.
    """
    __tablename__ = "ota_updates"

    id = Column(Integer, primary_key=True, index=True)
    version = Column(String(20), nullable=False)
    device_type = Column(String(50), nullable=False)  # esp8266, esp32c6, etc.
    release_date = Column(DateTime, default=func.now(), nullable=False)
    description = Column(Text)
    url = Column(String(255), nullable=False)
    md5_hash = Column(String(32), nullable=False)
    is_active = Column(Boolean, default=True)
