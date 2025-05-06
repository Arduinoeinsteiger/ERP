/**
 * Nextcloud API Integration für die SwissAirDry ExApp
 * 
 * Dieses Modul stellt Funktionen zur Verbindung mit der Nextcloud API bereit.
 * Es unterstützt die wichtigsten Nextcloud-API-Ressourcen wie:
 * - Deck API für Projektmanagement
 * - Datei-API (WebDAV) für Dokumentenverwaltung
 * - Benachrichtigungen API
 * - OCS API für Benutzerverwaltung
 */

class NextcloudAPI {
  constructor() {
    this.baseUrl = this._detectNextcloudBaseUrl();
    this.token = null;
    this.userId = null;
    this.initialized = false;
    
    // Status der API-Endpunkte
    this.apiStatus = {
      ocs: false,
      webdav: false,
      deck: false,
      notifications: false
    };
    
    console.log('Nextcloud API Client initialisiert');
  }
  
  /**
   * Erkennt die Basis-URL der Nextcloud-Instanz
   * @returns {string} - Die erkannte Basis-URL
   * @private
   */
  _detectNextcloudBaseUrl() {
    // In einer Nextcloud-Umgebung wird die URL von der Plattform bereitgestellt
    if (typeof OC !== 'undefined' && OC.generateUrl) {
      return OC.generateUrl('');
    }
    
    // Fallback für Entwicklungsumgebungen
    return window.location.origin;
  }
  
  /**
   * Initialisiert die API-Verbindung
   * @returns {Promise<boolean>} - true, wenn erfolgreich
   */
  async initialize() {
    if (this.initialized) {
      return true;
    }
    
    try {
      // In einer Nextcloud-Umgebung wird der Benutzer bereits authentifiziert sein
      if (typeof OC !== 'undefined' && OC.getCurrentUser) {
        this.userId = OC.getCurrentUser().uid;
        console.log(`Nextcloud-Benutzer erkannt: ${this.userId}`);
      }
      
      // Status der API-Endpunkte prüfen
      await this._checkApiStatus();
      
      this.initialized = true;
      return true;
    } catch (error) {
      console.error('Fehler bei der Initialisierung der Nextcloud API:', error);
      this.initialized = false;
      return false;
    }
  }
  
  /**
   * Prüft die Verfügbarkeit der verschiedenen API-Endpunkte
   * @returns {Promise<void>}
   * @private
   */
  async _checkApiStatus() {
    try {
      // OCS API prüfen
      const ocsResponse = await fetch(`${this.baseUrl}/ocs/v2.php/cloud/capabilities`, {
        method: 'GET',
        headers: {
          'OCS-APIRequest': 'true',
          'Accept': 'application/json'
        }
      });
      this.apiStatus.ocs = ocsResponse.ok;
      
      // WebDAV API prüfen
      const webdavResponse = await fetch(`${this.baseUrl}/remote.php/dav/files/${this.userId || 'admin'}`, {
        method: 'PROPFIND',
        headers: {
          'Depth': '0',
          'Content-Type': 'application/xml'
        }
      });
      this.apiStatus.webdav = webdavResponse.status === 207;
      
      // Deck API prüfen
      const deckResponse = await fetch(`${this.baseUrl}/ocs/v2.php/apps/deck/api/v1.0/boards`, {
        method: 'GET',
        headers: {
          'OCS-APIRequest': 'true',
          'Accept': 'application/json'
        }
      });
      this.apiStatus.deck = deckResponse.ok;
      
      // Benachrichtigungen API prüfen
      const notificationsResponse = await fetch(`${this.baseUrl}/ocs/v2.php/apps/notifications/api/v2/notifications`, {
        method: 'GET',
        headers: {
          'OCS-APIRequest': 'true',
          'Accept': 'application/json'
        }
      });
      this.apiStatus.notifications = notificationsResponse.ok;
      
      console.log('Nextcloud API Status:', this.apiStatus);
    } catch (error) {
      console.error('Fehler beim Prüfen der API-Status:', error);
    }
  }
  
