<?php
declare(strict_types=1);

namespace OCA\SwissAirDry\AppInfo;

use OCP\AppFramework\App;
use OCP\AppFramework\Bootstrap\IBootstrap;
use OCP\AppFramework\Bootstrap\IRegistrationContext;
use OCP\AppFramework\Bootstrap\IBootContext;
use OCP\IConfig;

/**
 * Class Application
 *
 * @package OCA\SwissAirDry\AppInfo
 */
class Application extends App implements IBootstrap {
    public const APP_ID = 'swissairdry';

    public function __construct() {
        parent::__construct(self::APP_ID);
    }

    public function register(IRegistrationContext $context): void {
        // Register App API callbacks
        
        // This app is an External App, which means most of the functionality
        // is handled by a separate Docker container (ExApp)
    }

    public function boot(IBootContext $context): void {
        // Get server container
        $serverContainer = $context->getServerContainer();
        
        // Get config service
        $config = $serverContainer->get(IConfig::class);
        
        // Set up default configuration if needed
        $appConfig = $config->getAppValue(self::APP_ID, 'app_config', '');
        if (empty($appConfig)) {
            $defaultConfig = json_encode([
                'api_url' => 'http://localhost:5000',
                'mqtt' => [
                    'broker' => 'localhost',
                    'port' => 1883,
                    'ws_port' => 9001,
                ]
            ]);
            $config->setAppValue(self::APP_ID, 'app_config', $defaultConfig);
        }
    }
}