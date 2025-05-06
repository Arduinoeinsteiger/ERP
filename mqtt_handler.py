"""
MQTT handler for the SwissAirDry platform.

This module provides MQTT communication functionality for device connectivity.
"""
import os
import json
import logging
import asyncio
import threading
from typing import Optional, Dict, Any, List, Callable

# For Flask version (synchronous)
import paho.mqtt.client as paho_mqtt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global MQTT handler instance
_mqtt_handler = None

class MQTTHandler:
    """
    Handles MQTT communication between the platform and devices.
    """
    def __init__(
        self, 
        broker: str = "localhost", 
        port: int = 1883, 
        username: Optional[str] = None, 
        password: Optional[str] = None,
        client_id: str = "swissairdry-server"
    ):
        self.broker = broker
        self.port = port
        self.username = username
        self.password = password
        self.client_id = client_id
        self.client = None
        self.paho_client = None  # For synchronous operations
        self.connected = False
        self.subscribed_topics = set()
        self.message_callbacks: Dict[str, List[Callable]] = {}

    # Synchronous methods for Flask
    def connect_sync(self) -> None:
        """
        Connect to the MQTT broker (synchronous version for Flask).
        """
        try:
            # Initialize Paho MQTT client
            self.paho_client = paho_mqtt.Client(client_id=self.client_id)
            
            # Set up callbacks
            self.paho_client.on_connect = self._paho_on_connect
            self.paho_client.on_message = self._paho_on_message
            self.paho_client.on_disconnect = self._paho_on_disconnect
            
            # Set credentials if provided
            if self.username and self.password:
                self.paho_client.username_pw_set(self.username, self.password)
            
            # Connect to broker with a short timeout
            self.paho_client.connect_async(self.broker, self.port)
            
            # Start the loop in a background thread
            self.paho_client.loop_start()
            
            logger.info(f"MQTT client initialized with broker {self.broker}:{self.port}")
            self.connected = True
        except Exception as e:
            logger.warning(f"Could not initialize MQTT connection: {e}")
            # Don't raise the exception, allow the application to continue

    def disconnect_sync(self) -> None:
        """
        Disconnect from the MQTT broker (synchronous version for Flask).
        """
        if self.paho_client:
            try:
                self.paho_client.loop_stop()
                if self.connected:
                    self.paho_client.disconnect()
                self.connected = False
                logger.info("Disconnected from MQTT broker")
            except Exception as e:
                logger.warning(f"Error disconnecting from MQTT broker: {e}")
                self.connected = False

    def subscribe_sync(self, topic: str) -> None:
        """
        Subscribe to an MQTT topic (synchronous version for Flask).
        """
        if not self.paho_client or not self.connected:
            logger.warning("Cannot subscribe: MQTT client not connected")
            # Track the topic for future subscription when connection is available
            self.subscribed_topics.add(topic)
            return
        
        if topic in self.subscribed_topics:
            logger.debug(f"Already subscribed to {topic}")
            return
        
        try:
            self.paho_client.subscribe(topic, qos=1)
            self.subscribed_topics.add(topic)
            logger.info(f"Subscribed to topic: {topic}")
        except Exception as e:
            logger.warning(f"Error subscribing to topic {topic}: {e}")
            # Add to subscribed topics anyway so we can retry on reconnect
            self.subscribed_topics.add(topic)

    def publish_sync(self, topic: str, payload: Any, retain: bool = False) -> None:
        """
        Publish a message to an MQTT topic (synchronous version for Flask).
        """
        if not self.paho_client or not self.connected:
            logger.warning(f"Cannot publish to {topic}: MQTT client not connected")
            return
        
        try:
            # Convert dictionary payload to JSON string
            if isinstance(payload, dict):
                payload = json.dumps(payload)
            
            self.paho_client.publish(topic, payload, qos=1, retain=retain)
            logger.debug(f"Published to {topic}: {payload}")
        except Exception as e:
            logger.warning(f"Error publishing to topic {topic}: {e}")

    # Paho MQTT Callback methods
    def _paho_on_connect(self, client, userdata, flags, rc):
        """
        Callback for when the client connects to the broker (Paho version).
        """
        if rc == 0:
            self.connected = True
            logger.info("MQTT connection established")
            
            # Re-subscribe to topics
            for topic in self.subscribed_topics:
                self.subscribe_sync(topic)
        else:
            logger.error(f"Failed to connect to MQTT broker with code: {rc}")

    def _paho_on_message(self, client, userdata, msg):
        """
        Callback for when a message is received from the broker (Paho version).
        """
        try:
            topic = msg.topic
            payload_str = msg.payload.decode()
            logger.debug(f"Received message on {topic}: {payload_str}")
            
            # Process callbacks for exact topic match
            self._process_topic_callbacks(topic, payload_str)
            
            # Process callbacks for wildcard topics
            for registered_topic in self.message_callbacks:
                if self._topic_matches_subscription(registered_topic, topic):
                    self._process_topic_callbacks(registered_topic, payload_str)
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")

    def _paho_on_disconnect(self, client, userdata, rc):
        """
        Callback for when the client disconnects from the broker (Paho version).
        """
        self.connected = False
        if rc != 0:
            logger.error(f"MQTT disconnected with error code: {rc}")
        else:
            logger.info("MQTT disconnected")

    # Asynchronous methods (kept for compatibility)
    async def connect(self) -> None:
        """
        Connect to the MQTT broker.
        """
        # Call synchronous version for now
        self.connect_sync()
    
    async def disconnect(self) -> None:
        """
        Disconnect from the MQTT broker.
        """
        # Call synchronous version for now
        self.disconnect_sync()
    
    async def subscribe(self, topic: str) -> None:
        """
        Subscribe to an MQTT topic.
        """
        # Call synchronous version for now
        self.subscribe_sync(topic)
    
    async def publish(self, topic: str, payload: Any, retain: bool = False) -> None:
        """
        Publish a message to an MQTT topic.
        """
        # Call synchronous version for now
        self.publish_sync(topic, payload, retain)
    
    def register_callback(self, topic: str, callback: Callable) -> None:
        """
        Register a callback function for a specific topic.
        """
        if topic not in self.message_callbacks:
            self.message_callbacks[topic] = []
        
        self.message_callbacks[topic].append(callback)
        logger.debug(f"Registered callback for topic {topic}")
    
    def _process_topic_callbacks(self, topic: str, payload_str: str) -> None:
        """
        Process callbacks for a specific topic.
        """
        if topic in self.message_callbacks:
            try:
                # Try to parse as JSON
                payload_data = json.loads(payload_str)
            except json.JSONDecodeError:
                # If not JSON, use the raw string
                payload_data = payload_str
            
            for callback in self.message_callbacks[topic]:
                try:
                    callback(topic, payload_data)
                except Exception as e:
                    logger.error(f"Error in callback for {topic}: {e}")
    
    def _topic_matches_subscription(self, subscription: str, topic: str) -> bool:
        """
        Check if a topic matches a subscription pattern (with wildcards).
        """
        if subscription == topic:
            return True
        
        subscription_parts = subscription.split('/')
        topic_parts = topic.split('/')
        
        if len(subscription_parts) > len(topic_parts) and '#' not in subscription_parts:
            return False
        
        for i, sub_part in enumerate(subscription_parts):
            # Multi-level wildcard
            if sub_part == '#':
                return True
            
            # Single-level wildcard
            if sub_part == '+':
                continue
            
            # Topic parts must match up to the length of subscription parts
            if i >= len(topic_parts) or sub_part != topic_parts[i]:
                return False
        
        # All parts matched and lengths are equal
        return len(subscription_parts) == len(topic_parts)

# Global getter function
def get_mqtt_handler() -> MQTTHandler:
    """
    Get the global MQTT handler instance.
    """
    global _mqtt_handler
    if _mqtt_handler is None:
        _mqtt_handler = MQTTHandler(
            broker=os.getenv("MQTT_BROKER", "localhost"),
            port=int(os.getenv("MQTT_PORT", 1883)),
            username=os.getenv("MQTT_USERNAME", ""),
            password=os.getenv("MQTT_PASSWORD", ""),
        )
    return _mqtt_handler
