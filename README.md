# ENSURE

ENSURE（The Encyclopedia of Suppressor tRNA with an AI Assistant）是一个面向 suppressor tRNA 研究的数据库与可视化平台，聚合疾病与癌症相关编码变异、natural sup-tRNA、engineered sup-tRNA 以及 tRNA functional elements 数据，并提供结构展示、序列检索、数据下载和 AI 助手能力。

- 在线访问: https://trna.lumoxuan.cn/
- 论文: ENSURE: the encyclopedia of suppressor tRNA with an AI assistant, *Nucleic Acids Research* (2025), DOI: `10.1093/nar/gkaf1062`, PMID: `41160884`
- 本仓库包含 ENSURE 的 Vue 3 前端、Flask 后端、帮助文档和离线数据处理脚本

## 数据范围

以下数量来自论文摘要，线上库内容可能会继续更新：

- 2152 条 disease- and cancer-associated nonsense/missense/frameshift variants
- 86 条 experimentally validated natural sup-tRNAs
- 1108 条 engineered suppressor tRNA strategies
- 487 条 curated tRNA element records

## 主要模块

- `Coding Variation in Disease/Cancer`: 浏览疾病和癌症中的 missense、nonsense、frameshift 变异
- `Natural sup-tRNA`: 查看天然 suppressor tRNA 的物种、序列和结构信息
- `Engineered sup-tRNA`: 浏览工程化 sup-tRNA 与治疗策略条目
- `tRNA Elements`: 汇总 modification/function、aaRS recognition、EF-Tu recognition 等功能元件
- `Display / Expanded`: 查看条目详情、二维结构和相关可视化
- `Blast / Search`: 按序列进行比对检索
- `Download`: 导出单表或整站数据集
- `AI Yingying`: 结合数据库、帮助文档与可选 PubMed 检索的对话助手
- `Admin`: 后台可管理 `Engineered_sup_tRNA` 数据，并在 MySQL 中维护 LLM provider/model 配置（DeepSeek / Ollama）
- `Help / Docs / Audio`: 面向用户的帮助文档、API 说明与教学资源页面

站点路由概览见 `public/docs/99-Site-Map.md`，API 快速说明见 `public/docs/98-API-Reference.md`。

## 技术栈

- 前端: Vue 3, Vite, TypeScript, Element Plus, Vue Router
- 可视化: ECharts, D3, NGL, vue-echarts, vxe-table
- 后端: Flask, SQLAlchemy, MySQL, Biopython, Pandas
- AI 相关: Ollama-compatible chat backend、文档检索、可选 PubMed 工具
- 部署相关: Gunicorn、可选 MinIO 导出缓存

## 仓库结构

```text
.
├── src/                # Vue 3 前端源码
├── public/docs/        # 站内帮助文档、站点地图、API 说明、论文 PDF
├── Flask/              # 主 Flask API（表格、导出、AI、检索）
├── searchservice.py    # 独立的轻量序列搜索/比对服务
├── tools/data-prep/    # 离线数据处理、序列整理、BLAST 辅助脚本
├── vite.config.js      # 前端构建与本地代理配置
└── package.json        # 前端依赖与脚本
```

## 本地开发

### 前置要求

- Node.js 18+
- `pnpm`（仓库包含 `pnpm-lock.yaml`）
- Python 3.10+（建议）
- MySQL（完整后端需要）
- 可选: Ollama、MinIO

### 只启动前端

如果你只想看静态页面或做前端开发：

```bash
pnpm install
pnpm dev
pnpm build
pnpm preview
```

默认开发地址为 `http://localhost:5174`。

注意：很多页面依赖后端接口；如果没有后端，表格、下载、AI、序列检索等功能不会完整工作。

### 启动完整 ENSURE 后端

推荐直接使用仓库内置的跨平台启动脚本。它会在首次启动时自动：

- 创建 `Flask/.venv`
- 安装 `Flask/requirements.txt` 中的后端依赖
- 启动 Flask 后端

1. 配置环境变量

后端会自动读取 `Flask/.env`。至少需要以下数据库配置之一：

- `DATABASE_URL`
- 或 `MYSQL_HOST`、`MYSQL_PORT`、`MYSQL_DB`/`MYSQL_DATABASE`、`MYSQL_USER`、`MYSQL_PASSWORD`

常见可选配置：

