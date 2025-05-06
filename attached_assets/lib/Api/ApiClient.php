<?php
declare(strict_types=1);

namespace OCA\SwissAirDry\Api;

use Exception;
use GuzzleHttp\Client;
use OCP\ILogger;

/**
 * Client für die SwissAirDry REST API
 */
class ApiClient {
    /** @var Client */
    private $httpClient;
    
    /** @var ILogger */
    private $logger;
    
    /** @var string */
    private $apiEndpoint;
    
    /** @var int */
    private $apiPort;
    
    /** @var string */
    private $apiBasePath;

    /**
     * Konstruktor
     * 
     * @param ILogger $logger Logger für Fehlerberichte
     * @param string $apiEndpoint API-Endpunkt (z.B. api.vgnc.org)
     * @param int $apiPort API-Port (Standard: 443)
     * @param string $apiBasePath API-Basispfad (Standard: /v1)
     */
    public function __construct(
        ILogger $logger,
        string $apiEndpoint = 'api.vgnc.org',
        int $apiPort = 443,
        string $apiBasePath = '/v1'
    ) {
        $this->logger = $logger;
        $this->apiEndpoint = $apiEndpoint;
        $this->apiPort = $apiPort;
        $this->apiBasePath = $apiBasePath;
        
        // Standard-Port für HTTP/HTTPS
        $protocol = ($apiPort === 443) ? 'https' : 'http';
        
        // Basis-URL für API-Anfragen
        $baseUrl = $protocol . '://' . $apiEndpoint;
        if ($apiPort !== 80 && $apiPort !== 443) {
            $baseUrl .= ':' . $apiPort;
        }
        $baseUrl .= $apiBasePath;
        
        // HTTP-Client initialisieren
        $this->httpClient = new Client([
            'base_uri' => $baseUrl,
            'timeout' => 10,
            'verify' => false // In Produktionsumgebung auf true setzen!
        ]);
    }
    
    /**
     * GET-Anfrage an die API senden
     * 
     * @param string $endpoint API-Endpoint (z.B. /devices)
     * @param array $queryParams Query-Parameter
     * @param array $headers Zusätzliche HTTP-Header
     * @return array Antwort als Array
     * @throws Exception Bei Fehlern
     */
    public function get(string $endpoint, array $queryParams = [], array $headers = []): array {
        try {
            $response = $this->httpClient->get($endpoint, [
                'query' => $queryParams,
                'headers' => $headers
            ]);
            
            $body = (string) $response->getBody();
            $data = json_decode($body, true);
            
            if (json_last_error() !== JSON_ERROR_NONE) {
                throw new Exception('Ungültige JSON-Antwort: ' . json_last_error_msg());
            }
            
            return $data;
        } catch (Exception $e) {
            $this->logger->error('SwissAirDry API-Fehler (GET ' . $endpoint . '): ' . $e->getMessage(), [
                'app' => 'swissairdry'
            ]);
            throw new Exception('API-Anfrage fehlgeschlagen: ' . $e->getMessage());
        }
    }
    
    /**
     * POST-Anfrage an die API senden
     * 
     * @param string $endpoint API-Endpoint (z.B. /devices)
     * @param array|null $data POST-Daten
     * @param array $headers Zusätzliche HTTP-Header
     * @return array Antwort als Array
     * @throws Exception Bei Fehlern
     */
    public function post(string $endpoint, ?array $data = null, array $headers = []): array {
        try {
            $options = ['headers' => $headers];
            
            if ($data !== null) {
                $options['json'] = $data;
            }
            
            $response = $this->httpClient->post($endpoint, $options);
            
            $body = (string) $response->getBody();
            $responseData = json_decode($body, true);
            
            if (json_last_error() !== JSON_ERROR_NONE) {
                throw new Exception('Ungültige JSON-Antwort: ' . json_last_error_msg());
            }
            
            return $responseData;
        } catch (Exception $e) {
            $this->logger->error('SwissAirDry API-Fehler (POST ' . $endpoint . '): ' . $e->getMessage(), [
                'app' => 'swissairdry'
            ]);
            throw new Exception('API-Anfrage fehlgeschlagen: ' . $e->getMessage());
        }
    }
    
    /**
     * PUT-Anfrage an die API senden
     * 
     * @param string $endpoint API-Endpoint (z.B. /devices/123)
     * @param array|null $data PUT-Daten
     * @param array $headers Zusätzliche HTTP-Header
     * @return array Antwort als Array
     * @throws Exception Bei Fehlern
     */
    public function put(string $endpoint, ?array $data = null, array $headers = []): array {
        try {
            $options = ['headers' => $headers];
            
            if ($data !== null) {
                $options['json'] = $data;
            }
            
            $response = $this->httpClient->put($endpoint, $options);
            
            $body = (string) $response->getBody();
            $responseData = json_decode($body, true);
            
            if (json_last_error() !== JSON_ERROR_NONE) {
                throw new Exception('Ungültige JSON-Antwort: ' . json_last_error_msg());
            }
            
            return $responseData;
        } catch (Exception $e) {
            $this->logger->error('SwissAirDry API-Fehler (PUT ' . $endpoint . '): ' . $e->getMessage(), [
                'app' => 'swissairdry'
            ]);
            throw new Exception('API-Anfrage fehlgeschlagen: ' . $e->getMessage());
        }
    }
    
    /**
     * DELETE-Anfrage an die API senden
     * 
     * @param string $endpoint API-Endpoint (z.B. /devices/123)
     * @param array $headers Zusätzliche HTTP-Header
     * @return array Antwort als Array
     * @throws Exception Bei Fehlern
     */
    public function delete(string $endpoint, array $headers = []): array {
        try {
            $response = $this->httpClient->delete($endpoint, [
                'headers' => $headers
            ]);
            
            $body = (string) $response->getBody();
            $responseData = json_decode($body, true);
            
            if (json_last_error() !== JSON_ERROR_NONE) {
                throw new Exception('Ungültige JSON-Antwort: ' . json_last_error_msg());
            }
            
            return $responseData;
        } catch (Exception $e) {
            $this->logger->error('SwissAirDry API-Fehler (DELETE ' . $endpoint . '): ' . $e->getMessage(), [
                'app' => 'swissairdry'
            ]);
            throw new Exception('API-Anfrage fehlgeschlagen: ' . $e->getMessage());
        }
    }
    
    /**
     * Überprüft die Verbindung zur API
     * 
     * @return bool True, wenn die Verbindung erfolgreich ist, sonst false
     */
    public function checkConnection(): bool {
        try {
            // Root-Endpunkt der API abfragen
            $this->get('/');
            return true;
        } catch (Exception $e) {
            return false;
        }
    }
}