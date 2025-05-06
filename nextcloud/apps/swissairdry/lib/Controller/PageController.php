<?php
declare(strict_types=1);

namespace OCA\SwissAirDry\Controller;

use OCP\IRequest;
use OCP\AppFramework\Http\TemplateResponse;
use OCP\AppFramework\Controller;
use OCP\Util;
use OCP\IConfig;
use OCA\SwissAirDry\AppInfo\Application;

class PageController extends Controller {
    /** @var IConfig */
    private $config;

    /** @var string */
    private $userId;

    public function __construct(
        string $appName,
        IRequest $request,
        IConfig $config,
        $userId
    ) {
        parent::__construct($appName, $request);
        $this->config = $config;
        $this->userId = $userId;
    }

    /**
     * @NoAdminRequired
     * @NoCSRFRequired
     */
    public function index() {
        Util::addScript('swissairdry', 'main');
        Util::addStyle('swissairdry', 'style');

        $appConfig = json_decode(
            $this->config->getAppValue(Application::APP_ID, 'app_config', '{}'),
            true
        );

        $params = [
            'app_id' => Application::APP_ID,
            'api_url' => $appConfig['api_url'] ?? 'http://localhost:5000',
            'mqtt' => $appConfig['mqtt'] ?? [
                'broker' => 'localhost',
                'port' => 1883,
                'ws_port' => 9001,
            ],
            'user_id' => $this->userId,
        ];

        return new TemplateResponse('swissairdry', 'index', $params);
    }

    /**
     * @NoAdminRequired
     * @NoCSRFRequired
     */
    public function devices() {
        Util::addScript('swissairdry', 'devices');
        Util::addStyle('swissairdry', 'style');

        return new TemplateResponse('swissairdry', 'devices');
    }

    /**
     * @NoAdminRequired
     * @NoCSRFRequired
     */
    public function settings() {
        Util::addScript('swissairdry', 'settings');
        Util::addStyle('swissairdry', 'style');

        return new TemplateResponse('swissairdry', 'settings');
    }
}