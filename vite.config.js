import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import path from "path"
import terser from "@rollup/plugin-terser"; // 引入 terser 插件

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
    })
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
      }
    },
  },
})
