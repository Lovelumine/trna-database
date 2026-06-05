# AF3 missing pdbid completion

Date: 2026-06-05

Scope: `Engineered_sup_tRNA` rows that had sequence and secondary structure but no `pdbid`.

## Completed jobs

| PMID | ENSURE_ID | pdbid | AF3 job | Interpretation note |
| --- | --- | --- | --- | --- |
| 30778053 | ensure-364 | PRF | PRFFOLD | AF3 model generated; no identical existing model reused |
| 41261131 | 1200 | PRA | PRAFOLD | Reporter screen hit; not disease treatment validation |
| 41261131 | 1204 | PRB | PRBFOLD | Reporter screen hit; not disease treatment validation |
| 41261131 | 1210 | PRC | PRCFOLD | In vivo GFP reporter |
| 41261131 | 1211 | PRD | PRDFOLD | In vivo GFP reporter |
| 41261131 | 1212 | PRE | PREFOLD | Hurler syndrome related validation |

## AF3 run

- Input JSONs: `docs/curation/tRNAtherapeutics/af3_inputs/*.json`
- Server output directory: `/mnt/raid/alphafold3/outputs/ensure-trna-missing-pdbid`
- Docker image used: `alphafold3:latest`
- Output copied locally under ignored working data: `field-curation-workdir/af3_outputs/ensure-trna-missing-pdbid/`

## MinIO upload

Uploaded 5 AF3 sample CIFs for each job, 30 CIF files total, using the frontend path convention:

`ensure-af3/{lowercase_pdbid}fold/seed-1_sample-{0..4}/model.cif`

Object prefixes:

- `ensure-af3/prafold/`
- `ensure-af3/prbfold/`
- `ensure-af3/prcfold/`
- `ensure-af3/prdfold/`
- `ensure-af3/prefold/`
- `ensure-af3/prffold/`

Signed S3 `HEAD` checks passed for the sample-0 object of each prefix. Public HTTPS checks from the local environment returned 403 even for known existing MinIO assets, so upload validation used authenticated S3 metadata checks rather than browser fetches.

## Database update

Before updating, the six affected rows were exported to:

`field-curation-workdir/full_tRNAtherapeutics/backups/Engineered_sup_TRNA_af3_pdbid_before_20260605_154211.tsv`

Executed SQL:

`docs/curation/tRNAtherapeutics/af3_inputs/update_pdbid_after_af3_upload.sql`

Post-update verification:

- `ensure-364` -> `PRF`
- `1200` -> `PRA`
- `1204` -> `PRB`
- `1210` -> `PRC`
- `1211` -> `PRD`
- `1212` -> `PRE`
- Live `Engineered_sup_tRNA` missing `pdbid` count: `0`

## Remaining manual work

This AF3 pass only closes the `pdbid` gap. The remaining high-priority curation gaps are origin tRNA sequence and origin secondary structure gaps documented in:

- `docs/curation/tRNAtherapeutics/reports/manual_action_required_validated.md`
- `docs/curation/tRNAtherapeutics/manifests/field_gap_report.tsv`
