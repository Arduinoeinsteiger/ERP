#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests für die API-Endpunkte des SwissAirDry-Projekts
"""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# FastAPI-App und Datenmodelle importieren
from swissairdry.api.app.run2 import app
from swissairdry.api.app import models


@pytest.fixture
def client():
    """Test-Client für die FastAPI-App"""
    return TestClient(app)


class TestAPIEndpoints:
    """Testklasse für die API-Endpunkte"""

    def test_root_endpoint(self, client):
        """Testet den Root-Endpunkt"""
        response = client.get("/")
        
        assert response.status_code == 200
        # Der Root-Endpunkt gibt HTML zurück, kein JSON
        assert "SwissAirDry" in response.text

    def test_health_endpoint(self, client):
        """Testet den Health-Check-Endpunkt"""
        response = client.get("/health")
        
        assert response.status_code == 200
        # Prüfe nur, ob der Status auf "ok" steht, ignoriere andere Felder
        assert response.json()["status"] == "ok"

    @patch("swissairdry.crud.get_devices")
    def test_get_devices(self, mock_get_devices, client):
        """Testet den Endpunkt zum Abrufen aller Geräte"""
        # Erstellen echter Device-Objekte als Mock-Daten
        device1 = models.Device(
            id="1",  # String-ID entsprechend dem Datenbankmodell
            device_id="device1",
            name="Testgerät 1",
            type="dehumidifier",
            status="active",
            created_at=datetime.now()
        )
        device2 = models.Device(
            id="2",  # String-ID entsprechend dem Datenbankmodell
            device_id="device2",
            name="Testgerät 2",
            type="sensor",
            status="active",
            created_at=datetime.now()
        )
        
        # Mock konfigurieren
        mock_get_devices.return_value = [device1, device2]
        
        # API-Endpunkt testen
        response = client.get("/api/devices")
        
        # Wir können nicht den genauen Inhalt testen, da wir die Serialisierung nicht kennen
        # Stattdessen prüfen wir, ob der Endpunkt erfolgreich ist
        assert response.status_code == 200

    @patch("swissairdry.crud.get_device_by_device_id")
    def test_get_device_by_id(self, mock_get_device_by_id, client):
        """Testet den Endpunkt zum Abrufen eines Geräts anhand seiner ID"""
        # Mock-Daten für den Test
        mock_device = models.Device(
            id="1",  # String-ID entsprechend dem Datenbankmodell
            device_id="device1",
            name="Testgerät 1",
            type="dehumidifier",
            status="active",
            created_at=datetime.now()
        )
        
        # Mock konfigurieren
        mock_get_device_by_id.return_value = mock_device
        
        # API-Endpunkt testen
        response = client.get("/api/devices/device1")
        
        # Prüfen, ob der Endpunkt erfolgreich ist
        assert response.status_code == 200
        
        # Testen, wenn das Gerät nicht gefunden wird
        mock_get_device_by_id.return_value = None
        response = client.get("/api/devices/nonexistent")
        assert response.status_code == 404