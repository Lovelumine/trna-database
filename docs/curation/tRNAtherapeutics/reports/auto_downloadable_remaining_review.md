# Auto-Downloadable Remaining Gap Review

Review date: 2026-06-08

Scope: live `Engineered_sup_tRNA` rows still missing origin/suppressor sequence or secondary structure after the PMID 9447966 update. This pass only accepts evidence from automatically accessible PubMed/PMC/OA package files, publisher-public attachments, or linked open repository files. No database rows were updated in this pass because no new remaining row had a complete, unambiguous sequence evidence chain.

## Current Live Gaps

Source: `docs/curation/tRNAtherapeutics/manifests/field_gap_report.tsv`.

| PMID | Rows | Missing fields | Decision |
|---|---:|---|---|
| 2602139 | 3 | origin/sup sequence and secondary structure | No DB change; PMC HTML is accessible but article body is scanned/abstract-level for sequence purposes, and direct PDF download returns challenge HTML. Complete suppressor tRNA sequence not found. |
| 6363071 | 1 | origin/sup sequence and secondary structure | No DB change; Wiley/Mendeley full text blocked. Abstract only supports anticodon replacement, not complete sequence. |
| 11866580 | 1 | origin/sup sequence and secondary structure | No DB change; ACS DOI returns Cloudflare 403, no PMCID. |
| 15222758 | 1 | origin sequence and secondary structure | No DB change; ACS DOI returns Cloudflare 403. Existing suppressor sequence is retained, but origin cannot be derived without paper/source confirmation. |
| 17698637 | 2 | origin/sup sequence and secondary structure | No DB change; article and official RNA Journal PDF are accessible, and linked Saks 1996 THG73 source was downloaded, but ENAS source remains blocked and THG73 terminal-length convention needs manual sequence review before upload. |
| 19378306 | 2 | origin/sup sequence and secondary structure | No DB change; PMC HTML is accessible, but NIHMS/Angew supplementary downloads are challenge HTML, not PDFs. |
| 19749377 | 2 | origin/sup sequence and secondary structure | No DB change; OUP DOI returns Cloudflare 403, no local full text. |
| 23274575 | 4 | origin sequence and secondary structure for `ensure-836` | No DB change; Elsevier DOI only returns landing/redirect HTML. Existing suppressor sequence is retained, but origin cannot be safely reverted without paper/source confirmation. |
| 23379331 | 2 | origin sequence and secondary structure for `ensure-849` | No DB change; PMC HTML is accessible, but NIHMS/ACS supplementary downloads are challenge HTML. Existing Pyl(UUA) suppressor sequence is retained. |
| 30778053 | 518 | 85 origin sequences and secondary structures | No DB change; OA package and Supplementary Data were already exhausted by two conservative passes. Remaining rows lack a unique exact parent/origin reconstruction under the current evidence rules. |
| 33069552 | 2 | origin/sup sequence and secondary structure | No DB change; PMC HTML is accessible, but NIHMS supplement is challenge HTML. Article describes PylT copy/source choices but does not uniquely map the two DB rows to exact tRNA sequences. |

## New Files Checked

- [Saks 1996 Caltech record HTML](../../../../field-curation-workdir/full_tRNAtherapeutics/linked_sources/17698637/saks1996_caltech.html): open repository landing page for the linked THG73 source.
- [Saks 1996 PDF](../../../../field-curation-workdir/full_tRNAtherapeutics/linked_sources/17698637/saks1996_SAKjbc96.pdf): valid 6-page PDF, 268 KB.

Important finding: Saks 1996 Figure 2 supports that THG73 is derived from *Tetrahymena thermophila* tRNA Gln(CUA), with U73 changed to G73, and gives the construct/RNA sequence diagram. It also states the experimental FokI transcript lacks the 3' terminal CA and is chemically ligated to dCA-amino acid. Because the database must consistently choose either the 74-mer transcript or full 76-mer mature/ligated molecule, this was not uploaded without manual review.

## Invalid Downloads

These local files have `.pdf` names but `file` identifies them as HTML/challenge documents, so they were not used as evidence:

- `field-curation-workdir/full_tRNAtherapeutics/invalid_downloads_pmc_challenge/papers/2602139/2602139_PMC335204.pdf`
- `field-curation-workdir/full_tRNAtherapeutics/invalid_downloads_pmc_challenge/papers/17698637/17698637_PMC1986817.pdf`
- `field-curation-workdir/full_tRNAtherapeutics/supplementary/19378306/anie200900683-sup-0001-misc_information.pdf`
- `field-curation-workdir/full_tRNAtherapeutics/supplementary/19378306/NIHMS146422-supplement-Supplemental_Information.pdf`
- `field-curation-workdir/full_tRNAtherapeutics/supplementary/23379331/bi4000244_si_001.pdf`
- `field-curation-workdir/full_tRNAtherapeutics/supplementary/23379331/NIHMS507917-supplement-SI.pdf`
- `field-curation-workdir/full_tRNAtherapeutics/supplementary/33069552/NIHMS1639676-supplement-1.pdf`

## Manual Inputs Needed

- PMID 17698637: confirm THG73 sequence storage convention from Saks 1996 Figure 2: 74-mer FokI transcript versus full 76-mer after terminal CA/dCA addition. Also provide or locate Cload 1996 / Kleina 1990 full text for ENAS.
- PMID 19378306: real supplementary PDF for `NIHMS146422-supplement-Supplemental_Information.pdf` or Angew SI.
- PMID 23379331: real `NIHMS507917-supplement-SI.pdf` / ACS SI.
- PMID 33069552: real `NIHMS1639676-supplement-1.pdf`, especially Tables S1/S2 with gBlock/primer/plasmid sequence details.
- PMIDs 11866580, 15222758, 19749377, 23274575: publisher full text and any supplementary data.

## 30778053 Status

PMID 30778053 is considered exhausted under the current conservative rule:

- Supplementary Data 1 exact tRNAscan-SE ID correction already applied: 81 accepted rows.
- GtRNAdb exact origin sequence/secondary-structure update already applied: 9 accepted rows.
- Remaining 85 origin gaps are not automatically filled because replacing the suppressor anticodon does not produce a unique exact GtRNAdb origin candidate, or the ACE sequence is ambiguous.
