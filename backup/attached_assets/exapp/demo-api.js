/**
 * Demo-API für die SwissAirDry ExApp
 * 
 * Dieses Skript stellt Testdaten für die Entwicklung bereit und kann in die
 * index.html inkludiert werden, um die App ohne Backend zu testen.
 */

class SwissAirDryDemoAPI {
  constructor() {
    this.devices = this.generateDevices(10);
    this.alarms = this.generateAlarms(15);
    
    // Simulierte API-Status
    this.apiStatus = true;
    this.mqttStatus = true;
    this.deckStatus = Math.random() > 0.3; // Zufällig an/aus
    
    console.log('SwissAirDry Demo-API initialisiert');
  }
  
  /**
   * Generiert zufällige Geräte für Testzwecke
   * @param {number} count - Anzahl zu generierender Geräte
   * @returns {Array} - Liste der Geräte
   */
  generateDevices(count) {
    const types = ['Lüfter', 'Luftentfeuchter', 'Kombigerät', 'Heizgerät'];
    const statusOptions = ['active', 'inactive', 'warning', 'alarm'];
    const locations = [
      { address: 'Musterstraße 1, 12345 Musterstadt', latitude: 48.137154, longitude: 11.576124 },
      { address: 'Beispielweg 42, 54321 Beispielhausen', latitude: 52.520008, longitude: 13.404954 },
      { address: 'Am Testplatz 7, 98765 Testdorf', latitude: 50.110924, longitude: 8.682127 },
    ];
    
    const devices = [];
    
    for (let i = 0; i < count; i++) {
      const deviceId = `SARD-${String(i + 1).padStart(3, '0')}`;
      const type = types[Math.floor(Math.random() * types.length)];
      const status = statusOptions[Math.floor(Math.random() * statusOptions.length)];
      const location = locations[Math.floor(Math.random() * locations.length)];
      
      // Erstelle Gerät mit zufälligen Sensorwerten
      const device = {
        id: deviceId,
        name: `${type} ${deviceId}`,
        type: type,
        status: status,
        temperature: Math.round((15 + Math.random() * 25) * 10) / 10, // 15-40°C
        humidity: Math.round(Math.random() * 100), // 0-100%
        battery: status === 'inactive' ? Math.round(Math.random() * 20) : Math.round(40 + Math.random() * 60), // 0-20% wenn inaktiv, sonst 40-100%
        pressure: Math.round(980 + Math.random() * 40), // 980-1020 hPa
        last_seen: new Date(Date.now() - Math.random() * 86400000 * 3).toISOString(), // 0-3 Tage in der Vergangenheit
        location: location
      };
      
      // Bei Warnungen oder Alarmen spezifischere Werte setzen
      if (status === 'warning' || status === 'alarm') {
        if (Math.random() > 0.5) {
          device.temperature = status === 'alarm' ? Math.round((35 + Math.random() * 15) * 10) / 10 : Math.round((30 + Math.random() * 5) * 10) / 10;
        } else {
          device.humidity = status === 'alarm' ? Math.round(90 + Math.random() * 10) : Math.round(80 + Math.random() * 10);
        }
      }
      
      devices.push(device);
    }
    
    return devices;
  }
  
  /**
   * Generiert zufällige Alarme für Testzwecke
   * @param {number} count - Anzahl zu generierender Alarme
   * @returns {Array} - Liste der Alarme
   */
  generateAlarms(count) {
    const types = ['temperature', 'humidity', 'connectivity', 'battery'];
    const severities = ['low', 'medium', 'high', 'critical'];
    const alarms = [];
    
    for (let i = 0; i < count; i++) {
      const type = types[Math.floor(Math.random() * types.length)];
      const severity = severities[Math.floor(Math.random() * severities.length)];
      const deviceIndex = Math.floor(Math.random() * this.devices.length);
      const device = this.devices[deviceIndex];
      
      // Bestimme Titel und Beschreibung basierend auf Typ
      let title, description;
      
      switch (type) {
        case 'temperature':
          const temp = Math.round((35 + Math.random() * 15) * 10) / 10;
          title = `Hohe Temperatur`;
          description = `Die Temperatur hat den Grenzwert überschritten: ${temp}°C`;
          break;
        case 'humidity':
          const humidity = Math.round(90 + Math.random() * 10);
          title = `Hohe Luftfeuchtigkeit`;
          description = `Die Luftfeuchtigkeit hat den Grenzwert überschritten: ${humidity}%`;
          break;
        case 'connectivity':
          title = `Verbindungsproblem`;
          description = `Das Gerät hat die Verbindung verloren. Letzte Kommunikation vor ${Math.round(Math.random() * 24)} Stunden.`;
          break;
        case 'battery':
          const battery = Math.round(Math.random() * 15);
          title = `Niedriger Batteriestand`;
          description = `Der Batteriestand ist kritisch niedrig: ${battery}%`;
          break;
      }
      
      // Erstelle Alarm
      const alarm = {
        id: `ALARM-${String(i + 1).padStart(3, '0')}`,
        type: type,
        title: title,
        description: description,
        severity: severity,
        device_id: device.id,
        timestamp: new Date(Date.now() - Math.random() * 604800000).toISOString(), // Bis zu 7 Tage in der Vergangenheit
      };
      
      alarms.push(alarm);
    }
    
    // Sortiere nach Zeitstempel, neueste zuerst
    return alarms.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  }
  
