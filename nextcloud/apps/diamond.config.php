<?php
/**
 * Diamond App-Konfiguration für SwissAirDry
 */

$CONFIG = [
    // Diamond App Einstellungen
    'diamond' => [
        'enabled' => true,
        'api_url' => 'http://api:5000',
        'device_sync_interval' => 300,  // Geräte-Synchronisierungsintervall in Sekunden
        'authentication' => [
            'type' => 'basic',
            'username' => 'swissairdry',
            'password' => 'swissairdryaccesstoken',
        ],
        'mqtt' => [
            'broker' => 'mqtt',
            'port' => 1883,
            'username' => '',
            'password' => '',
            'client_id' => 'nextcloud-diamond',
            'topics' => [
                'devices' => 'swissairdry/+/status',
                'telemetry' => 'swissairdry/+/telemetry',
                'control' => 'swissairdry/+/control',
            ],
        ],
        'device_types' => [
            'esp8266' => 'ESP8266 Gerät',
            'esp32' => 'ESP32 Gerät',
            'esp32c6' => 'ESP32-C6 Gerät',
        ],
    ],
    
    // Zusätzliche Nextcloud-Konfigurationen für Diamond-App
    'app.diamond.cache_ttl' => 300,
    'app.diamond.notification_enabled' => true,
    'app.diamond.dashboard_widgets' => ['status', 'telemetry', 'devices'],
];