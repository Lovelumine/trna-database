import { createApp } from 'vue';
import App from './App.vue';
import { initTheme } from './utils/theme';
import { createRouter, createWebHistory, RouteLocationNormalized, RouteRecordRaw } from 'vue-router';
import PageNotFound from './views/404.vue'; // 引入404组件
import EnsureSTable from './components/EnsureSTable.vue'

// 引入样式
import './style.css';
import './assets/global.css';
import './assets/herf.css';
import './assets/bot.css';
import './assets/search.css';
// import 'vue-easy-lightbox/dist/vue-easy-lightbox.css';

import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';
import * as ElIcons from '@element-plus/icons-vue'; // 引入 Element Plus 图标

import NProgress from 'nprogress';
import 'nprogress/nprogress.css'; // 引入 NProgress 样式

// FontAwesome 图标库配置
import { library } from '@fortawesome/fontawesome-svg-core';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';

// 导入图标
import './utils/icons';

//动态美化效果
import VWave from 'v-wave';

import * as echarts from 'echarts/core'
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  VisualMapComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'
import { BarChart, LineChart,TreemapChart, HeatmapChart } from 'echarts/charts'
import 'echarts-wordcloud';

echarts.use([
  TitleComponent,
  TooltipComponent,
  GridComponent,
  BarChart,
  CanvasRenderer,
  LegendComponent,
  VisualMapComponent,
  TreemapChart,
  LineChart,
  HeatmapChart
])

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
// 引入表格组件
import STable from '@shene/table';
import '@shene/table/dist/index.css';
import 'vxe-table/lib/style.css';
import VXETable from 'vxe-table';
import VueMatomo from 'vue-matomo';

import VueSidebarMenu from 'vue-sidebar-menu';
import 'vue-sidebar-menu/dist/vue-sidebar-menu.css';

function redirectLegacyAdminRoute(to: RouteLocationNormalized) {
  const search = new URLSearchParams();
  let hashPath = '/workspace';

  if (to.path === '/admin/login') {
    hashPath = '/login';
  } else if (to.path === '/admin/engineered-sup-trna') {
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

  const target = `/help.html${search.toString() ? `?${search.toString()}` : ''}${to.hash || ''}`;
  window.location.replace(target);
  return false;
}

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
  { path: '/help', beforeEnter: redirectStandaloneHelpRoute },
  { path: '/download', name: 'download', component: Download },
  { path: '/AIYingying', name: 'AIYingying', component: AIYingying },
  { path: '/audio', name: 'audio', component: audio },
  { path: '/blast', name: 'blast', component: BlastSearch }, // 新添加的 BLAST 搜索路由
  { path: '/admin', beforeEnter: redirectLegacyAdminRoute },
  { path: '/admin/login', beforeEnter: redirectLegacyAdminRoute },
  { path: '/admin/workspace', beforeEnter: redirectLegacyAdminRoute },
  { path: '/admin/engineered-sup-trna', beforeEnter: redirectLegacyAdminRoute },
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

app.component('VChart', VChart)


// 注册所有图标组件
for (const name in ElIcons) {
  app.component(name, (ElIcons as any)[name]);
}

app.component('font-awesome-icon', FontAwesomeIcon);

app.use(STable);
app.component('s-table', EnsureSTable)
app.use(VXETable);
app.use(router);
app.use(VWave, {});
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
