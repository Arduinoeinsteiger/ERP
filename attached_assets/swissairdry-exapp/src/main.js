/**
 * Main Application Entry Point
 * 
 * Diese Datei initialisiert die Vue-Anwendung für die SwissAirDry ExApp
 * und konfiguriert alle benötigten Plugins und globalen Komponenten.
 */

import { createApp } from 'vue';
import App from './App.vue';
import router from './router';

// Styling
import './assets/main.css';

// Globale Komponenten
import StatusIndicator from './components/shared/StatusIndicator.vue';
import LoadingSpinner from './components/shared/LoadingSpinner.vue';
import EmptyState from './components/shared/EmptyState.vue';
import ErrorState from './components/shared/ErrorState.vue';

// Konfiguration für Nextcloud-Integration
const nextcloudConfig = {
  // Parameter aus URL extrahieren, wenn sie von Nextcloud gesetzt wurden
  getUrlParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
  }
};

// App erstellen
const app = createApp(App);

// Router einbinden
app.use(router);

// Globale Komponenten registrieren
app.component('StatusIndicator', StatusIndicator);
app.component('LoadingSpinner', LoadingSpinner);
app.component('EmptyState', EmptyState);
app.component('ErrorState', ErrorState);

// Globale Eigenschaften
app.config.globalProperties.$nextcloud = nextcloudConfig;

// Error-Handler für Produktion
app.config.errorHandler = (err, vm, info) => {
  console.error('Vue-Anwendungsfehler:', err);
  console.error('Komponente:', vm);
  console.error('Info:', info);
  
  // In Nextcloud-Umgebung Benachrichtigung anzeigen
  if (window.OCS && window.OCS.message) {
    window.OCS.message.error('Ein Fehler ist aufgetreten. Bitte aktualisieren Sie die Seite oder kontaktieren Sie den Administrator.');
  }
};

// App mounten
app.mount('#app');