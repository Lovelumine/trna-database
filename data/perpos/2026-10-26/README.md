# Per-Position Alignment Variation — 数据表来源

这张图读的是 MySQL 表 `engineered_sup_trna_perpos_counts`。2026-10-26 起，表里的
数字由 LLM-tRNAAlign 的 SprinzlMap 重算得到，不再由每条记录自带的对齐字符串按列
直接比较。

- `perpos_sprinzlmap_20261026.tsv`：当前线上表的 207 行（76 个规范 Sprinzl 列 +
  131 个插入/V 列），合计 match 73 757 / mismatch 4 597 / insertion 1 180 /
  deletion 238。
- `perpos_ensure_published_before_20261026.tsv`：替换前的 312 行快照。线上旧表已经
  删除，这份文件是唯一副本。

## 口径差别

两套编号在 1–76 规范列上完全一致，差别在环区多出来残基的命名：旧表给每个额外残基
起一个插入列名（`31i1…31i7`、`32i1…32i16`），规范槽位留空；SprinzlMap 让这些残基
直接占掉本来空着的规范位（`24`、`25`、`26`、`44`），长可变臂用 `V11…V17 → V1…V5 →
V27…V21` 插在 45 与 46 之间。逐格核对（同一序列，两套坐标，162 304 个规范格）：
74.9 % 完全一致，11.5 % 同一列放不同残基，7.0 % 旧表填了我们空，6.6 % 我们填了旧表空。

事件总量没有丢：mismatch 4 372 → 4 597，insertion 1 136 → 1 180，deletion 260 → 238。

## 复现

```
python3 benchmark/scripts/ensure_cohort_inputs.py --out-dir <cohort>
python3 benchmark/scripts/run_numbering_benchmark.py --run-id 20261026-2147-ensure-suptna-v2 ...
python3 benchmark/scripts/ensure_perpos_sprinzlmap.py --run-id 20261026-2147-ensure-suptna-v2 ...
python3 benchmark/scripts/push_perpos_to_ensure.py --tsv ... --run-id 20261026-2147-ensure-suptna-v2
```

脚本都在 LLM-tRNAAlign 仓库的 `benchmark/scripts/`。运行记录存在该项目自己的 MySQL
(`benchmark_executions`) 与 MinIO (`llm-trnaalign-artifacts`)，本次 run id 为
`20261026-2147-ensure-suptna-v2`（1 034 条，全部成功，序列还原 100 %）。
替换动作记在 `engineered_sup_trna_perpos_provenance`。
