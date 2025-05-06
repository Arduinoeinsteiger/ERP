<?php
/** @var array $_ */
/** @var \OCP\IL10N $l */
script('swissairdry', 'main');
style('swissairdry', 'style');
?>

<div id="swissairdry-app" data-api-url="<?php p($_['api_url']); ?>" data-user="<?php p($_['user_id']); ?>">
    <div class="app-content">
        <h2><?php p($l->t('SwissAirDry Dashboard')); ?></h2>
        
        <div class="dashboard">
            <div class="dashboard-header">
                <div class="status-indicator online">
                    <span class="status-dot"></span>
                    <span class="status-text"><?php p($l->t('System Online')); ?></span>
                </div>
                <div class="dashboard-actions">
                    <button class="primary" id="refreshDashboard">
                        <span class="icon-refresh"></span>
                        <?php p($l->t('Refresh')); ?>
                    </button>
                </div>
            </div>
            
            <div class="card-container">
                <div class="card summary-card">
                    <h3><?php p($l->t('System Overview')); ?></h3>
                    <div class="card-content">
                        <div class="summary-item">
                            <span class="label"><?php p($l->t('Total Devices')); ?></span>
                            <span class="value" id="totalDevices">-</span>
                        </div>
                        <div class="summary-item">
                            <span class="label"><?php p($l->t('Online Devices')); ?></span>
                            <span class="value" id="onlineDevices">-</span>
                        </div>
                        <div class="summary-item">
                            <span class="label"><?php p($l->t('Latest Reading')); ?></span>
                            <span class="value" id="latestReading">-</span>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <h3><?php p($l->t('Recent Activity')); ?></h3>
                    <div class="card-content">
                        <ul class="activity-list" id="activityList">
                            <li class="empty-list"><?php p($l->t('No recent activity')); ?></li>
                        </ul>
                    </div>
                </div>
            </div>
            
            <div class="device-list-container">
                <h3><?php p($l->t('Your Devices')); ?></h3>
                <div class="device-list" id="deviceList">
                    <div class="empty-list"><?php p($l->t('No devices found')); ?></div>
                </div>
            </div>
        </div>
    </div>
</div>

<script type="text/javascript">
    document.addEventListener('DOMContentLoaded', function() {
        // This code will be replaced by the main.js file
        // It's here just to provide basic functionality when JavaScript is disabled
        
        // Set up refresh button
        const refreshButton = document.getElementById('refreshDashboard');
        if (refreshButton) {
            refreshButton.addEventListener('click', function() {
                window.location.reload();
            });
        }
    });
</script>