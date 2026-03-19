# Legacy `pictureid` Runtime Cutover Plan

## Goal

把站点从“运行时直接用 `pictureid -> https://.../picture/{value}.png` 模板拼接”彻底升级到“前台与后台统一消费结构化媒体绑定”的模式。

这次升级的目标是切掉历史 `pictureid` 的运行时 fallback 和后台迁移控制面，不再让前台依赖硬编码 URL 模板。

## Verified Current State

2026-03-19 在当前数据库中再次核验，结果如下：

- `nonsense_sup_rna`：`pictureid` 非空记录 `52` 条，`table_field/pictureid` 绑定 `52` 条
- `frameshift_sup_trna`：`pictureid` 非空记录 `34` 条，`table_field/pictureid` 绑定 `34` 条
- 合计 `pictureid` 字段绑定 `86` 条
- `source_type='legacy_pictureid'` 的媒体资产 `77` 条
- `pictureid` 绑定缺失目标资产 `0` 条

结论：

- 历史 `pictureid` 数据回填已经完成
- 旧迁移面板和 dry-run/execute 接口不再需要继续保留
- 但 `pictureid` 原始字段本身仍然存在于业务表，后台编辑时仍需继续同步结构化绑定

## Scope

本次升级包含：

1. 删除管理端“历史 `pictureid` 迁移”面板
2. 删除 `/admin/api/media/legacy_pictureid/preview` 与 `/admin/api/media/legacy_pictureid/migrate`
3. 删除前台页面对 `pictureid` 模板 URL 的运行时 fallback
4. 删除 `tableMedia.ts` 里针对 `pictureid`/BLAST 的默认模板规则
5. 让 BLAST 结果页改为读取结构化媒体绑定，而不是把 `pictureid` 拼成固定 MinIO URL

本次升级不包含：

- 删除数据库中的 `pictureid` 列
- 删除后台 `create/update` 后的 `_sync_legacy_pictureid_field_binding`
- 删除 `legacy_pictureid` 资产类型本身

## Why The Sync Bridge Stays

虽然历史数据已经迁完，但 `pictureid` 字段仍然是后台可编辑的真实数据库列。

如果现在连 `_sync_legacy_pictureid_field_binding` 一起删除，会立刻产生两个问题：

- 管理员后续修改 `pictureid` 后，结构化绑定不会跟着更新
- 前台已经切到只读结构化绑定后，图片会因为绑定过期而消失

因此，本次切的是“运行时 fallback”和“迁移控制面”，不是“字段级同步桥接”。

## Current Legacy Dependencies

升级前仍有这些旧依赖：

- `src/utils/tableMedia.ts`
  - `nonsense_sup_rna.pictureid`
  - `frameshift_sup_trna.pictureid`
  - `frameshift_sup_trna.Notes`
  - `blast_results.pictureid`
- `src/views/natural-sup-tRNA/natural-sup-tRNA-1.vue`
  - `resolveMediaSource(TABLE_NAME, 'pictureid', record?.pictureid)`
- `src/views/natural-sup-tRNA/Frameshift sup-tRNA.vue`
  - `resolveMediaSource(TABLE_NAME, 'pictureid', record?.pictureid)`
  - `Notes` 位置仍按旧模板尝试渲染图片
- `src/views/blast/BlastResults.vue`
  - `pictureid` 行仍走旧按钮逻辑
- `src/views/blast/keycell.tsx`
  - 直接硬编码 `https://minio.lumoxuan.cn/ensure/picture/${pictureid}.png`
- `src/views/admin/AdminMediaPanel.vue`
  - 还保留历史迁移面板
- `src/utils/admin.ts`
  - 还保留历史迁移 preview / migrate API client
- `Flask/app/routes.py`
  - 还保留历史迁移 preview / migrate 路由和辅助函数

## Target State

升级完成后，行为应为：

- Natural Nonsense sup-tRNA 与 Frameshift sup-tRNA 页面只读结构化媒体绑定
- BLAST 结果页只在记录存在结构化绑定时显示图片预览入口
- 管理端媒体页不再展示历史迁移操作区
- `tableMedia.ts` 不再把 `pictureid` 视为默认模板图片字段
- 后台继续在 `pictureid` 字段写入后同步绑定，直到后续专门做 schema cleanup

## Implementation Steps

### Step 1. Remove Admin Migration Surface

- 删除 `AdminMediaPanel.vue` 中的历史迁移面板、状态和事件
- 删除 `src/utils/admin.ts` 中的 preview / migrate 类型与 API client
- 删除 `src/utils/adminI18n.ts` 中仅供迁移面板使用的文案
- 删除 `Flask/app/routes.py` 中的 preview / migrate 路由与对应辅助函数
- 删除只覆盖 preview / migrate 的测试

### Step 2. Cut Public Runtime Over To Structured Media

- `natural-sup-tRNA-1.vue`
  - 改为优先读取 `Structure of sup-tRNA` 绑定
  - 再读取 `pictureid` 绑定
  - 不再调用 `resolveMediaSource(..., 'pictureid', ...)`
- `Frameshift sup-tRNA.vue`
  - 同样移除 `pictureid` 模板 fallback
  - `Notes` 仅在有结构化图片或真实 URL 时才渲染图片，否则显示文本
- `BlastResults.vue`
  - `pictureid` 行改为读取 `row_data.__media.fields.pictureid`
  - 若无绑定则显示不可用，不再拼接模板 URL
- `/search` 与 tool `search_alignment`
  - 在返回 MySQL 对齐结果前给 `row_data` 注入 `__media`

### Step 3. Remove Default Legacy Templates

- 删除 `src/utils/tableMedia.ts` 中以下默认模板规则：
  - `nonsense_sup_rna.pictureid`
  - `frameshift_sup_trna.pictureid`
  - `frameshift_sup_trna.Notes`
  - `blast_results.pictureid`
- 保留 `Structure of sup-tRNA` 这类仍然真实存在的媒体字段默认规则

## Acceptance Criteria

满足以下条件才算本次升级完成：

- 管理端媒体页不再出现“历史 `pictureid` 迁移”卡片
- `/admin/api/media/legacy_pictureid/preview` 返回 404
- `/admin/api/media/legacy_pictureid/migrate` 返回 404
- Nonsense / Frameshift 页面仍能正常显示历史结构图
- BLAST 结果页点击 `pictureid` 时能打开绑定图片，不再依赖固定 MinIO 模板 URL
- `tableMedia.ts` 中不再存在 `pictureid` 的默认模板图片规则
- 后台 `pictureid` 字段编辑后，结构化绑定仍能继续同步

## Verification

- `pytest Flask/tests/test_media_admin.py -q`
- `npm run build`
- 手工检查：
  - 媒体页首屏
  - `nonsense_sup_rna`
  - `frameshift_sup_trna`
  - BLAST 搜索结果展开行

## Deferred Cleanup

只有在后续满足这两个条件后，才能删除最后的同步桥接：

1. 后台不再允许把 `pictureid` 作为业务字段编辑
2. 前台与后台图片选择都改成“直接绑定资产”，不再依赖原始 `pictureid` 值

那时才可以继续删除：

- `_sync_legacy_pictureid_field_binding`
- `_legacy_pictureid_row_summary`
- `_legacy_pictureid_sync_asset`
- `legacy_pictureid` 相关管理端特殊处理
