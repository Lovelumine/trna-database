// vite.config.js
import { defineConfig } from "file:///home/yingying/Documents/trna-database/node_modules/.pnpm/vite@5.2.12_@types+node@20.14.6_sass@1.77.6_terser@5.31.1/node_modules/vite/dist/node/index.js";
import vue from "file:///home/yingying/Documents/trna-database/node_modules/.pnpm/@vitejs+plugin-vue@5.0.5_vite@5.2.12_@types+node@20.14.6_sass@1.77.6_terser@5.31.1__vue@3.4.27_typescript@5.4.5_/node_modules/@vitejs/plugin-vue/dist/index.mjs";
import vueJsx from "file:///home/yingying/Documents/trna-database/node_modules/.pnpm/@vitejs+plugin-vue-jsx@3.1.0_vite@5.2.12_@types+node@20.14.6_sass@1.77.6_terser@5.31.1__vue@3.4.27_typescript@5.4.5_/node_modules/@vitejs/plugin-vue-jsx/dist/index.mjs";
import path from "path";
import terser from "file:///home/yingying/Documents/trna-database/node_modules/.pnpm/@rollup+plugin-terser@0.4.4_rollup@4.18.0/node_modules/@rollup/plugin-terser/dist/es/index.js";
import { viteStaticCopy } from "file:///home/yingying/Documents/trna-database/node_modules/.pnpm/vite-plugin-static-copy@1.0.5_vite@5.2.12_@types+node@20.14.6_sass@1.77.6_terser@5.31.1_/node_modules/vite-plugin-static-copy/dist/index.js";
var __vite_injected_original_dirname = "/home/yingying/Documents/trna-database";
var allowedOrigin = "https://trna.lumoxuan.cn/";
var vite_config_default = defineConfig({
  plugins: [
    vue(),
    vueJsx({}),
    terser({
      // 配置 terser 插件
      format: {
        comments: false
        // 移除注释
      },
      compress: {
        drop_console: true,
        // 移除 console
        drop_debugger: true
        // 移除 debugger
      },
      mangle: {
        // 混淆配置
        properties: {
          regex: /^_/
          // 混淆以 _ 开头的属性名
        },
        toplevel: true,
        // 混淆顶层作用域中的变量和函数名称
        reserved: ["_", "Vue"]
        // 不混淆全局的 Vue 变量以及其他可能需要保留的标识符
      }
    })
  ],
  resolve: {
    alias: {
      "@": path.resolve(__vite_injected_original_dirname, "src")
    }
  },
  esbuild: {
    jsxFactory: "h",
    jsxFragment: "Fragment",
    jsxInject: "import { h } from 'vue';"
  },
  build: {
    sourcemap: false,
    // 生产环境中不生成 source map
    minify: "terser"
    // 确保使用 terser 进行代码压缩和混淆
  },
  assetsInclude: ["**/*.txt"],
  server: {
    host: "0.0.0.0",
    // 允许外部访问
    port: 5174,
    // 使用5174端口
    strictPort: true,
    proxy: {
      "/scan": {
        target: "http://localhost:3456",
        changeOrigin: true
      },
      "/align": {
        target: "http://localhost:3457",
        changeOrigin: true
      },
      "/chat": {
        target: "http://localhost:3001",
        changeOrigin: true
      },
      "/api": {
        target: "http://localhost:8080/api",
        changeOrigin: true
      },
      "/run-blast": {
        target: "http://localhost:3945",
        changeOrigin: true
      }
    },
    // 使用 configureServer API 添加中间件来检查请求来源
    configureServer: (server) => {
      server.middlewares.use((req, res, next) => {
        const origin = req.headers.origin;
        if (origin && origin !== allowedOrigin) {
          res.statusCode = 403;
          res.end("Forbidden");
        } else {
          next();
        }
      });
    }
  },
  optimizeDeps: {
    exclude: [
      "@formkit/vue",
      "@formkit/addons",
      "@formkit/i18n",
      "chunk-LH747XKU.js",
      "chunk-G3PMV62Z.js"
    ]
  },
  base: "./"
});
export {
  vite_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcuanMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCIvaG9tZS95aW5neWluZy9Eb2N1bWVudHMvdHJuYS1kYXRhYmFzZVwiO2NvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9maWxlbmFtZSA9IFwiL2hvbWUveWluZ3lpbmcvRG9jdW1lbnRzL3RybmEtZGF0YWJhc2Uvdml0ZS5jb25maWcuanNcIjtjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfaW1wb3J0X21ldGFfdXJsID0gXCJmaWxlOi8vL2hvbWUveWluZ3lpbmcvRG9jdW1lbnRzL3RybmEtZGF0YWJhc2Uvdml0ZS5jb25maWcuanNcIjtpbXBvcnQgeyBkZWZpbmVDb25maWcgfSBmcm9tICd2aXRlJ1xuaW1wb3J0IHZ1ZSBmcm9tICdAdml0ZWpzL3BsdWdpbi12dWUnXG5pbXBvcnQgdnVlSnN4IGZyb20gJ0B2aXRlanMvcGx1Z2luLXZ1ZS1qc3gnXG5pbXBvcnQgcGF0aCBmcm9tIFwicGF0aFwiXG5pbXBvcnQgdGVyc2VyIGZyb20gXCJAcm9sbHVwL3BsdWdpbi10ZXJzZXJcIjsgLy8gXHU1RjE1XHU1MTY1IHRlcnNlciBcdTYzRDJcdTRFRjZcbmltcG9ydCB7IHZpdGVTdGF0aWNDb3B5IH0gZnJvbSAndml0ZS1wbHVnaW4tc3RhdGljLWNvcHknOyAvLyBcdTVGMTVcdTUxNjUgdml0ZS1wbHVnaW4tc3RhdGljLWNvcHkgXHU2M0QyXHU0RUY2XG5cbi8vIFx1NTE0MVx1OEJCOFx1NzY4NFx1Njc2NVx1NkU5MFx1N0FEOVx1NzBCOVxuY29uc3QgYWxsb3dlZE9yaWdpbiA9ICdodHRwczovL3RybmEubHVtb3h1YW4uY24vJztcblxuZXhwb3J0IGRlZmF1bHQgZGVmaW5lQ29uZmlnKHtcbiAgcGx1Z2luczogW1xuICAgIHZ1ZSgpLFxuICAgIHZ1ZUpzeCh7fSksXG4gICAgdGVyc2VyKHsgLy8gXHU5MTREXHU3RjZFIHRlcnNlciBcdTYzRDJcdTRFRjZcbiAgICAgIGZvcm1hdDoge1xuICAgICAgICBjb21tZW50czogZmFsc2UsIC8vIFx1NzlGQlx1OTY2NFx1NkNFOFx1OTFDQVxuICAgICAgfSxcbiAgICAgIGNvbXByZXNzOiB7XG4gICAgICAgIGRyb3BfY29uc29sZTogdHJ1ZSwgLy8gXHU3OUZCXHU5NjY0IGNvbnNvbGVcbiAgICAgICAgZHJvcF9kZWJ1Z2dlcjogdHJ1ZSAvLyBcdTc5RkJcdTk2NjQgZGVidWdnZXJcbiAgICAgIH0sXG4gICAgICBtYW5nbGU6IHsgLy8gXHU2REY3XHU2REM2XHU5MTREXHU3RjZFXG4gICAgICAgIHByb3BlcnRpZXM6IHtcbiAgICAgICAgICByZWdleDogL15fLyAvLyBcdTZERjdcdTZEQzZcdTRFRTUgXyBcdTVGMDBcdTU5MzRcdTc2ODRcdTVDNUVcdTYwMjdcdTU0MERcbiAgICAgICAgfSxcbiAgICAgICAgdG9wbGV2ZWw6IHRydWUsIC8vIFx1NkRGN1x1NkRDNlx1OTg3Nlx1NUM0Mlx1NEY1Q1x1NzUyOFx1NTdERlx1NEUyRFx1NzY4NFx1NTNEOFx1OTFDRlx1NTQ4Q1x1NTFGRFx1NjU3MFx1NTQwRFx1NzlGMFxuICAgICAgICByZXNlcnZlZDogWydfJywgJ1Z1ZSddIC8vIFx1NEUwRFx1NkRGN1x1NkRDNlx1NTE2OFx1NUM0MFx1NzY4NCBWdWUgXHU1M0Q4XHU5MUNGXHU0RUU1XHU1M0NBXHU1MTc2XHU0RUQ2XHU1M0VGXHU4MEZEXHU5NzAwXHU4OTgxXHU0RkREXHU3NTU5XHU3Njg0XHU2ODA3XHU4QkM2XHU3QjI2XG4gICAgICB9XG4gICAgfSksXG4gIF0sXG4gIHJlc29sdmU6IHtcbiAgICBhbGlhczoge1xuICAgICAgXCJAXCI6IHBhdGgucmVzb2x2ZShfX2Rpcm5hbWUsICdzcmMnKVxuICAgIH1cbiAgfSxcbiAgZXNidWlsZDoge1xuICAgIGpzeEZhY3Rvcnk6ICdoJyxcbiAgICBqc3hGcmFnbWVudDogJ0ZyYWdtZW50JyxcbiAgICBqc3hJbmplY3Q6IFwiaW1wb3J0IHsgaCB9IGZyb20gJ3Z1ZSc7XCJcbiAgfSxcbiAgYnVpbGQ6IHtcbiAgICBzb3VyY2VtYXA6IGZhbHNlLCAvLyBcdTc1MUZcdTRFQTdcdTczQUZcdTU4ODNcdTRFMkRcdTRFMERcdTc1MUZcdTYyMTAgc291cmNlIG1hcFxuICAgIG1pbmlmeTogJ3RlcnNlcicgLy8gXHU3ODZFXHU0RkREXHU0RjdGXHU3NTI4IHRlcnNlciBcdThGREJcdTg4NENcdTRFRTNcdTc4MDFcdTUzOEJcdTdGMjlcdTU0OENcdTZERjdcdTZEQzZcbiAgfSxcbiAgYXNzZXRzSW5jbHVkZTogWycqKi8qLnR4dCddLFxuICBzZXJ2ZXI6IHtcbiAgICBob3N0OiAnMC4wLjAuMCcsIC8vIFx1NTE0MVx1OEJCOFx1NTkxNlx1OTBFOFx1OEJCRlx1OTVFRVxuICAgIHBvcnQ6IDUxNzQsIC8vIFx1NEY3Rlx1NzUyODUxNzRcdTdBRUZcdTUzRTNcbiAgICBzdHJpY3RQb3J0OiB0cnVlLFxuICAgIHByb3h5OiB7XG4gICAgICAnL3NjYW4nOiB7XG4gICAgICAgIHRhcmdldDogJ2h0dHA6Ly9sb2NhbGhvc3Q6MzQ1NicsXG4gICAgICAgIGNoYW5nZU9yaWdpbjogdHJ1ZSxcbiAgICAgIH0sXG4gICAgICAnL2FsaWduJzoge1xuICAgICAgICB0YXJnZXQ6ICdodHRwOi8vbG9jYWxob3N0OjM0NTcnLFxuICAgICAgICBjaGFuZ2VPcmlnaW46IHRydWUsXG4gICAgICB9LCAgICAgIFxuICAgICAgJy9jaGF0Jzoge1xuICAgICAgICB0YXJnZXQ6ICdodHRwOi8vbG9jYWxob3N0OjMwMDEnLFxuICAgICAgICBjaGFuZ2VPcmlnaW46IHRydWUsXG4gICAgICB9LFxuICAgICAgJy9hcGknOiB7XG4gICAgICAgIHRhcmdldDogJ2h0dHA6Ly9sb2NhbGhvc3Q6ODA4MC9hcGknLFxuICAgICAgICBjaGFuZ2VPcmlnaW46IHRydWUsXG4gICAgICB9LFxuICAgICAgJy9ydW4tYmxhc3QnOiB7XG4gICAgICAgIHRhcmdldDogJ2h0dHA6Ly9sb2NhbGhvc3Q6Mzk0NScsXG4gICAgICAgIGNoYW5nZU9yaWdpbjogdHJ1ZSxcbiAgICAgIH1cbiAgICB9LFxuICAgIC8vIFx1NEY3Rlx1NzUyOCBjb25maWd1cmVTZXJ2ZXIgQVBJIFx1NkRGQlx1NTJBMFx1NEUyRFx1OTVGNFx1NEVGNlx1Njc2NVx1NjhDMFx1NjdFNVx1OEJGN1x1NkM0Mlx1Njc2NVx1NkU5MFxuICAgIGNvbmZpZ3VyZVNlcnZlcjogKHNlcnZlcikgPT4ge1xuICAgICAgc2VydmVyLm1pZGRsZXdhcmVzLnVzZSgocmVxLCByZXMsIG5leHQpID0+IHtcbiAgICAgICAgY29uc3Qgb3JpZ2luID0gcmVxLmhlYWRlcnMub3JpZ2luO1xuICAgICAgICBpZiAob3JpZ2luICYmIG9yaWdpbiAhPT0gYWxsb3dlZE9yaWdpbikge1xuICAgICAgICAgIHJlcy5zdGF0dXNDb2RlID0gNDAzO1xuICAgICAgICAgIHJlcy5lbmQoJ0ZvcmJpZGRlbicpO1xuICAgICAgICB9IGVsc2Uge1xuICAgICAgICAgIG5leHQoKTtcbiAgICAgICAgfVxuICAgICAgfSk7XG4gICAgfVxuICB9LFxuICBvcHRpbWl6ZURlcHM6IHtcbiAgICBleGNsdWRlOiBbXG4gICAgICAnQGZvcm1raXQvdnVlJyxcbiAgICAgICdAZm9ybWtpdC9hZGRvbnMnLFxuICAgICAgJ0Bmb3Jta2l0L2kxOG4nLFxuICAgICAgJ2NodW5rLUxINzQ3WEtVLmpzJyxcbiAgICAgICdjaHVuay1HM1BNVjYyWi5qcydcbiAgICBdXG4gIH0sXG4gIGJhc2U6IFwiLi9cIlxufSlcbiJdLAogICJtYXBwaW5ncyI6ICI7QUFBb1MsU0FBUyxvQkFBb0I7QUFDalUsT0FBTyxTQUFTO0FBQ2hCLE9BQU8sWUFBWTtBQUNuQixPQUFPLFVBQVU7QUFDakIsT0FBTyxZQUFZO0FBQ25CLFNBQVMsc0JBQXNCO0FBTC9CLElBQU0sbUNBQW1DO0FBUXpDLElBQU0sZ0JBQWdCO0FBRXRCLElBQU8sc0JBQVEsYUFBYTtBQUFBLEVBQzFCLFNBQVM7QUFBQSxJQUNQLElBQUk7QUFBQSxJQUNKLE9BQU8sQ0FBQyxDQUFDO0FBQUEsSUFDVCxPQUFPO0FBQUE7QUFBQSxNQUNMLFFBQVE7QUFBQSxRQUNOLFVBQVU7QUFBQTtBQUFBLE1BQ1o7QUFBQSxNQUNBLFVBQVU7QUFBQSxRQUNSLGNBQWM7QUFBQTtBQUFBLFFBQ2QsZUFBZTtBQUFBO0FBQUEsTUFDakI7QUFBQSxNQUNBLFFBQVE7QUFBQTtBQUFBLFFBQ04sWUFBWTtBQUFBLFVBQ1YsT0FBTztBQUFBO0FBQUEsUUFDVDtBQUFBLFFBQ0EsVUFBVTtBQUFBO0FBQUEsUUFDVixVQUFVLENBQUMsS0FBSyxLQUFLO0FBQUE7QUFBQSxNQUN2QjtBQUFBLElBQ0YsQ0FBQztBQUFBLEVBQ0g7QUFBQSxFQUNBLFNBQVM7QUFBQSxJQUNQLE9BQU87QUFBQSxNQUNMLEtBQUssS0FBSyxRQUFRLGtDQUFXLEtBQUs7QUFBQSxJQUNwQztBQUFBLEVBQ0Y7QUFBQSxFQUNBLFNBQVM7QUFBQSxJQUNQLFlBQVk7QUFBQSxJQUNaLGFBQWE7QUFBQSxJQUNiLFdBQVc7QUFBQSxFQUNiO0FBQUEsRUFDQSxPQUFPO0FBQUEsSUFDTCxXQUFXO0FBQUE7QUFBQSxJQUNYLFFBQVE7QUFBQTtBQUFBLEVBQ1Y7QUFBQSxFQUNBLGVBQWUsQ0FBQyxVQUFVO0FBQUEsRUFDMUIsUUFBUTtBQUFBLElBQ04sTUFBTTtBQUFBO0FBQUEsSUFDTixNQUFNO0FBQUE7QUFBQSxJQUNOLFlBQVk7QUFBQSxJQUNaLE9BQU87QUFBQSxNQUNMLFNBQVM7QUFBQSxRQUNQLFFBQVE7QUFBQSxRQUNSLGNBQWM7QUFBQSxNQUNoQjtBQUFBLE1BQ0EsVUFBVTtBQUFBLFFBQ1IsUUFBUTtBQUFBLFFBQ1IsY0FBYztBQUFBLE1BQ2hCO0FBQUEsTUFDQSxTQUFTO0FBQUEsUUFDUCxRQUFRO0FBQUEsUUFDUixjQUFjO0FBQUEsTUFDaEI7QUFBQSxNQUNBLFFBQVE7QUFBQSxRQUNOLFFBQVE7QUFBQSxRQUNSLGNBQWM7QUFBQSxNQUNoQjtBQUFBLE1BQ0EsY0FBYztBQUFBLFFBQ1osUUFBUTtBQUFBLFFBQ1IsY0FBYztBQUFBLE1BQ2hCO0FBQUEsSUFDRjtBQUFBO0FBQUEsSUFFQSxpQkFBaUIsQ0FBQyxXQUFXO0FBQzNCLGFBQU8sWUFBWSxJQUFJLENBQUMsS0FBSyxLQUFLLFNBQVM7QUFDekMsY0FBTSxTQUFTLElBQUksUUFBUTtBQUMzQixZQUFJLFVBQVUsV0FBVyxlQUFlO0FBQ3RDLGNBQUksYUFBYTtBQUNqQixjQUFJLElBQUksV0FBVztBQUFBLFFBQ3JCLE9BQU87QUFDTCxlQUFLO0FBQUEsUUFDUDtBQUFBLE1BQ0YsQ0FBQztBQUFBLElBQ0g7QUFBQSxFQUNGO0FBQUEsRUFDQSxjQUFjO0FBQUEsSUFDWixTQUFTO0FBQUEsTUFDUDtBQUFBLE1BQ0E7QUFBQSxNQUNBO0FBQUEsTUFDQTtBQUFBLE1BQ0E7QUFBQSxJQUNGO0FBQUEsRUFDRjtBQUFBLEVBQ0EsTUFBTTtBQUNSLENBQUM7IiwKICAibmFtZXMiOiBbXQp9Cg==
