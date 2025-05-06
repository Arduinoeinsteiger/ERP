/**
 * SwissAirDry ExApp - Hauptskript
 * 
 * Dieses Skript stellt die Hauptfunktionalität der SwissAirDry ExApp bereit und 
 * ist für das Rendering der Benutzeroberfläche und die Interaktion mit den APIs verantwortlich.
 */

// App-Namespace
const SwissAirDry = {
  // Konfiguration
  config: {
    demoMode: false,
    apiBaseUrl: '',
    updateInterval: 30000, // 30 Sekunden
    darkMode: false,
    language: 'de',
    useNextcloudAPI: true
  },
  
  // Aktueller Status/Daten
  state: {
    devices: [],
    alarms: [],
    dashboard: null,
    currentView: 'dashboard',
    apiStatus: false,
    mqttStatus: false,
    deckStatus: false,
    nextcloudAPIStatus: false,
    loading: true,
    error: null
  },
  
  // DOM-Elemente
  elements: {
    app: null,
    navigation: null,
    content: null,
    statusBar: null
  },
  
  /**
   * Initialisiert die App
   */
  async init() {
    console.log('SwissAirDry ExApp wird initialisiert');
    
    // URL-Parameter prüfen
    const urlParams = new URLSearchParams(window.location.search);
    this.config.demoMode = urlParams.get('demo') === 'true';
    
    if (this.config.demoMode) {
      console.log('Demo-Modus aktiviert');
    }
    
    // DOM-Elemente initialisieren
    this.elements.app = document.getElementById('swissairdry-app');
    if (!this.elements.app) {
      console.error('App-Container nicht gefunden');
      return;
    }
    
    // API-Basis-URL basierend auf der aktuellen Domain
    this.config.apiBaseUrl = `${window.location.origin}/api`;
    
    // Dark Mode aus Local Storage laden
    const storedDarkMode = localStorage.getItem('swissairdry_dark_mode');
    if (storedDarkMode !== null) {
      this.config.darkMode = storedDarkMode === 'true';
      this._applyDarkMode();
    }
    
    // Initialen DOM-Baum rendern
    this._renderAppStructure();
    
    // Nextcloud API initialisieren, falls gewünscht
    if (this.config.useNextcloudAPI && typeof nextcloudApi !== 'undefined') {
      try {
        await nextcloudApi.initialize();
        this.state.nextcloudAPIStatus = true;
        
        // Überprüfen, ob Deck verfügbar ist
        this.state.deckStatus = nextcloudApi.apiStatus.deck;
      } catch (error) {
        console.error('Fehler bei der Nextcloud API-Initialisierung:', error);
        this.state.nextcloudAPIStatus = false;
      }
    }
    
    // Erste Daten laden
    await this._loadInitialData();
    
    // Hashchange-Event-Listener für Navigation
    window.addEventListener('hashchange', () => this._handleRouteChange());
    
    // Initiale Route verarbeiten
    this._handleRouteChange();
    
    // Auto-Update starten
    this._startAutoUpdate();
    
    // App als geladen markieren
    this.state.loading = false;
    this._updateUI();
    
    console.log('SwissAirDry ExApp erfolgreich initialisiert');
  },
  
  /**
   * Rendert die grundlegende App-Struktur
   * @private
   */
  _renderAppStructure() {
    // Grundstruktur erstellen
    this.elements.app.innerHTML = `
      <div class="sard-container${this.config.darkMode ? ' dark-mode' : ''}">
        <header class="sard-header">
          <div class="sard-logo">
            <img src="img/swissairdry-logo.svg" alt="SwissAirDry Logo">
            <span>SwissAirDry</span>
          </div>
          <nav class="sard-nav">
            <ul>
              <li><a href="#dashboard" class="active" title="Dashboard"><i class="icon-dashboard"></i><span>Dashboard</span></a></li>
              <li><a href="#devices" title="Geräte"><i class="icon-category-monitoring"></i><span>Geräte</span></a></li>
              <li><a href="#alarms" title="Alarme"><i class="icon-alert"></i><span>Alarme</span></a></li>
              <li><a href="#settings" title="Einstellungen"><i class="icon-settings"></i><span>Einstellungen</span></a></li>
            </ul>
          </nav>
          <div class="sard-header-right">
            <button class="sard-refresh-btn" title="Aktualisieren"><i class="icon-refresh"></i></button>
            <button class="sard-dark-mode-toggle" title="Dark Mode umschalten">
              ${this.config.darkMode ? '<i class="icon-sun"></i>' : '<i class="icon-moon"></i>'}
            </button>
          </div>
        </header>
        
        <main class="sard-main">
          <div class="sard-content">
            <div class="sard-loading">
              <span class="icon-loading"></span>
              <span>Daten werden geladen...</span>
            </div>
          </div>
        </main>
        
        <footer class="sard-footer">
          <div class="sard-status-bar">
            <div class="sard-status-item" title="API-Status">
              <i class="icon-loading"></i> API
            </div>
            <div class="sard-status-item" title="MQTT-Status">
              <i class="icon-loading"></i> MQTT
            </div>
            <div class="sard-status-item" title="Deck-Integration">
              <i class="icon-loading"></i> Deck
            </div>
            <div class="sard-version">v1.0.0</div>
          </div>
        </footer>
      </div>
    `;
    
    // DOM-Referenzen aktualisieren
    this.elements.navigation = this.elements.app.querySelector('.sard-nav');
    this.elements.content = this.elements.app.querySelector('.sard-content');
    this.elements.statusBar = this.elements.app.querySelector('.sard-status-bar');
    
    // Event-Listener hinzufügen
    const refreshBtn = this.elements.app.querySelector('.sard-refresh-btn');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', () => this._refreshData());
    }
    
    const darkModeToggle = this.elements.app.querySelector('.sard-dark-mode-toggle');
    if (darkModeToggle) {
      darkModeToggle.addEventListener('click', () => this._toggleDarkMode());
    }
  },
  
  /**
   * Initialdaten laden
   * @private
   */
  async _loadInitialData() {
    try {
      // Status abrufen
      const statusData = await this._fetchData('/status');
      this.state.apiStatus = statusData.api || false;
      this.state.mqttStatus = statusData.mqtt || false;
      this.state.deckStatus = statusData.deck?.initialized || false;
      
      // Dashboard-Daten laden
      await this._loadDashboardData();
      
      // Status-Bar aktualisieren
      this._updateStatusBar();
    } catch (error) {
      console.error('Fehler beim Laden der Initialdaten:', error);
      this.state.error = 'Fehler beim Laden der Initialdaten. Bitte versuchen Sie es später erneut.';
    }
  },
  
  /**
   * Dashboard-Daten laden
   * @private
   */
  async _loadDashboardData() {
    try {
      const dashboardData = await this._fetchData('/dashboard');
      this.state.dashboard = dashboardData;
      this.state.devices = dashboardData.devices || [];
      this.state.alarms = dashboardData.alarms || [];
      
      // UI aktualisieren, wenn wir im Dashboard sind
      if (this.state.currentView === 'dashboard') {
        this._renderDashboard();
      }
    } catch (error) {
      console.error('Fehler beim Laden der Dashboard-Daten:', error);
      this.state.error = 'Fehler beim Laden der Dashboard-Daten. Bitte versuchen Sie es später erneut.';
      
      if (this.state.currentView === 'dashboard') {
        this._renderErrorState(this.state.error);
      }
    }
  },
  
  /**
   * Geräteliste laden
   * @private
   */
  async _loadDevices() {
    try {
      const deviceData = await this._fetchData('/devices');
      this.state.devices = deviceData.devices || [];
      
      // UI aktualisieren, wenn wir in der Geräteliste sind
      if (this.state.currentView === 'devices') {
        this._renderDeviceList();
      }
    } catch (error) {
      console.error('Fehler beim Laden der Geräteliste:', error);
      this.state.error = 'Fehler beim Laden der Geräteliste. Bitte versuchen Sie es später erneut.';
      
      if (this.state.currentView === 'devices') {
        this._renderErrorState(this.state.error);
      }
    }
  },
  
  /**
   * Alarmliste laden
   * @private
   */
  async _loadAlarms() {
    try {
      const alarmData = await this._fetchData('/alarms');
      this.state.alarms = alarmData.alarms || [];
      
      // UI aktualisieren, wenn wir in der Alarmliste sind
      if (this.state.currentView === 'alarms') {
        this._renderAlarmList();
      }
    } catch (error) {
      console.error('Fehler beim Laden der Alarmliste:', error);
      this.state.error = 'Fehler beim Laden der Alarmliste. Bitte versuchen Sie es später erneut.';
      
      if (this.state.currentView === 'alarms') {
        this._renderErrorState(this.state.error);
      }
    }
  },
  
  /**
   * Daten von der API abrufen
   * @param {string} endpoint - API-Endpunkt
   * @returns {Promise<Object>} - Die Antwortdaten
   * @private
   */
  async _fetchData(endpoint) {
    try {
      const response = await fetch(`${this.config.apiBaseUrl}${endpoint}`);
      
      if (!response.ok) {
        throw new Error(`HTTP Fehler: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`Fehler beim Abrufen von ${endpoint}:`, error);
      throw error;
    }
  },
  
  /**
   * Aktualisiert die Statusleiste basierend auf dem aktuellen Zustand
   * @private
   */
  _updateStatusBar() {
    const apiStatus = this.elements.statusBar.querySelector('.sard-status-item:nth-child(1)');
    const mqttStatus = this.elements.statusBar.querySelector('.sard-status-item:nth-child(2)');
    const deckStatus = this.elements.statusBar.querySelector('.sard-status-item:nth-child(3)');
    
    // API-Status
    if (apiStatus) {
      apiStatus.innerHTML = this.state.apiStatus
        ? '<i class="icon-checkmark"></i> API'
        : '<i class="icon-error"></i> API';
        
      apiStatus.classList.toggle('status-ok', this.state.apiStatus);
      apiStatus.classList.toggle('status-error', !this.state.apiStatus);
    }
    
    // MQTT-Status
    if (mqttStatus) {
      mqttStatus.innerHTML = this.state.mqttStatus
        ? '<i class="icon-checkmark"></i> MQTT'
        : '<i class="icon-error"></i> MQTT';
        
      mqttStatus.classList.toggle('status-ok', this.state.mqttStatus);
      mqttStatus.classList.toggle('status-error', !this.state.mqttStatus);
    }
    
    // Deck-Status
    if (deckStatus) {
      deckStatus.innerHTML = this.state.deckStatus
        ? '<i class="icon-checkmark"></i> Deck'
        : '<i class="icon-warning"></i> Deck';
        
      deckStatus.classList.toggle('status-ok', this.state.deckStatus);
      deckStatus.classList.toggle('status-warning', !this.state.deckStatus);
    }
  },
  
  /**
   * Startet den Auto-Update-Timer
   * @private
   */
  _startAutoUpdate() {
    // Bestehenden Timer löschen, falls vorhanden
    if (this._updateTimer) {
      clearInterval(this._updateTimer);
    }
    
    // Neuen Timer setzen
    this._updateTimer = setInterval(() => {
      this._refreshData();
    }, this.config.updateInterval);
  },
  
  /**
   * Aktualisiert die Daten manuell
   * @private
   */
  async _refreshData() {
    const refreshBtn = this.elements.app.querySelector('.sard-refresh-btn');
    if (refreshBtn) {
      refreshBtn.classList.add('rotating');
    }
    
    try {
      // Status aktualisieren
      const statusData = await this._fetchData('/status');
      this.state.apiStatus = statusData.api || false;
      this.state.mqttStatus = statusData.mqtt || false;
      this.state.deckStatus = statusData.deck?.initialized || false;
      
      // Daten basierend auf der aktuellen Ansicht aktualisieren
      switch (this.state.currentView) {
        case 'dashboard':
          await this._loadDashboardData();
          break;
        case 'devices':
          await this._loadDevices();
          break;
        case 'alarms':
          await this._loadAlarms();
          break;
      }
      
      // UI aktualisieren
      this._updateUI();
    } catch (error) {
      console.error('Fehler beim Aktualisieren der Daten:', error);
    } finally {
      // Refresh-Button-Animation stoppen
      if (refreshBtn) {
        refreshBtn.classList.remove('rotating');
      }
    }
  },
  
  /**
   * Verarbeitet Routen-Änderungen (Hash-basierte Navigation)
   * @private
   */
  _handleRouteChange() {
    const hash = window.location.hash.substring(1) || 'dashboard';
    
    // Aktive Navigation-Links updaten
    const navLinks = this.elements.navigation.querySelectorAll('a');
    navLinks.forEach(link => {
      const linkHash = link.getAttribute('href').substring(1);
      link.classList.toggle('active', linkHash === hash);
    });
    
    // Speichere aktuelle Ansicht und rendere entsprechend
    this.state.currentView = hash;
    
    switch (hash) {
      case 'dashboard':
        this._renderDashboard();
        break;
      case 'devices':
        this._loadDevices();
        break;
      case 'alarms':
        this._loadAlarms();
        break;
      case 'settings':
        this._renderSettings();
        break;
      default:
        this._renderDashboard();
    }
  },
  
  /**
   * Rendert das Dashboard
   * @private
   */
  _renderDashboard() {
    if (this.state.loading) {
      this._renderLoadingState();
      return;
    }
    
    if (this.state.error) {
      this._renderErrorState(this.state.error);
      return;
    }
    
    const dashboard = this.state.dashboard || {};
    const devices = this.state.devices || [];
    const recentAlarms = dashboard.recentAlarms || this.state.alarms?.slice(0, 5) || [];
    
    let deviceStatusCounts = {
      active: 0,
      inactive: 0,
      warning: 0,
      alarm: 0
    };
    
    // Gerätestatus zählen
    devices.forEach(device => {
      if (deviceStatusCounts[device.status] !== undefined) {
        deviceStatusCounts[device.status]++;
      }
    });
    
    // HTML für das Dashboard generieren
    const dashboardHtml = `
      <div class="sard-dashboard">
        <div class="sard-dashboard-header">
          <h1>Dashboard</h1>
          <div class="sard-last-updated">
            Zuletzt aktualisiert: ${new Date().toLocaleTimeString()}
          </div>
        </div>
        
        <div class="sard-dashboard-grid">
          <!-- Geräteübersicht -->
          <div class="sard-card sard-device-overview">
            <div class="sard-card-header">
              <h2>Geräteübersicht</h2>
              <a href="#devices" class="sard-card-link">Alle anzeigen</a>
            </div>
            <div class="sard-card-content">
              <div class="sard-status-boxes">
                <div class="sard-status-box status-active">
                  <div class="sard-status-value">${deviceStatusCounts.active}</div>
                  <div class="sard-status-label">Aktiv</div>
                </div>
                <div class="sard-status-box status-inactive">
                  <div class="sard-status-value">${deviceStatusCounts.inactive}</div>
                  <div class="sard-status-label">Inaktiv</div>
                </div>
                <div class="sard-status-box status-warning">
                  <div class="sard-status-value">${deviceStatusCounts.warning}</div>
                  <div class="sard-status-label">Warnung</div>
                </div>
                <div class="sard-status-box status-alarm">
                  <div class="sard-status-value">${deviceStatusCounts.alarm}</div>
                  <div class="sard-status-label">Alarm</div>
                </div>
              </div>
              
              <div class="sard-device-list-preview">
                <h3>Neueste Geräte</h3>
                <ul>
                  ${devices.slice(0, 5).map(device => `
                    <li class="sard-device-item status-${device.status}">
                      <div class="sard-device-icon">
                        <i class="icon-category-monitoring"></i>
                      </div>
                      <div class="sard-device-info">
                        <div class="sard-device-name">${device.name}</div>
                        <div class="sard-device-details">
                          <span class="sard-device-type">${device.type}</span>
                          <span class="sard-device-temperature">${device.temperature}°C</span>
                          <span class="sard-device-humidity">${device.humidity}%</span>
                        </div>
                      </div>
                      <div class="sard-device-status">
                        <span class="sard-status-indicator status-${device.status}"></span>
                      </div>
                    </li>
                  `).join('')}
                </ul>
              </div>
            </div>
          </div>
          
          <!-- Alarme -->
          <div class="sard-card sard-alarms-overview">
            <div class="sard-card-header">
              <h2>Neueste Alarme</h2>
              <a href="#alarms" class="sard-card-link">Alle anzeigen</a>
            </div>
            <div class="sard-card-content">
              ${recentAlarms.length > 0 ? `
                <ul class="sard-alarm-list-preview">
                  ${recentAlarms.map(alarm => `
                    <li class="sard-alarm-item severity-${alarm.severity}">
                      <div class="sard-alarm-icon">
                        <i class="icon-alert"></i>
                      </div>
                      <div class="sard-alarm-info">
                        <div class="sard-alarm-title">${alarm.title}</div>
                        <div class="sard-alarm-description">${alarm.description}</div>
                        <div class="sard-alarm-details">
                          <span class="sard-alarm-device">Gerät: ${alarm.device_id}</span>
                          <span class="sard-alarm-timestamp">${new Date(alarm.timestamp).toLocaleString()}</span>
                        </div>
                      </div>
                    </li>
                  `).join('')}
                </ul>
              ` : `
                <div class="sard-empty-state">
                  <i class="icon-checkmark"></i>
                  <p>Keine Alarme vorhanden</p>
                </div>
              `}
            </div>
          </div>
          
          <!-- Systemstatus -->
          <div class="sard-card sard-system-status">
            <div class="sard-card-header">
              <h2>Systemstatus</h2>
            </div>
            <div class="sard-card-content">
              <div class="sard-status-details">
                <div class="sard-status-detail-item ${this.state.apiStatus ? 'status-ok' : 'status-error'}">
                  <div class="sard-status-icon">
                    ${this.state.apiStatus ? '<i class="icon-checkmark"></i>' : '<i class="icon-error"></i>'}
                  </div>
                  <div class="sard-status-text">
                    <div class="sard-status-title">API</div>
                    <div class="sard-status-value">${this.state.apiStatus ? 'Verbunden' : 'Fehler'}</div>
                  </div>
                </div>
                
                <div class="sard-status-detail-item ${this.state.mqttStatus ? 'status-ok' : 'status-error'}">
                  <div class="sard-status-icon">
                    ${this.state.mqttStatus ? '<i class="icon-checkmark"></i>' : '<i class="icon-error"></i>'}
                  </div>
                  <div class="sard-status-text">
                    <div class="sard-status-title">MQTT</div>
                    <div class="sard-status-value">${this.state.mqttStatus ? 'Verbunden' : 'Fehler'}</div>
                  </div>
                </div>
                
                <div class="sard-status-detail-item ${this.state.deckStatus ? 'status-ok' : 'status-warning'}">
                  <div class="sard-status-icon">
                    ${this.state.deckStatus ? '<i class="icon-checkmark"></i>' : '<i class="icon-warning"></i>'}
                  </div>
                  <div class="sard-status-text">
                    <div class="sard-status-title">Deck Integration</div>
                    <div class="sard-status-value">${this.state.deckStatus ? 'Aktiv' : 'Inaktiv'}</div>
                  </div>
                </div>
                
                <div class="sard-status-detail-item ${this.state.nextcloudAPIStatus ? 'status-ok' : 'status-warning'}">
                  <div class="sard-status-icon">
                    ${this.state.nextcloudAPIStatus ? '<i class="icon-checkmark"></i>' : '<i class="icon-warning"></i>'}
                  </div>
                  <div class="sard-status-text">
                    <div class="sard-status-title">Nextcloud API</div>
                    <div class="sard-status-value">${this.state.nextcloudAPIStatus ? 'Verbunden' : 'Nicht verfügbar'}</div>
                  </div>
                </div>
              </div>
              
              <!-- Nextcloud Integration Actions -->
              ${this.state.nextcloudAPIStatus ? `
                <div class="sard-nextcloud-actions">
                  <h3>Nextcloud Integration</h3>
                  <div class="sard-action-buttons">
                    <button class="sard-btn sard-btn-primary sard-create-board-btn">
                      <i class="icon-add"></i> SwissAirDry Board erstellen
                    </button>
                    <button class="sard-btn sard-btn-warning sard-create-alarm-board-btn">
                      <i class="icon-add"></i> Alarm-Board erstellen
                    </button>
                  </div>
                </div>
              ` : ''}
            </div>
          </div>
        </div>
      </div>
    `;
    
    // Render und Event-Listener hinzufügen
    this.elements.content.innerHTML = dashboardHtml;
    
    // Event-Listener für Nextcloud Integration
    if (this.state.nextcloudAPIStatus) {
      const createBoardBtn = this.elements.content.querySelector('.sard-create-board-btn');
      const createAlarmBoardBtn = this.elements.content.querySelector('.sard-create-alarm-board-btn');
      
      if (createBoardBtn) {
        createBoardBtn.addEventListener('click', async () => {
          try {
            createBoardBtn.disabled = true;
            createBoardBtn.innerHTML = '<i class="icon-loading"></i> Wird erstellt...';
            
            const board = await nextcloudApi.createSwissAirDryBoard();
            
            createBoardBtn.innerHTML = '<i class="icon-checkmark"></i> Board erstellt';
            createBoardBtn.classList.add('sard-btn-success');
            
            // Status aktualisieren
            this.state.deckStatus = true;
            this._updateStatusBar();
            
            setTimeout(() => {
              createBoardBtn.disabled = false;
              createBoardBtn.innerHTML = '<i class="icon-add"></i> SwissAirDry Board erstellen';
              createBoardBtn.classList.remove('sard-btn-success');
            }, 3000);
          } catch (error) {
            console.error('Fehler beim Erstellen des Boards:', error);
            createBoardBtn.innerHTML = '<i class="icon-error"></i> Fehler';
            createBoardBtn.classList.add('sard-btn-danger');
            
            setTimeout(() => {
              createBoardBtn.disabled = false;
              createBoardBtn.innerHTML = '<i class="icon-add"></i> SwissAirDry Board erstellen';
              createBoardBtn.classList.remove('sard-btn-danger');
            }, 3000);
          }
        });
      }
      
      if (createAlarmBoardBtn) {
        createAlarmBoardBtn.addEventListener('click', async () => {
          try {
            createAlarmBoardBtn.disabled = true;
            createAlarmBoardBtn.innerHTML = '<i class="icon-loading"></i> Wird erstellt...';
            
            const board = await nextcloudApi.createAlarmBoard();
            
            createAlarmBoardBtn.innerHTML = '<i class="icon-checkmark"></i> Board erstellt';
            createAlarmBoardBtn.classList.add('sard-btn-success');
            
            // Status aktualisieren
            this.state.deckStatus = true;
            this._updateStatusBar();
            
            setTimeout(() => {
              createAlarmBoardBtn.disabled = false;
              createAlarmBoardBtn.innerHTML = '<i class="icon-add"></i> Alarm-Board erstellen';
              createAlarmBoardBtn.classList.remove('sard-btn-success');
            }, 3000);
          } catch (error) {
            console.error('Fehler beim Erstellen des Alarm-Boards:', error);
            createAlarmBoardBtn.innerHTML = '<i class="icon-error"></i> Fehler';
            createAlarmBoardBtn.classList.add('sard-btn-danger');
            
            setTimeout(() => {
              createAlarmBoardBtn.disabled = false;
              createAlarmBoardBtn.innerHTML = '<i class="icon-add"></i> Alarm-Board erstellen';
              createAlarmBoardBtn.classList.remove('sard-btn-danger');
            }, 3000);
          }
        });
      }
    }
  },
  
  /**
   * Rendert die Geräteliste
   * @private
   */
  _renderDeviceList() {
    if (this.state.loading) {
      this._renderLoadingState();
      return;
    }
    
    if (this.state.error) {
      this._renderErrorState(this.state.error);
      return;
    }
    
    const devices = this.state.devices || [];
    
    // HTML für die Geräteliste generieren
    const devicesHtml = `
      <div class="sard-devices">
        <div class="sard-dashboard-header">
          <h1>Geräte</h1>
          <div class="sard-last-updated">
            Zuletzt aktualisiert: ${new Date().toLocaleTimeString()}
          </div>
        </div>
        
        <div class="sard-card">
          <div class="sard-card-header">
            <h2>Geräteliste</h2>
            <div class="sard-filters">
              <select class="sard-filter-select" id="device-filter">
                <option value="all">Alle Geräte</option>
                <option value="active">Nur aktive</option>
                <option value="inactive">Nur inaktive</option>
                <option value="warning">Mit Warnungen</option>
                <option value="alarm">Mit Alarmen</option>
              </select>
              <input type="text" class="sard-search-input" id="device-search" placeholder="Gerät suchen...">
            </div>
          </div>
          <div class="sard-card-content">
            ${devices.length > 0 ? `
              <div class="sard-device-grid">
                ${devices.map(device => `
                  <div class="sard-device-card status-${device.status}" data-device-id="${device.id}">
                    <div class="sard-device-card-header">
                      <div class="sard-device-name">${device.name}</div>
                      <div class="sard-device-status">
                        <span class="sard-status-indicator status-${device.status}"></span>
                        <span class="sard-status-text">${this._getStatusText(device.status)}</span>
                      </div>
                    </div>
                    <div class="sard-device-card-content">
                      <div class="sard-device-type">
                        <i class="icon-category-monitoring"></i>
                        <span>${device.type}</span>
                      </div>
                      <div class="sard-device-sensors">
                        <div class="sard-sensor">
                          <i class="icon-temperature"></i>
                          <span>${device.temperature}°C</span>
                        </div>
                        <div class="sard-sensor">
                          <i class="icon-humidity"></i>
                          <span>${device.humidity}%</span>
                        </div>
                        <div class="sard-sensor">
                          <i class="icon-battery"></i>
                          <span>${device.battery}%</span>
                        </div>
                      </div>
                      <div class="sard-device-last-seen">
                        Zuletzt gesehen: ${new Date(device.last_seen).toLocaleString()}
                      </div>
                    </div>
                    <div class="sard-device-card-footer">
                      <button class="sard-btn sard-btn-detail" data-device-id="${device.id}">
                        Details
                      </button>
                      ${this.state.nextcloudAPIStatus ? `
                        <button class="sard-btn sard-btn-add-to-deck" data-device-id="${device.id}">
                          Zu Deck hinzufügen
                        </button>
                      ` : ''}
                    </div>
                  </div>
                `).join('')}
              </div>
            ` : `
              <div class="sard-empty-state">
                <i class="icon-category-monitoring"></i>
                <p>Keine Geräte gefunden</p>
              </div>
            `}
          </div>
        </div>
      </div>
    `;
    
    // Rendern und Event-Listener hinzufügen
    this.elements.content.innerHTML = devicesHtml;
    
    // Filter-Event-Listener
    const filterSelect = document.getElementById('device-filter');
    const searchInput = document.getElementById('device-search');
    
    if (filterSelect) {
      filterSelect.addEventListener('change', () => this._filterDevices());
    }
    
    if (searchInput) {
      searchInput.addEventListener('input', () => this._filterDevices());
    }
    
    // Detail-Button-Event-Listener
    const detailButtons = this.elements.content.querySelectorAll('.sard-btn-detail');
    detailButtons.forEach(button => {
      button.addEventListener('click', (event) => {
        const deviceId = event.target.dataset.deviceId;
        this._showDeviceDetails(deviceId);
      });
    });
    
    // Deck-Button-Event-Listener
    if (this.state.nextcloudAPIStatus) {
      const deckButtons = this.elements.content.querySelectorAll('.sard-btn-add-to-deck');
      deckButtons.forEach(button => {
        button.addEventListener('click', async (event) => {
          const deviceId = event.target.dataset.deviceId;
          await this._addDeviceToDeck(deviceId);
        });
      });
    }
  },
  
  /**
   * Filtert die Geräteliste basierend auf dem ausgewählten Filter und der Suche
   * @private
   */
  _filterDevices() {
    const filterSelect = document.getElementById('device-filter');
    const searchInput = document.getElementById('device-search');
    
    if (!filterSelect || !searchInput) return;
    
    const filterValue = filterSelect.value;
    const searchValue = searchInput.value.toLowerCase();
    
    const deviceCards = this.elements.content.querySelectorAll('.sard-device-card');
    
    deviceCards.forEach(card => {
      const deviceId = card.dataset.deviceId;
      const device = this.state.devices.find(d => d.id === deviceId);
      
      if (!device) return;
      
      // Filter überprüfen
      let matchesFilter = filterValue === 'all' || device.status === filterValue;
      
      // Suche überprüfen
      let matchesSearch = device.name.toLowerCase().includes(searchValue) ||
                          device.id.toLowerCase().includes(searchValue) ||
                          device.type.toLowerCase().includes(searchValue);
      
      // Sichtbarkeit setzen
      card.style.display = matchesFilter && matchesSearch ? 'block' : 'none';
    });
  },
  
  /**
   * Zeigt Details zu einem Gerät an
   * @param {string} deviceId - ID des Geräts
   * @private
   */
  async _showDeviceDetails(deviceId) {
    try {
      // Lade Details vom Gerät
      const device = await this._fetchData(`/devices/${deviceId}`);
      
      // Modal erstellen
      const modalHtml = `
        <div class="sard-modal">
          <div class="sard-modal-overlay"></div>
          <div class="sard-modal-container">
            <div class="sard-modal-header">
              <h2>${device.name}</h2>
              <button class="sard-modal-close">&times;</button>
            </div>
            <div class="sard-modal-body">
              <div class="sard-device-detail-grid">
                <div class="sard-device-info-section">
                  <h3>Geräteinformationen</h3>
                  <div class="sard-info-item">
                    <div class="sard-info-label">ID:</div>
                    <div class="sard-info-value">${device.id}</div>
                  </div>
                  <div class="sard-info-item">
                    <div class="sard-info-label">Typ:</div>
                    <div class="sard-info-value">${device.type}</div>
                  </div>
                  <div class="sard-info-item">
                    <div class="sard-info-label">Status:</div>
                    <div class="sard-info-value">
                      <span class="sard-status-indicator status-${device.status}"></span>
                      ${this._getStatusText(device.status)}
                    </div>
                  </div>
                  <div class="sard-info-item">
                    <div class="sard-info-label">Zuletzt gesehen:</div>
                    <div class="sard-info-value">${new Date(device.last_seen).toLocaleString()}</div>
                  </div>
                </div>
                
                <div class="sard-device-sensors-section">
                  <h3>Sensoren</h3>
                  <div class="sard-sensor-grid">
                    <div class="sard-sensor-card">
                      <div class="sard-sensor-icon">
                        <i class="icon-temperature"></i>
                      </div>
                      <div class="sard-sensor-value">${device.temperature}°C</div>
                      <div class="sard-sensor-label">Temperatur</div>
                    </div>
                    
                    <div class="sard-sensor-card">
                      <div class="sard-sensor-icon">
                        <i class="icon-humidity"></i>
                      </div>
                      <div class="sard-sensor-value">${device.humidity}%</div>
                      <div class="sard-sensor-label">Luftfeuchtigkeit</div>
                    </div>
                    
                    <div class="sard-sensor-card">
                      <div class="sard-sensor-icon">
                        <i class="icon-battery${device.battery < 20 ? '-low' : ''}"></i>
                      </div>
                      <div class="sard-sensor-value">${device.battery}%</div>
                      <div class="sard-sensor-label">Batteriestand</div>
                    </div>
                    
                    <div class="sard-sensor-card">
                      <div class="sard-sensor-icon">
                        <i class="icon-pressure"></i>
                      </div>
                      <div class="sard-sensor-value">${device.pressure} hPa</div>
                      <div class="sard-sensor-label">Luftdruck</div>
                    </div>
                  </div>
                </div>
                
                ${device.location ? `
                  <div class="sard-device-location-section">
                    <h3>Standort</h3>
                    <div class="sard-info-item">
                      <div class="sard-info-label">Adresse:</div>
                      <div class="sard-info-value">${device.location.address}</div>
                    </div>
                    <div class="sard-info-item">
                      <div class="sard-info-label">Koordinaten:</div>
                      <div class="sard-info-value">
                        ${device.location.latitude}, ${device.location.longitude}
                      </div>
                    </div>
                    <!-- Hier könnte eine Karte eingebunden werden -->
                  </div>
                ` : ''}
              </div>
            </div>
            <div class="sard-modal-footer">
              <button class="sard-btn sard-btn-primary sard-modal-close-btn">Schließen</button>
              ${this.state.nextcloudAPIStatus ? `
                <button class="sard-btn sard-btn-secondary sard-add-to-deck-btn" data-device-id="${device.id}">
                  Zu Deck hinzufügen
                </button>
              ` : ''}
            </div>
          </div>
        </div>
      `;
      
      // Modal einfügen und anzeigen
      const modalElement = document.createElement('div');
      modalElement.innerHTML = modalHtml;
      document.body.appendChild(modalElement.firstChild);
      
      // Event-Listener für Modal-Schließen
      const modal = document.querySelector('.sard-modal');
      const closeBtn = modal.querySelector('.sard-modal-close');
      const closeBtnFooter = modal.querySelector('.sard-modal-close-btn');
      const overlay = modal.querySelector('.sard-modal-overlay');
      
      const closeModal = () => {
        modal.remove();
      };
      
      closeBtn.addEventListener('click', closeModal);
      closeBtnFooter.addEventListener('click', closeModal);
      overlay.addEventListener('click', closeModal);
      
      // Event-Listener für "Zu Deck hinzufügen"
      if (this.state.nextcloudAPIStatus) {
        const deckBtn = modal.querySelector('.sard-add-to-deck-btn');
        if (deckBtn) {
          deckBtn.addEventListener('click', async () => {
            await this._addDeviceToDeck(device.id);
          });
        }
      }
    } catch (error) {
      console.error(`Fehler beim Laden der Gerätedetails für ${deviceId}:`, error);
      this._showNotification('Fehler beim Laden der Gerätedetails', 'error');
    }
  },
  
  /**
   * Fügt ein Gerät zu Deck hinzu
   * @param {string} deviceId - ID des Geräts
   * @private
   */
  async _addDeviceToDeck(deviceId) {
    if (!this.state.nextcloudAPIStatus) {
      this._showNotification('Nextcloud API ist nicht verfügbar', 'error');
      return;
    }
    
    try {
      const device = this.state.devices.find(d => d.id === deviceId);
      
      if (!device) {
        throw new Error(`Gerät nicht gefunden: ${deviceId}`);
      }
      
      // Boards abrufen
      const boards = await nextcloudApi.getDeckBoards();
      let board = boards.find(b => b.title === 'SwissAirDry Geräte');
      
      // Board erstellen, wenn es nicht existiert
      if (!board) {
        board = await nextcloudApi.createSwissAirDryBoard();
      }
      
      // Stacks abrufen
      const stacks = await nextcloudApi.getDeckStacks(board.id);
      const firstStack = stacks[0];
      
      if (!firstStack) {
        throw new Error('Kein Stack gefunden');
      }
      
      // Karte erstellen
      const cardTitle = `${device.name} [${device.id}]`;
      const cardDescription = `Typ: ${device.type}\nStatus: ${this._getStatusText(device.status)}\nTemperatur: ${device.temperature}°C\nLuftfeuchtigkeit: ${device.humidity}%\nBatteriestand: ${device.battery}%\nZuletzt gesehen: ${new Date(device.last_seen).toLocaleString()}`;
      
      await nextcloudApi.createDeckCard(board.id, firstStack.id, cardTitle, cardDescription);
      
      this._showNotification(`Gerät ${device.id} wurde zu Deck hinzugefügt`, 'success');
    } catch (error) {
      console.error(`Fehler beim Hinzufügen des Geräts ${deviceId} zu Deck:`, error);
      this._showNotification('Fehler beim Hinzufügen zu Deck', 'error');
    }
  },
  
  /**
   * Rendert die Alarmliste
   * @private
   */
  _renderAlarmList() {
    if (this.state.loading) {
      this._renderLoadingState();
      return;
    }
    
    if (this.state.error) {
      this._renderErrorState(this.state.error);
      return;
    }
    
    const alarms = this.state.alarms || [];
    
    // HTML für die Alarmliste generieren
    const alarmsHtml = `
      <div class="sard-alarms">
        <div class="sard-dashboard-header">
          <h1>Alarme</h1>
          <div class="sard-last-updated">
            Zuletzt aktualisiert: ${new Date().toLocaleTimeString()}
          </div>
        </div>
        
        <div class="sard-card">
          <div class="sard-card-header">
            <h2>Alarmliste</h2>
            <div class="sard-filters">
              <select class="sard-filter-select" id="alarm-filter">
                <option value="all">Alle Alarme</option>
                <option value="critical">Nur kritische</option>
                <option value="high">Hohe Priorität</option>
                <option value="medium">Mittlere Priorität</option>
                <option value="low">Niedrige Priorität</option>
              </select>
              <input type="text" class="sard-search-input" id="alarm-search" placeholder="Alarm suchen...">
            </div>
          </div>
          <div class="sard-card-content">
            ${alarms.length > 0 ? `
              <div class="sard-alarm-list">
                ${alarms.map(alarm => `
                  <div class="sard-alarm-card severity-${alarm.severity}" data-alarm-id="${alarm.id}">
                    <div class="sard-alarm-card-header">
                      <div class="sard-alarm-severity">
                        <span class="sard-severity-indicator severity-${alarm.severity}"></span>
                        <span class="sard-severity-text">${this._getSeverityText(alarm.severity)}</span>
                      </div>
                      <div class="sard-alarm-timestamp">
                        ${new Date(alarm.timestamp).toLocaleString()}
                      </div>
                    </div>
                    <div class="sard-alarm-card-content">
                      <div class="sard-alarm-title">
                        <i class="icon-alert"></i>
                        <span>${alarm.title}</span>
                      </div>
                      <div class="sard-alarm-description">
                        ${alarm.description}
                      </div>
                      <div class="sard-alarm-device">
                        <i class="icon-category-monitoring"></i>
                        <span>Gerät: ${alarm.device_id}</span>
                      </div>
                    </div>
                    <div class="sard-alarm-card-footer">
                      <button class="sard-btn sard-btn-detail" data-alarm-id="${alarm.id}">
                        Details
                      </button>
                      ${this.state.nextcloudAPIStatus ? `
                        <button class="sard-btn sard-btn-add-to-deck" data-alarm-id="${alarm.id}">
                          Zu Deck hinzufügen
                        </button>
                      ` : ''}
                    </div>
                  </div>
                `).join('')}
              </div>
            ` : `
              <div class="sard-empty-state">
                <i class="icon-checkmark"></i>
                <p>Keine Alarme gefunden</p>
              </div>
            `}
          </div>
        </div>
      </div>
    `;
    
    // Rendern und Event-Listener hinzufügen
    this.elements.content.innerHTML = alarmsHtml;
    
    // Filter-Event-Listener
    const filterSelect = document.getElementById('alarm-filter');
    const searchInput = document.getElementById('alarm-search');
    
    if (filterSelect) {
      filterSelect.addEventListener('change', () => this._filterAlarms());
    }
    
    if (searchInput) {
      searchInput.addEventListener('input', () => this._filterAlarms());
    }
    
    // Detail-Button-Event-Listener
    const detailButtons = this.elements.content.querySelectorAll('.sard-btn-detail');
    detailButtons.forEach(button => {
      button.addEventListener('click', (event) => {
        const alarmId = event.target.dataset.alarmId;
        this._showAlarmDetails(alarmId);
      });
    });
    
    // Deck-Button-Event-Listener
    if (this.state.nextcloudAPIStatus) {
      const deckButtons = this.elements.content.querySelectorAll('.sard-btn-add-to-deck');
      deckButtons.forEach(button => {
        button.addEventListener('click', async (event) => {
          const alarmId = event.target.dataset.alarmId;
          await this._addAlarmToDeck(alarmId);
        });
      });
    }
  },
  
  /**
   * Filtert die Alarmliste basierend auf dem ausgewählten Filter und der Suche
   * @private
   */
  _filterAlarms() {
    const filterSelect = document.getElementById('alarm-filter');
    const searchInput = document.getElementById('alarm-search');
    
    if (!filterSelect || !searchInput) return;
    
    const filterValue = filterSelect.value;
    const searchValue = searchInput.value.toLowerCase();
    
    const alarmCards = this.elements.content.querySelectorAll('.sard-alarm-card');
    
    alarmCards.forEach(card => {
      const alarmId = card.dataset.alarmId;
      const alarm = this.state.alarms.find(a => a.id === alarmId);
      
      if (!alarm) return;
      
      // Filter überprüfen
      let matchesFilter = filterValue === 'all' || alarm.severity === filterValue;
      
      // Suche überprüfen
      let matchesSearch = alarm.title.toLowerCase().includes(searchValue) ||
                          alarm.description.toLowerCase().includes(searchValue) ||
                          alarm.device_id.toLowerCase().includes(searchValue);
      
      // Sichtbarkeit setzen
      card.style.display = matchesFilter && matchesSearch ? 'block' : 'none';
    });
  },
  
  /**
   * Zeigt Details zu einem Alarm an
   * @param {string} alarmId - ID des Alarms
   * @private
   */
  _showAlarmDetails(alarmId) {
    const alarm = this.state.alarms.find(a => a.id === alarmId);
    
    if (!alarm) {
      this._showNotification('Alarm nicht gefunden', 'error');
      return;
    }
    
    // Modal erstellen
    const modalHtml = `
      <div class="sard-modal">
        <div class="sard-modal-overlay"></div>
        <div class="sard-modal-container">
          <div class="sard-modal-header">
            <h2>${alarm.title}</h2>
            <button class="sard-modal-close">&times;</button>
          </div>
          <div class="sard-modal-body">
            <div class="sard-alarm-detail-grid">
              <div class="sard-alarm-info-section">
                <h3>Alarminformationen</h3>
                <div class="sard-info-item">
                  <div class="sard-info-label">ID:</div>
                  <div class="sard-info-value">${alarm.id}</div>
                </div>
                <div class="sard-info-item">
                  <div class="sard-info-label">Typ:</div>
                  <div class="sard-info-value">${alarm.type}</div>
                </div>
                <div class="sard-info-item">
                  <div class="sard-info-label">Schweregrad:</div>
                  <div class="sard-info-value">
                    <span class="sard-severity-indicator severity-${alarm.severity}"></span>
                    ${this._getSeverityText(alarm.severity)}
                  </div>
                </div>
                <div class="sard-info-item">
                  <div class="sard-info-label">Zeitstempel:</div>
                  <div class="sard-info-value">${new Date(alarm.timestamp).toLocaleString()}</div>
                </div>
                <div class="sard-info-item">
                  <div class="sard-info-label">Gerät:</div>
                  <div class="sard-info-value">${alarm.device_id}</div>
                </div>
              </div>
              
              <div class="sard-alarm-description-section">
                <h3>Beschreibung</h3>
                <div class="sard-alarm-description-text">
                  ${alarm.description}
                </div>
              </div>
            </div>
          </div>
          <div class="sard-modal-footer">
            <button class="sard-btn sard-btn-primary sard-modal-close-btn">Schließen</button>
            ${this.state.nextcloudAPIStatus ? `
              <button class="sard-btn sard-btn-secondary sard-add-to-deck-btn" data-alarm-id="${alarm.id}">
                Zu Deck hinzufügen
              </button>
            ` : ''}
          </div>
        </div>
      </div>
    `;
    
    // Modal einfügen und anzeigen
    const modalElement = document.createElement('div');
    modalElement.innerHTML = modalHtml;
    document.body.appendChild(modalElement.firstChild);
    
    // Event-Listener für Modal-Schließen
    const modal = document.querySelector('.sard-modal');
    const closeBtn = modal.querySelector('.sard-modal-close');
    const closeBtnFooter = modal.querySelector('.sard-modal-close-btn');
    const overlay = modal.querySelector('.sard-modal-overlay');
    
    const closeModal = () => {
      modal.remove();
    };
    
    closeBtn.addEventListener('click', closeModal);
    closeBtnFooter.addEventListener('click', closeModal);
    overlay.addEventListener('click', closeModal);
    
    // Event-Listener für "Zu Deck hinzufügen"
    if (this.state.nextcloudAPIStatus) {
      const deckBtn = modal.querySelector('.sard-add-to-deck-btn');
      if (deckBtn) {
        deckBtn.addEventListener('click', async () => {
          await this._addAlarmToDeck(alarm.id);
        });
      }
    }
  },
  
  /**
   * Fügt einen Alarm zu Deck hinzu
   * @param {string} alarmId - ID des Alarms
   * @private
   */
  async _addAlarmToDeck(alarmId) {
    if (!this.state.nextcloudAPIStatus) {
      this._showNotification('Nextcloud API ist nicht verfügbar', 'error');
      return;
    }
    
    try {
      const alarm = this.state.alarms.find(a => a.id === alarmId);
      
      if (!alarm) {
        throw new Error(`Alarm nicht gefunden: ${alarmId}`);
      }
      
      // Boards abrufen
      const boards = await nextcloudApi.getDeckBoards();
      let board = boards.find(b => b.title === 'SwissAirDry Alarme');
      
      // Board erstellen, wenn es nicht existiert
      if (!board) {
        board = await nextcloudApi.createAlarmBoard();
      }
      
      // Stacks abrufen
      const stacks = await nextcloudApi.getDeckStacks(board.id);
      const firstStack = stacks[0];
      
      if (!firstStack) {
        throw new Error('Kein Stack gefunden');
      }
      
      // Karte erstellen
      await nextcloudApi.createAlarmCard(alarm, board.id, firstStack.id);
      
      this._showNotification(`Alarm ${alarm.id} wurde zu Deck hinzugefügt`, 'success');
    } catch (error) {
      console.error(`Fehler beim Hinzufügen des Alarms ${alarmId} zu Deck:`, error);
      this._showNotification('Fehler beim Hinzufügen zu Deck', 'error');
    }
  },
  
  /**
   * Rendert die Einstellungsseite
   * @private
   */
  _renderSettings() {
    const settingsHtml = `
      <div class="sard-settings">
        <div class="sard-dashboard-header">
          <h1>Einstellungen</h1>
        </div>
        
        <div class="sard-card">
          <div class="sard-card-header">
            <h2>Anzeigeeinstellungen</h2>
          </div>
          <div class="sard-card-content">
            <div class="sard-settings-group">
              <div class="sard-setting-item">
                <div class="sard-setting-label">Dark Mode</div>
                <div class="sard-setting-control">
                  <label class="sard-toggle">
                    <input type="checkbox" id="dark-mode-toggle" ${this.config.darkMode ? 'checked' : ''}>
                    <span class="sard-toggle-slider"></span>
                  </label>
                </div>
              </div>
              
              <div class="sard-setting-item">
                <div class="sard-setting-label">Auto-Update-Intervall</div>
                <div class="sard-setting-control">
                  <select id="update-interval">
                    <option value="10000" ${this.config.updateInterval === 10000 ? 'selected' : ''}>10 Sekunden</option>
                    <option value="30000" ${this.config.updateInterval === 30000 ? 'selected' : ''}>30 Sekunden</option>
                    <option value="60000" ${this.config.updateInterval === 60000 ? 'selected' : ''}>1 Minute</option>
                    <option value="300000" ${this.config.updateInterval === 300000 ? 'selected' : ''}>5 Minuten</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="sard-card">
          <div class="sard-card-header">
            <h2>API-Einstellungen</h2>
          </div>
          <div class="sard-card-content">
            <div class="sard-settings-group">
              <div class="sard-setting-item">
                <div class="sard-setting-label">API-Basis-URL</div>
                <div class="sard-setting-control">
                  <input type="text" id="api-base-url" value="${this.config.apiBaseUrl}">
                </div>
              </div>
              
              <div class="sard-setting-item">
                <div class="sard-setting-label">Nextcloud API verwenden</div>
                <div class="sard-setting-control">
                  <label class="sard-toggle">
                    <input type="checkbox" id="use-nextcloud-api" ${this.config.useNextcloudAPI ? 'checked' : ''}>
                    <span class="sard-toggle-slider"></span>
                  </label>
                </div>
              </div>
            </div>
            
            <div class="sard-setting-actions">
              <button class="sard-btn sard-btn-primary" id="save-api-settings">Einstellungen speichern</button>
              <button class="sard-btn sard-btn-secondary" id="test-api-connection">API-Verbindung testen</button>
            </div>
          </div>
        </div>
        
        <div class="sard-card">
          <div class="sard-card-header">
            <h2>Über</h2>
          </div>
          <div class="sard-card-content">
            <div class="sard-about">
              <div class="sard-about-logo">
                <img src="img/swissairdry-logo.svg" alt="SwissAirDry Logo">
              </div>
              <div class="sard-about-info">
                <h3>SwissAirDry ExApp</h3>
                <p>Version 1.0.0</p>
                <p>Eine modulare IoT-Plattform zur Geräteverwaltung und Überwachung von Trocknungsgeräten</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
    
    // Rendern und Event-Listener hinzufügen
    this.elements.content.innerHTML = settingsHtml;
    
    // Dark Mode Toggle
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    if (darkModeToggle) {
      darkModeToggle.addEventListener('change', (event) => {
        this.config.darkMode = event.target.checked;
        this._applyDarkMode();
        localStorage.setItem('swissairdry_dark_mode', this.config.darkMode);
      });
    }
    
    // Update-Intervall
    const updateIntervalSelect = document.getElementById('update-interval');
    if (updateIntervalSelect) {
      updateIntervalSelect.addEventListener('change', (event) => {
        this.config.updateInterval = parseInt(event.target.value, 10);
        this._startAutoUpdate();
        localStorage.setItem('swissairdry_update_interval', this.config.updateInterval);
      });
    }
    
    // API-Einstellungen
    const apiBaseUrlInput = document.getElementById('api-base-url');
    const useNextcloudApiToggle = document.getElementById('use-nextcloud-api');
    const saveApiSettingsBtn = document.getElementById('save-api-settings');
    const testApiConnectionBtn = document.getElementById('test-api-connection');
    
    if (saveApiSettingsBtn) {
      saveApiSettingsBtn.addEventListener('click', () => {
        if (apiBaseUrlInput) {
          this.config.apiBaseUrl = apiBaseUrlInput.value;
        }
        
        if (useNextcloudApiToggle) {
          this.config.useNextcloudAPI = useNextcloudApiToggle.checked;
        }
        
        localStorage.setItem('swissairdry_api_base_url', this.config.apiBaseUrl);
        localStorage.setItem('swissairdry_use_nextcloud_api', this.config.useNextcloudAPI);
        
        this._showNotification('Einstellungen gespeichert', 'success');
      });
    }
    
    if (testApiConnectionBtn) {
      testApiConnectionBtn.addEventListener('click', async () => {
        testApiConnectionBtn.disabled = true;
        testApiConnectionBtn.innerHTML = '<i class="icon-loading"></i> Verbinde...';
        
        try {
          const apiBaseUrl = apiBaseUrlInput ? apiBaseUrlInput.value : this.config.apiBaseUrl;
          const response = await fetch(`${apiBaseUrl}/status`);
          
          if (response.ok) {
            const data = await response.json();
            this._showNotification('API-Verbindung erfolgreich', 'success');
            testApiConnectionBtn.innerHTML = '<i class="icon-checkmark"></i> Verbindung erfolgreich';
            testApiConnectionBtn.classList.add('sard-btn-success');
            
            setTimeout(() => {
              testApiConnectionBtn.disabled = false;
              testApiConnectionBtn.innerHTML = 'API-Verbindung testen';
              testApiConnectionBtn.classList.remove('sard-btn-success');
            }, 3000);
          } else {
            throw new Error(`HTTP Fehler: ${response.status}`);
          }
        } catch (error) {
          console.error('Fehler beim Testen der API-Verbindung:', error);
          this._showNotification('API-Verbindung fehlgeschlagen', 'error');
          testApiConnectionBtn.innerHTML = '<i class="icon-error"></i> Verbindung fehlgeschlagen';
          testApiConnectionBtn.classList.add('sard-btn-danger');
          
          setTimeout(() => {
            testApiConnectionBtn.disabled = false;
            testApiConnectionBtn.innerHTML = 'API-Verbindung testen';
            testApiConnectionBtn.classList.remove('sard-btn-danger');
          }, 3000);
        }
      });
    }
  },
  
  /**
   * Wechselt den Dark Mode ein/aus
   * @private
   */
  _toggleDarkMode() {
    this.config.darkMode = !this.config.darkMode;
    this._applyDarkMode();
    localStorage.setItem('swissairdry_dark_mode', this.config.darkMode);
  },
  
  /**
   * Wendet den Dark Mode auf die App an
   * @private
   */
  _applyDarkMode() {
    const container = this.elements.app.querySelector('.sard-container');
    if (container) {
      container.classList.toggle('dark-mode', this.config.darkMode);
    }
    
    const darkModeToggle = this.elements.app.querySelector('.sard-dark-mode-toggle');
    if (darkModeToggle) {
      darkModeToggle.innerHTML = this.config.darkMode ? '<i class="icon-sun"></i>' : '<i class="icon-moon"></i>';
    }
  },
  
  /**
   * Rendert einen Ladezustand
   * @private
   */
  _renderLoadingState() {
    this.elements.content.innerHTML = `
      <div class="sard-loading">
        <span class="icon-loading"></span>
        <span>Daten werden geladen...</span>
      </div>
    `;
  },
  
  /**
   * Rendert einen Fehlerzustand
   * @param {string} errorMessage - Fehlermeldung
   * @private
   */
  _renderErrorState(errorMessage) {
    this.elements.content.innerHTML = `
      <div class="sard-error">
        <i class="icon-error"></i>
        <h2>Fehler</h2>
        <p>${errorMessage}</p>
        <button class="sard-btn sard-btn-primary sard-retry-btn">
          <i class="icon-refresh"></i> Erneut versuchen
        </button>
      </div>
    `;
    
    const retryBtn = this.elements.content.querySelector('.sard-retry-btn');
    if (retryBtn) {
      retryBtn.addEventListener('click', () => {
        this.state.error = null;
        this._refreshData();
      });
    }
  },
  
  /**
   * Aktualisiert die Benutzeroberfläche
   * @private
   */
  _updateUI() {
    // Status-Bar aktualisieren
    this._updateStatusBar();
    
    // Aktuelle Ansicht neu rendern
    this._handleRouteChange();
  },
  
  /**
   * Zeigt eine Benachrichtigung an
   * @param {string} message - Nachrichtentext
   * @param {string} type - Typ der Benachrichtigung ('success', 'error', 'warning', 'info')
   * @private
   */
  _showNotification(message, type = 'info') {
    // Bestehende Benachrichtigungen prüfen
    const existingNotification = document.querySelector('.sard-notification');
    if (existingNotification) {
      existingNotification.remove();
    }
    
    // Benachrichtigung erstellen
    const notification = document.createElement('div');
    notification.className = `sard-notification notification-${type}`;
    
    let icon;
    switch (type) {
      case 'success':
        icon = 'checkmark';
        break;
      case 'error':
        icon = 'error';
        break;
      case 'warning':
        icon = 'warning';
        break;
      default:
        icon = 'info';
    }
    
    notification.innerHTML = `
      <div class="sard-notification-icon">
        <i class="icon-${icon}"></i>
      </div>
      <div class="sard-notification-content">
        ${message}
      </div>
      <button class="sard-notification-close">&times;</button>
    `;
    
    // Benachrichtigung einfügen
    document.body.appendChild(notification);
    
    // Event-Listener für Schließen-Button
    const closeBtn = notification.querySelector('.sard-notification-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        notification.classList.add('sard-notification-closing');
        setTimeout(() => {
          notification.remove();
        }, 300);
      });
    }
    
    // Automatisch ausblenden nach 5 Sekunden
    setTimeout(() => {
      if (document.body.contains(notification)) {
        notification.classList.add('sard-notification-closing');
        setTimeout(() => {
          if (document.body.contains(notification)) {
            notification.remove();
          }
        }, 300);
      }
    }, 5000);
  },
  
  /**
   * Gibt den Statustext für einen Gerätestatus zurück
   * @param {string} status - Gerätestatus
   * @returns {string} - Lesbarer Statustext
   * @private
   */
  _getStatusText(status) {
    switch (status) {
      case 'active':
        return 'Aktiv';
      case 'inactive':
        return 'Inaktiv';
      case 'warning':
        return 'Warnung';
      case 'alarm':
        return 'Alarm';
      default:
        return 'Unbekannt';
    }
  },
  
  /**
   * Gibt den Schweregrad-Text für einen Alarmschweregrad zurück
   * @param {string} severity - Alarmschweregrad
   * @returns {string} - Lesbarer Schweregrad-Text
   * @private
   */
  _getSeverityText(severity) {
    switch (severity) {
      case 'critical':
        return 'Kritisch';
      case 'high':
        return 'Hoch';
      case 'medium':
        return 'Mittel';
      case 'low':
        return 'Niedrig';
      default:
        return 'Unbekannt';
    }
  }
};

// App initialisieren, wenn das DOM geladen ist
document.addEventListener('DOMContentLoaded', () => {
  SwissAirDry.init();
});