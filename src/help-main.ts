import { createApp } from 'vue';
import { createRouter, createWebHistory, type RouteLocationNormalized, type RouteRecordRaw } from 'vue-router';
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';

import App from './App.vue';
import { initTheme } from './utils/theme';
import './style.css';
import './assets/global.css';
import './assets/herf.css';
import './assets/bot.css';
import './assets/search.css';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import './utils/icons';

const Help = () => import('./views/help/help.vue');

function buildTarget(to: RouteLocationNormalized) {
  const search = new URLSearchParams();
  Object.entries(to.query || {}).forEach(([key, value]) => {
    if (Array.isArray(value)) {
      value.forEach((item) => search.append(key, String(item)));
      return;
    }
    if (value != null) {
      search.set(key, String(value));
    }
  });
  return `${to.path}${search.toString() ? `?${search.toString()}` : ''}${to.hash || ''}`;
}

function leaveHelpEntry(to: RouteLocationNormalized) {
  window.location.assign(buildTarget(to));
  return false;
}

function redirectLegacyHelp(to: RouteLocationNormalized) {
  const search = new URLSearchParams();
  Object.entries(to.query || {}).forEach(([key, value]) => {
    if (Array.isArray(value)) {
      value.forEach((item) => search.append(key, String(item)));
      return;
    }
    if (value != null) {
      search.set(key, String(value));
    }
  });
  const target = `/help.html${search.toString() ? `?${search.toString()}` : ''}${to.hash || ''}`;
  window.location.replace(target);
  return false;
}

const externalRoutes = [
  '/',
  '/CodingVariationDisease',
  '/tRNAtherapeutics',
  '/naturalsuptRNA',
  '/tRNAElements',
  '/blast',
  '/AIYingying',
  '/download',
  '/about',
  '/audio',
  '/admin',
  '/admin/login',
  '/admin/workspace'
];

const routes: RouteRecordRaw[] = [
  { path: '/help.html', name: 'help-standalone', component: Help },
  { path: '/help', beforeEnter: redirectLegacyHelp },
  ...externalRoutes.map((path) => ({ path, beforeEnter: leaveHelpEntry })),
  { path: '/:pathMatch(.*)*', redirect: '/help.html' }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to) {
    if (to.hash) {
      return { el: to.hash, behavior: 'smooth' };
    }
    return { top: 0 };
  }
});

initTheme();

const app = createApp(App);
app.component('font-awesome-icon', FontAwesomeIcon);
app.use(router);
app.use(ElementPlus);
app.mount('#app');
