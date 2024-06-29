import { createApp } from 'vue';
import App from './App.vue';
import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';
import PageNotFound from './views/404.vue'; // 引入404组件

// 引入样式
import './assets/global.css';
import './assets/herf.css';
import './assets/bot.css';
import './assets/search.css';

import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';
import * as ElIcons from '@element-plus/icons-vue'; // 引入 Element Plus 图标

// 引入组件
const Home = () => import('./views/Home.vue');
const CodingVariationDisease = () => import('./views/Coding Variation Disease/Coding Variation Disease.vue');
const tRNAtherapeutics = () => import('./views/tRNAtherapeutics/tRNAtherapeutics.vue');
const naturalsuptRNA = () => import('./views/natural-sup-tRNA/natural-sup-tRNA.vue');
const tRNAElements = () => import('./views/tRNA elements/tRNA elements.vue');
const ExpandedRow = () => import('./views/tRNAtherapeutics/ExpandedRow.vue');
const Display = () => import('./views/display/Display.vue');
const About = () => import('./views/about/about.vue');
const Help = () => import('./views/help/help.vue');
const Download = () => import('./views/download/download.vue');

// 引入表格组件
import STable from '@shene/table';
import '@shene/table/dist/index.css';
import 'vxe-table/lib/style.css';
import VXETable from 'vxe-table';
import VueMatomo from 'vue-matomo';

import VueSidebarMenu from 'vue-sidebar-menu';
import 'vue-sidebar-menu/dist/vue-sidebar-menu.css';

// 路由配置，使用懒加载
const routes: RouteRecordRaw[] = [
  { path: '/', component: Home },
  { path: '/CodingVariationDisease', component: CodingVariationDisease },
  { path: '/tRNAtherapeutics', component: tRNAtherapeutics },
  { path: '/naturalsuptRNA', component: naturalsuptRNA },
  { path: '/tRNAElements', component: tRNAElements },
  { path: '/expanded/:key', name: 'ExpandedRow', component: ExpandedRow },
  { path: '/about', name: 'about', component: About },
  { path: '/display/:tRNAName', name: 'Display', component: Display },
  { path: '/help', name: 'help', component: Help },
  { path: '/download', name: 'download', component: Download },
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: PageNotFound } // 404路由
];

// 创建路由器实例
const router = createRouter({
  history: createWebHistory(),
  routes
});

// 创建 Vue 应用实例
const app = createApp(App);

// 注册所有图标组件
for (const name in ElIcons) {
  app.component(name, (ElIcons as any)[name]);
}

app.use(STable);
app.use(VXETable);
app.use(router);
app.use(ElementPlus);
app.use(VueSidebarMenu);

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

// 预加载其他路由组件
const prefetchRoutes = [
  '/CodingVariationDisease',
  '/tRNAtherapeutics',
  '/naturalsuptRNA',
  '/tRNAElements',
  '/about',
  '/help',
  '/download'
];

prefetchRoutes.forEach(route => {
  router.resolve({ path: route }).matched.forEach(record => {
    const loadComponent = record.components.default as any;
    if (typeof loadComponent === 'function') {
      loadComponent().then((component: any) => {
        // Optionally, you can store the loaded component for future use
        // For example, in a global store or local variable
      });
    }
  });
});
