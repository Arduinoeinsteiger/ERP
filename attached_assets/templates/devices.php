<?php
script('swissairdry', 'swissairdry-devices');
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
                <div class="section-header">
                    <h2><?php p($l->t('Geräte')); ?></h2>
                    <div class="section-actions">
                        <div class="device-filter">
                            <input type="text" id="device-filter" placeholder="<?php p($l->t('Filtern...')); ?>">
                        </div>
                        <button id="refresh-devices-btn" class="button">
                            <span class="icon-refresh"></span>
                            <?php p($l->t('Aktualisieren')); ?>
                        </button>
                    </div>
                </div>
                
                <div class="device-actions-bar">
                    <div class="view-switcher">
                        <button class="view-btn active" data-view="grid">
                            <span class="icon-toggle-pictures"></span>
                            <?php p($l->t('Kacheln')); ?>
                        </button>
                        <button class="view-btn" data-view="list">
                            <span class="icon-toggle-filelist"></span>
                            <?php p($l->t('Liste')); ?>
                        </button>
                    </div>
                    
                    <div class="device-sort">
                        <label for="device-sort"><?php p($l->t('Sortieren nach:')); ?></label>
                        <select id="device-sort">
                            <option value="name"><?php p($l->t('Name')); ?></option>
                            <option value="status"><?php p($l->t('Status')); ?></option>
                            <option value="type"><?php p($l->t('Typ')); ?></option>
                            <option value="lastSeen"><?php p($l->t('Zuletzt gesehen')); ?></option>
                        </select>
                    </div>
                </div>
                
                <div id="devices-container" class="devices-grid">
                    <div class="loading-container">
                        <div class="icon-loading"></div>
                        <span><?php p($l->t('Lade Geräte...')); ?></span>
                    </div>
                </div>
                
                <div class="pagination" id="devices-pagination">
                    <button class="pagination-prev" disabled>
                        <span class="icon-triangle-n"></span>
                        <?php p($l->t('Vorherige')); ?>
                    </button>
                    <span class="pagination-info"><?php p($l->t('Seite')); ?> <span id="current-page">1</span> <?php p($l->t('von')); ?> <span id="total-pages">1</span></span>
                    <button class="pagination-next" disabled>
                        <?php p($l->t('Nächste')); ?>
                        <span class="icon-triangle-s"></span>
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>