# PMID 9447966 update review

- Scope: five C. elegans tRNA^Trp amber suppressor rows `ensure-995` through `ensure-999`.
- Main article evidence: PMID 9447966 reports that the assayed `sup-5`, `sup-7`, `sup-24`, `sup-28`, and `sup-29` genes are individual tRNA^Trp family suppressors with identical coding sequences and differential expression.
- Sequence evidence: original molecular characterization PMID 3221861 Fig. 2b gives the mature tRNA^Trp coding sequence; the abstract/figure state all five suppressors carry a single anticodon change from `CCA` to `CTA`.
- Sequence convention: Fig. 2 caption states the 3' `CCA` is not encoded, so the stored origin/suppressor sequences are 73 nt without appended terminal CCA.
- Origin/suppressor relationship: origin RNA is Trp(CCA); suppressor RNA is Trp/Sup(CUA), generated only by the documented anticodon first-base change.
- Secondary structures: computed with local `tRNAscan-SE -E`; origin is classified as Trp/CCA and suppressor as Sup/CTA, both score 63.8.
- Secondary structure: `(((((((..((((.......)))).(((((.......))))).....(((((.......)))))))))).)).`.
- Sprinzl JSON: generated through `https://llm-trna.lumoxuan.cn/api/align/` with `use_llm=false`; origin template `caePb2_chrUn.trna102-TrpCCA`, suppressor template `caePb2_chrUn.trna102-TrpCCA`.
- `tRNAscan-SE_ID_of_origin_tRNA`, `rnacentral_ID_of_origin_tRNA`, and `pdbid` are intentionally not changed. The paper gives locus names and coding sequence but not a database genomic tRNAscan ID.
- TSV: `/home/yingying/Documents/trna-database/docs/curation/tRNAtherapeutics/extractions/9447966_kondo_trp_updates.tsv`.
- SQL: `/home/yingying/Documents/trna-database/docs/curation/tRNAtherapeutics/sql/9447966_kondo_trp_updates.sql`.
- Raw llm-trna responses: `/home/yingying/Documents/trna-database/field-curation-workdir/full_tRNAtherapeutics/extractions/9447966_llm_trna_api`.
- Live DB update executed on 2026-06-08. Verification returned origin/suppressor sequence lengths `73/73`, secondary-structure lengths `73/73`, Sprinzl JSON lengths `100/100`, and unchanged pdbids `ALH`, `ALI`, `ALJ`, `ALK`, `ALL`.
- Pre-update TSV backup: `/home/yingying/Documents/trna-database/field-curation-workdir/full_tRNAtherapeutics/backups/Engineered_sup_tRNA_PMID9447966_before_20260608_085045.tsv`.
