# 数据库补充计划

日期：2026-05-21

范围：`Engineered_sup_tRNA` 全表 1136 行。

## 已完成的补库前置工作

- 已完成全表数据库备份。
- 已完成 65 个 PMID 的来源下载和验证。
- 已生成每篇 PMID 的 md 说明。
- 已隔离 108 个 PMC binary endpoint 返回的 challenge 假文件。
- 已通过 PMC OA package 获得 16 篇的真实 PDF/XML 和 52 个真实 supplementary 文件。

## 不能直接自动补的字段

当前缺二级结构的行同时缺 origin sequence，因此不能直接用 `tRNAscan-SE` 自动补。必须先从论文、补充表或可靠数据库来源补齐序列。

受影响 PMID：

| PMID | 受影响行数 | 主要问题 |
| --- | ---: | --- |
| 2602139 | 3 | origin/sup sequence 缺失 |
| 6363071 | 1 | origin/sup sequence 缺失；全文需人工获取 |
| 9447966 | 5 | origin/sup sequence 缺失 |
| 11866580 | 1 | origin/sup sequence 缺失；全文需人工获取 |
| 15222758 | 1 | origin sequence 缺失；全文需人工获取 |
| 17685515 | 8 | origin/sup sequence 缺失；全文需人工获取 |
| 17698637 | 2 | origin/sup sequence 缺失 |
| 19378306 | 2 | origin/sup sequence 缺失 |
| 19749377 | 2 | origin/sup sequence 缺失；全文需人工获取 |
| 23274575 | 1 | origin sequence 缺失；全文需人工获取 |
| 23379331 | 2 | origin sequence 缺失 |
| 24386240 | 1 | origin sequence 缺失 |
| 30778053 | 95 | origin sequence 缺失；supplementary 已下载，可作为优先整理对象 |
| 31346230 | 1 | origin/sup sequence 缺失 |
| 33069552 | 2 | origin/sup sequence 缺失 |
| 39558163 | 3 | origin sequence 缺失；supplementary 已下载 |

行级清单：

`field-curation-workdir/full_tRNAtherapeutics/row_gap_report.tsv`

## AF3 pdbid 缺口处理状态

这些行的序列和二级结构已存在，原先只差三维结构模型。2026-06-05 已完成 AF3 预测、CIF 上传和数据库 `pdbid` 回填；实时库 `Engineered_sup_tRNA` 当前 `pdbid` 缺口为 0。

| PMID | ENSURE_ID | 计划 pdbid | 说明 |
| --- | --- | --- | --- |
| 30778053 | ensure-364 | PRF | AF3 新预测；无同序列模型可复用 |
| 41261131 | 1200 | PRA | AF3 新预测；reporter screen hit，不作为疾病治疗验证证据 |
| 41261131 | 1204 | PRB | AF3 新预测；reporter screen hit，不作为疾病治疗验证证据 |
| 41261131 | 1210 | PRC | AF3 新预测；in vivo GFP reporter |
| 41261131 | 1211 | PRD | AF3 新预测；in vivo GFP reporter |
| 41261131 | 1212 | PRE | AF3 新预测；Hurler syndrome 相关验证 |

AF3 输入目录：

`field-curation-workdir/full_tRNAtherapeutics/af3_inputs/`

已执行回填 SQL：

`field-curation-workdir/full_tRNAtherapeutics/af3_inputs/update_pdbid_after_af3_upload.sql`

完成记录：

`docs/curation/tRNAtherapeutics/reports/af3_missing_pdbid_completion_20260605.md`

## 建议补库顺序

1. 先处理已有真实全文和 supplementary 的 PMID，避免靠摘要猜字段。
2. 优先处理 `30778053`，因为它占 95 个 origin sequence/secondary-structure 缺口，且 OA package 和 supplementary 已经下载。
3. 再处理 `39558163`，缺 3 个 origin sequence，已有 PMC/OA 材料。
4. 对没有 PMCID 的 21 篇，等待用户提供全文 PDF/补充数据后再补。
5. `pdbid` 的 AF3 CIF 已上传并完成回填；后续只需继续处理 origin sequence/secondary-structure 缺口。

## 当前不应执行的操作

- 不应把 PMC challenge HTML 当作 supplementary。
- 不应从 `sup-tRNA_gene` 中的序列字符串直接当作 origin sequence。
- 不应在没有论文证据时用“反向改 anticodon”的方式推断 origin sequence。
- 不应为没有论文证据的剩余字段做推断式补库；尤其不能把 reporter screen hit 写成疾病治疗验证。
