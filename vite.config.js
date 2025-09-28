import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import vueJsx from '@vitejs/plugin-vue-jsx';
import path from 'path';
import terser from '@rollup/plugin-terser'; // 引入 terser 插件
import { viteStaticCopy } from 'vite-plugin-static-copy'; // 引入 vite-plugin-static-copy 插件

// 允许的来源站点
const allowedOrigin = 'https://trna.lumoxuan.cn/';

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
    alias: {
      "@": path.resolve(__dirname, 'src') // 设置别名
    }
  },
  esbuild: {
    jsxFactory: 'h',
    jsxFragment: 'Fragment',
    jsxInject: "import { h } from 'vue';"
  },
  build: {
    sourcemap: false, // 生产环境中不生成 source map
    minify: 'terser', // 确保使用 terser 进行代码压缩和混淆
    cssCodeSplit: false, // 确保 CSS 分割到单独的文件中
    assetsInlineLimit: 4096, // 将小于 4KB 的文件内联到 JavaScript 中
    outDir: 'dist', // 设置构建输出目录
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            return 'vendor';  // 将第三方库拆分到单独的 vendor 文件
          }
          if (id.includes('views')) {
            return 'views';  // 页面级组件放到一个 views chunk
          }
        }
      }
    }
  },
  assetsInclude: ['**/*.txt'], // 确保处理 .txt 文件
  server: {
    host: '0.0.0.0', // 允许外部访问
    port: 5174, // 使用5174端口
    strictPort: true,
    proxy: {
      '/scan': {
        target: 'http://localhost:3456',
        changeOrigin: true,
      },      
      '/search': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/align': {
        target: 'http://localhost:3457',
        changeOrigin: true,
      },      
      '/chat/api': {
        target: 'http://223.82.75.76:8080',
        changeOrigin: true,
      },
      '/run-blast': {
        target: 'http://localhost:3945',
        changeOrigin: true,
      }
    },
    // 使用 configureServer API 添加中间件来检查请求来源
    configureServer: (server) => {
      server.middlewares.use((req, res, next) => {
        const origin = req.headers.origin;
        if (origin && origin !== allowedOrigin) {
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
      '@formkit/vue',
      '@formkit/addons',
      '@formkit/i18n',
      'chunk-LH747XKU.js',
      'chunk-G3PMV62Z.js'
    ]
  },
  base: './', // 设置基础路径为相对路径
})