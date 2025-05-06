<?php
declare(strict_types=1);

namespace OCA\SwissAirDry\Controller;

use OCA\SwissAirDry\Service\ApiService;
use OCA\SwissAirDry\Service\DeviceService;
use OCA\SwissAirDry\Service\SettingsService;
use OCP\AppFramework\Controller;
use OCP\AppFramework\Http\TemplateResponse;
use OCP\IRequest;
use OCP\Util;

class PageController extends Controller {
    /** @var string */
    private $userId;
    
    /** @var ApiService */
    private $apiService;
    
    /** @var DeviceService */
    private $deviceService;
    
    /** @var SettingsService */
    private $settingsService;

    public function __construct(
        string $appName,
        IRequest $request,
        ?string $userId,
        ApiService $apiService,
        DeviceService $deviceService,
        SettingsService $settingsService
    ) {
        parent::__construct($appName, $request);
        $this->userId = $userId;
        $this->apiService = $apiService;
        $this->deviceService = $deviceService;
        $this->settingsService = $settingsService;
    }

    /**
     * @NoAdminRequired
     * @NoCSRFRequired
     */
    public function index(): TemplateResponse {
        Util::addScript($this->appName, 'swissairdry-main');
        Util::addStyle($this->appName, 'style');
        
        $settings = $this->settingsService->getSettings($this->userId);
        
        return new TemplateResponse(
            $this->appName,
            'index',
            [
                'user' => $this->userId,
                'apiEndpoint' => $settings['apiEndpoint'] ?? 'api.vgnc.org',
                'apiPort' => $settings['apiPort'] ?? 443,
                'apiBasePath' => $settings['apiBasePath'] ?? '/v1',
                'mqttBroker' => $settings['mqttBroker'] ?? 'mqtt.vgnc.org',
                'mqttPort' => $settings['mqttPort'] ?? 8883
            ]
        );
    }
    
    /**
     * @NoAdminRequired
     * @NoCSRFRequired
     */
    public function dashboard(): TemplateResponse {
        Util::addScript($this->appName, 'swissairdry-dashboard');
        Util::addStyle($this->appName, 'style');
        
        $devices = $this->deviceService->getDevices($this->userId);
        
        return new TemplateResponse(
            $this->appName,
            'dashboard',
            [
                'user' => $this->userId,
                'devices' => $devices
            ]
        );
    }
    
    /**
     * @NoAdminRequired
     * @NoCSRFRequired
     */
    public function devices(): TemplateResponse {
        Util::addScript($this->appName, 'swissairdry-devices');
        Util::addStyle($this->appName, 'style');
        
        $devices = $this->deviceService->getDevices($this->userId);
        
        return new TemplateResponse(
            $this->appName,
            'devices',
            [
                'user' => $this->userId,
                'devices' => $devices
            ]
        );
    }
    
    /**
     * @NoAdminRequired
     * @NoCSRFRequired
     */
    public function deviceDetail(string $id): TemplateResponse {
        Util::addScript($this->appName, 'swissairdry-device-detail');
        Util::addStyle($this->appName, 'style');
        
        $device = $this->deviceService->getDevice($this->userId, $id);
        $deviceData = $this->deviceService->getDeviceData($this->userId, $id);
        
        return new TemplateResponse(
            $this->appName,
            'device_detail',
            [
                'user' => $this->userId,
                'device' => $device,
                'deviceData' => $deviceData
            ]
        );
    }
    
    /**
     * @NoAdminRequired
     * @NoCSRFRequired
     */
    public function map(): TemplateResponse {
        Util::addScript($this->appName, 'swissairdry-map');
        Util::addStyle($this->appName, 'style');
        Util::addStyle($this->appName, 'map');
        
        $devices = $this->deviceService->getDevices($this->userId);
        $locations = $this->deviceService->getDeviceLocations($this->userId);
        
        return new TemplateResponse(
            $this->appName,
            'map',
            [
                'user' => $this->userId,
                'devices' => $devices,
                'locations' => $locations
            ]
        );
    }
    
    /**
     * @NoAdminRequired
     * @NoCSRFRequired
     */
    public function settings(): TemplateResponse {
        Util::addScript($this->appName, 'swissairdry-settings');
        Util::addStyle($this->appName, 'style');
        
        $settings = $this->settingsService->getSettings($this->userId);
        
        return new TemplateResponse(
            $this->appName,
            'settings',
            [
                'user' => $this->userId,
                'settings' => $settings
            ]
        );
    }
}