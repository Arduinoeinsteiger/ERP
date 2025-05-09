"""
Domain Manager for Domain Management System

This module provides functions to manage domains and DNS records.
It integrates with the DNS API provider and database models.
"""

import os
import json
import logging
import socket
import ipaddress
import requests
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session

from .models import DomainZone, DNSRecord, DomainServiceMapping, DNSProviderSettings
from .api_manager import get_dns_provider, DNSApiProvider, DNSRecord as ApiDNSRecord

# Logger configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_public_ip() -> Optional[str]:
    """
    Attempt to retrieve the public IP address of the server.
    
    Returns:
        Optional[str]: The public IP address, or None if unable to retrieve.
    """
    try:
        # Use a reliable service to get the public IP
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        data = response.json()
        return data.get('ip')
    except Exception as e:
        logger.error(f"Error retrieving public IP: {str(e)}")
        
        # Fallback: try another service
        try:
            response = requests.get('https://ifconfig.me/ip', timeout=5)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error retrieving public IP (fallback): {str(e)}")
            
            # Last resort: try to get the local IP (which might not be public)
            try:
                hostname = socket.gethostname()
                return socket.gethostbyname(hostname)
            except Exception as e:
                logger.error(f"Error retrieving local IP: {str(e)}")
                return None

def get_available_services() -> List[Dict[str, Any]]:
    """
    Get a list of available services that can be mapped to domains.
    
    Returns:
        List[Dict[str, Any]]: List of service information.
    """
    # Define the services available in the platform
    # Can be customized based on your application
    return [
        {
            "name": "api",
            "description": "API Server",
            "port": 8000,
            "required": True,
            "path": "/api",
            "default_subdomain": "api"
        },
        {
            "name": "web",
            "description": "Web Interface",
            "port": 5000,
            "required": True,
            "path": "/",
            "default_subdomain": "www"
        },
        {
            "name": "admin",
            "description": "Admin Panel",
            "port": 5001,
            "required": False,
            "path": "/admin",
            "default_subdomain": "admin"
        }
    ]

def get_zone_from_domain(domain: str, db: Session) -> Optional[DomainZone]:
    """
    Retrieve a zone from the database by domain name.
    
    Args:
        domain: The domain name to look up.
        db: Database session.
        
    Returns:
        Optional[DomainZone]: The domain zone if found, otherwise None.
    """
    return db.query(DomainZone).filter(DomainZone.name == domain).first()

def create_domain_zone(
    zone_id: str, 
    name: str, 
    status: str, 
    nameservers: List[str], 
    provider: str,
    db: Session
) -> DomainZone:
    """
    Create a new domain zone in the database.
    
    Args:
        zone_id: Provider zone ID.
        name: Domain name.
        status: Zone status.
        nameservers: List of nameservers.
        provider: DNS provider name.
        db: Database session.
        
    Returns:
        DomainZone: The newly created domain zone.
    """
    zone = DomainZone(
        zone_id=zone_id,
        name=name,
        status=status,
        nameservers=nameservers,
        provider=provider,
        is_active=True,
        description="Automatically added via Domain Manager"
    )
    db.add(zone)
    db.commit()
    db.refresh(zone)
    return zone

