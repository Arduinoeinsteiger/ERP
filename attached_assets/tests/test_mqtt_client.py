#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests für den MQTT-Client des SwissAirDry-Projekts
"""

import pytest
import json
from unittest.mock import patch, MagicMock

# Import der zu testenden Klasse
from swissairdry.api.mqtt_client import MQTTClient


class TestMQTTClient:
    """Testklasse für den MQTT-Client"""

    @pytest.fixture
    def mqtt_client(self):
        """Test-Fixture für den MQTT-Client"""
        with patch('paho.mqtt.client.Client') as mock_client:
            # Mock für den MQTT-Client erstellen
            client_instance = mock_client.return_value
            client_instance.connect.return_value = 0
            client_instance.loop_start.return_value = None
            
            # MQTT-Client mit Mock initialisieren
            mqtt_client = MQTTClient(host="test-broker", port=1883)
            
            yield mqtt_client
            
            # Aufräumen nach dem Test
            mqtt_client._client = None

    @pytest.mark.asyncio
    async def test_connect(self, mqtt_client):
        """Testet die connect-Methode"""
        result = await mqtt_client.connect()
        
        # Überprüfen, ob connect aufgerufen wurde
        mqtt_client._client.connect.assert_called_once_with("test-broker", 1883, 60)
        # Überprüfen, ob loop_start aufgerufen wurde
        mqtt_client._client.loop_start.assert_called_once()
        # Überprüfen, ob die Methode True zurückgibt
        assert result is True

    @pytest.mark.asyncio
    async def test_publish(self, mqtt_client):
        """Testet die publish-Methode"""
        # Mock für den MQTT-Client konfigurieren
        mqtt_client._client.publish.return_value.rc = 0
        
        # Dummy-Daten für den Test
        topic = "test/topic"
        payload = {"test": "data"}
        
        # Methode aufrufen
        result = await mqtt_client.publish(topic, payload)
        
        # Überprüfen, ob publish mit den richtigen Parametern aufgerufen wurde
        mqtt_client._client.publish.assert_called_once_with(
            topic,
            json.dumps(payload),
            qos=0,
            retain=False
        )
        
        # Überprüfen, ob die Methode True zurückgibt
        assert result is True

    @pytest.mark.asyncio
    async def test_subscribe(self, mqtt_client):
        """Testet die subscribe-Methode"""
        # Mock für den MQTT-Client konfigurieren
        mqtt_client._client.subscribe.return_value = [0, 0]
        
        # Methode aufrufen
        result = await mqtt_client.subscribe("test/topic")
        
        # Überprüfen, ob subscribe mit dem richtigen Parameter aufgerufen wurde
        mqtt_client._client.subscribe.assert_called_once_with("test/topic")
        
        # Überprüfen, ob die Methode True zurückgibt
        assert result is True

    def test_is_connected(self, mqtt_client):
        """Testet die is_connected-Methode"""
        # Fall 1: Client ist verbunden
        mqtt_client._client.is_connected.return_value = True
        assert mqtt_client.is_connected() is True
        
        # Fall 2: Client ist nicht verbunden
        mqtt_client._client.is_connected.return_value = False
        assert mqtt_client.is_connected() is False