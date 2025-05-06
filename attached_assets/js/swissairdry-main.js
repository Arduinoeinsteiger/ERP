/**
 * SwissAirDry App
 * 
 * @author Swiss Air Dry Team <info@swissairdry.com>
 * @copyright 2025 Swiss Air Dry Team
 */

(function() {
    'use strict';

    document.addEventListener('DOMContentLoaded', function() {
        // DOM-Elemente
        const apiStatusIndicator = document.getElementById('api-status-indicator');
        const apiStatusText = document.getElementById('api-status-text');
        const refreshBtn = document.getElementById('refresh-btn');
        const refreshIntervalSelect = document.getElementById('refresh-interval');
        const dashboardTilesContainer = document.getElementById('dashboard-tiles');
        
        // Einstellungen-Elemente
        const saveSettingsBtn = document.getElementById('swissairdry-save-settings');
        
        if (saveSettingsBtn) {
            saveSettingsBtn.addEventListener('click', saveSettings);
        }
        
        // API-Endpunkte
        const endpoints = {
            status: OC.generateUrl('/apps/swissairdry/api/mqtt/status'),
            devices: OC.generateUrl('/apps/swissairdry/api/devices'),
            settings: OC.generateUrl('/apps/swissairdry/api/settings')
        };
        
        // Intervall für automatische Aktualisierungen
        let refreshIntervalId = null;
        let refreshIntervalSeconds = parseInt(refreshIntervalSelect?.value || 30);
        
        // Initialisierung
        initApp();
        
        /**
         * App initialisieren
         */
        function initApp() {
            // Event-Listener registrieren
            if (refreshBtn) {
                refreshBtn.addEventListener('click', refreshDashboard);
            }
            
            if (refreshIntervalSelect) {
                refreshIntervalSelect.addEventListener('change', function() {
                    refreshIntervalSeconds = parseInt(this.value);
                    
                    if (refreshIntervalId) {
                        clearInterval(refreshIntervalId);
                        refreshIntervalId = null;
                    }
                    
                    if (refreshIntervalSeconds > 0) {
                        refreshIntervalId = setInterval(refreshDashboard, refreshIntervalSeconds * 1000);
                    }
                });
            }
            
            // Dashboard laden
            checkApiStatus();
            loadDashboardData();
            
            // Automatische Aktualisierung starten
            if (refreshIntervalSeconds > 0) {
                refreshIntervalId = setInterval(refreshDashboard, refreshIntervalSeconds * 1000);
            }
        }
        
        /**
         * Dashboard aktualisieren
         */
        function refreshDashboard() {
            checkApiStatus();
            loadDashboardData();
        }
        
        /**
         * API-Status prüfen
         */
        function checkApiStatus() {
            if (!apiStatusIndicator || !apiStatusText) {
                return;
            }
            
            apiStatusIndicator.classList.remove('online', 'offline');
            apiStatusText.textContent = t('swissairdry', 'Prüfe...');
            
            // MQTT-Status prüfen
            fetch(endpoints.status)
                .then(response => response.json())
                .then(data => {
                    updateApiStatus(data.connected ? 'online' : 'offline');
                })
                .catch(error => {
                    console.error('Fehler beim Abrufen des API-Status:', error);
                    updateApiStatus('offline');
                });
        }
        
        /**
         * API-Status aktualisieren
         * 
         * @param {string} status - Status der API ('online' oder 'offline')
         */
        function updateApiStatus(status) {
            if (!apiStatusIndicator || !apiStatusText) {
                return;
            }
            
            apiStatusIndicator.classList.remove('online', 'offline');
            apiStatusIndicator.classList.add(status);
            
            if (status === 'online') {
                apiStatusText.textContent = t('swissairdry', 'Verbunden');
            } else {
                apiStatusText.textContent = t('swissairdry', 'Nicht verbunden');
            }
        }
        
        /**
         * Dashboard-Daten laden
         */
        function loadDashboardData() {
            if (!dashboardTilesContainer) {
                return;
            }
            
            // Lade-Animation anzeigen
            dashboardTilesContainer.innerHTML = `
                <div class="tile loading">
                    <div class="icon-loading"></div>
                    <span>${t('swissairdry', 'Lade Daten...')}</span>
                </div>
            `;
            
            // Geräte abrufen
            fetch(endpoints.devices)
                .then(response => response.json())
                .then(devices => {
                    if (!Array.isArray(devices) || devices.length === 0) {
                        dashboardTilesContainer.innerHTML = `
                            <div class="tile">
                                <p>${t('swissairdry', 'Keine Geräte gefunden.')}</p>
                                <p>${t('swissairdry', 'Verbinden Sie ein Gerät mit der SwissAirDry API, um es hier anzuzeigen.')}</p>
                            </div>
                        `;
                        return;
                    }
                    
                    // Dashboard-Kacheln erstellen
                    dashboardTilesContainer.innerHTML = '';
                    
                    devices.forEach(device => {
                        const tile = createDeviceTile(device);
                        dashboardTilesContainer.appendChild(tile);
                    });
                })
                .catch(error => {
                    console.error('Fehler beim Laden der Geräte:', error);
                    dashboardTilesContainer.innerHTML = `
                        <div class="tile">
                            <p>${t('swissairdry', 'Fehler beim Laden der Geräte.')}</p>
                            <p>${error.message}</p>
                        </div>
                    `;
                });
        }
        
        /**
         * Gerätekachel erstellen
         * 
         * @param {Object} device - Gerätedaten
         * @returns {HTMLElement} - DOM-Element der Kachel
         */
        function createDeviceTile(device) {
            const tile = document.createElement('div');
            tile.className = 'tile';
            tile.dataset.deviceId = device.id;
            
            const statusClass = device.online ? 'online' : 'offline';
            const statusText = device.online ? t('swissairdry', 'Online') : t('swissairdry', 'Offline');
            
            // Basisdaten für die Kachel vorbereiten
            let html = `
                <div class="device-name">${escapeHTML(device.name || device.id)}</div>
                <div class="device-status">
                    <div class="device-status-indicator ${statusClass}"></div>
                    <span>${statusText}</span>
                </div>
                <div class="device-info">
                    <div>ID: ${escapeHTML(device.id)}</div>
                    <div>Typ: ${escapeHTML(device.type || t('swissairdry', 'Unbekannt'))}</div>
                </div>
            `;
            
            // Sensordaten hinzufügen, wenn vorhanden
            if (device.data) {
                html += '<div class="device-data">';
                
                if (device.data.temperature !== undefined) {
                    html += `
                        <div class="data-row">
                            <span class="data-label">${t('swissairdry', 'Temperatur')}:</span>
                            <span class="data-value">${device.data.temperature} °C</span>
                        </div>
                    `;
                }
                
                if (device.data.humidity !== undefined) {
                    html += `
                        <div class="data-row">
                            <span class="data-label">${t('swissairdry', 'Luftfeuchtigkeit')}:</span>
                            <span class="data-value">${device.data.humidity} %</span>
                        </div>
                    `;
                }
                
                if (device.data.pressure !== undefined) {
                    html += `
                        <div class="data-row">
                            <span class="data-label">${t('swissairdry', 'Druck')}:</span>
                            <span class="data-value">${device.data.pressure} hPa</span>
                        </div>
                    `;
                }
                
                if (device.data.power !== undefined) {
                    html += `
                        <div class="data-row">
                            <span class="data-label">${t('swissairdry', 'Leistung')}:</span>
                            <span class="data-value">${device.data.power} W</span>
                        </div>
                    `;
                }
                
                if (device.data.energy !== undefined) {
                    html += `
                        <div class="data-row">
                            <span class="data-label">${t('swissairdry', 'Energie')}:</span>
                            <span class="data-value">${device.data.energy} kWh</span>
                        </div>
                    `;
                }
                
                if (device.data.runtime !== undefined) {
                    const hours = Math.floor(device.data.runtime / 3600);
                    const minutes = Math.floor((device.data.runtime % 3600) / 60);
                    html += `
                        <div class="data-row">
                            <span class="data-label">${t('swissairdry', 'Laufzeit')}:</span>
                            <span class="data-value">${hours}h ${minutes}m</span>
                        </div>
                    `;
                }
                
                html += '</div>';
            }
            
            // Aktionsschaltflächen hinzufügen
            html += `
                <div class="device-actions">
                    <a href="${OC.generateUrl('/apps/swissairdry/devices/' + device.id)}" class="button">
                        ${t('swissairdry', 'Details')}
                    </a>
                    <button class="device-toggle-btn primary" data-device-id="${device.id}" data-state="${device.data?.relay_state ? 'on' : 'off'}">
                        ${device.data?.relay_state ? t('swissairdry', 'Ausschalten') : t('swissairdry', 'Einschalten')}
                    </button>
                </div>
            `;
            
            tile.innerHTML = html;
            
            // Event-Listener für Ein/Aus-Schalter
            const toggleBtn = tile.querySelector('.device-toggle-btn');
            if (toggleBtn) {
                toggleBtn.addEventListener('click', function() {
                    const deviceId = this.dataset.deviceId;
                    const currentState = this.dataset.state;
                    const newState = currentState === 'on' ? 'off' : 'on';
                    
                    sendDeviceCommand(deviceId, {
                        command: 'set_relay',
                        value: newState === 'on'
                    });
                });
            }
            
            return tile;
        }
        
        /**
         * Befehl an ein Gerät senden
         * 
         * @param {string} deviceId - Geräte-ID
         * @param {Object} commandData - Befehlsdaten
         */
        function sendDeviceCommand(deviceId, commandData) {
            fetch(OC.generateUrl(`/apps/swissairdry/api/devices/${deviceId}/command`), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'requesttoken': OC.requestToken
                },
                body: JSON.stringify(commandData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    OC.Notification.showTemporary(t('swissairdry', 'Befehl erfolgreich gesendet'));
                    // Nach kurzer Verzögerung aktualisieren
                    setTimeout(loadDashboardData, 1000);
                } else {
                    OC.Notification.showTemporary(t('swissairdry', 'Fehler beim Senden des Befehls: ') + data.error);
                }
            })
            .catch(error => {
                console.error('Fehler beim Senden des Befehls:', error);
                OC.Notification.showTemporary(t('swissairdry', 'Fehler beim Senden des Befehls: ') + error.message);
            });
        }
        
        /**
         * Einstellungen speichern
         */
        function saveSettings() {
            const settings = {
                apiEndpoint: document.getElementById('swissairdry-api-endpoint')?.value,
                apiPort: parseInt(document.getElementById('swissairdry-api-port')?.value || 443),
                apiBasePath: document.getElementById('swissairdry-api-basepath')?.value,
                mqttBroker: document.getElementById('swissairdry-mqtt-broker')?.value,
                mqttPort: parseInt(document.getElementById('swissairdry-mqtt-port')?.value || 8883),
                darkMode: document.getElementById('swissairdry-dark-mode')?.checked,
                notifications: document.getElementById('swissairdry-notifications')?.checked
            };
            
            fetch(endpoints.settings, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'requesttoken': OC.requestToken
                },
                body: JSON.stringify(settings)
            })
            .then(response => response.json())
            .then(data => {
                OC.Notification.showTemporary(t('swissairdry', 'Einstellungen erfolgreich gespeichert'));
                
                // Dunkelmodus umschalten
                if (settings.darkMode) {
                    document.querySelector('.app-swissairdry').classList.add('theme-dark');
                } else {
                    document.querySelector('.app-swissairdry').classList.remove('theme-dark');
                }
                
                // API-Status und Dashboard aktualisieren
                checkApiStatus();
                loadDashboardData();
            })
            .catch(error => {
                console.error('Fehler beim Speichern der Einstellungen:', error);
                OC.Notification.showTemporary(t('swissairdry', 'Fehler beim Speichern der Einstellungen: ') + error.message);
            });
        }
        
        /**
         * HTML-Sonderzeichen escapen
         * 
         * @param {string} unsafe - Unsicherer Text
         * @returns {string} - Escapeter Text
         */
        function escapeHTML(unsafe) {
            if (typeof unsafe !== 'string') {
                return '';
            }
            return unsafe
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        }
    });
})();