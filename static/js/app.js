/**
 * SwissAirDry Platform - Main JavaScript
 * 
 * This script provides client-side functionality for the SwissAirDry web interface.
 */

// Global state
const app = {
    devices: [],
    selectedDevice: null,
    refreshInterval: null,
};

// DOM elements
const elements = {
    deviceList: document.getElementById('device-list'),
    deviceDetail: document.getElementById('device-detail'),
    systemStatus: document.getElementById('system-status'),
    refreshButton: document.getElementById('refresh-button'),
    errorContainer: document.getElementById('error-container'),
};

// Initialize the application when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

/**
 * Initialize the application
 */
function initializeApp() {
    // Set up event listeners
    setupEventListeners();
    
    // Load initial data
    loadDevices();
    loadSystemStatus();
    
    // Set up auto-refresh (every 30 seconds)
    app.refreshInterval = setInterval(() => {
        loadDevices();
        loadSystemStatus();
    }, 30000);

    // Check if we're on the device detail page
    const urlParams = new URLSearchParams(window.location.search);
    const deviceId = urlParams.get('device');
    if (deviceId) {
        loadDeviceDetail(deviceId);
    }
}

/**
 * Set up event listeners
 */
function setupEventListeners() {
    // Refresh button
    if (elements.refreshButton) {
        elements.refreshButton.addEventListener('click', () => {
            loadDevices();
            loadSystemStatus();
            showMessage('Data refreshed', 'success');
        });
    }

    // Device power control buttons (delegated)
    document.addEventListener('click', (event) => {
        // Power toggle button
        if (event.target.classList.contains('power-toggle')) {
            const deviceId = event.target.dataset.deviceId;
            const currentState = event.target.dataset.state === 'true';
            toggleDevicePower(deviceId, !currentState);
        }
        
        // Fan speed controls
        if (event.target.classList.contains('fan-control')) {
            const deviceId = event.target.dataset.deviceId;
            const speed = parseInt(event.target.dataset.speed);
            setFanSpeed(deviceId, speed);
        }
        
        // OTA update trigger
        if (event.target.classList.contains('trigger-update')) {
            const deviceId = event.target.dataset.deviceId;
            triggerOtaUpdate(deviceId);
        }
    });
}

/**
 * Load devices from the API
 */
async function loadDevices() {
    try {
        const response = await fetch('/api/devices');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const devices = await response.json();
        app.devices = devices;
        
        // Update the UI
        renderDeviceList(devices);
    } catch (error) {
        console.error('Error loading devices:', error);
        showError(`Failed to load devices: ${error.message}`);
    }
}

/**
 * Load system status from the API
 */
async function loadSystemStatus() {
    if (!elements.systemStatus) return;
    
    try {
        const response = await fetch('/api/system/status');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const status = await response.json();
        renderSystemStatus(status);
    } catch (error) {
        console.error('Error loading system status:', error);
        showError(`Failed to load system status: ${error.message}`);
    }
}

/**
 * Load device detail from the API
 */
