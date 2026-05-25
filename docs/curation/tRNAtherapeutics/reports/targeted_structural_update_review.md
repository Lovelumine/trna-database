# Targeted structural/Sprinzl update review

Accepted rows: 2

Rows updated:

- `ensure-847` / PMID `24386240`: origin set to `His(GUG)`, species corrected to `Escherichia coli`, origin sequence computed by reverting amber `CUA` to `GUG`, secondary structures and Sprinzl JSON generated with llm-trna forced template `eschColi_chr.trna38-HisGTG`; existing tertiary placeholder `pdbid=AFP` retained.
- `ensure-848` / PMID `23379331`: origin set to `Tyr(GUA)`, species normalized to `Methanocaldococcus jannaschii`, origin sequence computed by reverting amber `CUA` to `GUA`, secondary structures and Sprinzl JSON generated with llm-trna forced template `methJann1_chr.trna20-TyrGTA`; existing tertiary placeholder `pdbid=AFQ` retained.

Evidence chain:

1. PMID 24386240 Figure S1 provides the precursor `tRNAHisCUA` sequence and marks the mature tRNA sequence in uppercase. That mature sequence exactly matches the database suppressor sequence for `ensure-847`.
2. PMID 24386240 identifies the suppressor system as the orthogonal Escherichia coli histidyl-tRNA synthetase/tRNAHis pair used in Caulobacter crescentus, so the origin tRNA source is Escherichia coli and the host/reaction system remains Caulobacter/E. coli as already represented elsewhere in the row.
3. PMID 23379331 states that the `proK-tRNA_CUA^MjTyr` cassette was amplified from pEVOL and used in pUltra. The row's existing MjTyr suppressor sequence is retained as the study sequence; only the cognate Tyr anticodon is inferred by single anticodon reversion.
4. The llm-trna API was used only for coordinate alignment and secondary-structure projection. It is not used as the literature source for biological identity.

Skipped rows:

- `ensure-849` / PMID `23379331` was not updated. The article discusses an ochre Mm-tRNA_UUA^Pyl(U25C) / MbPylRS(opt) pair, but the current database row has a source/sequence/anticodon conflict that needs plasmid or supplementary sequence confirmation before updating.

Review TSV: `field-curation-workdir/full_tRNAtherapeutics/extractions/targeted_structural_updates.tsv`
SQL: `field-curation-workdir/full_tRNAtherapeutics/sql/targeted_structural_updates.sql`
Raw API responses: `field-curation-workdir/full_tRNAtherapeutics/extractions/targeted_llm_trna_api`
Backup: `field-curation-workdir/full_tRNAtherapeutics/backups/Engineered_sup_tRNA_targeted_before_20260521_194439.tsv`