  /**
   * Lädt die Liste aller Deck-Boards
   * @returns {Promise<Array>} - Array mit Board-Objekten
   */
  async getDeckBoards() {
    if (!this.initialized) {
      await this.initialize();
    }
    
    if (!this.apiStatus.deck) {
      throw new Error('Deck-API ist nicht verfügbar');
    }
    
    try {
      const response = await fetch(`${this.baseUrl}/ocs/v2.php/apps/deck/api/v1.0/boards`, {
        method: 'GET',
        headers: {
          'OCS-APIRequest': 'true',
          'Accept': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP Fehler: ${response.status}`);
      }
      
      const data = await response.json();
      return data.ocs.data || [];
    } catch (error) {
      console.error('Fehler beim Laden der Deck-Boards:', error);
      throw error;
    }
  }
  
  /**
   * Erstellt ein neues Board in Deck
   * @param {string} title - Titel des Boards
   * @param {string} color - Farbe des Boards (hex code)
   * @returns {Promise<Object>} - Das erstellte Board-Objekt
   */
  async createDeckBoard(title, color = '0082c9') {
    if (!this.initialized) {
      await this.initialize();
    }
    
    if (!this.apiStatus.deck) {
      throw new Error('Deck-API ist nicht verfügbar');
    }
    
    try {
      const response = await fetch(`${this.baseUrl}/ocs/v2.php/apps/deck/api/v1.0/boards`, {
        method: 'POST',
        headers: {
          'OCS-APIRequest': 'true',
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          title: title,
          color: color
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP Fehler: ${response.status}`);
      }
      
      const data = await response.json();
      return data.ocs.data || {};
    } catch (error) {
      console.error('Fehler beim Erstellen eines Deck-Boards:', error);
      throw error;
    }
  }
  
  /**
   * Erstellt eine neue Karte in einem Deck-Board
   * @param {number} boardId - ID des Boards
   * @param {number} stackId - ID des Stacks
   * @param {string} title - Titel der Karte
   * @param {string} description - Beschreibung der Karte
   * @param {number} duedate - Fälligkeitsdatum (Unix Timestamp)
   * @returns {Promise<Object>} - Die erstellte Karten-Objekt
   */
  async createDeckCard(boardId, stackId, title, description = '', duedate = null) {
    if (!this.initialized) {
      await this.initialize();
    }
    
    if (!this.apiStatus.deck) {
      throw new Error('Deck-API ist nicht verfügbar');
    }
    
    try {
      const response = await fetch(`${this.baseUrl}/ocs/v2.php/apps/deck/api/v1.0/boards/${boardId}/stacks/${stackId}/cards`, {
        method: 'POST',
        headers: {
          'OCS-APIRequest': 'true',
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          title: title,
          description: description,
          type: 'text',
          order: 999,
          duedate: duedate
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP Fehler: ${response.status}`);
      }
      
      const data = await response.json();
      return data.ocs.data || {};
    } catch (error) {
      console.error('Fehler beim Erstellen einer Deck-Karte:', error);
      throw error;
    }
  }
  
  /**
   * Lädt einen Stack aus einem Deck-Board
   * @param {number} boardId - ID des Boards
   * @returns {Promise<Array>} - Array mit Stack-Objekten
   */
  async getDeckStacks(boardId) {
    if (!this.initialized) {
      await this.initialize();
    }
    
    if (!this.apiStatus.deck) {
      throw new Error('Deck-API ist nicht verfügbar');
    }
    
    try {
      const response = await fetch(`${this.baseUrl}/ocs/v2.php/apps/deck/api/v1.0/boards/${boardId}/stacks`, {
        method: 'GET',
        headers: {
          'OCS-APIRequest': 'true',
          'Accept': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP Fehler: ${response.status}`);
      }
      
      const data = await response.json();
      return data.ocs.data || [];
    } catch (error) {
      console.error('Fehler beim Laden der Deck-Stacks:', error);
      throw error;
    }
  }
  
  /**
   * Erstellt einen neuen Stack in einem Deck-Board
   * @param {number} boardId - ID des Boards
   * @param {string} title - Titel des Stacks
   * @returns {Promise<Object>} - Das erstellte Stack-Objekt
   */
  async createDeckStack(boardId, title) {
    if (!this.initialized) {
      await this.initialize();
    }
    
    if (!this.apiStatus.deck) {
      throw new Error('Deck-API ist nicht verfügbar');
    }
    
    try {
      const response = await fetch(`${this.baseUrl}/ocs/v2.php/apps/deck/api/v1.0/boards/${boardId}/stacks`, {
        method: 'POST',
        headers: {
          'OCS-APIRequest': 'true',
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          title: title,
          order: 999
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP Fehler: ${response.status}`);
      }
      
      const data = await response.json();
      return data.ocs.data || {};
    } catch (error) {
      console.error('Fehler beim Erstellen eines Deck-Stacks:', error);
      throw error;
    }
  }
  
  /**
   * Erstellt eine neue Benachrichtigung
   * @param {string} user - Benutzer-ID des Empfängers
   * @param {string} title - Titel der Benachrichtigung
   * @param {string} message - Nachrichtentext
   * @param {string} link - Link, der geöffnet werden soll (optional)
   * @returns {Promise<Object>} - Ergebnis der Anfrage
   */
  async createNotification(user, title, message, link = '') {
    if (!this.initialized) {
      await this.initialize();
    }
    
    if (!this.apiStatus.notifications) {
      throw new Error('Benachrichtigungs-API ist nicht verfügbar');
    }
    
    try {
      const response = await fetch(`${this.baseUrl}/ocs/v2.php/apps/notifications/api/v2/admin_notifications/${user}`, {
        method: 'POST',
        headers: {
          'OCS-APIRequest': 'true',
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          shortMessage: title,
          longMessage: message,
          link: link
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP Fehler: ${response.status}`);
      }
      
      const data = await response.json();
      return data.ocs.data || {};
    } catch (error) {
      console.error('Fehler beim Erstellen einer Benachrichtigung:', error);
      throw error;
    }
  }
  
  /**
   * Erstellt einen Ordner über WebDAV
   * @param {string} path - Pfad zum Ordner (relativ zum Benutzerverzeichnis)
   * @returns {Promise<boolean>} - true, wenn erfolgreich
   */
  async createFolder(path) {
    if (!this.initialized) {
      await this.initialize();
    }
    
    if (!this.apiStatus.webdav) {
      throw new Error('WebDAV-API ist nicht verfügbar');
    }
    
    try {
      const userId = this.userId || 'admin';
      const response = await fetch(`${this.baseUrl}/remote.php/dav/files/${userId}/${path}`, {
        method: 'MKCOL',
        headers: {
          'Content-Type': 'application/xml'
        }
      });
      
      return response.status === 201 || response.status === 405;
    } catch (error) {
      console.error('Fehler beim Erstellen eines Ordners:', error);
      throw error;
    }
  }
  
  /**
   * Lädt eine Datei über WebDAV hoch
   * @param {string} path - Pfad zur Datei (relativ zum Benutzerverzeichnis)
   * @param {Blob|File} content - Dateiinhalt als Blob oder File-Objekt
   * @param {string} contentType - MIME-Typ der Datei
   * @returns {Promise<boolean>} - true, wenn erfolgreich
   */
  async uploadFile(path, content, contentType) {
    if (!this.initialized) {
      await this.initialize();
    }
    
    if (!this.apiStatus.webdav) {
      throw new Error('WebDAV-API ist nicht verfügbar');
    }
    
    try {
      const userId = this.userId || 'admin';
      const response = await fetch(`${this.baseUrl}/remote.php/dav/files/${userId}/${path}`, {
        method: 'PUT',
        headers: {
          'Content-Type': contentType
        },
        body: content
      });
      
      return response.ok;
    } catch (error) {
      console.error('Fehler beim Hochladen einer Datei:', error);
      throw error;
    }
  }
  
  /**
   * Erstellt ein SwissAirDry Board in Deck mit den Standard-Stacks
   * @returns {Promise<Object>} - Das erstellte Board-Objekt
   */
  async createSwissAirDryBoard() {
    if (!this.initialized) {
      await this.initialize();
    }
    
    try {
      // Board erstellen
      const board = await this.createDeckBoard('SwissAirDry Geräte', '0082c9');
      
      // Standard-Stacks erstellen
      await this.createDeckStack(board.id, 'Neu');
      await this.createDeckStack(board.id, 'In Bearbeitung');
      await this.createDeckStack(board.id, 'Warten');
      await this.createDeckStack(board.id, 'Abgeschlossen');
      await this.createDeckStack(board.id, 'Archiviert');
      
      return board;
    } catch (error) {
      console.error('Fehler beim Erstellen des SwissAirDry Boards:', error);
      throw error;
    }
  }
  
  /**
   * Erstellt ein Alarm-Board in Deck
   * @returns {Promise<Object>} - Das erstellte Board-Objekt
   */
  async createAlarmBoard() {
    if (!this.initialized) {
      await this.initialize();
    }
    
    try {
      // Board erstellen
      const board = await this.createDeckBoard('SwissAirDry Alarme', 'FF5555');
      
      // Standard-Stacks erstellen
      await this.createDeckStack(board.id, 'Neu');
      await this.createDeckStack(board.id, 'In Bearbeitung');
      await this.createDeckStack(board.id, 'Gelöst');
      await this.createDeckStack(board.id, 'Ignoriert');
      
      return board;
    } catch (error) {
      console.error('Fehler beim Erstellen des Alarm Boards:', error);
      throw error;
    }
  }
  
  /**
   * Erstellt eine Alarm-Karte in Deck
   * @param {Object} alarm - Alarm-Objekt mit Informationen
   * @param {number} boardId - ID des Alarm-Boards
   * @param {number} stackId - ID des Stacks (optional, Standard: erster Stack)
   * @returns {Promise<Object>} - Die erstellte Karte
   */
  async createAlarmCard(alarm, boardId, stackId = null) {
    if (!this.initialized) {
      await this.initialize();
    }
    
    if (!boardId) {
      throw new Error('Board-ID ist erforderlich');
    }
    
    try {
      // Wenn keine Stack-ID angegeben wurde, nehmen wir den ersten Stack
      if (!stackId) {
        const stacks = await this.getDeckStacks(boardId);
        if (stacks.length === 0) {
          throw new Error('Keine Stacks im Board gefunden');
        }
        stackId = stacks[0].id;
      }
      
      // Karte erstellen
      const dueDate = alarm.due_date ? Math.floor(new Date(alarm.due_date).getTime() / 1000) : null;
      const title = `${alarm.title || 'Alarm'} - ${alarm.device_id || 'Unbekanntes Gerät'}`;
      const description = `Typ: ${alarm.type || 'Unbekannt'}\nSchweregrad: ${alarm.severity || 'Mittel'}\n\n${alarm.description || ''}`;
      
      return await this.createDeckCard(boardId, stackId, title, description, dueDate);
    } catch (error) {
      console.error('Fehler beim Erstellen der Alarm-Karte:', error);
      throw error;
    }
  }
}

// Singleton-Instanz
const nextcloudApi = new NextcloudAPI();

// In einer Nextcloud-Umgebung initialisieren wir die API automatisch
if (typeof OC !== 'undefined') {
  document.addEventListener('DOMContentLoaded', async () => {
    console.log('Initialisiere Nextcloud API...');
    await nextcloudApi.initialize();
  });
}