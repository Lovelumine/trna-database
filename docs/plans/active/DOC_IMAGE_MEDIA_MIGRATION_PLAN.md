# Doc Image Media Migration Plan

## Goal

将 `public/docs/*.md` 里的历史 Markdown 图片从“直接写死旧 URL”升级为“媒体库资产 + 文档绑定 + Markdown 回写”。

最终状态：

- 历史文档图片进入 `media_assets`
- 新导入图片统一标记为 `source_type=docs`
- 文档中的旧 URL 回写成媒体库 `public_url`
- 每个文档图片位置生成 `doc_image` 绑定
- 后续 admin 保存 Markdown 时，`doc_image` 绑定自动同步，不再漂移

## Current State

- 历史文档图片仍直接写在 `public/docs/*.md`
- 管理后台已经支持“从媒体库插图 / 上传并插图”，但这只覆盖新编辑
- 后端当前只能通过扫描 Markdown 内容识别 `doc_image` 引用，还没有结构化绑定同步

## Scope

本次只处理 `public/docs/*.md` 中的 Markdown 图片语法：

- `![alt](url)`
- `![alt](url "title")`

不处理：

- HTML `<img>`
- PDF
- 站点其他页面中的硬编码图片 URL

## Migration Contract

### Asset Contract

- 先按 `public_url` 精确复用已有资产
- 若 URL 未命中，则下载图片并按 `sha256 + size_bytes` 复用已有资产
- 仍未命中时，上传新资产到媒体库
- 新上传资产统一使用 `source_type=docs`

### Markdown Rewrite Contract

- 只改写图片 URL，不改动正文结构
- 优先保留原来的 alt 文本
- 原 URL 与媒体库 URL 相同时，不重复改写

### Binding Contract

- 每个文档图片位置写入一条 `doc_image` 绑定
- `resource_name = 文档文件名`
- `slot_key = image_001 / image_002 / ...`
- `extra_json` 保存原始 `src / alt / title`

## Execution Steps

1. 新增迁移脚本 `Flask/scripts/migrate_doc_markdown_images.py`
2. 扫描 `public/docs/*.md`，提取 Markdown 图片引用
3. 逐张图片执行“URL 命中 -> 哈希复用 -> 上传新资产”
4. 将旧 URL 回写为媒体库 `public_url`
5. 对每篇文档同步 `doc_image` 绑定
6. 给 admin 文档保存/创建/删除补上 `doc_image` 绑定同步
7. 输出 JSON 迁移报告

## Validation

- 所有历史 Markdown 图片 URL 都应能命中媒体库资产或被新建资产替代
- 改写后的 Markdown 不再指向旧 `help/` 或 `trna.lumoxuan.cn/docs/` 图片 URL
- `media detail` 中应能看到 `doc_image` 结构化引用，不再只靠扫描
- 重跑迁移脚本应保持幂等

## Rollback

- Markdown 文件本身受 Git 管理，可直接回退
- 迁移报告保留本次导入与改写结果，便于核对
- 若需要删除新导入资产，先删除 `doc_image` 绑定，再清理 `media_assets`

## Execution Log

- Completed: initial scan found `19` historical Markdown image refs across `4` docs
- Completed: restored `5` missing local source images from Git history before migration
- Completed: imported `19` images into `media_assets` with `source_type=docs`
- Completed: rewrote `19` legacy image URLs in `4` Markdown docs
- Completed: added `doc_image` binding sync for admin doc create/save/delete
- Completed: final migration report written to `docs/reports/doc_image_media_migration_report.json`
