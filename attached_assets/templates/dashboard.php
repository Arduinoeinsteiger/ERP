<?php
script('swissairdry', 'swissairdry-dashboard');
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
                <h2><?php p($l->t('Dashboard')); ?></h2>
                
                <div class="dashboard-overview">
                    <div class="overview-card total-devices">
                        <div class="card-icon icon-contacts"></div>
                        <div class="card-content">
                            <div class="card-title"><?php p($l->t('Geräte')); ?></div>
                            <div class="card-value" id="device-count">
                                <div class="icon-loading"></div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="overview-card online-devices">
                        <div class="card-icon icon-checkmark"></div>
                        <div class="card-content">
                            <div class="card-title"><?php p($l->t('Online')); ?></div>
                            <div class="card-value" id="device-online-count">
                                <div class="icon-loading"></div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="overview-card alerts">
                        <div class="card-icon icon-error"></div>
                        <div class="card-content">
                            <div class="card-title"><?php p($l->t('Warnungen')); ?></div>
                            <div class="card-value" id="alert-count">
                                <div class="icon-loading"></div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="overview-card energy">
                        <div class="card-icon icon-quota"></div>
                        <div class="card-content">
                            <div class="card-title"><?php p($l->t('Energieverbrauch')); ?></div>
                            <div class="card-value" id="energy-usage">
                                <div class="icon-loading"></div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="dashboard-charts">
                    <div class="chart-container">
                        <h3><?php p($l->t('Luftfeuchtigkeit (letzte 24 Stunden)')); ?></h3>
                        <div class="chart" id="humidity-chart">
                            <div class="chart-loading">
                                <div class="icon-loading"></div>
                                <span><?php p($l->t('Lade Diagramm...')); ?></span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="chart-container">
                        <h3><?php p($l->t('Temperatur (letzte 24 Stunden)')); ?></h3>
                        <div class="chart" id="temperature-chart">
                            <div class="chart-loading">
                                <div class="icon-loading"></div>
                                <span><?php p($l->t('Lade Diagramm...')); ?></span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="section-header">
                    <h3><?php p($l->t('Aktive Geräte')); ?></h3>
                    <div class="device-filter">
                        <input type="text" id="device-filter" placeholder="<?php p($l->t('Filtern...')); ?>">
                    </div>
                </div>
                
                <div class="device-list" id="device-list">
                    <div class="loading-container">
                        <div class="icon-loading"></div>
                        <span><?php p($l->t('Lade Geräte...')); ?></span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>