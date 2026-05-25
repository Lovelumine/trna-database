# tRNAtherapeutics Curation Package

This directory is the GitHub-safe export of the local `field-curation-workdir`.

It includes curation protocols, validated reports, per-PMID notes, manifests, SQL drafts, extraction tables, and AF3 input plans for the `Engineered_sup_tRNA` table. Raw downloaded literature files are intentionally excluded from GitHub.

## Start Here

- [Curation protocol](CURATION_PROTOCOL.md)
- [Validated full curation status](reports/tRNAtherapeutics_full_curation_status_validated.md)
- [Manual action required](reports/manual_action_required_validated.md)
- [Database supplement plan](reports/database_supplement_plan.md)
- [Per-PMID notes](notes/)
- [Validated paper manifest](manifests/paper_manifest_validated.tsv)
- [Validated supplementary inventory](manifests/supplementary_inventory_validated.tsv)
- [Row-level gap report](manifests/row_gap_report.tsv)
- [AF3 input plan](af3_inputs/pdbid_plan.tsv)

## Omitted From GitHub

The local workspace contains files that should not be committed directly:

- Downloaded PDFs, HTML full texts, Excel/Word supplementary files, and PMC OA tarballs.
- MySQL dumps, API snapshots, and local database backups.
- Large extracted archives and intermediate scratch files.

Those files remain under the ignored local directory:

`field-curation-workdir/`

Some report links point to local `papers/` or `supplementary/` folders. Those links are useful inside the local workspace but are intentionally not mirrored here.

## Regeneration Scripts

The scripts used to create these reports are tracked under:

[tools/curation/tRNAtherapeutics/scripts](../../../tools/curation/tRNAtherapeutics/scripts)
