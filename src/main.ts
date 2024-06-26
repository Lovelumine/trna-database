import { createApp } from 'vue';
import App from './App.vue';
import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';
import PageNotFound from './views/404.vue'; // 引入404组件

// // import 'fornac/app/scripts/fornac.js';
// import './views/display/scripts/fornac.js'
// 引入样式
import './assets/global.css';
import './assets/herf.css';
import './assets/bot.css'
// import './assets/mouse.css';
import './assets/search.css';

import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';
import * as ElIcons from '@element-plus/icons-vue'; // 引入 Element Plus 图标



// 引入组件
import Home from './views/Home.vue';
import CodingVariationDisease from './views/Coding Variation Disease/Coding Variation Disease.vue';
import tRNAtherapeutics from './views/tRNAtherapeutics/tRNAtherapeutics.vue';
import naturalsuptRNA from './views/natural-sup-tRNA/natural-sup-tRNA.vue';
import tRNAElements from './views/tRNA elements/tRNA elements.vue';
import ExpandedRow from './views/tRNAtherapeutics/ExpandedRow.vue';  // 引入新组件
import Display from './views/display/Display.vue';
import about from './views/about/about.vue';
import help from './views/help/help.vue';
import download from './views/download/download.vue';

// 引入表格组件
import STable from '@shene/table';
import '@shene/table/dist/index.css';
import 'vxe-table/lib/style.css';
import VXETable from 'vxe-table';

// 路由配置，使用懒加载
const routes: RouteRecordRaw[] = [
  { path: '/', component: () => import('./views/Home.vue') },
  { path: '/CodingVariationDisease', component: () => import('./views/Coding Variation Disease/Coding Variation Disease.vue') },
  { path: '/tRNAtherapeutics', component: () => import('./views/tRNAtherapeutics/tRNAtherapeutics.vue') },
  { path: '/naturalsuptRNA', component: () => import('./views/natural-sup-tRNA/natural-sup-tRNA.vue') },
  { path: '/tRNAElements', component: () => import('./views/tRNA elements/tRNA elements.vue') },
  { path: '/expanded/:key', name: 'ExpandedRow', component: () => import('./views/tRNAtherapeutics/ExpandedRow.vue') },
  { path: '/about', name: 'about', component: () => import('./views/about/about.vue') },
  { path: '/display/:tRNAName', name: 'Display', component: () => import('./views/display/Display.vue') }, // 动态路由
  { path: '/help', name: 'help', component: () => import('./views/help/help.vue') },
  { path: '/download', name: 'download', component: () => import('./views/download/download.vue') },
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
  app.component(name, ElIcons[name]);
}

app.use(STable);
app.use(VXETable);
app.use(router);
app.use(ElementPlus);
app.mount('#app');

