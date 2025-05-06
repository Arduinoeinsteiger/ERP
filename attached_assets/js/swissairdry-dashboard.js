/**
 * SwissAirDry App - Dashboard
 * 
 * @author Swiss Air Dry Team <info@swissairdry.com>
 * @copyright 2025 Swiss Air Dry Team
 */

(function() {
    'use strict';

    document.addEventListener('DOMContentLoaded', function() {
        // DOM-Elemente
        const deviceCountEl = document.getElementById('device-count');
        const deviceOnlineCountEl = document.getElementById('device-online-count');
        const alertCountEl = document.getElementById('alert-count');
        const energyUsageEl = document.getElementById('energy-usage');
        const humidityChartEl = document.getElementById('humidity-chart');
        const temperatureChartEl = document.getElementById('temperature-chart');
        const deviceListEl = document.getElementById('device-list');
        const deviceFilterEl = document.getElementById('device-filter');
        
        // API-Endpunkte
        const endpoints = {
            devices: OC.generateUrl('/apps/swissairdry/api/devices'),
            deviceData: OC.generateUrl('/apps/swissairdry/api/devices/{id}/data')
        };
        
        // Diagramm-Instanzen
        let humidityChart = null;
        let temperatureChart = null;
        
        // Geräteliste
        let devices = [];
        
        // Initialisierung
        initDashboard();
        
        /**
         * Dashboard initialisieren
         */
        function initDashboard() {
            // Geräteliste laden
            loadDevices();
            
            // Filter-Listener
            if (deviceFilterEl) {
                deviceFilterEl.addEventListener('input', filterDevices);
            }
            
            // Automatisches Aktualisieren alle 30 Sekunden
            setInterval(loadDevices, 30000);
        }
        
        /**
         * Geräte laden
         */
        function loadDevices() {
            // Lade-Animation anzeigen
            showLoading();
            
            fetch(endpoints.devices)
                .then(response => response.json())
                .then(data => {
                    devices = data;
                    updateDashboardStats(devices);
                    renderDeviceList(devices);
                    loadChartData(devices);
                })
                .catch(error => {
                    console.error('Fehler beim Laden der Geräte:', error);
                    OC.Notification.showTemporary(
                        t('swissairdry', 'Fehler beim Laden der Geräte: {error}', { error: error.message })
                    );
                    showLoadingError();
                });
        }
        
        /**
         * Dashboard-Statistiken aktualisieren
         */
        function updateDashboardStats(devices) {
            if (!devices || !Array.isArray(devices)) {
                return;
            }
            
            // Gerätezählung
            if (deviceCountEl) {
                deviceCountEl.textContent = devices.length;
            }
            
            // Online-Geräte zählen
            const onlineDevices = devices.filter(device => device.online);
            if (deviceOnlineCountEl) {
                deviceOnlineCountEl.textContent = onlineDevices.length;
            }
            
            // Warnungen zählen
            const alerts = devices.reduce((count, device) => {
                return count + (device.alerts ? device.alerts.length : 0);
            }, 0);
            if (alertCountEl) {
                alertCountEl.textContent = alerts;
            }
            
            // Energieverbrauch berechnen
            const totalEnergy = devices.reduce((total, device) => {
                return total + (device.data && device.data.energy ? parseFloat(device.data.energy) : 0);
            }, 0);
            if (energyUsageEl) {
                energyUsageEl.textContent = totalEnergy.toFixed(2) + ' kWh';
            }
        }
        
        /**
         * Geräteliste rendern
         */
        function renderDeviceList(devices) {
            if (!deviceListEl || !devices || !Array.isArray(devices)) {
                return;
            }
            
            if (devices.length === 0) {
                deviceListEl.innerHTML = `
                    <div class="empty-state">
                        <p>${t('swissairdry', 'Keine Geräte gefunden.')}</p>
                        <p>${t('swissairdry', 'Verbinden Sie ein Gerät mit der SwissAirDry API, um es hier anzuzeigen.')}</p>
                    </div>
                `;
                return;
            }
            
            // Filter anwenden, falls vorhanden
            let filteredDevices = devices;
            const filterValue = deviceFilterEl ? deviceFilterEl.value.toLowerCase() : '';
            if (filterValue) {
                filteredDevices = devices.filter(device => 
                    (device.name && device.name.toLowerCase().includes(filterValue)) ||
                    device.id.toLowerCase().includes(filterValue) ||
                    (device.type && device.type.toLowerCase().includes(filterValue))
                );
            }
            
            if (filteredDevices.length === 0) {
                deviceListEl.innerHTML = `
                    <div class="empty-state">
                        <p>${t('swissairdry', 'Keine Geräte entsprechen dem Filter.')}</p>
                    </div>
                `;
                return;
            }
            
            // Nach Status sortieren: online zuerst, dann offline
            filteredDevices.sort((a, b) => {
                if (a.online && !b.online) return -1;
                if (!a.online && b.online) return 1;
                return (a.name || a.id).localeCompare(b.name || b.id);
            });
            
            // Geräte-HTML erstellen
            let html = '';
            filteredDevices.forEach(device => {
                const statusClass = device.online ? 'online' : 'offline';
                const statusText = device.online ? t('swissairdry', 'Online') : t('swissairdry', 'Offline');
                
                html += `
                    <div class="device-list-item ${statusClass}" data-device-id="${escapeHTML(device.id)}">
                        <div class="device-status">
                            <div class="device-status-indicator ${statusClass}"></div>
                            <span>${statusText}</span>
                        </div>
                        <div class="device-info">
                            <div class="device-name">${escapeHTML(device.name || device.id)}</div>
                            <div class="device-type">${escapeHTML(device.type || t('swissairdry', 'Unbekannt'))}</div>
                        </div>
                        <div class="device-data-summary">
                `;
                
                // Sensordaten anzeigen, falls vorhanden
                if (device.data) {
                    if (device.data.temperature !== undefined) {
                        html += `<div class="data-item temperature">${device.data.temperature} °C</div>`;
                    }
                    
                    if (device.data.humidity !== undefined) {
                        html += `<div class="data-item humidity">${device.data.humidity} %</div>`;
                    }
                    
                    if (device.data.power !== undefined) {
                        html += `<div class="data-item power">${device.data.power} W</div>`;
                    }
                }
                
                html += `
                        </div>
                        <div class="device-actions">
                            <a href="${OC.generateUrl('/apps/swissairdry/devices/' + device.id)}" class="button">
                                ${t('swissairdry', 'Details')}
                            </a>
                        </div>
                    </div>
                `;
            });
            
            deviceListEl.innerHTML = html;
            
            // Event-Listener für Geräte-Klicks
            const deviceItems = deviceListEl.querySelectorAll('.device-list-item');
            deviceItems.forEach(item => {
                item.addEventListener('click', function(e) {
                    // Nur wenn nicht auf einen Button oder Link geklickt wurde
                    if (!e.target.closest('a') && !e.target.closest('button')) {
                        const deviceId = this.dataset.deviceId;
                        window.location.href = OC.generateUrl('/apps/swissairdry/devices/' + deviceId);
                    }
                });
            });
        }
        
        /**
         * Diagrammdaten laden
         */
        function loadChartData(devices) {
            if (!humidityChartEl || !temperatureChartEl || !devices || !Array.isArray(devices)) {
                return;
            }
            
            // Nur Online-Geräte verwenden
            const onlineDevices = devices.filter(device => device.online);
            
            if (onlineDevices.length === 0) {
                showChartNoData(humidityChartEl);
                showChartNoData(temperatureChartEl);
                return;
            }
            
            // Sensordaten der letzten 24 Stunden abrufen für bis zu 5 Geräte
            const devicePromises = onlineDevices.slice(0, 5).map(device => 
                fetch(endpoints.deviceData.replace('{id}', device.id))
                    .then(response => response.json())
                    .then(data => ({
                        device: device,
                        data: data
                    }))
                    .catch(error => {
                        console.error(`Fehler beim Laden der Daten für Gerät ${device.id}:`, error);
                        return {
                            device: device,
                            data: null
                        };
                    })
            );
            
            Promise.all(devicePromises)
                .then(results => {
                    // Daten für Diagramme aufbereiten
                    const humidityData = {
                        labels: [],
                        datasets: []
                    };
                    
                    const temperatureData = {
                        labels: [],
                        datasets: []
                    };
                    
                    // Zeitachse erstellen (letzte 24 Stunden in 1-Stunden-Intervallen)
                    const now = new Date();
                    for (let i = 24; i >= 0; i--) {
                        const date = new Date(now.getTime() - i * 60 * 60 * 1000);
                        const label = date.getHours() + ':00';
                        humidityData.labels.push(label);
                        temperatureData.labels.push(label);
                    }
                    
                    // Daten für jedes Gerät hinzufügen
                    results.forEach((result, index) => {
                        if (!result.data || !result.data.history) {
                            return;
                        }
                        
                        // Farbe basierend auf Index
                        const colors = [
                            '#0082c9', // Nextcloud-Blau
                            '#30caff',
                            '#00c292',
                            '#ffa92b',
                            '#ff6347'
                        ];
                        const color = colors[index % colors.length];
                        
                        // Luftfeuchtigkeitsdaten
                        if (result.data.history.humidity) {
                            humidityData.datasets.push({
                                label: result.device.name || result.device.id,
                                data: generateDataPoints(result.data.history.humidity, 25),
                                borderColor: color,
                                backgroundColor: color + '20',
                                fill: false,
                                tension: 0.4
                            });
                        }
                        
                        // Temperaturdaten
                        if (result.data.history.temperature) {
                            temperatureData.datasets.push({
                                label: result.device.name || result.device.id,
                                data: generateDataPoints(result.data.history.temperature, 21),
                                borderColor: color,
                                backgroundColor: color + '20',
                                fill: false,
                                tension: 0.4
                            });
                        }
                    });
                    
                    // Diagramme erstellen
                    updateHumidityChart(humidityData);
                    updateTemperatureChart(temperatureData);
                })
                .catch(error => {
                    console.error('Fehler beim Laden der Diagrammdaten:', error);
                    showChartError(humidityChartEl);
                    showChartError(temperatureChartEl);
                });
        }
        
        /**
         * Generiert Datenpunkte für ein Diagramm
         * Bei fehlenden Daten wird ein Standardwert verwendet
         */
        function generateDataPoints(data, defaultValue) {
            const points = [];
            for (let i = 0; i <= 24; i++) {
                const point = data[i] !== undefined ? data[i] : defaultValue;
                points.push(point);
            }
            return points;
        }
        
        /**
         * Aktualisiert das Luftfeuchtigkeitsdiagramm
         */
        function updateHumidityChart(data) {
            if (!humidityChartEl) {
                return;
            }
            
            humidityChartEl.innerHTML = '';
            
            if (!data.datasets || data.datasets.length === 0) {
                showChartNoData(humidityChartEl);
                return;
            }
            
            const canvas = document.createElement('canvas');
            canvas.id = 'humidity-chart-canvas';
            humidityChartEl.appendChild(canvas);
            
            const ctx = canvas.getContext('2d');
            
            if (humidityChart) {
                humidityChart.destroy();
            }
            
            humidityChart = new Chart(ctx, {
                type: 'line',
                data: data,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: false,
                            min: 0,
                            max: 100,
                            title: {
                                display: true,
                                text: t('swissairdry', 'Luftfeuchtigkeit (%)')
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: t('swissairdry', 'Zeit')
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'top'
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false
                        }
                    }
                }
            });
        }
        
        /**
         * Aktualisiert das Temperaturdiagramm
         */
        function updateTemperatureChart(data) {
            if (!temperatureChartEl) {
                return;
            }
            
            temperatureChartEl.innerHTML = '';
            
            if (!data.datasets || data.datasets.length === 0) {
                showChartNoData(temperatureChartEl);
                return;
            }
            
            const canvas = document.createElement('canvas');
            canvas.id = 'temperature-chart-canvas';
            temperatureChartEl.appendChild(canvas);
            
            const ctx = canvas.getContext('2d');
            
            if (temperatureChart) {
                temperatureChart.destroy();
            }
            
            temperatureChart = new Chart(ctx, {
                type: 'line',
                data: data,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: false,
                            title: {
                                display: true,
                                text: t('swissairdry', 'Temperatur (°C)')
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: t('swissairdry', 'Zeit')
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'top'
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false
                        }
                    }
                }
            });
        }
        
        /**
         * Lade-Animation anzeigen
         */
        function showLoading() {
            if (deviceCountEl) deviceCountEl.innerHTML = '<div class="icon-loading"></div>';
            if (deviceOnlineCountEl) deviceOnlineCountEl.innerHTML = '<div class="icon-loading"></div>';
            if (alertCountEl) alertCountEl.innerHTML = '<div class="icon-loading"></div>';
            if (energyUsageEl) energyUsageEl.innerHTML = '<div class="icon-loading"></div>';
            
            if (deviceListEl) {
                deviceListEl.innerHTML = `
                    <div class="loading-container">
                        <div class="icon-loading"></div>
                        <span>${t('swissairdry', 'Lade Geräte...')}</span>
                    </div>
                `;
            }
        }
        
        /**
         * Fehler beim Laden anzeigen
         */
        function showLoadingError() {
            if (deviceCountEl) deviceCountEl.textContent = '-';
            if (deviceOnlineCountEl) deviceOnlineCountEl.textContent = '-';
            if (alertCountEl) alertCountEl.textContent = '-';
            if (energyUsageEl) energyUsageEl.textContent = '-';
            
            if (deviceListEl) {
                deviceListEl.innerHTML = `
                    <div class="empty-state error">
                        <p>${t('swissairdry', 'Fehler beim Laden der Geräte.')}</p>
                        <p>${t('swissairdry', 'Bitte überprüfen Sie Ihre API-Verbindung in den Einstellungen.')}</p>
                    </div>
                `;
            }
            
            showChartError(humidityChartEl);
            showChartError(temperatureChartEl);
        }
        
        /**
         * "Keine Daten" im Diagramm anzeigen
         */
        function showChartNoData(chartEl) {
            if (!chartEl) {
                return;
            }
            
            chartEl.innerHTML = `
                <div class="chart-no-data">
                    <span>${t('swissairdry', 'Keine Daten verfügbar')}</span>
                </div>
            `;
        }
        
        /**
         * Fehler im Diagramm anzeigen
         */
        function showChartError(chartEl) {
            if (!chartEl) {
                return;
            }
            
            chartEl.innerHTML = `
                <div class="chart-error">
                    <span>${t('swissairdry', 'Fehler beim Laden der Diagrammdaten')}</span>
                </div>
            `;
        }
        
        /**
         * Gerätliste filtern
         */
        function filterDevices() {
            renderDeviceList(devices);
        }
        
        /**
         * HTML-Sonderzeichen escapen
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