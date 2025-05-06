<?php
declare(strict_types=1);

namespace OCA\SwissAirDry\Service;

use Exception;
use OCP\IConfig;

class DeviceService {
    /** @var ApiService */
    private $apiService;
    
    /** @var MqttService */
    private $mqttService;
    
    /** @var IConfig */
    private $config;
    
    /** @var string */
    private $appName;

    public function __construct(
        string $appName,
        ApiService $apiService,
        MqttService $mqttService,
        IConfig $config
    ) {
        $this->appName = $appName;
        $this->apiService = $apiService;
        $this->mqttService = $mqttService;
        $this->config = $config;
    }

    /**
     * Ruft alle Geräte ab
     * 
     * @param string $userId Benutzer-ID
     * @return array Liste der Geräte
     * @throws Exception bei Fehlern
     */
    public function getDevices(string $userId): array {
        try {
            return $this->apiService->get($userId, '/devices');
        } catch (Exception $e) {
            throw new Exception('Fehler beim Abrufen der Geräte: ' . $e->getMessage());
        }
    }
    
    /**
     * Ruft ein einzelnes Gerät anhand seiner ID ab
     * 
     * @param string $userId Benutzer-ID
     * @param string $deviceId Geräte-ID
     * @return array|null Gerätedaten oder null, wenn nicht gefunden
     * @throws Exception bei Fehlern
     */
    public function getDevice(string $userId, string $deviceId): ?array {
        try {
            return $this->apiService->get($userId, '/devices/' . $deviceId);
        } catch (Exception $e) {
            if (strpos($e->getMessage(), '404') !== false) {
                return null; // Gerät nicht gefunden
            }
            throw new Exception('Fehler beim Abrufen des Geräts: ' . $e->getMessage());
        }
    }
    
    /**
     * Aktualisiert die Daten eines Geräts
     * 
     * @param string $userId Benutzer-ID
     * @param string $deviceId Geräte-ID
     * @param array $data Zu aktualisierende Daten
     * @return array Aktualisierte Gerätedaten
     * @throws Exception bei Fehlern
     */
    public function updateDevice(string $userId, string $deviceId, array $data): array {
        try {
            return $this->apiService->put($userId, '/devices/' . $deviceId, $data);
        } catch (Exception $e) {
            throw new Exception('Fehler beim Aktualisieren des Geräts: ' . $e->getMessage());
        }
    }
    
    /**
     * Sendet einen Befehl an ein Gerät
     * 
     * @param string $userId Benutzer-ID
     * @param string $deviceId Geräte-ID
     * @param array $commandData Befehlsdaten
     * @return array Antwort auf den Befehl
     * @throws Exception bei Fehlern
     */
    public function sendCommand(string $userId, string $deviceId, array $commandData): array {
        try {
            // Senden über API
            $apiResponse = $this->apiService->post(
                $userId, 
                '/devices/' . $deviceId . '/command',
                $commandData
            );
            
            // Zusätzlich über MQTT senden
            $topic = 'swissairdry/' . $deviceId . '/command';
            $this->mqttService->publish($topic, $commandData);
            
            return $apiResponse;
        } catch (Exception $e) {
            throw new Exception('Fehler beim Senden des Befehls: ' . $e->getMessage());
        }
    }
    
    /**
     * Ruft die Sensordaten eines Geräts ab
     * 
     * @param string $userId Benutzer-ID
     * @param string $deviceId Geräte-ID
     * @return array Sensordaten
     * @throws Exception bei Fehlern
     */
    public function getDeviceData(string $userId, string $deviceId): array {
        try {
            return $this->apiService->get($userId, '/devices/' . $deviceId . '/data');
        } catch (Exception $e) {
            throw new Exception('Fehler beim Abrufen der Gerätedaten: ' . $e->getMessage());
        }
    }
    
    /**
     * Ruft die Position eines Geräts ab
     * 
     * @param string $userId Benutzer-ID
     * @param string $deviceId Geräte-ID
     * @return array Positionsdaten
     * @throws Exception bei Fehlern
     */
    public function getDeviceLocation(string $userId, string $deviceId): array {
        try {
            return $this->apiService->get($userId, '/devices/' . $deviceId . '/location');
        } catch (Exception $e) {
            throw new Exception('Fehler beim Abrufen des Gerätestandorts: ' . $e->getMessage());
        }
    }
    
    /**
     * Ruft die Positionsdaten aller Geräte ab
     * 
     * @param string $userId Benutzer-ID
     * @return array Positionsdaten für alle Geräte
     * @throws Exception bei Fehlern
     */
    public function getDeviceLocations(string $userId): array {
        try {
            return $this->apiService->get($userId, '/locations');
        } catch (Exception $e) {
            throw new Exception('Fehler beim Abrufen der Gerätestandorte: ' . $e->getMessage());
        }
    }
}