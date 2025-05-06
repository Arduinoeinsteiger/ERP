# SwissAirDry Platform

A comprehensive IoT system for monitoring and controlling drying devices with ESP8266/ESP32 hardware.

![SwissAirDry Logo](generated-icon.png)

## Overview

SwissAirDry is a complete IoT solution that integrates backend APIs, MQTT communication, PostgreSQL database, and ESP32/ESP8266 devices. The system provides web dashboards for device management, status monitoring, and configuration. IoT devices include Wemos D1 Mini with display capabilities (64px and 128px variants) showing device status and QR codes for easy access.

The platform now includes Nextcloud integration through the ExApp (External App) architecture, providing a seamless connection between the SwissAirDry ecosystem and Nextcloud services.

## Main Components

- **Flask Backend**: Provides API endpoints and web interface
- **MQTT Communication**: Enables real-time communication with IoT devices
- **PostgreSQL Database**: Stores device data, sensor readings, and configurations
- **ESP8266/ESP32 Firmware**: Optimized for various hardware configurations
- **Nextcloud Integration**: ExApp for integration with Nextcloud environments

## Features

- Real-time monitoring and control of drying devices
- Device management with automatic discovery
- Sensor data storage (temperature, humidity, pressure, fan speed, power consumption)
- Over-the-Air (OTA) firmware updates
- QR code display for easy access to device information
- Responsive web user interface
- Nextcloud integration for extended functionality

## System Architecture

```
+------------------+      +------------------+     +-------------------+
|                  |      |                  |     |                   |
|   IoT Devices    |<---->|   MQTT Broker    |<--->|   Flask Backend   |
| (ESP8266/ESP32)  |      | (Mosquitto)      |     | (API/Web Interface)|
|                  |      |                  |     |                   |
+------------------+      +------------------+     +--------+----------+
                                                           |
                                                           v
                               +-------------+    +-------------------+
                               |             |    |                   |
                               |  Nextcloud  |<-->|   PostgreSQL DB   |
                               |   ExApp     |    |                   |
                               |             |    |                   |
                               +-------------+    +-------------------+
```

## Installation

### Prerequisites

- Docker and Docker Compose
- Or: Python 3.8+ and PostgreSQL
- MQTT Broker (Mosquitto)
- ESP8266/ESP32 with support for the required sensors

### Docker Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/swissairdry.git
   cd swissairdry
   ```

2. Start Docker Compose:
   ```bash
   docker-compose up -d
   ```

3. The web application is available at http://localhost:5000.

### Manual Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/swissairdry.git
   cd swissairdry
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up the PostgreSQL database.

4. Configure environment variables (see `.env.example`).

5. Start the server:
   ```bash
   gunicorn --bind 0.0.0.0:5000 main:app
   ```

## Firmware Installation

The firmware for ESP8266/ESP32 devices is located in the `firmware/` folder. Follow the instructions in the corresponding README file in that directory.

## Configuration

### MQTT Settings

MQTT configuration can be adjusted through environment variables or directly in the `mqtt/config/mosquitto.conf` file.

### Database Settings

Database settings are configured through environment variables. See `.env.example` for available options.

## API Documentation

The API endpoints allow management of devices, sensor data, and configurations. Detailed documentation is available at `/api/docs` when the server is running.

## Nextcloud Integration

The SwissAirDry platform can be integrated with Nextcloud. To do this, you need to:

1. Install the ExApp in your Nextcloud instance
2. Configure the ExApp daemon to communicate with the SwissAirDry API

## License

This project is licensed under the MIT License. See the LICENSE file for more information.

## Authors

- Your names and contact information

## Contributing

Contributions to the project are welcome! Please fork the repository and submit pull requests.