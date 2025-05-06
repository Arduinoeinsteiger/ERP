<?php
declare(strict_types=1);

namespace OCA\SwissAirDry\Controller;

use OCA\SwissAirDry\Service\MqttService;
use OCA\SwissAirDry\Service\SettingsService;
use OCP\AppFramework\Controller;
use OCP\AppFramework\Http;
use OCP\AppFramework\Http\JSONResponse;
use OCP\IRequest;

class MqttController extends Controller {
    /** @var string */
    private $userId;
    
    /** @var MqttService */
    private $mqttService;
    
    /** @var SettingsService */
    private $settingsService;

    public function __construct(
        string $appName,
        IRequest $request,
        ?string $userId,
        MqttService $mqttService,
        SettingsService $settingsService
    ) {
        parent::__construct($appName, $request);
        $this->userId = $userId;
        $this->mqttService = $mqttService;
        $this->settingsService = $settingsService;
    }

    /**
     * @NoAdminRequired
     * @NoCSRFRequired
     */
    public function publish(): JSONResponse {
        try {
            $params = $this->request->getParams();
            
            if (!isset($params['topic']) || !isset($params['payload'])) {
                return new JSONResponse(
                    ['error' => 'Missing required parameters: topic, payload'],
                    Http::STATUS_BAD_REQUEST
                );
            }
            
            $topic = $params['topic'];
            $payload = $params['payload'];
            $qos = $params['qos'] ?? 0;
            $retain = $params['retain'] ?? false;
            
            $result = $this->mqttService->publish($topic, $payload, $qos, $retain);
            
            return new JSONResponse([
                'success' => $result,
                'topic' => $topic
            ]);
        } catch (\Exception $e) {
            return new JSONResponse(
                ['error' => $e->getMessage()],
                Http::STATUS_INTERNAL_SERVER_ERROR
            );
        }
    }
    
    /**
     * @NoAdminRequired
     * @NoCSRFRequired
     */
    public function status(): JSONResponse {
        try {
            $status = $this->mqttService->getStatus();
            
            return new JSONResponse([
                'connected' => $status['connected'],
                'broker' => $status['broker'],
                'port' => $status['port'],
                'lastError' => $status['lastError'] ?? null
            ]);
        } catch (\Exception $e) {
            return new JSONResponse(
                ['error' => $e->getMessage()],
                Http::STATUS_INTERNAL_SERVER_ERROR
            );
        }
    }
}