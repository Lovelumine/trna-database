# Host RNA toolchain pin

The app host (`223.82.75.76`) carries one copy of each external RNA tool, at the
newest published build. Everything in this repository resolves them by name from
`/usr/local/bin`, which holds symlinks into conda prefixes under
`/home/yingying/tools`.

| Tool | Version on 2026-11-05 | Resolves to | Used by |
| --- | --- | --- | --- |
| `tRNAscan-SE` | 2.0.13 (Jul 2026) | `~/tools/trnascan-se-2.0.13/bin` | `tools/data-prep/oop.py` (`-E -f`), curation helpers |
| Infernal `cm*` | 1.1.5 (Sep 2023) | `~/tools/infernal-1.1.5/bin` | alignment helpers in `tools/`, `scripts/` |
| ViennaRNA `RNA*` | 2.7.2 | `~/tools/viennarna-2.7.2/bin` | structure helpers |
| `pdftotext` (poppler) | 22.02.0-2ubuntu0.15 | apt | the Flask backend's document reader (its only subprocess call) |

Removed on 2026-11-05: apt `trnascan-se 2.0.9`, `trnascan-se-common`, `infernal
1.1.4`, and the September 2024 source builds of Infernal 1.1.4 and ViennaRNA 2.6.4
that had been installed straight into `/usr/local/bin`. The superseded binaries are
preserved in `/root/toolchain-backup-20261105/usr-local-bin/`; restoring them plus
`apt-get install trnascan-se infernal` undoes the switch.

## What this backend does and does not depend on

`ensure-backend.service` serves the ENSURE site on port 8010. The request path
never calls an RNA tool: the only subprocess in `Flask/app/routes.py` is
`pdftotext -layout` for reading document PDFs. The alignment tables the assistant
queries are precomputed, so a toolchain change cannot alter what the site answers
until a data-preparation script is re-run.

The scripts that do call the tools are offline:

- `tools/data-prep/oop.py` — `tRNAscan-SE -E -f` for secondary structures and
  `blastn` for pairwise display. It now prints the tRNAscan-SE build it used and
  honours `TRNASCAN_SE_BIN` to point at another build for a reproduction run.
- `tools/curation/**`, `field-curation-workdir/**` — mention tRNAscan-SE scores as
  recorded fields; they do not invoke the binary.

## Version boundaries in stored data

Rows produced before 2026-11-05 were computed with tRNAscan-SE 2.0.9 and Infernal
1.1.4. Measured equivalence on 200 records sampled from the SprinzlMap cohort,
with the option sets these scripts actually pass:

- `tRNAscan-SE -E -f` payload: 0 differences between 2.0.9 and 2.0.13;
- `tRNAscan-SE -z 100 -X 0 -G -Q -o -f` hit columns: 0 differences between 2.0.9,
  2.0.12 and 2.0.13, with identical model asset trees (99/99 files by md5);
- `RNAfold --noPS`: all 200 structures and MFE energies identical between 2.6.4
  and 2.7.2.

So no stored row needs recomputation to stay consistent, and no back-fill marker is
required. The full measurement record lives in the SprinzlMap repository at
`docs/operations/documentation/production-toolchain-2026-11-05.md`, with
intermediates in `~/build/tools/upgrade-20261105/`.
