import { createApp, defineAsyncComponent } from 'vue';
import App from './App.vue';
import { initTheme } from './utils/theme';
import { createRouter, createWebHistory, RouteLocationNormalized, RouteRecordRaw } from 'vue-router';
import PageNotFound from './views/404.vue'; // 引入404组件

// 引入样式
import './style.css';
import './assets/global.css';
import './assets/herf.css';
import './assets/bot.css';
import './assets/search.css';
// import 'vue-easy-lightbox/dist/vue-easy-lightbox.css';

import NProgress from 'nprogress';
import 'nprogress/nprogress.css'; // 引入 NProgress 样式

import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';

// 导入图标
import './utils/icons';

//动态美化效果
import VWave from 'v-wave';

// 引入组件
const Home = () => import('./views/Home.vue');
const CodingVariationDisease = () => import('./views/Coding Variation Disease/Coding Variation Disease.vue');
const tRNAtherapeutics = () => import('./views/tRNAtherapeutics/tRNAtherapeutics.vue');
const naturalsuptRNA = () => import('./views/natural-sup-tRNA/natural-sup-tRNA.vue');
const tRNAElements = () => import('./views/tRNA elements/tRNA elements.vue');
const ExpandedRow = () => import('./views/tRNAtherapeutics/ExpandedRow.vue');
const Display = () => import('./views/display/Display.vue');
const About = () => import('./views/about/about.vue');
const Download = () => import('./views/download/download.vue');
const AIYingying = () => import('./views/AIYingying/AIYingying.vue');
const BlastSearch = () => import('./views/blast/BlastSearch.vue'); // 新添加的 BLAST 搜索组件
const audio = () => import('./views/audio/audio.vue');
const EnsureSTable = defineAsyncComponent(() => import('./components/EnsureSTable.vue'));
import VueMatomo from 'vue-matomo';

import { APP_PATHS, MAIN_PREFETCH_ROUTE_PATHS } from './config/navigation';

function redirectLegacyAdminRoute(to: RouteLocationNormalized) {
  const search = new URLSearchParams();
  let hashPath = '/workspace';

  if (to.path === APP_PATHS.adminLogin) {
    hashPath = '/login';
  } else if (to.path === APP_PATHS.adminEngineered) {
    search.set('view', 'table');
    search.set('resource', 'Engineered_sup_tRNA');
  } else {
    Object.entries(to.query || {}).forEach(([key, value]) => {
      if (Array.isArray(value)) {
        value.forEach((item) => search.append(key, String(item)));
        return;
      }
      if (value != null) {
        search.set(key, String(value));
      }
    });
  }

  const target = `/admin.html#${hashPath}${search.toString() ? `?${search.toString()}` : ''}`;
  window.location.replace(target);
  return false;
}

function redirectStandaloneHelpRoute(to: RouteLocationNormalized) {
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

  const target = `${APP_PATHS.helpEntry}${search.toString() ? `?${search.toString()}` : ''}${to.hash || ''}`;
  window.location.replace(target);
  return false;
}

// 路由配置，使用懒加载
const routes: RouteRecordRaw[] = [
  { path: APP_PATHS.home, component: Home },
  { path: APP_PATHS.disease, component: CodingVariationDisease },
  { path: APP_PATHS.therapeutics, component: tRNAtherapeutics },
  { path: APP_PATHS.natural, component: naturalsuptRNA },
  { path: APP_PATHS.elements, component: tRNAElements },
  { path: APP_PATHS.expanded, name: 'ExpandedRow', component: ExpandedRow },
  { path: APP_PATHS.about, name: 'about', component: About },
  { path: '/display/:tRNAName', name: 'Display', component: Display },
  { path: APP_PATHS.help, beforeEnter: redirectStandaloneHelpRoute },
  { path: APP_PATHS.download, name: 'download', component: Download },
  { path: APP_PATHS.ai, name: 'AIYingying', component: AIYingying },
  { path: APP_PATHS.audio, name: 'audio', component: audio },
  { path: APP_PATHS.blast, name: 'blast', component: BlastSearch },
  { path: APP_PATHS.admin, beforeEnter: redirectLegacyAdminRoute },
  { path: APP_PATHS.adminLogin, beforeEnter: redirectLegacyAdminRoute },
  { path: APP_PATHS.adminWorkspace, beforeEnter: redirectLegacyAdminRoute },
  { path: APP_PATHS.adminEngineered, beforeEnter: redirectLegacyAdminRoute },
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: PageNotFound } // 404路由
];

// 创建路由器实例
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

// 添加路由钩子来控制 NProgress
router.beforeEach(async (to, from, next) => {
  NProgress.start();
  next();
});

router.afterEach(() => {
  NProgress.done();
});

// 创建 Vue 应用实例
const app = createApp(App);

initTheme();

app.component('font-awesome-icon', FontAwesomeIcon);

app.component('s-table', EnsureSTable)
app.use(router);
app.use(VWave, {});

// 配置 Vue Matomo
app.use(VueMatomo, {
  // 配置 Matomo 服务器和站点 ID
  host: 'https://analysis.lumoxuan.cn',
  siteId: 1,

  // 其他可选配置
  trackerFileName: 'matomo',
  enableLinkTracking: true,
  trackInitialView: true,
  disableCookies: false,
  requireConsent: false,
  requireCookieConsent: false,
  enableHeartBeatTimer: false,
  heartBeatTimerInterval: 15,
  debug: false,
  userId: undefined,
  cookieDomain: undefined,
  domains: undefined,
  preInitActions: [],
  trackSiteSearch: false,
  crossOrigin: undefined,
  router: router
});

app.mount('#app');

const prefetchLightRoutes = () => {
  MAIN_PREFETCH_ROUTE_PATHS.forEach(route => {
    router.resolve({ path: route }).matched.forEach(record => {
      const loadComponent = record.components.default as any;
      if (typeof loadComponent === 'function') {
        void loadComponent();
      }
    });
  });
};

if ('requestIdleCallback' in window) {
  window.requestIdleCallback(prefetchLightRoutes, { timeout: 2500 });
} else {
  window.setTimeout(prefetchLightRoutes, 1500);
}