  /**
   * Liefert Mock-Daten für das Dashboard
   * @returns {Promise} - Promise mit Dashboard-Daten
   */
  async getDashboard() {
    // Kurze Verzögerung simulieren
    await new Promise(resolve => setTimeout(resolve, 300));
    
    return {
      devices: this.devices,
      alarms: this.alarms,
      recentAlarms: this.alarms.slice(0, 5),
      api_status: this.apiStatus,
      mqtt_status: this.mqttStatus,
      deck_status: this.deckStatus
    };
  }
  
  /**
   * Liefert Mock-Daten für Geräte
   * @returns {Promise} - Promise mit Gerätedaten
   */
  async getDevices() {
    // Kurze Verzögerung simulieren
    await new Promise(resolve => setTimeout(resolve, 400));
    
    return {
      devices: this.devices
    };
  }
  
  /**
   * Liefert Mock-Daten für ein bestimmtes Gerät
   * @param {string} deviceId - ID des Geräts
   * @returns {Promise} - Promise mit Gerätedaten
   */
  async getDevice(deviceId) {
    // Kurze Verzögerung simulieren
    await new Promise(resolve => setTimeout(resolve, 200));
    
    const device = this.devices.find(d => d.id === deviceId);
    
    if (!device) {
      throw new Error(`Gerät nicht gefunden: ${deviceId}`);
    }
    
    return device;
  }
  
  /**
   * Liefert Mock-Daten für Alarme
   * @returns {Promise} - Promise mit Alarmdaten
   */
  async getAlarms() {
    // Kurze Verzögerung simulieren
    await new Promise(resolve => setTimeout(resolve, 350));
    
    return {
      alarms: this.alarms
    };
  }
  
  /**
   * Liefert Mock-Statusdaten
   * @returns {Promise} - Promise mit Statusdaten
   */
  async getStatus() {
    // Kurze Verzögerung simulieren
    await new Promise(resolve => setTimeout(resolve, 100));
    
    return {
      status: 'ok',
      version: '1.0.0',
      api: this.apiStatus,
      mqtt: this.mqttStatus,
      deck: {
        available: true,
        initialized: this.deckStatus
      }
    };
  }
  
  /**
   * Simuliert einen API-Fehler mit bestimmter Wahrscheinlichkeit
   * @param {number} probability - Wahrscheinlichkeit eines Fehlers (0-1)
   * @throws {Error} - Wirft einen Fehler mit definierter Wahrscheinlichkeit
   */
  maybeError(probability = 0.1) {
    if (Math.random() < probability) {
      throw new Error('Simulierter API-Fehler');
    }
  }
}

// Singleton-Instanz
const demoApi = new SwissAirDryDemoAPI();

// Mock-Implementierung des globalen fetch für Demo-Zwecke
if (typeof window !== 'undefined' && window.location.search.includes('demo=true')) {
  console.log('Demo-Modus aktiviert, API-Anfragen werden simuliert');
  
  const originalFetch = window.fetch;
  
  window.fetch = function(url, options) {
    // Überprüfe, ob die URL eine API-Anfrage ist
    if (typeof url === 'string' && url.includes('/api/')) {
      return new Promise((resolve, reject) => {
        // Kurze Verzögerung simulieren
        setTimeout(async () => {
          try {
            let response;
            
            // Fehler mit geringer Wahrscheinlichkeit simulieren
            demoApi.maybeError(0.05);
            
            // API-Endpunkte simulieren
            if (url.includes('/status')) {
              response = await demoApi.getStatus();
            } else if (url.includes('/devices/') && url.split('/').length > 3) {
              const deviceId = url.split('/').pop();
              response = await demoApi.getDevice(deviceId);
            } else if (url.includes('/devices')) {
              response = await demoApi.getDevices();
            } else if (url.includes('/alarms')) {
              response = await demoApi.getAlarms();
            } else if (url.includes('/dashboard')) {
              response = await demoApi.getDashboard();
            } else {
              // Fallback auf Standard-Status
              response = await demoApi.getStatus();
            }
            
            // Response-Objekt simulieren
            resolve({
              ok: true,
              status: 200,
              json: () => Promise.resolve(response)
            });
          } catch (err) {
            // Fehlerobjekt simulieren
            resolve({
              ok: false,
              status: 500,
              json: () => Promise.resolve({ error: err.message })
            });
          }
        }, Math.random() * 300 + 100); // 100-400ms Verzögerung
      });
    }
    
    // Wenn keine API-Anfrage, verwende das originale fetch
    return originalFetch.apply(this, arguments);
  };
}