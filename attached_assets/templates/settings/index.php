<div id="app-settings">
    <div id="app-settings-header">
        <button class="settings-button" data-apps-slide-toggle="#app-settings-content">
            <?php p($l->t('Einstellungen')); ?>
        </button>
    </div>
    <div id="app-settings-content">
        <div class="settings-section">
            <h3><?php p($l->t('API-Verbindung')); ?></h3>
            <div class="settings-item">
                <label for="swissairdry-api-endpoint"><?php p($l->t('API-Endpunkt')); ?></label>
                <input type="text" id="swissairdry-api-endpoint" 
                       value="<?php p($_['apiEndpoint']); ?>" 
                       placeholder="api.vgnc.org" />
            </div>
            <div class="settings-item">
                <label for="swissairdry-api-port"><?php p($l->t('API-Port')); ?></label>
                <input type="number" id="swissairdry-api-port" 
                       value="<?php p($_['apiPort']); ?>" 
                       placeholder="443" min="1" max="65535" />
            </div>
            <div class="settings-item">
                <label for="swissairdry-api-basepath"><?php p($l->t('API-Basispfad')); ?></label>
                <input type="text" id="swissairdry-api-basepath" 
                       value="<?php p($_['apiBasePath']); ?>" 
                       placeholder="/v1" />
            </div>
        </div>
        
        <div class="settings-section">
            <h3><?php p($l->t('MQTT-Verbindung')); ?></h3>
            <div class="settings-item">
                <label for="swissairdry-mqtt-broker"><?php p($l->t('MQTT-Broker')); ?></label>
                <input type="text" id="swissairdry-mqtt-broker" 
                       value="<?php p($_['mqttBroker']); ?>" 
                       placeholder="mqtt.vgnc.org" />
            </div>
            <div class="settings-item">
                <label for="swissairdry-mqtt-port"><?php p($l->t('MQTT-Port')); ?></label>
                <input type="number" id="swissairdry-mqtt-port" 
                       value="<?php p($_['mqttPort']); ?>" 
                       placeholder="8883" min="1" max="65535" />
            </div>
        </div>
        
        <div class="settings-section">
            <h3><?php p($l->t('Darstellung')); ?></h3>
            <div class="settings-item">
                <input type="checkbox" id="swissairdry-dark-mode" 
                       <?php if ($_['darkMode']) { p('checked'); } ?> />
                <label for="swissairdry-dark-mode"><?php p($l->t('Dunkelmodus')); ?></label>
            </div>
            <div class="settings-item">
                <input type="checkbox" id="swissairdry-notifications" 
                       <?php if ($_['notifications']) { p('checked'); } ?> />
                <label for="swissairdry-notifications"><?php p($l->t('Benachrichtigungen')); ?></label>
            </div>
        </div>
        
        <div class="settings-section">
            <button id="swissairdry-save-settings" class="primary">
                <?php p($l->t('Speichern')); ?>
            </button>
        </div>
    </div>
</div>