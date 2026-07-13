import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import vueJsx from '@vitejs/plugin-vue-jsx';
import path from 'path';
import terser from '@rollup/plugin-terser'; // 引入 terser 插件
import { viteStaticCopy } from 'vite-plugin-static-copy'; // 引入 vite-plugin-static-copy 插件

const backendTarget = 'http://localhost:8010';

// 允许的来源站点
const allowedOrigins = new Set([
  'https://trna.lumoxuan.cn/',
  'http://localhost:5174',
  'http://127.0.0.1:5174',
]);

function includesAny(value, needles) {
  return needles.some(needle => value.includes(needle));
}

function vendorChunk(id) {
  if (!id.includes('node_modules')) {
    return;
  }

  const normalized = id.split(path.sep).join('/');

  if (includesAny(normalized, ['/node_modules/vue/', '/node_modules/@vue/', '/node_modules/vue-router/'])) {
    return 'vue-vendor';
  }
  if (includesAny(normalized, ['/node_modules/@element-plus/icons-vue/'])) {
    return 'element-icons';
  }
  if (includesAny(normalized, [
    '/node_modules/element-plus/',
    '/node_modules/@element-plus/',
    '/node_modules/@popperjs/',
    '/node_modules/@sxzz/',
    '/node_modules/async-validator/',
    '/node_modules/dayjs/',
    '/node_modules/lodash-unified/',
    '/node_modules/memoize-one/',
    '/node_modules/normalize-wheel-es/',
  ])) {
    return 'element-plus';
  }
  if (includesAny(normalized, ['/node_modules/@shene/table/', '/node_modules/vxe-table/', '/node_modules/xe-utils/'])) {
    return 'table-vendor';
  }
  if (includesAny(normalized, [
    '/node_modules/echarts/',
    '/node_modules/echarts-wordcloud/',
    '/node_modules/vue-echarts/',
    '/node_modules/zrender/',
    '/node_modules/tslib/',
    '/node_modules/vue-demi/',
  ])) {
    return 'echarts';
  }
  if (includesAny(normalized, ['/node_modules/d3', '/node_modules/internmap/'])) {
    return 'd3';
  }
  if (includesAny(normalized, ['/node_modules/ngl/'])) {
    return 'ngl';
  }
  if (includesAny(normalized, [
    '/node_modules/three/',
    '/node_modules/molstar/',
    '/node_modules/rxjs/',
    '/node_modules/fp-ts/',
    '/node_modules/react/',
    '/node_modules/react-dom/',
  ])) {
    return 'structure-vendor';
  }
  if (includesAny(normalized, [
    '/node_modules/markdown-it/',
    '/node_modules/marked/',
    '/node_modules/linkify-it/',
    '/node_modules/mdurl/',
    '/node_modules/entities/',
    '/node_modules/uc.micro/',
  ])) {
    return 'markdown';
  }
  if (includesAny(normalized, [
    '/node_modules/vue-easy-lightbox/',
    '/node_modules/vue3-video-play/',
    '/node_modules/hls.js/',
    '/node_modules/srt-parser-2/',
  ])) {
    return 'media';
  }
  if (includesAny(normalized, ['/node_modules/@fortawesome/'])) {
    return 'fontawesome';
  }
  if (includesAny(normalized, [
    '/node_modules/axios/',
    '/node_modules/lodash',
    '/node_modules/nprogress/',
    '/node_modules/v-wave/',
    '/node_modules/vue-matomo/',
  ])) {
    return 'app-vendor';
  }
  return 'vendor-misc';
}

export default defineConfig({
  plugins: [
    vue(),
    vueJsx({}),
    terser({ // 配置 terser 插件
      format: {
        comments: false, // 移除注释
      },
      compress: {
        drop_console: false, // 移除 console
        drop_debugger: false // 移除 debugger
      },
      // mangle: { // 混淆配置
      //   properties: {
      //     regex: /^_/ // 混淆以 _ 开头的属性名
      //   },
      //   toplevel: true, // 混淆顶层作用域中的变量和函数名称
      //   reserved: ['_', 'Vue'] // 不混淆全局的 Vue 变量以及其他可能需要保留的标识符
      // }
    }),
  ],
  resolve: {
    alias: [
      { find: "@", replacement: path.resolve(__dirname, 'src') }, // 设置别名
      // 仅重写裸导入的入口，避免影响样式路径（vue3-video-play/dist/style.css）
      { find: /^vue3-video-play$/, replacement: "vue3-video-play/dist/index.mjs" },
    ]
  },
  esbuild: {
    jsxFactory: 'h',
    jsxFragment: 'Fragment',
    jsxInject: "import { h } from 'vue';"
  },
  build: {
    sourcemap: false, // 生产环境中不生成 source map
    minify: 'terser', // 确保使用 terser 进行代码压缩和混淆
    cssCodeSplit: true, // 按入口和异步模块拆分 CSS，避免单个样式包过大
    chunkSizeWarningLimit: 1000,
    assetsInlineLimit: 4096, // 将小于 4KB 的文件内联到 JavaScript 中
    outDir: 'dist', // 设置构建输出目录
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, 'index.html'),
        admin: path.resolve(__dirname, 'admin.html'),
        help: path.resolve(__dirname, 'help.html'),
      },
      output: {
        manualChunks: vendorChunk
      }
    }
  },
  assetsInclude: ['**/*.txt'], // 确保处理 .txt 文件
  server: {
    host: '0.0.0.0', // 允许外部访问
    port: 5174, // 使用5174端口
    strictPort: true,
    proxy: {
      '/search': {
        target: backendTarget,
        changeOrigin: true,
      },
      '/search_table': {
        target: backendTarget,
        changeOrigin: true,
      },      
      '/table_rows': {
        target: backendTarget,
        changeOrigin: true,
      },
      '/table_stats': {
        target: backendTarget,
        changeOrigin: true,
      },
      '/table_fulltext_rebuild': {
        target: backendTarget,
        changeOrigin: true,
      },
      '/download_table': {
        target: backendTarget,
        changeOrigin: true,
      },
      '/download_table_status': {
        target: backendTarget,
        changeOrigin: true,
      },
      '/download_bundle_status': {
        target: backendTarget,
        changeOrigin: true,
      },
      '/chat/api': {
        target: backendTarget,
        changeOrigin: true,
      },
      '/admin/api': {
        target: backendTarget,
        changeOrigin: true,
      },
      // 后端 Engineered_sup_tRNA CRUD 代理
      '/engineered_sup_trna': {
        target: backendTarget,
        changeOrigin: true,
      },
    },
    // 使用 configureServer API 添加中间件来检查请求来源
    configureServer: (server) => {
      server.middlewares.use((req, res, next) => {
        const origin = req.headers.origin;
        if (origin && !allowedOrigins.has(origin)) {
          res.statusCode = 403;
          res.end('Forbidden');
        } else {
          next();
        }
      });
    }
  },
  optimizeDeps: {
    exclude: [
      'vue3-video-play',
      '@formkit/vue',
      '@formkit/addons',
      '@formkit/i18n',
      'chunk-LH747XKU.js',
      'chunk-G3PMV62Z.js'
    ]
  },
  // The public site uses history-mode routes (for example
  // /expanded/ensure-0 and /admin/login). Root-relative assets keep direct
  // visits to nested routes from incorrectly requesting /expanded/assets/*.
  base: '/',
})
