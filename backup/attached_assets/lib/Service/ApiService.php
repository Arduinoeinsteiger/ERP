<?php
declare(strict_types=1);

namespace OCA\SwissAirDry\Service;

use Exception;
use OCP\IConfig;
use OCP\Http\Client\IClientService;

class ApiService {
    /** @var IClientService */
    private $clientService;
    
    /** @var SettingsService */
    private $settingsService;
    
    /** @var IConfig */
    private $config;
    
    /** @var string */
    private $appName;

    public function __construct(
        string $appName,
        IClientService $clientService,
        SettingsService $settingsService,
        IConfig $config
    ) {
        $this->appName = $appName;
        $this->clientService = $clientService;
        $this->settingsService = $settingsService;
        $this->config = $config;
    }

    /**
     * Führt eine GET-Anfrage an die SwissAirDry-API aus
     * 
     * @param string $userId Benutzer-ID
     * @param string $endpoint API-Endpunkt (z.B. '/devices')
     * @param array $params Query-Parameter
     * @return array Antwort-Daten als Array
     * @throws Exception bei Fehlern
     */
    public function get(string $userId, string $endpoint, array $params = []): array {
        $settings = $this->settingsService->getSettings($userId);
        $client = $this->clientService->newClient();
        
        $protocol = ($settings['apiPort'] === 443) ? 'https' : 'http';
        $baseUrl = $protocol . '://' . $settings['apiEndpoint'];
        
        if ($settings['apiPort'] !== 80 && $settings['apiPort'] !== 443) {
            $baseUrl .= ':' . $settings['apiPort'];
        }
        
        $baseUrl .= $settings['apiBasePath'];
        $url = $baseUrl . $endpoint;
        
        try {
            $response = $client->get($url, [
                'query' => $params,
                'timeout' => 30,
                'verify' => false // In Produktionsumgebung auf true setzen!
            ]);
            
            $body = $response->getBody();
            $data = json_decode($body, true);
            
            if (json_last_error() !== JSON_ERROR_NONE) {
                throw new Exception('Ungültige JSON-Antwort: ' . json_last_error_msg());
            }
            
            return $data;
        } catch (Exception $e) {
            throw new Exception('API-Anfrage fehlgeschlagen: ' . $e->getMessage());
        }
    }
    
    /**
     * Führt eine POST-Anfrage an die SwissAirDry-API aus
     * 
     * @param string $userId Benutzer-ID
     * @param string $endpoint API-Endpunkt (z.B. '/devices')
     * @param array $data POST-Daten
     * @return array Antwort-Daten als Array
     * @throws Exception bei Fehlern
     */
    public function post(string $userId, string $endpoint, array $data = []): array {
        $settings = $this->settingsService->getSettings($userId);
        $client = $this->clientService->newClient();
        
        $protocol = ($settings['apiPort'] === 443) ? 'https' : 'http';
        $baseUrl = $protocol . '://' . $settings['apiEndpoint'];
        
        if ($settings['apiPort'] !== 80 && $settings['apiPort'] !== 443) {
            $baseUrl .= ':' . $settings['apiPort'];
        }
        
        $baseUrl .= $settings['apiBasePath'];
        $url = $baseUrl . $endpoint;
        
        try {
            $response = $client->post($url, [
                'json' => $data,
                'timeout' => 30,
                'verify' => false // In Produktionsumgebung auf true setzen!
            ]);
            
            $body = $response->getBody();
            $responseData = json_decode($body, true);
            
            if (json_last_error() !== JSON_ERROR_NONE) {
                throw new Exception('Ungültige JSON-Antwort: ' . json_last_error_msg());
            }
            
            return $responseData;
        } catch (Exception $e) {
            throw new Exception('API-Anfrage fehlgeschlagen: ' . $e->getMessage());
        }
    }
    
    /**
     * Führt eine PUT-Anfrage an die SwissAirDry-API aus
     * 
     * @param string $userId Benutzer-ID
     * @param string $endpoint API-Endpunkt (z.B. '/devices/123')
     * @param array $data PUT-Daten
     * @return array Antwort-Daten als Array
     * @throws Exception bei Fehlern
     */
    public function put(string $userId, string $endpoint, array $data = []): array {
        $settings = $this->settingsService->getSettings($userId);
        $client = $this->clientService->newClient();
        
        $protocol = ($settings['apiPort'] === 443) ? 'https' : 'http';
        $baseUrl = $protocol . '://' . $settings['apiEndpoint'];
        
        if ($settings['apiPort'] !== 80 && $settings['apiPort'] !== 443) {
            $baseUrl .= ':' . $settings['apiPort'];
        }
        
        $baseUrl .= $settings['apiBasePath'];
        $url = $baseUrl . $endpoint;
        
        try {
            $response = $client->put($url, [
                'json' => $data,
                'timeout' => 30,
                'verify' => false // In Produktionsumgebung auf true setzen!
            ]);
            
            $body = $response->getBody();
            $responseData = json_decode($body, true);
            
            if (json_last_error() !== JSON_ERROR_NONE) {
                throw new Exception('Ungültige JSON-Antwort: ' . json_last_error_msg());
            }
            
            return $responseData;
        } catch (Exception $e) {
            throw new Exception('API-Anfrage fehlgeschlagen: ' . $e->getMessage());
        }
    }
}