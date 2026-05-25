# PMID 30778053 exact GtRNAdb-backed updates

This review file includes only rows where the missing parent/origin tRNA can be reconstructed without choosing among ambiguous anticodons.

Evidence chain:

1. The article methods state that tRNA gene sequences were obtained from tRNAscan-SE/GtRNAdb and that anticodons were mutated to UAG/UGA/UAA.
2. Supplementary Data 1 (`41467_2019_8329_MOESM5_ESM.xlsx`) provides the ACE-tRNA sequences with the engineered suppressor anticodon highlighted in red/lowercase.
3. For each accepted row, replacing only that suppressor anticodon with one candidate parent anticodon produced exactly one hg19 GtRNAdb confidence/filtered sequence with matching amino acid and anticodon.
4. The origin secondary structure is copied from the matching GtRNAdb `hg19-tRNAs-detailed.ss` entry.
5. `js_origin_tRNA` and `js_sup_tRNA` were generated from existing database Sprinzl templates with the same non-gap sequence length, preferring the same origin amino acid/anticodon. Sequence preservation is deterministic because bases are consumed left-to-right into the template coordinates.

Accepted updates: 9
Accepted updates with Sprinzl/alignment JSON: 9
Unresolved/ambiguous rows left untouched: 85
Max `js_origin_tRNA` length: 2154
Max `js_sup_tRNA` length: 4871

Review TSV: `field-curation-workdir/full_tRNAtherapeutics/extractions/30778053_gtrnadb_exact_updates.tsv`
Unresolved TSV: `field-curation-workdir/full_tRNAtherapeutics/extractions/30778053_unresolved_origin_anticodon.tsv`
SQL: `field-curation-workdir/full_tRNAtherapeutics/sql/30778053_gtrnadb_exact_updates.sql`

## Upload log

- Executed SQL on online MySQL: 2026-05-21 19:13:45 CST.
- PMID 30778053 missing origin sequence/secondary structure/aa fields changed from 94 to 85.
- Missing `js_origin_tRNA`/`js_sup_tRNA` changed from 110 to 101.
- Verified updated rows: `ensure-105`, `ensure-119`, `ensure-120`, `ensure-136`, `ensure-150`, `ensure-151`, `ensure-372`, `ensure-395`, `ensure-418`.
- Online `/search_table` verification returned 518 PMID rows; updated rows are present in snapshot `field-curation-workdir/full_tRNAtherapeutics/backups/api_30778053_after_gtrnadb_exact.json`.
