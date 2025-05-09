"""
Domain Management System

A reusable domain management system that can be integrated with any Flask application.
It provides functionality to manage domains and DNS records using various DNS providers.
"""

from .models import (
    DomainZone, DNSRecord, DomainServiceMapping, 
    DNSProviderSettings, init_db, Base
)
from .api_manager import (
    DNSApiProvider, CloudflareProvider, DNSRecord as ApiDNSRecord, 
    DomainInfo, get_dns_provider
)
from .domain_manager import (
    get_public_ip, get_available_services, get_zone_from_domain,
    create_domain_zone, create_dns_record_db, create_service_mapping,
    get_dns_provider_from_db, import_domains, setup_service_domains,
    get_domain_status, save_provider_settings
)
from .routes import domain_bp

__version__ = "1.0.0"
__all__ = [
    # Models
    'DomainZone', 'DNSRecord', 'DomainServiceMapping', 
    'DNSProviderSettings', 'init_db', 'Base',
    
    # API Manager
    'DNSApiProvider', 'CloudflareProvider', 'ApiDNSRecord', 
    'DomainInfo', 'get_dns_provider',
    
    # Domain Manager
    'get_public_ip', 'get_available_services', 'get_zone_from_domain',
    'create_domain_zone', 'create_dns_record_db', 'create_service_mapping',
    'get_dns_provider_from_db', 'import_domains', 'setup_service_domains',
    'get_domain_status', 'save_provider_settings',
    
    # Routes
    'domain_bp',
]

def init_app(app, engine=None):
    """
    Initialize the domain management system with a Flask application.
    
    Args:
        app: Flask application
        engine: SQLAlchemy engine (optional)
    """
    # Register blueprint
    app.register_blueprint(domain_bp)
    
    # Initialize database if engine provided
    if engine:
        init_db(engine)