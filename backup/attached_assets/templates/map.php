<?php
script('swissairdry', 'swissairdry-map');
style('swissairdry', 'style');
style('swissairdry', 'map');
?>

<div id="swissairdry-app" class="app-swissairdry">
    <div id="app-navigation">
        <?php print_unescaped($this->inc('navigation/index')); ?>
        <?php print_unescaped($this->inc('settings/index')); ?>
    </div>

    <div id="app-content">
        <div id="app-content-wrapper">
            <div class="section">
                <div class="section-header">
                    <h2><?php p($l->t('Gerätestandorte')); ?></h2>
                    <div class="section-actions">
                        <button id="refresh-map-btn" class="button">
                            <span class="icon-refresh"></span>
                            <?php p($l->t('Aktualisieren')); ?>
                        </button>
                    </div>
                </div>
                
                <div class="map-container">
                    <div id="devices-map" class="devices-map">
                        <div class="map-loading">
                            <div class="icon-loading"></div>
                            <span><?php p($l->t('Lade Karte...')); ?></span>
                        </div>
                    </div>
                    
                    <div class="map-sidebar">
                        <h3><?php p($l->t('Geräteliste')); ?></h3>
                        <div class="map-device-filter">
                            <input type="text" id="map-device-filter" placeholder="<?php p($l->t('Filtern...')); ?>">
                        </div>
                        
                        <div class="map-device-list" id="map-device-list">
                            <div class="loading-container">
                                <div class="icon-loading"></div>
                                <span><?php p($l->t('Lade Geräte...')); ?></span>
                            </div>
                        </div>
                        
                        <div class="map-device-details" id="map-device-details">
                            <h3><?php p($l->t('Gerätedetails')); ?></h3>
                            <div id="map-selected-device">
                                <p><?php p($l->t('Wählen Sie ein Gerät auf der Karte oder aus der Liste aus, um Details anzuzeigen.')); ?></p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="map-controls">
                    <div class="map-control-group">
                        <label><?php p($l->t('Ansicht:')); ?></label>
                        <div class="map-view-buttons">
                            <button class="map-view-btn active" data-view="roadmap">
                                <?php p($l->t('Karte')); ?>
                            </button>
                            <button class="map-view-btn" data-view="satellite">
                                <?php p($l->t('Satellit')); ?>
                            </button>
                            <button class="map-view-btn" data-view="hybrid">
                                <?php p($l->t('Hybrid')); ?>
                            </button>
                        </div>
                    </div>
                    
                    <div class="map-control-group">
                        <label for="map-time-range"><?php p($l->t('Zeitraum:')); ?></label>
                        <select id="map-time-range">
                            <option value="live"><?php p($l->t('Live')); ?></option>
                            <option value="today"><?php p($l->t('Heute')); ?></option>
                            <option value="week"><?php p($l->t('Letzte Woche')); ?></option>
                            <option value="month"><?php p($l->t('Letzter Monat')); ?></option>
                        </select>
                    </div>
                    
                    <div class="map-control-group">
                        <label><?php p($l->t('Anzeigen:')); ?></label>
                        <div class="map-layer-controls">
                            <div class="map-layer-control">
                                <input type="checkbox" id="show-device-paths" checked>
                                <label for="show-device-paths"><?php p($l->t('Gerätepfade')); ?></label>
                            </div>
                            <div class="map-layer-control">
                                <input type="checkbox" id="show-heat-map">
                                <label for="show-heat-map"><?php p($l->t('Heatmap')); ?></label>
                            </div>
                            <div class="map-layer-control">
                                <input type="checkbox" id="show-clusters" checked>
                                <label for="show-clusters"><?php p($l->t('Cluster')); ?></label>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>