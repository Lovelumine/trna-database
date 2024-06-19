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
import PTCinDisease from './views/PTC in Disease/PTC in Disease.vue';
import tRNAtherapeutics from './views/tRNAtherapeutics/tRNAtherapeutics.vue';
import naturalsuptRNA from './views/natural-sup-tRNA/natural-sup-tRNA.vue';
import TrnaElements from './views/tRNA elements/tRNA elements.vue';
import Display from './views/display/Display.vue';

// 引入表格组件
import STable from '@shene/table';
import '@shene/table/dist/index.css';
import 'vxe-table/lib/style.css';
import VXETable from 'vxe-table';

// 路由配置
const routes: RouteRecordRaw[] = [
    { path: '/', component: Home },
    { path: '/PTC-in-Disease', component: PTCinDisease },
    { path: '/tRNAtherapeutics', component: tRNAtherapeutics },
    { path: '/naturalsuptRNA', component: naturalsuptRNA },
    { path: '/TrnaElements', component: TrnaElements },
    { path: '/display/:tRNAName', component: Display }, // 动态路由
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

