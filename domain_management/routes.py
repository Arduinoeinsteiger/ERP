"""
Flask routes for Domain Management System

This module provides Flask routes for the domain management system.
It can be included in your Flask application to provide domain management functionality.
"""

import os
from typing import Dict, Any, Optional, List
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy.orm import Session

from .models import DomainZone, DNSRecord, DomainServiceMapping, DNSProviderSettings
from .domain_manager import (
    get_domain_status, import_domains, setup_service_domains,
    get_available_services, get_public_ip, save_provider_settings
)

# Create a Blueprint for the domain management routes
# This can be registered with your Flask application
domain_bp = Blueprint('domain', __name__, url_prefix='/domains')

# Helper function to get a database session
# This should be replaced with your application's get_db function
def get_db():
    """Example get_db function - replace with your own."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    engine = create_engine(os.environ.get("DATABASE_URL"))
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@domain_bp.route('/')
def index():
    """Render the domain management page."""
    db = next(get_db())
    try:
        # Get domain status
        status = get_domain_status(db)
        
        # Prepare template variables
        api_connected = status.get("api_connected", False)
        zones = status.get("zones", [])
        service_mappings = status.get("service_mappings", {})
        public_ip = status.get("public_ip", "")
        provider = status.get("provider", "cloudflare")
        
        return render_template(
            'domain_management/index.html',
            api_connected=api_connected,
            zones=zones,
            service_mappings=service_mappings,
            public_ip=public_ip,
            provider=provider
        )
    except Exception as e:
        flash(f"Error loading domain management: {str(e)}", "danger")
        return redirect(url_for('index'))
    finally:
        db.close()

@domain_bp.route('/connect')
def connect_api():
    """Connect to DNS API provider."""
    provider = request.args.get('provider', 'cloudflare')
    
    # Check if environment variable is set
    env_var_name = f"{provider.upper()}_API_TOKEN"
    if os.environ.get(env_var_name):
        flash(f"Using {provider.title()} API token from environment variable.", "info")
        return redirect(url_for('domain.index'))
    
    # Show form to enter API token
    return render_template('domain_management/connect.html', provider=provider)

@domain_bp.route('/connect', methods=['POST'])
def connect_api_post():
    """Process API connection form."""
    provider = request.form.get('provider', 'cloudflare')
    api_token = request.form.get('api_token')
    
    if not api_token:
        flash("API token is required.", "danger")
        return redirect(url_for('domain.connect_api'))
    
    db = next(get_db())
    try:
        # Save provider settings
        success = save_provider_settings(db, provider, api_token)
        
        if success:
            flash(f"Successfully connected to {provider.title()}!", "success")
        else:
            flash(f"Failed to connect to {provider.title()}. Please check your API token.", "danger")
        
        return redirect(url_for('domain.index'))
    except Exception as e:
        flash(f"Error connecting to {provider.title()}: {str(e)}", "danger")
        return redirect(url_for('domain.connect_api'))
    finally:
        db.close()

@domain_bp.route('/import')
def import_domain():
    """Import domains from DNS provider."""
    provider = request.args.get('provider', 'cloudflare')
    db = next(get_db())
    try:
        # Import domains from provider
        zone_count, record_count, errors = import_domains(db, provider)
        
        if errors:
            for error in errors:
                flash(f"Error: {error}", "danger")
        
        if zone_count > 0 or record_count > 0:
            flash(f"{zone_count} domains and {record_count} DNS records successfully imported.", "success")
        else:
            flash("No new domains found or imported.", "info")
        
        return redirect(url_for('domain.index'))
    except Exception as e:
        flash(f"Error importing domains: {str(e)}", "danger")
        return redirect(url_for('domain.index'))
    finally:
        db.close()

@domain_bp.route('/view/<int:zone_id>')
def view_domain(zone_id):
    """View detailed information about a domain zone."""
    db = next(get_db())
    try:
        zone = db.query(DomainZone).filter_by(id=zone_id).first()
        if not zone:
            flash(f"Domain with ID {zone_id} not found.", "danger")
            return redirect(url_for('domain.index'))
        
        dns_records = db.query(DNSRecord).filter_by(zone_id=zone.id).all()
        service_mappings = db.query(DomainServiceMapping).filter_by(zone_id=zone.id).all()
        
        return render_template(
            'domain_management/details.html',
            zone=zone,
            dns_records=dns_records,
            service_mappings=service_mappings
        )
    except Exception as e:
        flash(f"Error viewing domain details: {str(e)}", "danger")
        return redirect(url_for('domain.index'))
    finally:
        db.close()

@domain_bp.route('/dns/<int:zone_id>')
def dns_records(zone_id):
    """View DNS records for a domain zone."""
    db = next(get_db())
    try:
        zone = db.query(DomainZone).filter_by(id=zone_id).first()
        if not zone:
            flash(f"Domain with ID {zone_id} not found.", "danger")
            return redirect(url_for('domain.index'))
        
        dns_records = db.query(DNSRecord).filter_by(zone_id=zone.id).all()
        
        return render_template(
            'domain_management/dns.html',
            zone=zone,
            dns_records=dns_records
        )
    except Exception as e:
        flash(f"Error viewing DNS records: {str(e)}", "danger")
        return redirect(url_for('domain.index'))
    finally:
        db.close()

@domain_bp.route('/dns/<int:zone_id>/add', methods=['POST'])
def dns_add_record(zone_id):
    """Add a new DNS record to a domain zone."""
    db = next(get_db())
    try:
        zone = db.query(DomainZone).filter_by(id=zone_id).first()
        if not zone:
            flash(f"Domain with ID {zone_id} not found.", "danger")
            return redirect(url_for('domain.index'))
        
        # Get form data
        record_type = request.form.get('type')
        record_name = request.form.get('name')
        record_content = request.form.get('content')
        record_ttl = request.form.get('ttl', 1)
        record_proxied = request.form.get('proxied') == 'true'
        
        # Validate form data
        if not record_type or not record_name or not record_content:
            flash("Type, name and content are required for DNS record.", "danger")
            return redirect(url_for('domain.dns_records', zone_id=zone_id))
        
        # Add DNS record
        # This is a simplified implementation - actual implementation would use the DNS provider
        flash("Adding DNS records is not implemented in this example.", "warning")
        return redirect(url_for('domain.dns_records', zone_id=zone_id))
    except Exception as e:
        flash(f"Error adding DNS record: {str(e)}", "danger")
        return redirect(url_for('domain.dns_records', zone_id=zone_id))
    finally:
        db.close()

@domain_bp.route('/dns/<int:zone_id>/delete/<int:record_id>', methods=['POST'])
def dns_delete_record(zone_id, record_id):
    """Delete a DNS record from a domain zone."""
    db = next(get_db())
    try:
        zone = db.query(DomainZone).filter_by(id=zone_id).first()
        if not zone:
            flash(f"Domain with ID {zone_id} not found.", "danger")
            return redirect(url_for('domain.index'))
        
        record = db.query(DNSRecord).filter_by(id=record_id, zone_id=zone.id).first()
        if not record:
            flash(f"DNS record with ID {record_id} not found.", "danger")
            return redirect(url_for('domain.dns_records', zone_id=zone_id))
        
        # Delete DNS record
        # This is a simplified implementation - actual implementation would use the DNS provider
        flash("Deleting DNS records is not implemented in this example.", "warning")
        return redirect(url_for('domain.dns_records', zone_id=zone_id))
    except Exception as e:
        flash(f"Error deleting DNS record: {str(e)}", "danger")
        return redirect(url_for('domain.dns_records', zone_id=zone_id))
    finally:
        db.close()

@domain_bp.route('/configure-services/<int:zone_id>', methods=['GET', 'POST'])
def configure_services(zone_id):
    """Configure services for a domain zone."""
    db = next(get_db())
    try:
        zone = db.query(DomainZone).filter_by(id=zone_id).first()
        if not zone:
            flash(f"Domain with ID {zone_id} not found.", "danger")
            return redirect(url_for('domain.index'))
        
        if request.method == 'POST':
            # Get IP address from form or auto-detect
            ip_address = request.form.get('ip_address')
            if not ip_address:
                ip_address = get_public_ip()
                if not ip_address:
                    flash("Error: IP address could not be automatically detected.", "danger")
                    return redirect(request.url)
            
            # Set up service domains
            provider = zone.provider
            services_count, errors = setup_service_domains(
                zone_id=zone.id,
                domain=zone.name,
                ip_address=ip_address,
                db=db,
                provider=provider
            )
            
            if errors:
                for error in errors:
                    flash(f"Error: {error}", "danger")
            
            if services_count > 0:
                flash(f"{services_count} services successfully configured.", "success")
            else:
                flash("No services configured.", "info")
            
            return redirect(url_for('domain.index'))
        
        # GET request: show configuration form
        available_services = get_available_services()
        public_ip = get_public_ip()
        
        return render_template(
            'domain_management/configure_services.html',
            zone=zone,
            available_services=available_services,
            public_ip=public_ip
        )
    except Exception as e:
        flash(f"Error configuring services: {str(e)}", "danger")
        return redirect(url_for('domain.index'))
    finally:
        db.close()

@domain_bp.route('/delete/<int:zone_id>', methods=['POST'])
def delete_domain(zone_id):
    """Delete a domain zone from the database."""
    db = next(get_db())
    try:
        zone = db.query(DomainZone).filter_by(id=zone_id).first()
        if not zone:
            flash(f"Domain with ID {zone_id} not found.", "danger")
            return redirect(url_for('domain.index'))
        
        # Note: We're only removing from our database, not from the DNS provider
        db.delete(zone)
        db.commit()
        
        flash(f"Domain '{zone.name}' successfully removed.", "success")
        return redirect(url_for('domain.index'))
    except Exception as e:
        db.rollback()
        flash(f"Error deleting domain: {str(e)}", "danger")
        return redirect(url_for('domain.index'))
    finally:
        db.close()

@domain_bp.route('/delete-mapping', methods=['POST'])
def delete_mapping():
    """Delete a service mapping."""
    service_name = request.args.get('service')
    zone_name = request.args.get('zone')
    
    if not service_name or not zone_name:
        flash("Error: Service name and domain name are required.", "danger")
        return redirect(url_for('domain.index'))
    
    db = next(get_db())
    try:
        zone = db.query(DomainZone).filter_by(name=zone_name).first()
        if not zone:
            flash(f"Domain '{zone_name}' not found.", "danger")
            return redirect(url_for('domain.index'))
        
        mapping = db.query(DomainServiceMapping).filter_by(
            zone_id=zone.id,
            service_name=service_name
        ).first()
        
        if not mapping:
            flash(f"Mapping for service '{service_name}' on domain '{zone_name}' not found.", "danger")
            return redirect(url_for('domain.index'))
        
        db.delete(mapping)
        db.commit()
        
        flash(f"Mapping for service '{service_name}' on domain '{zone_name}' successfully removed.", "success")
        return redirect(url_for('domain.index'))
    except Exception as e:
        db.rollback()
        flash(f"Error deleting mapping: {str(e)}", "danger")
        return redirect(url_for('domain.index'))
    finally:
        db.close()

@domain_bp.route('/edit-mapping/<service>/<zone_name>', methods=['GET', 'POST'])
def edit_mapping(service, zone_name):
    """Edit a service mapping."""
    db = next(get_db())
    try:
        zone = db.query(DomainZone).filter_by(name=zone_name).first()
        if not zone:
            flash(f"Domain '{zone_name}' not found.", "danger")
            return redirect(url_for('domain.index'))
        
        mapping = db.query(DomainServiceMapping).filter_by(
            zone_id=zone.id,
            service_name=service
        ).first()
        
        if not mapping:
            flash(f"Mapping for service '{service}' on domain '{zone_name}' not found.", "danger")
            return redirect(url_for('domain.index'))
        
        if request.method == 'POST':
            # Update mapping
            subdomain = request.form.get('subdomain')
            https_enabled = request.form.get('https_enabled') == 'on'
            notes = request.form.get('notes')
            
            mapping.subdomain = subdomain
            mapping.https_enabled = https_enabled
            mapping.notes = notes
            
            db.commit()
            
            flash(f"Mapping for service '{service}' successfully updated.", "success")
            return redirect(url_for('domain.index'))
        
        # GET request: show edit form
        return render_template(
            'domain_management/edit_mapping.html',
            mapping=mapping,
            zone=zone,
            service=service
        )
    except Exception as e:
        db.rollback()
        flash(f"Error editing mapping: {str(e)}", "danger")
        return redirect(url_for('domain.index'))
    finally:
        db.close()

# API endpoints for domain management

@domain_bp.route('/api/status')
def api_status():
    """Get domain management status as JSON."""
    db = next(get_db())
    try:
        status = get_domain_status(db)
        return jsonify({"success": True, "status": status})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()

@domain_bp.route('/api/services')
def api_services():
    """Get available services as JSON."""
    services = get_available_services()
    return jsonify({"success": True, "services": services})

@domain_bp.route('/api/setup', methods=['POST'])
def api_setup():
    """Set up domain management."""
    data = request.json
    zone_id = data.get('zone_id')
    ip_address = data.get('ip_address')
    
    if not zone_id:
        return jsonify({"success": False, "error": "Zone ID is required"}), 400
    
    db = next(get_db())
    try:
        zone = db.query(DomainZone).filter_by(id=zone_id).first()
        if not zone:
            return jsonify({"success": False, "error": f"Domain zone with ID {zone_id} not found"}), 404
        
        services_count, errors = setup_service_domains(
            zone_id=zone.id,
            domain=zone.name,
            ip_address=ip_address,
            db=db,
            provider=zone.provider
        )
        
        return jsonify({
            "success": services_count > 0,
            "services_count": services_count,
            "errors": errors
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()