async function loadDeviceDetail(deviceId) {
    try {
        const response = await fetch(`/api/devices/${deviceId}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const device = await response.json();
        app.selectedDevice = device;
        
        // Load readings for this device
        loadDeviceReadings(deviceId);
        
        // Update the UI
        renderDeviceDetail(device);
    } catch (error) {
        console.error(`Error loading device ${deviceId}:`, error);
        showError(`Failed to load device details: ${error.message}`);
    }
}

/**
 * Load device readings from the API
 */
async function loadDeviceReadings(deviceId) {
    try {
        const response = await fetch(`/api/devices/${deviceId}/readings?limit=20`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const readings = await response.json();
        
        // Update the UI
        renderDeviceReadings(readings);
    } catch (error) {
        console.error(`Error loading readings for device ${deviceId}:`, error);
        showError(`Failed to load device readings: ${error.message}`);
    }
}

/**
 * Toggle device power state
 */
async function toggleDevicePower(deviceId, state) {
    try {
        const response = await fetch(`/api/devices/${deviceId}/control/power?state=${state}`, {
            method: 'POST',
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        showMessage(result.message, 'success');
        
        // Update the button state immediately for better UX
        const button = document.querySelector(`.power-toggle[data-device-id="${deviceId}"]`);
        if (button) {
            button.dataset.state = state.toString();
            button.innerHTML = state 
                ? '<i class="feather-power" style="color: green;"></i> On'
                : '<i class="feather-power" style="color: red;"></i> Off';
        }
        
        // Reload data after a short delay to reflect server state
        setTimeout(() => {
            loadDevices();
            if (app.selectedDevice && app.selectedDevice.device_id === deviceId) {
                loadDeviceDetail(deviceId);
            }
        }, 2000);
    } catch (error) {
        console.error(`Error toggling power for device ${deviceId}:`, error);
        showError(`Failed to control device: ${error.message}`);
    }
}

/**
 * Set fan speed for a device
 */
async function setFanSpeed(deviceId, speed) {
    try {
        const response = await fetch(`/api/devices/${deviceId}/control/fan?speed=${speed}`, {
            method: 'POST',
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        showMessage(result.message, 'success');
        
        // Update the UI to reflect the new fan speed
        const speedDisplay = document.querySelector(`.fan-speed-display[data-device-id="${deviceId}"]`);
        if (speedDisplay) {
            speedDisplay.textContent = `${speed}%`;
        }
        
        // Reload data after a short delay to reflect server state
        setTimeout(() => {
            if (app.selectedDevice && app.selectedDevice.device_id === deviceId) {
                loadDeviceDetail(deviceId);
            }
        }, 2000);
    } catch (error) {
        console.error(`Error setting fan speed for device ${deviceId}:`, error);
        showError(`Failed to control fan: ${error.message}`);
    }
}

/**
 * Trigger OTA update for a device
 */
async function triggerOtaUpdate(deviceId) {
    try {
        // Show a confirmation dialog
        if (!confirm('Are you sure you want to trigger an OTA update for this device?')) {
            return;
        }
        
        const response = await fetch(`/api/devices/${deviceId}/trigger-update`, {
            method: 'POST',
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        showMessage(result.message, 'success');
    } catch (error) {
        console.error(`Error triggering OTA update for device ${deviceId}:`, error);
        showError(`Failed to trigger update: ${error.message}`);
    }
}

/**
 * Render the device list
 */
function renderDeviceList(devices) {
    if (!elements.deviceList) return;
    
    elements.deviceList.innerHTML = '';
    
    if (devices.length === 0) {
        elements.deviceList.innerHTML = `
            <div class="empty-state">
                <i class="feather-alert-circle"></i>
                <p>No devices found</p>
            </div>
        `;
        return;
    }
    
    devices.forEach(device => {
        const deviceEl = document.createElement('div');
        deviceEl.className = 'device-item';
        deviceEl.classList.add(device.is_online ? 'online' : 'offline');
        
        deviceEl.innerHTML = `
            <div class="device-header">
                <h3>${device.name}</h3>
                <span class="device-status ${device.is_online ? 'online' : 'offline'}">
                    ${device.is_online ? 'Online' : 'Offline'}
                </span>
            </div>
            <div class="device-info">
                <p><strong>ID:</strong> ${device.device_id}</p>
                <p><strong>Type:</strong> ${device.type}</p>
                <p><strong>Firmware:</strong> ${device.firmware_version || 'Unknown'}</p>
            </div>
            <div class="device-controls">
                <button class="power-toggle" data-device-id="${device.device_id}" data-state="${device.is_online}">
                    <i class="feather-power" style="color: ${device.is_online ? 'green' : 'red'};"></i>
                    ${device.is_online ? 'On' : 'Off'}
                </button>
                <a href="/devices?device=${device.device_id}" class="btn btn-outline">
                    <i class="feather-info"></i> Details
                </a>
            </div>
        `;
        
        elements.deviceList.appendChild(deviceEl);
    });
}

/**
 * Render device detail
 */
function renderDeviceDetail(device) {
    if (!elements.deviceDetail) return;
    
    elements.deviceDetail.innerHTML = `
        <div class="device-detail-header">
            <h2>${device.name}</h2>
            <span class="device-status ${device.is_online ? 'online' : 'offline'}">
                ${device.is_online ? 'Online' : 'Offline'}
            </span>
        </div>
        
        <div class="device-metadata">
            <div class="metadata-item">
                <span class="label">Device ID</span>
                <span class="value">${device.device_id}</span>
            </div>
            <div class="metadata-item">
                <span class="label">Type</span>
                <span class="value">${device.type}</span>
            </div>
            <div class="metadata-item">
                <span class="label">Firmware</span>
                <span class="value">${device.firmware_version || 'Unknown'}</span>
            </div>
            <div class="metadata-item">
                <span class="label">IP Address</span>
                <span class="value">${device.ip_address || 'Unknown'}</span>
            </div>
            <div class="metadata-item">
                <span class="label">MAC Address</span>
                <span class="value">${device.mac_address || 'Unknown'}</span>
            </div>
            <div class="metadata-item">
                <span class="label">Last Seen</span>
                <span class="value">${device.last_seen ? new Date(device.last_seen).toLocaleString() : 'Never'}</span>
            </div>
        </div>
        
        <div class="device-controls-panel">
            <h3>Device Controls</h3>
            <div class="control-group">
                <label>Power</label>
                <button class="power-toggle" data-device-id="${device.device_id}" data-state="${device.is_online}">
                    <i class="feather-power" style="color: ${device.is_online ? 'green' : 'red'};"></i>
                    ${device.is_online ? 'On' : 'Off'}
                </button>
            </div>
            
            <div class="control-group">
                <label>Fan Speed: <span class="fan-speed-display" data-device-id="${device.device_id}">0%</span></label>
                <div class="fan-speed-buttons">
                    <button class="fan-control" data-device-id="${device.device_id}" data-speed="0">Off</button>
                    <button class="fan-control" data-device-id="${device.device_id}" data-speed="25">25%</button>
                    <button class="fan-control" data-device-id="${device.device_id}" data-speed="50">50%</button>
                    <button class="fan-control" data-device-id="${device.device_id}" data-speed="75">75%</button>
                    <button class="fan-control" data-device-id="${device.device_id}" data-speed="100">100%</button>
                </div>
            </div>
        </div>
        
        <div class="device-maintenance">
            <h3>Maintenance</h3>
            <button class="trigger-update" data-device-id="${device.device_id}">
                <i class="feather-download-cloud"></i> Check for Updates
            </button>
        </div>
        
        <div class="device-readings">
            <h3>Sensor Readings</h3>
            <div id="readings-container">
                <div class="loading">Loading readings...</div>
            </div>
        </div>
    `;
}

/**
 * Render device readings
 */
function renderDeviceReadings(readings) {
    const container = document.getElementById('readings-container');
    if (!container) return;
    
    if (readings.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="feather-alert-circle"></i>
                <p>No readings available</p>
            </div>
        `;
        return;
    }
    
    // Create a readings table
    container.innerHTML = `
        <table class="readings-table">
            <thead>
                <tr>
                    <th>Time</th>
                    <th>Temperature</th>
                    <th>Humidity</th>
                    <th>Pressure</th>
                    <th>Fan Speed</th>
                    <th>Power</th>
                </tr>
            </thead>
            <tbody id="readings-tbody"></tbody>
        </table>
    `;
    
    const tbody = document.getElementById('readings-tbody');
    readings.forEach(reading => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${new Date(reading.timestamp).toLocaleString()}</td>
            <td>${reading.temperature !== null ? reading.temperature + '°C' : '-'}</td>
            <td>${reading.humidity !== null ? reading.humidity + '%' : '-'}</td>
            <td>${reading.pressure !== null ? reading.pressure + ' hPa' : '-'}</td>
            <td>${reading.fan_speed !== null ? reading.fan_speed + '%' : '-'}</td>
            <td>${reading.power_consumption !== null ? reading.power_consumption + ' W' : '-'}</td>
        `;
        tbody.appendChild(row);
    });
    
    // If we have temperature and humidity data, render a chart
    if (readings.some(r => r.temperature !== null || r.humidity !== null)) {
        renderReadingsChart(readings);
    }
}

/**
 * Render a chart for device readings
 */
function renderReadingsChart(readings) {
    // Create a container for the chart
    const container = document.getElementById('readings-container');
    const chartContainer = document.createElement('div');
    chartContainer.id = 'readings-chart';
    chartContainer.classList.add('chart-container');
    container.insertBefore(chartContainer, container.firstChild);
    
    // Prepare data for the chart
    const timestamps = readings.map(r => new Date(r.timestamp).toLocaleString());
    const temperatures = readings.map(r => r.temperature);
    const humidities = readings.map(r => r.humidity);
    
    // Create a chart using Chart.js
    const ctx = document.createElement('canvas');
    chartContainer.appendChild(ctx);
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: timestamps.reverse(),
            datasets: [
                {
                    label: 'Temperature (°C)',
                    data: temperatures.reverse(),
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.1)',
                    yAxisID: 'y',
                },
                {
                    label: 'Humidity (%)',
                    data: humidities.reverse(),
                    borderColor: 'rgb(54, 162, 235)',
                    backgroundColor: 'rgba(54, 162, 235, 0.1)',
                    yAxisID: 'y1',
                }
            ]
        },
        options: {
            responsive: true,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Temperature (°C)'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Humidity (%)'
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
                }
            }
        }
    });
}

/**
 * Render system status
 */
function renderSystemStatus(status) {
    if (!elements.systemStatus) return;
    
    elements.systemStatus.innerHTML = `
        <div class="status-card">
            <div class="status-header">
                <h3>System Overview</h3>
                <span class="timestamp">Last updated: ${new Date().toLocaleTimeString()}</span>
            </div>
            <div class="status-metrics">
                <div class="metric">
                    <span class="metric-value">${status.total_devices}</span>
                    <span class="metric-label">Total Devices</span>
                </div>
                <div class="metric">
                    <span class="metric-value">${status.online_devices}</span>
                    <span class="metric-label">Online</span>
                </div>
                <div class="metric">
                    <span class="metric-value">${status.offline_devices}</span>
                    <span class="metric-label">Offline</span>
                </div>
            </div>
        </div>
    `;
}

/**
 * Show an error message
 */
function showError(message) {
    if (!elements.errorContainer) return;
    
    const errorElement = document.createElement('div');
    errorElement.className = 'alert alert-error';
    errorElement.innerHTML = `
        <i class="feather-alert-triangle"></i>
        <span>${message}</span>
        <button class="close-button">&times;</button>
    `;
    
    // Add close button functionality
    errorElement.querySelector('.close-button').addEventListener('click', () => {
        errorElement.remove();
    });
    
    elements.errorContainer.appendChild(errorElement);
    
    // Auto-remove after 10 seconds
    setTimeout(() => {
        if (errorElement.parentNode) {
            errorElement.remove();
        }
    }, 10000);
}

/**
 * Show a message
 */
function showMessage(message, type = 'info') {
    if (!elements.errorContainer) return;
    
    const messageElement = document.createElement('div');
    messageElement.className = `alert alert-${type}`;
    
    let icon = 'info';
    if (type === 'success') icon = 'check-circle';
    if (type === 'warning') icon = 'alert-triangle';
    if (type === 'error') icon = 'alert-circle';
    
    messageElement.innerHTML = `
        <i class="feather-${icon}"></i>
        <span>${message}</span>
        <button class="close-button">&times;</button>
    `;
    
    // Add close button functionality
    messageElement.querySelector('.close-button').addEventListener('click', () => {
        messageElement.remove();
    });
    
    elements.errorContainer.appendChild(messageElement);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (messageElement.parentNode) {
            messageElement.remove();
        }
    }, 5000);
}
