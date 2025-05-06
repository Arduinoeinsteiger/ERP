<?php
declare(strict_types=1);

namespace OCA\SwissAirDry\Controller;

use OCA\SwissAirDry\Service\ApiService;
use OCA\SwissAirDry\Service\DeviceService;
use OCP\AppFramework\Controller;
use OCP\AppFramework\Http;
use OCP\AppFramework\Http\JSONResponse;
use OCP\IRequest;

class ApiController extends Controller {
    /** @var string */
    private $userId;
    
    /** @var ApiService */
    private $apiService;
    
    /** @var DeviceService */
    private $deviceService;

    public function __construct(
        string $appName,
        IRequest $request,
        ?string $userId,
        ApiService $apiService,
        DeviceService $deviceService
    ) {
        parent::__construct($appName, $request);
        $this->userId = $userId;
        $this->apiService = $apiService;
        $this->deviceService = $deviceService;
    }

    /**
     * @NoAdminRequired
     * @NoCSRFRequired
     */
    public function getDevices(): JSONResponse {
        try {
            $devices = $this->deviceService->getDevices($this->userId);
            return new JSONResponse($devices);
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
    public function getDevice(string $id): JSONResponse {
        try {
            $device = $this->deviceService->getDevice($this->userId, $id);
            if (!$device) {
                return new JSONResponse(
                    ['error' => 'Device not found'],
                    Http::STATUS_NOT_FOUND
                );
            }
            return new JSONResponse($device);
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
    public function updateDevice(string $id): JSONResponse {
        try {
            $data = $this->request->getParams();
            $device = $this->deviceService->updateDevice($this->userId, $id, $data);
            return new JSONResponse($device);
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
    public function sendCommand(string $id): JSONResponse {
        try {
            $data = $this->request->getParams();
            $result = $this->deviceService->sendCommand($this->userId, $id, $data);
            return new JSONResponse($result);
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
    public function getDeviceData(string $id): JSONResponse {
        try {
            $data = $this->deviceService->getDeviceData($this->userId, $id);
            return new JSONResponse($data);
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
    public function getDeviceLocation(string $id): JSONResponse {
        try {
            $location = $this->deviceService->getDeviceLocation($this->userId, $id);
            return new JSONResponse($location);
        } catch (\Exception $e) {
            return new JSONResponse(
                ['error' => $e->getMessage()],
                Http::STATUS_INTERNAL_SERVER_ERROR
            );
        }
    }
}