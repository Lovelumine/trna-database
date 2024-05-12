import { createApp } from 'vue';
import App from './App.vue';
import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';


// // import 'fornac/app/scripts/fornac.js';
// import './views/display/scripts/fornac.js'
// 引入样式
import './assets/global.css';
import './assets/herf.css';
import './assets/mouse.css';
import './assets/search.css';

import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';

// 引入组件
import Home from './views/Home.vue';
import CodingVariationDisease from './views/CodingVariationDisease.vue';
import Display from './views/display/Display.vue';

// 引入表格组件
import STable from '@shene/table';
import '@shene/table/dist/index.css';
import 'vxe-table/lib/style.css';
import VXETable from 'vxe-table';

// 路由配置
const routes: RouteRecordRaw[] = [
    { path: '/', component: Home },
    { path: '/coding-variation-disease', component: CodingVariationDisease },
    { path: '/display/:tRNAName', component: Display } // 动态路由
];

// 创建路由器实例
const router = createRouter({
  history: createWebHistory(),
  routes
});

// 创建 Vue 应用实例
const app = createApp(App);
app.use(STable);
app.use(VXETable);
app.use(router);
app.use(ElementPlus);
app.mount('#app');
