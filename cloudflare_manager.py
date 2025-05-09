"""
Cloudflare Domain Management for SwissAirDry Platform

This module provides functionality to manage domains and DNS records
through the Cloudflare API, enabling easy domain configuration for
different SwissAirDry services.
"""

import os
import json
import logging
import requests
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass

# Logger configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DNSRecord:
    """Representation of a DNS record."""
    name: str
    type: str
    content: str
    ttl: int = 1  # Auto TTL
    proxied: bool = True
    id: Optional[str] = None
    zone_id: Optional[str] = None

@dataclass
class DomainInfo:
    """Information about a domain zone."""
    name: str
    zone_id: str
    status: str
    nameservers: List[str]
    dns_records: Optional[List[DNSRecord]] = None

class CloudflareManager:
    """
    Manages Cloudflare domains and DNS records for the SwissAirDry platform.
    """
    BASE_URL = "https://api.cloudflare.com/client/v4"
    
    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize the Cloudflare API manager.
        
        Args:
            api_token: Cloudflare API token. If None, it will be read from environment variable.
        """
        self.api_token = api_token or os.environ.get("CLOUDFLARE_API_TOKEN", "")
        if not self.api_token:
            logger.warning("No Cloudflare API token provided. Domain management is disabled.")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
    
    def verify_token(self) -> bool:
        """
        Verify that the API token is valid.
        
        Returns:
            bool: True if the token is valid, False otherwise.
        """
        if not self.api_token:
            return False
            
        try:
            response = requests.get(
                f"{self.BASE_URL}/user/tokens/verify",
                headers=self.headers
            )
            data = response.json()
            if data.get("success", False):
                logger.info("Cloudflare API token verified successfully!")
                return True
            else:
                logger.error(f"Failed to verify Cloudflare API token: {data.get('errors')}")
                return False
        except Exception as e:
            logger.error(f"Error verifying Cloudflare API token: {str(e)}")
            return False
    
    def get_zones(self) -> List[DomainInfo]:
        """
        Get all zones (domains) available with the current API token.
        
        Returns:
            List[DomainInfo]: List of domain information objects.
        """
        if not self.api_token:
            return []
            
        try:
            response = requests.get(
                f"{self.BASE_URL}/zones?per_page=50",
                headers=self.headers
            )
            data = response.json()
            
            if not data.get("success", False):
                logger.error(f"Failed to fetch zones: {data.get('errors')}")
                return []
                
            zones = []
            for zone in data.get("result", []):
                zones.append(DomainInfo(
                    name=zone.get("name"),
                    zone_id=zone.get("id"),
                    status=zone.get("status"),
                    nameservers=zone.get("name_servers", [])
                ))
                
            return zones
        except Exception as e:
            logger.error(f"Error fetching zones: {str(e)}")
            return []
    
    def get_dns_records(self, zone_id: str) -> List[DNSRecord]:
        """
        Get all DNS records for a specific zone.
        
        Args:
            zone_id: The Cloudflare zone ID.
            
        Returns:
            List[DNSRecord]: List of DNS record objects.
        """
        if not self.api_token:
            return []
            
        try:
            response = requests.get(
                f"{self.BASE_URL}/zones/{zone_id}/dns_records?per_page=100",
                headers=self.headers
            )
            data = response.json()
            
            if not data.get("success", False):
                logger.error(f"Failed to fetch DNS records: {data.get('errors')}")
                return []
                
            records = []
            for record in data.get("result", []):
                records.append(DNSRecord(
                    id=record.get("id"),
                    zone_id=zone_id,
                    name=record.get("name"),
                    type=record.get("type"),
                    content=record.get("content"),
                    ttl=record.get("ttl"),
                    proxied=record.get("proxied", True)
                ))
                
            return records
        except Exception as e:
            logger.error(f"Error fetching DNS records: {str(e)}")
            return []
    
    def create_dns_record(self, zone_id: str, record: DNSRecord) -> Optional[DNSRecord]:
        """
        Create a new DNS record in the specified zone.
        
        Args:
            zone_id: The Cloudflare zone ID.
            record: The DNS record to create.
            
        Returns:
            Optional[DNSRecord]: The created DNS record with its ID, or None if failed.
        """
        if not self.api_token:
            return None
            
        try:
            payload = {
                "type": record.type,
                "name": record.name,
                "content": record.content,
                "ttl": record.ttl,
                "proxied": record.proxied
            }
            
            response = requests.post(
                f"{self.BASE_URL}/zones/{zone_id}/dns_records",
                headers=self.headers,
                json=payload
            )
            data = response.json()
            
            if not data.get("success", False):
                logger.error(f"Failed to create DNS record: {data.get('errors')}")
                return None
                
            new_record = data.get("result", {})
            return DNSRecord(
                id=new_record.get("id"),
                zone_id=zone_id,
                name=new_record.get("name"),
                type=new_record.get("type"),
                content=new_record.get("content"),
                ttl=new_record.get("ttl"),
                proxied=new_record.get("proxied", True)
            )
        except Exception as e:
            logger.error(f"Error creating DNS record: {str(e)}")
            return None
    
    def update_dns_record(self, zone_id: str, record_id: str, record: DNSRecord) -> bool:
        """
        Update an existing DNS record.
        
        Args:
            zone_id: The Cloudflare zone ID.
            record_id: The DNS record ID.
            record: The updated DNS record data.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.api_token:
            return False
            
        try:
            payload = {
                "type": record.type,
                "name": record.name,
                "content": record.content,
                "ttl": record.ttl,
                "proxied": record.proxied
            }
            
            response = requests.put(
                f"{self.BASE_URL}/zones/{zone_id}/dns_records/{record_id}",
                headers=self.headers,
                json=payload
            )
            data = response.json()
            
            if not data.get("success", False):
                logger.error(f"Failed to update DNS record: {data.get('errors')}")
                return False
                
            return True
        except Exception as e:
            logger.error(f"Error updating DNS record: {str(e)}")
            return False
    
    def delete_dns_record(self, zone_id: str, record_id: str) -> bool:
        """
        Delete a DNS record.
        
        Args:
            zone_id: The Cloudflare zone ID.
            record_id: The DNS record ID.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.api_token:
            return False
            
        try:
            response = requests.delete(
                f"{self.BASE_URL}/zones/{zone_id}/dns_records/{record_id}",
                headers=self.headers
            )
            data = response.json()
            
            if not data.get("success", False):
                logger.error(f"Failed to delete DNS record: {data.get('errors')}")
                return False
                
            return True
        except Exception as e:
            logger.error(f"Error deleting DNS record: {str(e)}")
            return False
    
    def configure_service_domain(
        self, 
        zone_id: str, 
        service_name: str, 
        subdomain: str, 
        ip_address: str
    ) -> bool:
        """
        Configure a domain for a specific service.
        
        Args:
            zone_id: The Cloudflare zone ID.
            service_name: Name of the service (for logging).
            subdomain: The subdomain part (without the domain).
            ip_address: IP address to point to.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.api_token:
            return False
            
        # Get zone details to get the domain name
        try:
            response = requests.get(
                f"{self.BASE_URL}/zones/{zone_id}",
                headers=self.headers
            )
            data = response.json()
            
            if not data.get("success", False):
                logger.error(f"Failed to get zone details: {data.get('errors')}")
                return False
                
            domain = data.get("result", {}).get("name")
            if not domain:
                logger.error("Failed to get domain name from zone details")
                return False
                
            # Construct the full domain name (FQDN)
            fqdn = f"{subdomain}.{domain}" if subdomain else domain
            
            # Check if DNS record already exists
            records = self.get_dns_records(zone_id)
            record_exists = False
            record_id = None
            
            for record in records:
                if record.name == fqdn and record.type == "A":
                    record_exists = True
                    record_id = record.id
                    break
            
            if record_exists and record_id:
                # Update existing record
                result = self.update_dns_record(
                    zone_id, 
                    record_id,
                    DNSRecord(
                        name=fqdn,
                        type="A",
                        content=ip_address,
                        proxied=True
                    )
                )
                if result:
                    logger.info(f"Updated DNS record for {service_name} at {fqdn}")
                    return True
                else:
                    logger.error(f"Failed to update DNS record for {service_name}")
                    return False
            else:
                # Create new record
                result = self.create_dns_record(
                    zone_id,
                    DNSRecord(
                        name=fqdn,
                        type="A",
                        content=ip_address,
                        proxied=True
                    )
                )
                if result:
                    logger.info(f"Created DNS record for {service_name} at {fqdn}")
                    return True
                else:
                    logger.error(f"Failed to create DNS record for {service_name}")
                    return False
        except Exception as e:
            logger.error(f"Error configuring service domain: {str(e)}")
            return False

# Singleton instance
_cloudflare_manager = None

def get_cloudflare_manager() -> CloudflareManager:
    """
    Get or create the CloudflareManager singleton instance.
    
    Returns:
        CloudflareManager: The manager instance.
    """
    global _cloudflare_manager
    if _cloudflare_manager is None:
        _cloudflare_manager = CloudflareManager()
    return _cloudflare_manager