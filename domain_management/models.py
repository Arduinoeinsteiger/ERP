"""
SQLAlchemy models for Domain Management System

This module provides the database models for the domain management system.
These models can be integrated with your existing SQLAlchemy setup.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

# Base class for models - can be replaced with your own Base class
Base = declarative_base()

class DomainZone(Base):
    """
    DomainZone model representing a DNS provider domain zone.
    """
    __tablename__ = "domain_zones"
    
    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(String(32), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    status = Column(String(20), nullable=False, default="active")
    nameservers = Column(JSON)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    is_active = Column(Boolean, default=True)
    is_primary = Column(Boolean, default=False)
    description = Column(Text)
    provider = Column(String(50), default="cloudflare", nullable=False)
    
    # Relationships
    dns_records = relationship("DNSRecord", back_populates="zone", cascade="all, delete")
    service_mappings = relationship("DomainServiceMapping", back_populates="zone", cascade="all, delete")
    
class DNSRecord(Base):
    """
    DNSRecord model for storing DNS records.
    """
    __tablename__ = "dns_records"
    
    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, ForeignKey("domain_zones.id", ondelete="CASCADE"))
    record_id = Column(String(32), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(String(10), nullable=False)  # A, AAAA, CNAME, TXT, etc.
    content = Column(String(255), nullable=False)
    ttl = Column(Integer, default=1)
    proxied = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    zone = relationship("DomainZone", back_populates="dns_records")
    
class DomainServiceMapping(Base):
    """
    DomainServiceMapping model linking services to domains.
    """
    __tablename__ = "domain_service_mappings"
    
    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, ForeignKey("domain_zones.id", ondelete="CASCADE"))
    service_name = Column(String(50), nullable=False)  # api, web, mqtt, etc.
    subdomain = Column(String(50))  # null for root domain
    dns_record_id = Column(Integer, ForeignKey("dns_records.id", ondelete="SET NULL"), nullable=True)
    is_active = Column(Boolean, default=True)
    https_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    notes = Column(Text)
    
    # Relationships
    zone = relationship("DomainZone", back_populates="service_mappings")
    dns_record = relationship("DNSRecord", foreign_keys=[dns_record_id])
    
class DNSProviderSettings(Base):
    """
    DNSProviderSettings model for storing provider API credentials.
    """
    __tablename__ = "dns_provider_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(50), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    api_token = Column(String(255))  # Stored encrypted or as reference to secure storage
    api_key = Column(String(255))    # Stored encrypted or as reference to secure storage
    api_email = Column(String(255))  # For some providers
    api_secret = Column(String(255)) # Stored encrypted or as reference to secure storage
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    settings = Column(JSON)  # Additional provider-specific settings

def init_db(engine):
    """
    Initialize the database by creating all tables.
    
    Args:
        engine: SQLAlchemy engine
    """
    Base.metadata.create_all(bind=engine)