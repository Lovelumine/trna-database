# tRNAtherapeutics 全量整理规范

本规范适用于 `/tRNAtherapeutics` 页面对应的 `Engineered_sup_tRNA` 表。

## 1. 先备份，再整理

- 在 MySQL 中建立整表时间戳备份。
- 导出同一时间点的 TSV/SQL 文件快照。
- 任何字段更新前，再按 PMID 或更新范围导出局部备份。

## 2. 按 PMID 组织证据

- 先按 `PMID` 分组，不按单条记录零散处理。
- 每个 PMID 必须有独立说明文档：`field-curation-workdir/full_tRNAtherapeutics/notes/{PMID}.md`。
- 每篇文档至少记录：题名、DOI、PMCID、数据库行数、来源下载状态、补充文件状态、字段缺失和人工待办。

## 3. 下载顺序

1. PubMed XML：用于 PMID、题名、DOI、PMCID、期刊年份等元数据。
2. PMC HTML/XML：有 PMCID 时优先下载，作为可验证全文证据。
3. PMC OA package：有 OA 包时下载 tar.gz，用于获得真实 PDF、NXML 和 supplementary 文件。
4. DOI landing page：没有 PMCID 或需要补救时下载；不能把 DOI landing page 当作全文 PDF。
5. 手动下载：没有 PMCID、publisher 阻挡、OA 包不可用、补充文件无法自动获取时，写入人工清单。

主要来源说明：

- PMC FTP/OA 文件服务说明：https://pmc.ncbi.nlm.nih.gov/tools/ftp/
- PMC OA Web Service API：https://pmc.ncbi.nlm.nih.gov/tools/oa-service/

## 4. 文件验证

- PDF 必须以 `%PDF` 文件头或 `file` 识别为 PDF。
- XLSX/DOCX/ZIP 应识别为 zip-based Office/ZIP 文件。
- PMC binary 端点返回的 `Preparing to download` / `cloudpmc-viewer-pow` HTML 不是有效附件，必须隔离到 `invalid_downloads_pmc_challenge/`。
- 只有验证通过的文件才能计入 `supplementary_inventory_validated.tsv`。

## 5. 字段补充原则

- 不从摘要或二手网页直接补实验字段。
- `Related_disease`、`PTC_gene`、`PTC(mutation_site)`、`Reading_through_efficiency`、`Reaction_system`、`Safety` 必须能追溯到论文正文、表格、图注或 supplementary。
- `1206-1209` 这类 reporter screen hit 不能写成疾病治疗验证。
- 同一 tRNA 序列可以复用序列驱动的结构模型，但实验结果必须按实验体系分别保留。
- `pdbid` 只有在 CIF 文件已上传并可通过前端 URL 访问后才回填。

## 6. 更新数据库

- 先生成 review TSV 和 SQL 草稿。
- 人工或脚本核对后再执行 SQL。
- 执行后记录：时间、备份路径、SQL 路径、更新行数、验证查询结果。

## 7. 当前全量产物

- 全量验证报告：`field-curation-workdir/full_tRNAtherapeutics/reports/tRNAtherapeutics_full_curation_status_validated.md`
- 人工处理清单：`field-curation-workdir/full_tRNAtherapeutics/reports/manual_action_required_validated.md`
- 验证后 manifest：`field-curation-workdir/full_tRNAtherapeutics/paper_manifest_validated.tsv`
- 验证后 supplementary 清单：`field-curation-workdir/full_tRNAtherapeutics/supplementary_inventory_validated.tsv`
- 字段缺失报告：`field-curation-workdir/full_tRNAtherapeutics/field_gap_report.tsv`