- `MINIO_ENDPOINT`、`MINIO_ACCESS_KEY`、`MINIO_SECRET_KEY`、`MINIO_BUCKET`、`MINIO_PUBLIC_BASE`
- `OLLAMA_BASE_URL`、`OLLAMA_MODEL`、`OLLAMA_TIMEOUT`
- `PUBMED_ENABLE`、`PUBMED_API_KEY`、`PUBMED_EMAIL`
- `EMBEDDING_ENABLE`、`EMBEDDING_INDEX_PATH`、`EMBEDDING_DOCS_DIR`
- `EXPORT_WARM_ON_START`、`EXPORT_WARM_FORMATS`

2. 启动 Flask API

Linux:

```bash
./Flask/start_backend.sh
```

Windows:

```bat
Flask\start_backend.bat
```

也可以直接用同一个 Python 脚本，在 Windows 和 Linux 都通用：

```bash
python Flask/scripts/start_backend.py
```

默认监听 `http://localhost:8010`。

如果你还想继续换端口，可以这样：

```bash
python Flask/scripts/start_backend.py --port 8020
```

也支持同时指定 host：

```bash
python Flask/scripts/start_backend.py --host 0.0.0.0 --port 8020
```

首次启动会自动装依赖；如果你后面更新了依赖，想强制重新安装：

```bash
python Flask/scripts/start_backend.py --install
```

3. 启动前端

```bash
pnpm install
pnpm dev
```

开发模式下，Vite 会把以下接口代理到 `http://localhost:8010`：

- `/search`
- `/table_rows`
- `/table_stats`
- `/table_fulltext_rebuild`
- `/download_table`
- `/download_table_status`
- `/download_bundle_status`
- `/chat/api/*`

### 手动方式（可选）

如果你不想用启动脚本，也可以手动启动：

```bash
cd Flask
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python wsgi.py
```

Linux 生产环境可选 Gunicorn：

```bash
cd Flask
source .venv/bin/activate
pip install gunicorn
gunicorn -c gunicorn.conf.py wsgi:app
```

### 仅启动轻量序列搜索服务

如果你只需要 CSV/URL 序列比对，不需要 MySQL、AI 和导出接口，可以直接运行仓库根目录下的 `searchservice.py`：

```bash
python -m venv .venv
source .venv/bin/activate
pip install flask flask-cors biopython pandas requests
python searchservice.py
```

这个服务只提供：

- `GET /health`
- `GET /search`
- `POST /search`

它不能替代 `Flask/` 下的完整 ENSURE API，并且默认监听 `8000` 端口；完整后端默认监听 `8010`。

## 前端可选环境变量

如果需要覆盖默认前端行为，可配置以下变量：

- `VITE_CHAT_API_BASE`: 自定义聊天接口前缀，默认是 `/chat/api`
- `VITE_OPENAI_API_KEY`: 音视频总结页面使用的可选 API key
- `VITE_API_KEY`、`VITE_API_KEY_11`、`VITE_API_KEY_DEFAULT`: AI 页面兼容使用的可选 key

## API 概览

完整后端中比较核心的接口包括：

- `GET /health`
- `POST /table_rows`
- `POST /table_stats`
- `POST /search`
- `GET /download_table`
- `GET /download_table_status`
- `GET /download_bundle_status`
- `GET /chat/api/application/profile`
- `GET /chat/api/open`
- `POST /chat/api/chat_message/<chat_id>`

更详细的示例请求可参考 `public/docs/98-API-Reference.md`。

## 开发说明

- `public/docs/` 下的 Markdown/PDF 同时用于帮助页和后端文档检索
- `tools/data-prep/` 保存了离线数据整理与 BLAST 辅助脚本
- 当前仓库没有看到可直接导入的完整 MySQL 数据快照；完整站点功能依赖现成数据库
- 生产环境 Gunicorn 监听与 worker 配置位于 `Flask/gunicorn.conf.py`

## 使用许可

ENSURE 数据库仅供学术与非商业研究使用。商业用途需事先获得作者和中山大学的书面许可。

## 引用

```text
Zhuo Ouyang, Yifeng Zhang, Fan Feng, Xudong Zeng, Qiuhui Wu, Abdul Hafeez,
Wenkai Teng, Yixin Kong, Xuan Bu, Yang Sun, Bin Li, Yanzi Wen, Zhao-Rong Lun,
Lianghu Qu, Xiao Feng, Lingling Zheng, ENSURE: the encyclopedia of suppressor
tRNA with an AI assistant, Nucleic Acids Research, 2025; gkaf1062,
https://doi.org/10.1093/nar/gkaf1062
```
