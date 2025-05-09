"""
Domain Management for the SwissAirDry platform.

This module provides functions to manage domains and DNS records in the SwissAirDry platform.
It integrates with Cloudflare for DNS management and provides a web interface
for configuring domains and service mappings.
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
import models
from cloudflare_manager import get_cloudflare_manager, DNSRecord

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
    # Define the services available in the SwissAirDry platform
    return [
        {
            "name": "api",
            "description": "Main API Server",
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
            "name": "mqtt",
            "description": "MQTT Broker",
            "port": 1883,
            "required": True,
            "path": None,  # MQTT doesn't use HTTP paths
            "default_subdomain": "mqtt"
        },
        {
            "name": "mqtt-ws",
            "description": "MQTT WebSocket",
            "port": 9001,
            "required": False,
            "path": None,
            "default_subdomain": "mqtt-ws"
        },
        {
            "name": "nextcloud",
            "description": "Nextcloud Integration",
            "port": 8080,
            "required": False,
            "path": "/",
            "default_subdomain": "cloud"
        },
        {
            "name": "exapp-daemon",
            "description": "SwissAirDry ExApp Daemon",
            "port": 8081,
            "required": False,
            "path": "/",
            "default_subdomain": "exapp"
        }
    ]

def get_zone_from_domain(domain: str, db: Session) -> Optional[models.DomainZone]:
    """
    Retrieve a zone from the database by domain name.
    
    Args:
        domain: The domain name to look up.
        db: Database session.
        
    Returns:
        Optional[models.DomainZone]: The domain zone if found, otherwise None.
    """
    return db.query(models.DomainZone).filter(models.DomainZone.name == domain).first()

def create_domain_zone(zone_id: str, name: str, status: str, nameservers: List[str], db: Session) -> models.DomainZone:
    """
    Create a new domain zone in the database.
    
    Args:
        zone_id: Cloudflare zone ID.
        name: Domain name.
        status: Zone status.
        nameservers: List of nameservers.
        db: Database session.
        
    Returns:
        models.DomainZone: The newly created domain zone.
    """
    zone = models.DomainZone(
        zone_id=zone_id,
        name=name,
        status=status,
        nameservers=nameservers,
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
) -> models.DNSRecord:
    """
    Create a new DNS record in the database.
    
    Args:
        zone_id: Database zone ID.
        record_id: Cloudflare record ID.
        name: DNS record name.
        type: DNS record type.
        content: DNS record content.
        ttl: TTL value.
        proxied: Whether the record is proxied.
        db: Database session.
        
    Returns:
        models.DNSRecord: The newly created DNS record.
    """
    record = models.DNSRecord(
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
) -> models.DomainServiceMapping:
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
        models.DomainServiceMapping: The newly created service mapping.
    """
    mapping = models.DomainServiceMapping(
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

def import_cloudflare_domains(db: Session) -> Tuple[int, int, List[str]]:
    """
    Import domains from Cloudflare into the local database.
    
    Args:
        db: Database session.
        
    Returns:
        Tuple[int, int, List[str]]: (number of zones imported, number of records imported, list of errors)
    """
    cf_manager = get_cloudflare_manager()
    
    if not cf_manager.verify_token():
        return 0, 0, ["Cloudflare API token verification failed"]
    
    zones = cf_manager.get_zones()
    if not zones:
        return 0, 0, ["No zones found in Cloudflare account"]
    
    zone_count = 0
    record_count = 0
    errors = []
    
    for zone in zones:
        # Check if zone already exists in the database
        existing_zone = db.query(models.DomainZone).filter(models.DomainZone.zone_id == zone.zone_id).first()
        
        if existing_zone:
            # Update existing zone
            existing_zone.name = zone.name
            existing_zone.status = zone.status
            existing_zone.nameservers = zone.nameservers
            existing_zone.updated_at = datetime.now()
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
                    db=db
                )
                zone_count += 1
            except Exception as e:
                errors.append(f"Failed to create zone {zone.name}: {str(e)}")
                continue
        
        # Get DNS records for this zone
        dns_records = cf_manager.get_dns_records(zone.zone_id)
        
        for record in dns_records:
            # Check if record already exists in the database
            existing_record = db.query(models.DNSRecord).filter(
                models.DNSRecord.record_id == record.id
            ).first()
            
            if existing_record:
                # Update existing record
                existing_record.name = record.name
                existing_record.type = record.type
                existing_record.content = record.content
                existing_record.ttl = record.ttl
                existing_record.proxied = record.proxied
                existing_record.updated_at = datetime.now()
                db.commit()
            else:
                # Create new record
                try:
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

def setup_service_domains(zone_id: int, domain: str, ip_address: Optional[str] = None, db: Session = None) -> Tuple[int, List[str]]:
    """
    Set up default service domain mappings for a domain.
    
    Args:
        zone_id: Database zone ID.
        domain: The domain name.
        ip_address: Server IP address (auto-detected if None).
        db: Database session.
        
    Returns:
        Tuple[int, List[str]]: (number of services set up, list of errors)
    """
    if not db:
        return 0, ["Database session is required"]
    
    # Get the domain zone from database
    db_zone = db.query(models.DomainZone).filter(models.DomainZone.id == zone_id).first()
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
    
    cf_manager = get_cloudflare_manager()
    if not cf_manager.verify_token():
        return 0, ["Cloudflare API token verification failed"]
    
    services = get_available_services()
    services_count = 0
    errors = []
    
    for service in services:
        service_name = service["name"]
        subdomain = service["default_subdomain"]
        
        # Configure DNS in Cloudflare
        success = cf_manager.configure_service_domain(
            cloudflare_zone_id,
            service_name,
            subdomain,
            ip_address
        )
        
        if not success:
            errors.append(f"Failed to configure {service_name} subdomain in Cloudflare")
            continue
        
        # Get the created/updated DNS record
        dns_records = cf_manager.get_dns_records(cloudflare_zone_id)
        fqdn = f"{subdomain}.{domain}" if subdomain else domain
        
        dns_record = None
        for record in dns_records:
            if record.name == fqdn and record.type == "A":
                dns_record = record
                break
        
        if not dns_record:
            errors.append(f"Failed to find DNS record for {fqdn} after creation")
            continue
        
        # Ensure the record exists in the database
        db_record = db.query(models.DNSRecord).filter(
            models.DNSRecord.record_id == dns_record.id
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

def get_domain_status(db: Session) -> Dict[str, Any]:
    """
    Get the current domain configuration status.
    
    Args:
        db: Database session.
        
    Returns:
        Dict[str, Any]: Domain status information.
    """
    zones = db.query(models.DomainZone).filter(models.DomainZone.is_active == True).all()
    
    cf_manager = get_cloudflare_manager()
    token_valid = cf_manager.verify_token() if cf_manager.api_token else False
    
    result = {
        "cloudflare_connected": token_valid,
        "zones_count": len(zones),
        "zones": [],
        "service_mappings": {},
        "public_ip": get_public_ip()
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
                dns_record = db.query(models.DNSRecord).filter(models.DNSRecord.id == mapping.dns_record_id).first()
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