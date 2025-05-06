<?php
script('swissairdry', 'swissairdry-main');
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
                <h2><?php p($l->t('Swiss Air Dry')); ?></h2>
                <div class="dashboard-container">
                    <div class="dashboard-header">
                        <div class="api-status">
                            <span class="status-label"><?php p($l->t('API-Status:')); ?></span>
                            <span class="status-indicator" id="api-status-indicator"></span>
                            <span class="status-text" id="api-status-text"><?php p($l->t('Prüfe...')); ?></span>
                        </div>
                        <div class="refresh-controls">
                            <button id="refresh-btn" class="refresh-button">
                                <span class="icon-refresh"></span>
                                <?php p($l->t('Aktualisieren')); ?>
                            </button>
                            <select id="refresh-interval" class="refresh-interval">
                                <option value="0"><?php p($l->t('Manuell')); ?></option>
                                <option value="10"><?php p($l->t('10 Sekunden')); ?></option>
                                <option value="30" selected><?php p($l->t('30 Sekunden')); ?></option>
                                <option value="60"><?php p($l->t('1 Minute')); ?></option>
                                <option value="300"><?php p($l->t('5 Minuten')); ?></option>
                            </select>
                        </div>
                    </div>

                    <div id="dashboard-tiles" class="dashboard-tiles">
                        <div class="tile loading">
                            <div class="icon-loading"></div>
                            <span><?php p($l->t('Lade Daten...')); ?></span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>