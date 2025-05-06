<?php
script('swissairdry', 'swissairdry-settings');
style('swissairdry', 'style');
?>

<div id="swissairdry-app" class="app-swissairdry">
    <div id="app-navigation">
        <?php print_unescaped($this->inc('navigation/index')); ?>
        <?php print_unescaped($this->inc('settings/index')); ?>
    </div>

    <div id="app-content">
        <div id="app-content-wrapper">
            <div class="section">
                <h2><?php p($l->t('Einstellungen')); ?></h2>
                
                <div class="settings-container">
                    <div class="settings-group">
                        <h3><?php p($l->t('API-Verbindung')); ?></h3>
                        <div class="settings-item">
                            <label for="settings-api-endpoint"><?php p($l->t('API-Endpunkt')); ?></label>
                            <input type="text" id="settings-api-endpoint" 
                                   value="<?php p($_['settings']['apiEndpoint'] ?? 'api.vgnc.org'); ?>" 
                                   placeholder="api.vgnc.org" />
                            <div class="settings-hint">
                                <?php p($l->t('Hostname oder IP-Adresse des SwissAirDry API-Servers')); ?>
                            </div>
                        </div>
                        
                        <div class="settings-item">
                            <label for="settings-api-port"><?php p($l->t('API-Port')); ?></label>
                            <input type="number" id="settings-api-port" 
                                   value="<?php p($_['settings']['apiPort'] ?? '443'); ?>" 
                                   placeholder="443" min="1" max="65535" />
                            <div class="settings-hint">
                                <?php p($l->t('Port des API-Servers (Standard: 443 für HTTPS, 80 für HTTP)')); ?>
                            </div>
                        </div>
                        
                        <div class="settings-item">
                            <label for="settings-api-basepath"><?php p($l->t('API-Basispfad')); ?></label>
                            <input type="text" id="settings-api-basepath" 
                                   value="<?php p($_['settings']['apiBasePath'] ?? '/v1'); ?>" 
                                   placeholder="/v1" />
                            <div class="settings-hint">
                                <?php p($l->t('Basispfad der API (z.B. /v1, /api)')); ?>
                            </div>
                        </div>
                        
                        <div class="settings-item">
                            <button id="test-api-connection" class="button">
                                <?php p($l->t('Verbindung testen')); ?>
                            </button>
                            <span id="api-connection-status"></span>
                        </div>
                    </div>
                    
                    <div class="settings-group">
                        <h3><?php p($l->t('MQTT-Verbindung')); ?></h3>
                        <div class="settings-item">
                            <label for="settings-mqtt-broker"><?php p($l->t('MQTT-Broker')); ?></label>
                            <input type="text" id="settings-mqtt-broker" 
                                   value="<?php p($_['settings']['mqttBroker'] ?? 'mqtt.vgnc.org'); ?>" 
                                   placeholder="mqtt.vgnc.org" />
                            <div class="settings-hint">
                                <?php p($l->t('Hostname oder IP-Adresse des MQTT-Brokers')); ?>
                            </div>
                        </div>
                        
                        <div class="settings-item">
                            <label for="settings-mqtt-port"><?php p($l->t('MQTT-Port')); ?></label>
                            <input type="number" id="settings-mqtt-port" 
                                   value="<?php p($_['settings']['mqttPort'] ?? '8883'); ?>" 
                                   placeholder="8883" min="1" max="65535" />
                            <div class="settings-hint">
                                <?php p($l->t('Port des MQTT-Brokers (Standard: 8883 für sicheres MQTT, 1883 für unverschlüsselt)')); ?>
                            </div>
                        </div>
                        
                        <div class="settings-item">
                            <input type="checkbox" id="settings-mqtt-secure" 
                                   <?php if ($_['settings']['mqttSecure'] ?? true) { p('checked'); } ?> />
                            <label for="settings-mqtt-secure"><?php p($l->t('Sichere Verbindung (TLS/SSL) verwenden')); ?></label>
                        </div>
                        
                        <div class="settings-item">
                            <button id="test-mqtt-connection" class="button">
                                <?php p($l->t('Verbindung testen')); ?>
                            </button>
                            <span id="mqtt-connection-status"></span>
                        </div>
                    </div>
                    
                    <div class="settings-group">
                        <h3><?php p($l->t('Dashboard')); ?></h3>
                        <div class="settings-item">
                            <label for="settings-refresh-interval"><?php p($l->t('Aktualisierungsintervall (Sekunden)')); ?></label>
                            <input type="number" id="settings-refresh-interval" 
                                   value="<?php p($_['settings']['refreshInterval'] ?? '30'); ?>" 
                                   placeholder="30" min="0" max="3600" />
                            <div class="settings-hint">
                                <?php p($l->t('Intervall für die automatische Aktualisierung der Daten (0 = deaktiviert)')); ?>
                            </div>
                        </div>
                        
                        <div class="settings-item">
                            <input type="checkbox" id="settings-dark-mode" 
                                   <?php if ($_['settings']['darkMode'] ?? false) { p('checked'); } ?> />
                            <label for="settings-dark-mode"><?php p($l->t('Dunkelmodus')); ?></label>
                        </div>
                        
                        <div class="settings-item">
                            <input type="checkbox" id="settings-notifications" 
                                   <?php if ($_['settings']['notifications'] ?? true) { p('checked'); } ?> />
                            <label for="settings-notifications"><?php p($l->t('Benachrichtigungen anzeigen')); ?></label>
                        </div>
                    </div>
                    
                    <div class="settings-actions">
                        <button id="save-settings" class="button primary">
                            <?php p($l->t('Einstellungen speichern')); ?>
                        </button>
                        <button id="reset-settings" class="button">
                            <?php p($l->t('Auf Standardwerte zurücksetzen')); ?>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>