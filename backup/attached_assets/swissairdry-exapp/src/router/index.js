import { createRouter, createWebHashHistory } from 'vue-router';

// Views
import Dashboard from '@/views/Dashboard.vue';

// Lazy-loaded views
const DevicesList = () => import('@/views/devices/DevicesList.vue');
const DeviceDetail = () => import('@/views/devices/DeviceDetail.vue');
const AlarmsList = () => import('@/views/alarms/AlarmsList.vue');
const AlarmDetail = () => import('@/views/alarms/AlarmDetail.vue');
const Settings = () => import('@/views/Settings.vue');
const NotFound = () => import('@/views/NotFound.vue');

/**
 * Router-Konfiguration für die SwissAirDry ExApp
 */
const routes = [
  {
    path: '/',
    name: 'dashboard',
    component: Dashboard,
    meta: {
      title: 'Dashboard',
      requiresAuth: false
    }
  },
  {
    path: '/dashboard',
    redirect: '/'
  },
  {
    path: '/devices',
    name: 'devices',
    component: DevicesList,
    meta: {
      title: 'Geräte',
      requiresAuth: false
    }
  },
  {
    path: '/devices/:id',
    name: 'device-detail',
    component: DeviceDetail,
    props: true,
    meta: {
      title: 'Gerät',
      requiresAuth: false
    }
  },
  {
    path: '/alarms',
    name: 'alarms',
    component: AlarmsList,
    meta: {
      title: 'Alarme',
      requiresAuth: false
    }
  },
  {
    path: '/alarms/:id',
    name: 'alarm-detail',
    component: AlarmDetail,
    props: true,
    meta: {
      title: 'Alarm',
      requiresAuth: false
    }
  },
  {
    path: '/settings',
    name: 'settings',
    component: Settings,
    meta: {
      title: 'Einstellungen',
      requiresAuth: false
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: NotFound,
    meta: {
      title: 'Seite nicht gefunden',
      requiresAuth: false
    }
  }
];

/**
 * Router-Instanz erstellen
 */
const router = createRouter({
  history: createWebHashHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    } else {
      return { top: 0 };
    }
  }
});

/**
 * Vor dem Routing Titel setzen und Berechtigungen prüfen
 */
router.beforeEach((to, from, next) => {
  // Seitentitel setzen
  document.title = to.meta.title 
    ? `${to.meta.title} | SwissAirDry` 
    : 'SwissAirDry';
  
  // In Nextcloud-Umgebung den Seitentitel über OCS API setzen
  if (window.OCS && window.OCS.setNavigationEntry) {
    window.OCS.setNavigationEntry({
      name: to.meta.title || 'SwissAirDry',
      active: true
    });
  }
  
  // Prüfen, ob Authentifizierung erforderlich ist
  if (to.meta.requiresAuth) {
    // Hier kann später eine Authentifizierung implementiert werden
    // Aktuell wird jeder Zugriff erlaubt
    next();
  } else {
    next();
  }
});

export default router;