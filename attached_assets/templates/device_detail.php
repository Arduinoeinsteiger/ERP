<?php
script('swissairdry', 'swissairdry-device-detail');
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
                <div class="device-header">
                    <div class="device-header-left">
                        <a href="<?php p(\OC::$server->getURLGenerator()->linkToRoute('swissairdry.page.devices')); ?>" class="button">
                            <span class="icon-arrow-left"></span>
                            <?php p($l->t('Zurück')); ?>
                        </a>
                    </div>
                    <h2 id="device-name">
                        <?php p(isset($_['device']['name']) ? $_['device']['name'] : ($_['device']['id'] ?? $l->t('Gerät'))); ?>
                    </h2>
                    <div class="device-header-right">
                        <button id="refresh-device-btn" class="button">
                            <span class="icon-refresh"></span>
                            <?php p($l->t('Aktualisieren')); ?>
                        </button>
                    </div>
                </div>
                
                <div class="device-status-bar">
                    <div class="device-status" id="device-status">
                        <div class="device-status-indicator"></div>
                        <span class="device-status-text"><?php p($l->t('Lade Status...')); ?></span>
                    </div>
                    
                    <div class="device-info-tags">
                        <div class="device-tag" id="device-id-tag">
                            <span class="tag-label"><?php p($l->t('ID:')); ?></span>
                            <span class="tag-value"><?php p($_['device']['id'] ?? ''); ?></span>
                        </div>
                        
                        <div class="device-tag" id="device-type-tag">
                            <span class="tag-label"><?php p($l->t('Typ:')); ?></span>
                            <span class="tag-value"><?php p($_['device']['type'] ?? $l->t('Unbekannt')); ?></span>
                        </div>
                        
                        <div class="device-tag" id="device-last-seen-tag">
                            <span class="tag-label"><?php p($l->t('Zuletzt gesehen:')); ?></span>
                            <span class="tag-value" id="device-last-seen"><?php p($l->t('Lade...')); ?></span>
                        </div>
                    </div>
                </div>
                
                <div class="device-detail-container">
                    <div class="device-control-panel">
                        <div class="control-section">
                            <h3><?php p($l->t('Steuerung')); ?></h3>
                            <div class="control-buttons">
                                <button id="device-toggle-btn" class="button primary">
                                    <span class="icon-toggle-on"></span>
                                    <span id="toggle-btn-text"><?php p($l->t('Einschalten')); ?></span>
                                </button>
                                
                                <button id="device-restart-btn" class="button">
                                    <span class="icon-history"></span>
                                    <?php p($l->t('Neustart')); ?>
                                </button>
                                
                                <button id="device-locate-btn" class="button">
                                    <span class="icon-location"></span>
                                    <?php p($l->t('Lokalisieren')); ?>
                                </button>
                            </div>
                        </div>
                        
                        <div class="control-section">
                            <h3><?php p($l->t('Geräteinformationen')); ?></h3>
                            <div class="device-properties" id="device-properties">
                                <div class="property-row">
                                    <span class="property-label"><?php p($l->t('Firmware:')); ?></span>
                                    <span class="property-value" id="device-firmware"><?php p($l->t('Lade...')); ?></span>
                                </div>
                                <div class="property-row">
                                    <span class="property-label"><?php p($l->t('IP-Adresse:')); ?></span>
                                    <span class="property-value" id="device-ip"><?php p($l->t('Lade...')); ?></span>
                                </div>
                                <div class="property-row">
                                    <span class="property-label"><?php p($l->t('MAC-Adresse:')); ?></span>
                                    <span class="property-value" id="device-mac"><?php p($l->t('Lade...')); ?></span>
                                </div>
                                <div class="property-row">
                                    <span class="property-label"><?php p($l->t('WLAN-Stärke:')); ?></span>
                                    <span class="property-value" id="device-wifi-strength"><?php p($l->t('Lade...')); ?></span>
                                </div>
                                <div class="property-row">
                                    <span class="property-label"><?php p($l->t('Laufzeit:')); ?></span>
                                    <span class="property-value" id="device-runtime"><?php p($l->t('Lade...')); ?></span>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="device-data-panel">
                        <div class="tabs-container">
                            <div class="tabs-header">
                                <button class="tab-btn active" data-tab="sensor-data"><?php p($l->t('Sensordaten')); ?></button>
                                <button class="tab-btn" data-tab="energy-data"><?php p($l->t('Energie')); ?></button>
                                <button class="tab-btn" data-tab="location-data"><?php p($l->t('Standort')); ?></button>
                                <button class="tab-btn" data-tab="logs"><?php p($l->t('Protokolle')); ?></button>
                            </div>
                            
                            <div class="tabs-content">
                                <div class="tab-panel active" id="sensor-data">
                                    <div class="device-charts">
                                        <div class="chart-container">
                                            <h3><?php p($l->t('Temperatur')); ?></h3>
                                            <div class="chart" id="temperature-chart">
                                                <div class="chart-loading">
                                                    <div class="icon-loading"></div>
                                                    <span><?php p($l->t('Lade Diagramm...')); ?></span>
                                                </div>
                                            </div>
                                        </div>
                                        
                                        <div class="chart-container">
                                            <h3><?php p($l->t('Luftfeuchtigkeit')); ?></h3>
                                            <div class="chart" id="humidity-chart">
                                                <div class="chart-loading">
                                                    <div class="icon-loading"></div>
                                                    <span><?php p($l->t('Lade Diagramm...')); ?></span>
                                                </div>
                                            </div>
                                        </div>
                                        
                                        <div class="chart-container">
                                            <h3><?php p($l->t('Druck')); ?></h3>
                                            <div class="chart" id="pressure-chart">
                                                <div class="chart-loading">
                                                    <div class="icon-loading"></div>
                                                    <span><?php p($l->t('Lade Diagramm...')); ?></span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="tab-panel" id="energy-data">
                                    <div class="device-charts">
                                        <div class="chart-container">
                                            <h3><?php p($l->t('Leistung')); ?></h3>
                                            <div class="chart" id="power-chart">
                                                <div class="chart-loading">
                                                    <div class="icon-loading"></div>
                                                    <span><?php p($l->t('Lade Diagramm...')); ?></span>
                                                </div>
                                            </div>
                                        </div>
                                        
                                        <div class="chart-container">
                                            <h3><?php p($l->t('Energieverbrauch')); ?></h3>
                                            <div class="chart" id="energy-chart">
                                                <div class="chart-loading">
                                                    <div class="icon-loading"></div>
                                                    <span><?php p($l->t('Lade Diagramm...')); ?></span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <div class="energy-summary">
                                        <div class="summary-card">
                                            <div class="summary-title"><?php p($l->t('Gesamt')); ?></div>
                                            <div class="summary-value" id="total-energy"><?php p($l->t('Lade...')); ?></div>
                                            <div class="summary-label"><?php p($l->t('kWh')); ?></div>
                                        </div>
                                        
                                        <div class="summary-card">
                                            <div class="summary-title"><?php p($l->t('Aktuell')); ?></div>
                                            <div class="summary-value" id="current-power"><?php p($l->t('Lade...')); ?></div>
                                            <div class="summary-label"><?php p($l->t('Watt')); ?></div>
                                        </div>
                                        
                                        <div class="summary-card">
                                            <div class="summary-title"><?php p($l->t('Kosten')); ?></div>
                                            <div class="summary-value" id="energy-cost"><?php p($l->t('Lade...')); ?></div>
                                            <div class="summary-label"><?php p($l->t('CHF')); ?></div>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="tab-panel" id="location-data">
                                    <div id="device-map" class="device-map">
                                        <div class="map-loading">
                                            <div class="icon-loading"></div>
                                            <span><?php p($l->t('Lade Karte...')); ?></span>
                                        </div>
                                    </div>
                                    
                                    <div class="location-details">
                                        <div class="location-property">
                                            <span class="property-label"><?php p($l->t('Letzte Position:')); ?></span>
                                            <span class="property-value" id="last-position"><?php p($l->t('Lade...')); ?></span>
                                        </div>
                                        
                                        <div class="location-property">
                                            <span class="property-label"><?php p($l->t('Aktualisiert:')); ?></span>
                                            <span class="property-value" id="location-updated"><?php p($l->t('Lade...')); ?></span>
                                        </div>
                                        
                                        <div class="location-property">
                                            <span class="property-label"><?php p($l->t('Genauigkeit:')); ?></span>
                                            <span class="property-value" id="location-accuracy"><?php p($l->t('Lade...')); ?></span>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="tab-panel" id="logs">
                                    <div class="logs-filter">
                                        <div class="filter-group">
                                            <label for="log-level"><?php p($l->t('Level:')); ?></label>
                                            <select id="log-level">
                                                <option value="all"><?php p($l->t('Alle')); ?></option>
                                                <option value="info"><?php p($l->t('Info')); ?></option>
                                                <option value="warning"><?php p($l->t('Warnung')); ?></option>
                                                <option value="error"><?php p($l->t('Fehler')); ?></option>
                                            </select>
                                        </div>
                                        
                                        <div class="filter-group">
                                            <label for="log-search"><?php p($l->t('Suche:')); ?></label>
                                            <input type="text" id="log-search" placeholder="<?php p($l->t('Suchbegriff...')); ?>">
                                        </div>
                                        
                                        <button id="refresh-logs-btn" class="button">
                                            <span class="icon-refresh"></span>
                                            <?php p($l->t('Aktualisieren')); ?>
                                        </button>
                                    </div>
                                    
                                    <div class="logs-container" id="device-logs">
                                        <div class="logs-loading">
                                            <div class="icon-loading"></div>
                                            <span><?php p($l->t('Lade Protokolle...')); ?></span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>