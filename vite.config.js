import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import path from "path"
import terser from "@rollup/plugin-terser"; // 引入 terser 插件
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
        drop_console: true, // 移除 console
        drop_debugger: true // 移除 debugger
      },
      mangle: { // 混淆配置
        properties: {
          regex: /^_/ // 混淆以 _ 开头的属性名
        },
        toplevel: true, // 混淆顶层作用域中的变量和函数名称
        reserved: ['_', 'Vue'] // 不混淆全局的 Vue 变量以及其他可能需要保留的标识符
      }
    }),
    // viteStaticCopy({
    //   targets: [
    //     {
    //       src: 'data/**/**/*', // 将根目录中的 webfonts 目录复制到打包后的输出目录中
    //       dest: 'data/webfonts'
    //     },
        
    //     {
    //       src: 'src/assets/global.css', // 将 global.css 文件复制到打包后的输出目录中
    //       dest: 'assets'
    //     },
    //     {
    //       src: 'src/fonts/**/*', // 将 fonts 目录中的所有文件复制到打包后的输出目录中
    //       dest: 'fonts'
    //     }
    //   ]
    // })
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, 'src')
    }
  },
  esbuild: {
    jsxFactory: 'h',
    jsxFragment: 'Fragment',
    jsxInject: "import { h } from 'vue';"
  },
  build: {
    sourcemap: false, // 生产环境中不生成 source map
    minify: 'terser' // 确保使用 terser 进行代码压缩和混淆
  },
  assetsInclude: ['**/*.txt'],
  server: {
    proxy: {
      '/scan': {
        target: 'http://localhost:3456',
        changeOrigin: true,
      },
      '/align': {
        target: 'http://localhost:3457',
        changeOrigin: true,
      },      
      '/api': {
        target: 'http://localhost:3001',
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
})
