<?php
declare(strict_types=1);

namespace OCA\SwissAirDry\Controller;

use OCA\SwissAirDry\Service\SettingsService;
use OCP\AppFramework\Controller;
use OCP\AppFramework\Http;
use OCP\AppFramework\Http\JSONResponse;
use OCP\IRequest;

class SettingsController extends Controller {
    /** @var string */
    private $userId;
    
    /** @var SettingsService */
    private $settingsService;

    public function __construct(
        string $appName,
        IRequest $request,
        ?string $userId,
        SettingsService $settingsService
    ) {
        parent::__construct($appName, $request);
        $this->userId = $userId;
        $this->settingsService = $settingsService;
    }

    /**
     * @NoAdminRequired
     * @NoCSRFRequired
     */
    public function get(): JSONResponse {
        try {
            $settings = $this->settingsService->getSettings($this->userId);
            return new JSONResponse($settings);
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
    public function update(): JSONResponse {
        try {
            $data = $this->request->getParams();
            $updatedSettings = $this->settingsService->updateSettings($this->userId, $data);
            return new JSONResponse($updatedSettings);
        } catch (\Exception $e) {
            return new JSONResponse(
                ['error' => $e->getMessage()],
                Http::STATUS_INTERNAL_SERVER_ERROR
            );
        }
    }
}