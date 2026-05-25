# PMID 30778053 Supplementary Data 1 direct corrections

Scope: fill only `tRNAscan-SE_ID_of_origin_tRNA` values explicitly recoverable from Supplementary Data 1.

Accepted updates: 81
Skipped rows: 5

Evidence chain:

1. Supplementary Data 1 (`41467_2019_8329_MOESM5_ESM.xlsx`) contains the `ACE-tRNA sequences` sheet with columns `tRNAscan-SE ID` and `ACE-tRNA sequence 5' -> 3'`.
2. Each accepted database row was matched by exact suppressor sequence to exactly one Supplementary Data 1 row.
3. The new value is the single `chr*.trna*` identifier present in that Supplementary Data 1 ID. A minor OCR/spacing artifact `c hr7.trna32` was normalized to `chr7.trna32` only after exact sequence matching.
4. Origin sequence, origin secondary structure, and Sprinzl JSON are intentionally not inferred in this correction batch.

Skipped rows mostly have either an ambiguous ACE sequence mapping to two IDs, or are outside Supplementary Data 1 species/suppressor rows.

## Upload log

- Executed SQL on online MySQL: 2026-05-21 22:21:29 CST.
- PMID 30778053 missing `tRNAscan-SE_ID_of_origin_tRNA` changed from 86 to 5.
- Remaining missing IDs: `ensure-187`, `ensure-224`, `ensure-232`, `ensure-269`, `ensure-542`.
- Origin sequence/secondary-structure/Sprinzl gaps were not changed by this batch.

Review TSV: `field-curation-workdir/full_tRNAtherapeutics/extractions/30778053_suppdata_direct_corrections.tsv`
Skipped TSV: `field-curation-workdir/full_tRNAtherapeutics/extractions/30778053_suppdata_direct_corrections_skipped.tsv`
SQL: `field-curation-workdir/full_tRNAtherapeutics/sql/30778053_suppdata_direct_corrections.sql`
Backup: `field-curation-workdir/full_tRNAtherapeutics/backups/Engineered_sup_tRNA_PMID30778053_before_suppdata_direct_20260521_221936.tsv`
