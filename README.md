
# ENSURE / tRNA 治疗数据库

ENSURE（the Encyclopedia of Suppressor tRNA with an AI assistant）是聚焦抑制型 tRNA 的学术数据库，提供可视化、检索、AI 辅助问答和后端序列比对服务，支持遗传疾病相关研究。网页版：https://trna.lumoxuan.cn/

ENSURE is an academic database focused on suppressor tRNAs. It combines visualization, search, an AI assistant, and a backend sequence alignment service to support research on genetic diseases. Web access: https://trna.lumoxuan.cn/

## 功能概览 | Features
- 浏览和检索抑制型 tRNA 数据，配合图表与表格展示  
- AI 助手回答 ENSURE 数据相关问题  
- Python Flask 序列搜索服务，按 PMID / ENSURE_ID 过滤并做 pairwise alignment  
- 基于 Vue 3 + Vite + Element Plus 的交互式前端  
- Browse and query suppressor tRNA entries with charts and tables  
- AI assistant for ENSURE-related queries  
- Python Flask alignment service with PMID / ENSURE_ID filters  
- Interactive frontend built with Vue 3, Vite, and Element Plus

## 仓库结构 | Repository
- `src/`: 前端源码（Vue 3、TypeScript、Element Plus）  
- `public/`: 静态资源与站点图标  
- `searchservice.py`: Flask 搜索/比对服务，默认监听 8000  
- `restart_searchservice.sh`: 定时重启 `searchservice.py` 的辅助脚本  
- `scan.py`: 打印项目目录树的工具脚本  
- 其他：`package.json`、`vite.config.js`、`tsconfig.json` 等构建配置  
- `src/`: Frontend source (Vue 3, TypeScript, Element Plus)  
- `public/`: Static assets and icons  
- `searchservice.py`: Flask search/alignment service (default port 8000)  
- `restart_searchservice.sh`: Helper to periodically restart the service  
- `scan.py`: Utility to print the project tree  
- Build configs: `package.json`, `vite.config.js`, `tsconfig.json`, etc.

## 快速开始（前端）| Frontend Quickstart
前置：Node.js 18+，推荐 pnpm。  
Prerequisites: Node.js 18+, pnpm recommended.

```bash
pnpm install
pnpm run dev       # dev server
pnpm run build     # production build
pnpm run preview   # preview build
```

## 可选：本地序列搜索服务 | Optional Alignment Service
用于在本地或远程 CSV 中按行筛选并对齐序列，可独立部署。  
Standalone Flask service for filtering/alignment across local or remote CSVs.

1) 安装依赖（Python 3.9+）：Install deps  
```bash
pip install flask flask-cors biopython pandas requests
```
2) 启动服务（默认 8000）：Run the service  
```bash
python searchservice.py
```
3) 守护/定时重启：Daemon-like restart  
```bash
chmod +x restart_searchservice.sh
./restart_searchservice.sh
```
接口：`/health`（GET，存活检查），`/search`（POST，字段 `query_seq`、`csv_paths`、`pmids`、`ensure_ids` 及打分参数）。  
Endpoints: `/health` for liveness; `/search` POST with `query_seq`, `csv_paths`, `pmids`, `ensure_ids`, and scoring params.

## 数据与使用许可 | Data & Usage
The ENSURE database is provided for academic and non-commercial research use only. Commercial use requires prior written permission from the authors and Sun Yat-sen University.  
ENSURE 数据库仅供学术与非商业研究使用；商业用途需事先获得作者和中山大学的书面许可。

## 引用 | Citation
Cite ENSURE:  
Zhuo Ouyang, Yifeng Zhang, Fan Feng, Xudong Zeng, Qiuhui Wu, Abdul Hafeez, Wenkai Teng, Yixin Kong, Xuan Bu, Yang Sun, Bin Li, Yanzi Wen, Zhao-Rong Lun, Lianghu Qu, Xiao Feng, Lingling Zheng, ENSURE: the encyclopedia of suppressor tRNA with an AI assistant, Nucleic Acids Research, 2025; gkaf1062, https://doi.org/10.1093/nar/gkaf1062
