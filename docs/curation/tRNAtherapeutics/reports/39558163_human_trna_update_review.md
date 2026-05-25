# PMID 39558163 human tRNA update review

Accepted rows: 3

Rows updated:

- `ensure-1034`, `ensure-1050`: Human sup-tRNAAla; origin set to `Ala(AGC)`, RNAcentral `URS000063E4FD_9606`, tRNAscan-SE `chr6.trna112`.
- `ensure-1052`: Human sup-tRNATyr; origin set to `Tyr(GUA)`, RNAcentral `URS0000636E2A_9606`, GtRNAdb/RNAcentral gene symbol `tRNA-Tyr-GTA-2-1`.

Evidence chain:

1. PMID 39558163 / PMCID PMC11662663 methods state that nucleic acid sequences of tRNAs and reporters are listed in Supplementary Tables S1 and S2.
2. Supplementary Table S1 lists the exact `Human sup-tRNAAla` and `Human sup-tRNATyr` nucleotide sequences used in the study.
3. The origin tRNA sequence is obtained by reverting the unique amber suppressor anticodon `CTA`/`CUA` to the cognate anticodon: `AGC` for Ala and `GTA`/`GUA` for Tyr. The terminal CCA present in the study sequence is retained so origin and suppressor sequences have the same mature-tRNA length used by the database row.
4. Ala core sequence without terminal CCA matches GtRNAdb hg19 `tRNA-Ala-AGC-1-1` / `chr6.trna112`, RNAcentral `URS000063E4FD_9606`.
5. Tyr core sequence without terminal CCA matches RNAcentral `URS0000636E2A_9606`, described as Homo sapiens tRNA-Tyr(GTA) 2-1 and annotated by GtRNAdb among other expert databases.
6. `Secondary structure`, `Secondary structure of sup-trna`, `js_origin_tRNA`, and `js_sup_tRNA` were generated through `https://llm-trna.lumoxuan.cn/api/align/` with `use_llm=false` and forced human templates. The added terminal CCA is represented as unpaired dots in the secondary structure.

Review TSV: `field-curation-workdir/full_tRNAtherapeutics/extractions/39558163_human_trna_updates.tsv`
SQL: `field-curation-workdir/full_tRNAtherapeutics/sql/39558163_human_trna_updates.sql`
Raw API responses: `field-curation-workdir/full_tRNAtherapeutics/extractions/39558163_llm_trna_api`
Backup: `field-curation-workdir/full_tRNAtherapeutics/backups/Engineered_sup_tRNA_PMID39558163_before_20260521_192526.tsv`
