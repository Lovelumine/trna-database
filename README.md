
# tRNA治疗数据库 🧬

欢迎访问 [tRNA治疗数据库](https://trna.lumoxuan.cn/)，一个致力于推动遗传疾病治疗研究的平台。

## 文件结构 📁
```
trna-database/
├── 📄 package.json
├── 📄 index.html
├── 📄 README.md
├── 📄 vite.config.js
├── 📄 tsconfig.json
├── 📄 .gitignore
├── 🐍 scan.py
├── 📂 data/
│   └── 📊 3-coding-variation-Disease.csv
├── 📂 public/
│   ├── 🖼️ vite.svg
│   ├── 🖼️ favicon.ico
│   └── 🖼️ logo.webp
├── 📂 src/
│   ├── 🖥️ App.vue
│   ├── 🖥️ main.ts
│   └── 📂 views/
│       ├── 🏠 Home.vue
│       └── 🧬 CodingVariationDisease.vue
└── 📂 assets/
    ├── 📄 mouse.css
    └── 📄 search.css
```

## 安装与运行 🛠️

### 环境需求 🌍

- Node.js
- npm 或 pnpm

### 安装依赖 📦

在项目根目录下运行以下命令安装依赖：

```bash
pnpm install
```

### 运行项目 🚀

启动开发服务器：

```bash
pnpm run dev
```

构建生产版本：

```bash
pnpm run build
```

预览生产构建：

```bash
pnpm run preview
```