def create_dns_record_db(
    zone_id: int, 
    record_id: str, 
    name: str, 
    type: str, 
    content: str, 
    ttl: int, 
    proxied: bool,
    db: Session
) -> DNSRecord:
    """
    Create a new DNS record in the database.
    
    Args:
        zone_id: Database zone ID.
        record_id: Provider record ID.
        name: DNS record name.
        type: DNS record type.
        content: DNS record content.
        ttl: TTL value.
        proxied: Whether the record is proxied.
        db: Database session.
        
    Returns:
        DNSRecord: The newly created DNS record.
    """
    record = DNSRecord(
        zone_id=zone_id,
        record_id=record_id,
        name=name,
        type=type,
        content=content,
        ttl=ttl,
        proxied=proxied
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

def create_service_mapping(
    zone_id: int,
    service_name: str,
    subdomain: Optional[str],
    dns_record_id: int,
    https_enabled: bool,
    notes: Optional[str],
    db: Session
) -> DomainServiceMapping:
    """
    Create a service to domain mapping in the database.
    
    Args:
        zone_id: Database zone ID.
        service_name: Service name.
        subdomain: Subdomain (or None for root domain).
        dns_record_id: Database DNS record ID.
        https_enabled: Whether HTTPS is enabled.
        notes: Additional notes.
        db: Database session.
        
    Returns:
        DomainServiceMapping: The newly created service mapping.
    """
    mapping = DomainServiceMapping(
        zone_id=zone_id,
        service_name=service_name,
        subdomain=subdomain,
        dns_record_id=dns_record_id,
        is_active=True,
        https_enabled=https_enabled,
        notes=notes
    )
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    return mapping

def get_dns_provider_from_db(db: Session, provider: str = "cloudflare") -> DNSApiProvider:
    """
    Get a DNS provider instance using credentials from the database.
    
    Args:
        db: Database session.
        provider: Provider name.
        
    Returns:
        DNSApiProvider: The DNS provider instance.
    """
    provider_settings = db.query(DNSProviderSettings).filter(
        DNSProviderSettings.provider == provider,
        DNSProviderSettings.is_active == True
    ).first()
    
    if provider_settings:
        # Use stored API credentials
        return get_dns_provider(provider, provider_settings.api_token)
    else:
        # Try environment variable
        return get_dns_provider(provider)

def import_domains(db: Session, provider: str = "cloudflare") -> Tuple[int, int, List[str]]:
    """
    Import domains from a DNS provider into the local database.
    
    Args:
        db: Database session.
        provider: DNS provider name.
        
    Returns:
        Tuple[int, int, List[str]]: (number of zones imported, number of records imported, list of errors)
    """
    dns_provider = get_dns_provider_from_db(db, provider)
    
    if not dns_provider.verify_token():
        return 0, 0, ["API token verification failed"]
    
    zones = dns_provider.get_zones()
    if not zones:
        return 0, 0, ["No zones found in provider account"]
    
    zone_count = 0
    record_count = 0
    errors = []
    
    for zone in zones:
        # Check if zone already exists in the database
        existing_zone = db.query(DomainZone).filter(DomainZone.zone_id == zone.zone_id).first()
        
        if existing_zone:
            # Update existing zone
            existing_zone.name = zone.name
            existing_zone.status = zone.status
            existing_zone.nameservers = zone.nameservers
            db.commit()
            db_zone = existing_zone
        else:
            # Create new zone
            try:
                db_zone = create_domain_zone(
                    zone_id=zone.zone_id,
                    name=zone.name,
                    status=zone.status,
                    nameservers=zone.nameservers,
                    provider=provider,
                    db=db
                )
                zone_count += 1
            except Exception as e:
                errors.append(f"Failed to create zone {zone.name}: {str(e)}")
                continue
        
        # Get DNS records for this zone
        dns_records = dns_provider.get_dns_records(zone.zone_id)
        
        for record in dns_records:
            # Check if record already exists in the database
            existing_record = db.query(DNSRecord).filter(
                DNSRecord.record_id == record.id
            ).first()
            
            if existing_record:
                # Update existing record
                existing_record.name = record.name
                existing_record.type = record.type
                existing_record.content = record.content
                existing_record.ttl = record.ttl
                existing_record.proxied = record.proxied
                db.commit()
            else:
                # Create new record
                try:
                    if record.id:  # Make sure record.id is not None
                        create_dns_record_db(
                            zone_id=db_zone.id,
                            record_id=record.id,
                            name=record.name,
                            type=record.type,
                            content=record.content,
                            ttl=record.ttl,
                            proxied=record.proxied,
                            db=db
                        )
                        record_count += 1
                except Exception as e:
                    errors.append(f"Failed to create DNS record {record.name}: {str(e)}")
                    continue
    
    return zone_count, record_count, errors

def setup_service_domains(
    zone_id: int, 
    domain: str, 
    ip_address: Optional[str] = None, 
    db: Session = None,
    provider: str = "cloudflare"
) -> Tuple[int, List[str]]:
    """
    Set up default service domain mappings for a domain.
    
    Args:
        zone_id: Database zone ID.
        domain: The domain name.
        ip_address: Server IP address (auto-detected if None).
        db: Database session.
        provider: DNS provider name.
        
    Returns:
        Tuple[int, List[str]]: (number of services set up, list of errors)
    """
    if not db:
        return 0, ["Database session is required"]
    
    # Get the domain zone from database
    db_zone = db.query(DomainZone).filter(DomainZone.id == zone_id).first()
    if not db_zone:
        return 0, [f"Domain zone with ID {zone_id} not found in database"]
    
    cloudflare_zone_id = db_zone.zone_id
    
    # Get or detect IP address
    if not ip_address:
        ip_address = get_public_ip()
        if not ip_address:
            return 0, ["Failed to auto-detect server IP address"]
    
    # Validate IP address format
    try:
        ipaddress.ip_address(ip_address)
    except ValueError:
        return 0, [f"Invalid IP address format: {ip_address}"]
    
    dns_provider = get_dns_provider_from_db(db, provider)
    if not dns_provider.verify_token():
        return 0, ["API token verification failed"]
    
    services = get_available_services()
    services_count = 0
    errors = []
    
    for service in services:
        service_name = service["name"]
        subdomain = service["default_subdomain"]
        
        # Configure DNS in provider
        success = dns_provider.configure_service_domain(
            cloudflare_zone_id,
            service_name,
            subdomain,
            ip_address
        )
        
        if not success:
            errors.append(f"Failed to configure {service_name} subdomain in DNS provider")
            continue
        
        # Get the created/updated DNS record
        dns_records = dns_provider.get_dns_records(cloudflare_zone_id)
        fqdn = f"{subdomain}.{domain}" if subdomain else domain
        
        dns_record = None
        for record in dns_records:
            if record.name == fqdn and record.type == "A":
                dns_record = record
                break
        
        if not dns_record or not dns_record.id:
            errors.append(f"Failed to find DNS record for {fqdn} after creation")
            continue
        
        # Ensure the record exists in the database
        db_record = db.query(DNSRecord).filter(
            DNSRecord.record_id == dns_record.id
        ).first()
        
        if not db_record:
            try:
                db_record = create_dns_record_db(
                    zone_id=db_zone.id,
                    record_id=dns_record.id,
                    name=dns_record.name,
                    type=dns_record.type,
                    content=dns_record.content,
                    ttl=dns_record.ttl,
                    proxied=dns_record.proxied,
                    db=db
                )
            except Exception as e:
                errors.append(f"Failed to create DNS record in database: {str(e)}")
                continue
        
        # Create service mapping
        try:
            create_service_mapping(
                zone_id=db_zone.id,
                service_name=service_name,
                subdomain=subdomain,
                dns_record_id=db_record.id,
                https_enabled=True,
                notes=f"Auto-configured for {service['description']}",
                db=db
            )
            services_count += 1
        except Exception as e:
            errors.append(f"Failed to create service mapping: {str(e)}")
            continue
    
    return services_count, errors

def get_domain_status(db: Session, provider: str = "cloudflare") -> Dict[str, Any]:
    """
    Get the current domain configuration status.
    
    Args:
        db: Database session.
        provider: DNS provider name.
        
    Returns:
        Dict[str, Any]: Domain status information.
    """
    zones = db.query(DomainZone).filter(DomainZone.is_active == True).all()
    
    dns_provider = get_dns_provider_from_db(db, provider)
    api_connected = dns_provider.verify_token() if dns_provider else False
    
    result = {
        "api_connected": api_connected,
        "zones_count": len(zones),
        "zones": [],
        "service_mappings": {},
        "public_ip": get_public_ip(),
        "provider": provider
    }
    
    for zone in zones:
        zone_info = {
            "id": zone.id,
            "zone_id": zone.zone_id,
            "name": zone.name,
            "status": zone.status,
            "is_primary": zone.is_primary,
            "nameservers": zone.nameservers,
            "dns_records_count": len(zone.dns_records) if zone.dns_records else 0,
            "service_mappings_count": len(zone.service_mappings) if zone.service_mappings else 0
        }
        result["zones"].append(zone_info)
        
        # Add service mappings
        for mapping in zone.service_mappings:
            if mapping.is_active:
                service_name = mapping.service_name
                if service_name not in result["service_mappings"]:
                    result["service_mappings"][service_name] = []
                
                # Get the associated DNS record
                dns_record = db.query(DNSRecord).filter(DNSRecord.id == mapping.dns_record_id).first()
                record_info = None
                if dns_record:
                    record_info = {
                        "name": dns_record.name,
                        "type": dns_record.type,
                        "content": dns_record.content,
                        "proxied": dns_record.proxied
                    }
                
                result["service_mappings"][service_name].append({
                    "zone_name": zone.name,
                    "subdomain": mapping.subdomain,
                    "full_domain": dns_record.name if dns_record else f"{mapping.subdomain}.{zone.name}" if mapping.subdomain else zone.name,
                    "https_enabled": mapping.https_enabled,
                    "dns_record": record_info
                })
    
    return result

def save_provider_settings(
    db: Session, 
    provider: str, 
    api_token: str, 
    api_key: Optional[str] = None,
    api_email: Optional[str] = None, 
    api_secret: Optional[str] = None,
    settings: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Save DNS provider settings to the database.
    
    Args:
        db: Database session.
        provider: Provider name.
        api_token: API token for the provider.
        api_key: Optional API key.
        api_email: Optional API email.
        api_secret: Optional API secret.
        settings: Optional additional settings.
        
    Returns:
        bool: Success status.
    """
    try:
        # Check if settings already exist for this provider
        provider_settings = db.query(DNSProviderSettings).filter(
            DNSProviderSettings.provider == provider
        ).first()
        
        if provider_settings:
            # Update existing settings
            provider_settings.api_token = api_token
            provider_settings.api_key = api_key
            provider_settings.api_email = api_email
            provider_settings.api_secret = api_secret
            provider_settings.is_active = True
            if settings:
                provider_settings.settings = settings
            provider_settings.updated_at = datetime.now()
        else:
            # Create new settings
            provider_settings = DNSProviderSettings(
                provider=provider,
                api_token=api_token,
                api_key=api_key,
                api_email=api_email,
                api_secret=api_secret,
                is_active=True,
                settings=settings or {}
            )
            db.add(provider_settings)
        
        db.commit()
        
        # Verify the saved settings work
        dns_provider = get_dns_provider(provider, api_token)
        if not dns_provider.verify_token():
            logger.warning(f"Saved {provider} API token does not work")
            return False
            
        return True
    except Exception as e:
        logger.error(f"Error saving provider settings: {str(e)}")
        db.rollback()
        return False