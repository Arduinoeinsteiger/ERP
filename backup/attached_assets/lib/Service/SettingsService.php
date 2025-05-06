<?php
declare(strict_types=1);

namespace OCA\SwissAirDry\Service;

use Exception;
use OCP\IConfig;
use OCP\ILogger;

class SettingsService {
    /** @var IConfig */
    private $config;
    
    /** @var ILogger */
    private $logger;
    
    /** @var string */
    private $appName;
    
    /** @var array */
    private $defaultSettings = [
        'apiEndpoint' => 'api.vgnc.org',
        'apiPort' => 443,
        'apiBasePath' => '/v1',
        'mqttBroker' => 'mqtt.vgnc.org',
        'mqttPort' => 8883,
        'mqttSecure' => true,
        'refreshInterval' => 30,
        'darkMode' => false,
        'notifications' => true
    ];

    public function __construct(
        string $appName,
        IConfig $config,
        ILogger $logger
    ) {
        $this->appName = $appName;
        $this->config = $config;
        $this->logger = $logger;
    }

    /**
     * Gibt die Einstellungen für einen Benutzer zurück
     * 
     * @param string $userId Benutzer-ID
     * @return array Einstellungen
     */
    public function getSettings(string $userId): array {
        $settings = $this->defaultSettings;
        
        // Gespeicherte Einstellungen aus der Datenbank laden
        foreach ($settings as $key => $defaultValue) {
            $storedValue = $this->config->getUserValue($userId, $this->appName, $key, null);
            
            if ($storedValue !== null) {
                // Typkonvertierung
                if (is_bool($defaultValue)) {
                    $settings[$key] = filter_var($storedValue, FILTER_VALIDATE_BOOLEAN);
                } elseif (is_int($defaultValue)) {
                    $settings[$key] = (int) $storedValue;
                } else {
                    $settings[$key] = $storedValue;
                }
            }
        }
        
        return $settings;
    }
    
    /**
     * Aktualisiert die Einstellungen für einen Benutzer
     * 
     * @param string $userId Benutzer-ID
     * @param array $data Neue Einstellungswerte
     * @return array Aktualisierte Einstellungen
     */
    public function updateSettings(string $userId, array $data): array {
        $currentSettings = $this->getSettings($userId);
        $updatedSettings = array_merge($currentSettings, $data);
        
        // Nur gültige Einstellungen speichern
        foreach ($updatedSettings as $key => $value) {
            if (array_key_exists($key, $this->defaultSettings)) {
                $this->config->setUserValue($userId, $this->appName, $key, (string) $value);
            }
        }
        
        // Aktualisierte Einstellungen zurückgeben
        return $this->getSettings($userId);
    }
}