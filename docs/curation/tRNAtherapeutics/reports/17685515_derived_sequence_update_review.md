# PMID 17685515 Derived Sequence Update Review

Database update executed after review.

## Rows

- Rows reviewed: 8
- ENSURE_IDs: ensure-1022, ensure-1023, ensure-1024, ensure-1025, ensure-1028, ensure-1029, ensure-1030, ensure-1031
- Proposed suppressor sequence is identical across these rows because all Kwon 2007 expression strains use `pREP4_ytRNAPhe_UG`.

## Evidence Status

- Furter 1998 full article is available locally and directly lists the yeast amber suppressor tRNA gene sequence with encoded 3' `CCA`.
- Furter 1998 states that G37 was replaced by A37 in the improved suppressor construct.
- Kwon 2006 full article is available locally and gives the `ytRNAPheCUA_UG` construction: `ytRNAPheCUA` was mutated at positions 30 and 40 to make the 30U-40G wobble pair.
- Kwon 2006 states that in vitro transcription produced 76-mer tRNA transcripts.
- Kwon's `UG_f` primer reverse complement exactly matches the proposed suppressor DNA segment.
- This is not identical to GenBank M10263/PDB 1EHZ; do not cite those as same-sequence structures.

## Proposed Files

- TSV: `docs/curation/tRNAtherapeutics/extractions/17685515_derived_sequence_updates.tsv`
- SQL draft: `docs/curation/tRNAtherapeutics/sql/17685515_derived_sequence_updates.sql`

## Execution Record

- Backup: `field-curation-workdir/full_tRNAtherapeutics/backups/Engineered_sup_tRNA_PMID17685515_before_20260605_195750.tsv`
- Updated rows: 8
- Verification query confirmed `Sequence_of_origin_tRNA`, `Sequence_of_sup-tRNA`, `Secondary structure`, and `Secondary structure of sup-trna` are all length 76 for `ensure-1022`, `ensure-1023`, `ensure-1024`, `ensure-1025`, `ensure-1028`, `ensure-1029`, `ensure-1030`, and `ensure-1031`.
- `tRNAscan-SE_ID_of_origin_tRNA` uses short value `Furter1998_Kwon2006` because the database column is `varchar(50)`; detailed evidence is documented in `docs/curation/tRNAtherapeutics/notes/17685515.md`.

## Residual Note

- Kwon 2006 SI was not available in the supplied files. The main article is sufficient for the tRNA sequence/mutation evidence used here.
- Kwon 2006 explicitly describes 76-mer transcripts, so the executed update includes encoded 3' `CCA` and appends unpaired dots to the tRNAscan core structure.
