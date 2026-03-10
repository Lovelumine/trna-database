import { createApp } from 'vue';
import { createRouter, createWebHashHistory, type RouteRecordRaw } from 'vue-router';
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';
import NProgress from 'nprogress';
import 'nprogress/nprogress.css';

import AdminApp from './views/admin/AdminApp.vue';
import './assets/admin.css';
import { initAdminPreferences } from './utils/adminPreferences';

const AdminLogin = () => import('./views/admin/AdminLogin.vue');
const AdminWorkspace = () => import('./views/admin/AdminWorkspace.vue');

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/workspace' },
  { path: '/login', name: 'admin-login', component: AdminLogin, meta: { adminGuest: true } },
  { path: '/workspace', name: 'admin-workspace', component: AdminWorkspace, meta: { requiresAdmin: true } },
  { path: '/:pathMatch(.*)*', redirect: '/workspace' }
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 };
  }
});

initAdminPreferences();

router.beforeEach(async (to, _from, next) => {
  NProgress.start();

  if (to.meta?.requiresAdmin) {
    try {
      const resp = await fetch('/admin/api/me', {
        method: 'GET',
        cache: 'no-store',
        credentials: 'same-origin'
      });
      if (!resp.ok) {
        next({ path: '/login', query: { next: to.fullPath } });
        return;
      }
    } catch {
      next({ path: '/login', query: { next: to.fullPath } });
      return;
    }
  }

  if (to.meta?.adminGuest) {
    try {
      const resp = await fetch('/admin/api/me', {
        method: 'GET',
        cache: 'no-store',
        credentials: 'same-origin'
      });
      if (resp.ok) {
        next('/workspace');
        return;
      }
    } catch {
      // Ignore auth probe failures on login page.
    }
  }

  next();
});

router.afterEach(() => {
  NProgress.done();
});

createApp(AdminApp)
  .use(router)
  .use(ElementPlus)
  .mount('#admin-app');
