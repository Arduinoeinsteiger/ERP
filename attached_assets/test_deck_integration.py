#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test-Skript für die SwissAirDry ExApp Deck-Integration
-----------------------------------------------------

Dieses Skript testet die Funktionalität der SwissAirDry ExApp Deck-Integration
durch das Senden von Testdaten an die ExApp-API.
"""

import os
import sys
import json
import requests
import logging
from datetime import datetime

# Konfiguration
EXAPP_URL = os.environ.get("EXAPP_URL", "http://localhost:8081")
API_TOKEN = os.environ.get("API_TOKEN", "")  # Optional, falls API-Token erforderlich ist

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('exapp_test')

def check_exapp_status():
    """Überprüft den Status der ExApp"""
    try:
        response = requests.get(f"{EXAPP_URL}/status")
        if response.status_code == 200:
            status_data = response.json()
            logger.info(f"ExApp Status: {status_data}")
            return status_data
        else:
            logger.error(f"Fehler beim Abrufen des ExApp-Status: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Verbindungsfehler zur ExApp: {e}")
        return None

def check_deck_status():
    """Überprüft den Status der Deck-Integration"""
    try:
        response = requests.get(f"{EXAPP_URL}/deck/status")
        if response.status_code == 200:
            status_data = response.json()
            logger.info(f"Deck Integration Status: {status_data}")
            return status_data
        else:
            logger.error(f"Fehler beim Abrufen des Deck-Status: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Verbindungsfehler zur Deck-Integration: {e}")
        return None

def create_test_job():
    """Erstellt einen Test-Job in Deck"""
    try:
        job_data = {
            "job_id": f"JOB-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "title": f"Testauftrag {datetime.now().strftime('%d.%m.%Y %H:%M')}",
            "description": "Dies ist ein Testauftrag, der vom SwissAirDry ExApp Test-Skript erstellt wurde.",
            "status": "Aktiv",
            "details": {
                "Kunde": "Test GmbH",
                "Kontakt": "Max Mustermann",
                "Telefon": "+49 123 456789",
                "Email": "test@example.com",
                "Priorität": "Hoch",
                "Geräte": ["SARD-001", "SARD-002", "SARD-003"]
            }
        }
        
        response = requests.post(
            f"{EXAPP_URL}/deck/jobs",
            json=job_data
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Job erstellt: {result}")
            return result
        else:
            logger.error(f"Fehler beim Erstellen des Jobs: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Fehler beim Erstellen des Jobs: {e}")
        return None

def create_test_alarm():
    """Erstellt einen Test-Alarm in Deck"""
    try:
        alarm_data = {
            "device_id": f"SARD-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "alarm_type": "Hohe Luftfeuchtigkeit",
            "description": f"Die Luftfeuchtigkeit hat den Grenzwert überschritten. Gemessen: 90%, Grenzwert: 80%. Zeitpunkt: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}",
        }
        
        response = requests.post(
            f"{EXAPP_URL}/deck/alarms",
            json=alarm_data
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Alarm erstellt: {result}")
            return result
        else:
            logger.error(f"Fehler beim Erstellen des Alarms: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Fehler beim Erstellen des Alarms: {e}")
        return None

def send_mqtt_alarm():
    """Sendet einen Test-Alarm über MQTT"""
    try:
        device_id = f"SARD-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        mqtt_data = {
            "topic": f"{device_id}/alarm",
            "payload": {
                "type": "Temperaturalarm",
                "description": f"Die Temperatur hat den Grenzwert überschritten. Gemessen: 35°C, Grenzwert: 30°C. Zeitpunkt: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}",
                "value": 35,
                "limit": 30,
                "timestamp": datetime.now().isoformat()
            },
            "qos": 1,
            "retain": False
        }
        
        response = requests.post(
            f"{EXAPP_URL}/mqtt/publish",
            json=mqtt_data
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"MQTT-Alarm gesendet: {result}")
            return result
        else:
            logger.error(f"Fehler beim Senden des MQTT-Alarms: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Fehler beim Senden des MQTT-Alarms: {e}")
        return None

def main():
    """Hauptfunktion für die Tests"""
    logger.info("Starte Tests für die SwissAirDry ExApp Deck-Integration")
    
    # ExApp-Status prüfen
    exapp_status = check_exapp_status()
    if not exapp_status or exapp_status.get('status') != 'ok':
        logger.error("ExApp ist nicht erreichbar oder nicht bereit. Breche Tests ab.")
        return
    
    # Deck-Status prüfen
    deck_status = check_deck_status()
    if not deck_status:
        logger.warning("Deck-Integration nicht verfügbar oder nicht initialisiert.")
        logger.info("Teste trotzdem die anderen Funktionen...")
    
    # Test-Job erstellen
    logger.info("Erstelle Test-Job...")
    job_result = create_test_job()
    
    # Test-Alarm erstellen
    logger.info("Erstelle Test-Alarm...")
    alarm_result = create_test_alarm()
    
    # MQTT-Alarm senden
    logger.info("Sende MQTT-Alarm...")
    mqtt_result = send_mqtt_alarm()
    
    # Ergebnisse zusammenfassen
    logger.info("Testergebnisse:")
    logger.info(f"- ExApp-Status: {'OK' if exapp_status else 'FEHLER'}")
    logger.info(f"- Deck-Status: {'OK' if deck_status else 'FEHLER'}")
    logger.info(f"- Job erstellen: {'OK' if job_result else 'FEHLER'}")
    logger.info(f"- Alarm erstellen: {'OK' if alarm_result else 'FEHLER'}")
    logger.info(f"- MQTT-Alarm senden: {'OK' if mqtt_result else 'FEHLER'}")
    
    logger.info("Tests abgeschlossen.")

if __name__ == "__main__":
    main()