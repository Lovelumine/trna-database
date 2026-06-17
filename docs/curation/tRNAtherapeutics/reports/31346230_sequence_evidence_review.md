# PMID 31346230 Sequence Evidence Review

## Database row

- `ENSURE_ID`: `ensure-852`
- Current tRNA annotation: `AzF(CUA)`, species source `Escherichia coli`
- Experimental system: `Trypanosoma brucei`
- Reporter: GFP `Tyr39TAG/UAG`
- Current gaps: origin/suppressor sequence and secondary structure are blank.

## Sources checked

- Main paper: Huot et al. 2019, PMID 31346230, DOI 10.1038/s41598-019-47268-4, PMCID PMC6658472.
- Supplement: `41598_2019_47268_MOESM1_ESM.docx`.
- Cited construct paper: Chatterjee et al. 2013, PMID 23818609, DOI 10.1073/pnas.1309584110, PMCID PMC3718144.
- Cited construct supplement: `1309584110_pnas.201309584SI.pdf`.

## Findings

- PMID 31346230 does not provide a nucleotide sequence for the expressed suppressor tRNA.
- PMID 31346230 says the system used a previously described evolved bacterial YRS/suppressor tRNA^Tyr_CUA pair from `E. coli`, citing PMID 23818609.
- PMID 31346230 Materials and Methods clarifies the construct sources: Addgene plasmid `pAcBac2.tR4-OMeYRS/GFP*` supplied oMeYRS and nsGFP; the tRNA construct was separately synthesized by Genescript.
- The synthesized tRNA construct contained the `E. coli` tRNA^Tyr_CUA gene plus 50 nt upstream and 30 nt downstream flanking sequence from a `T. brucei` tRNA^Leu gene.
- PMID 31346230 explicitly states that the genetically encoded 3' acceptor `CCA` present in the `E. coli` tRNA^Tyr_CUA gene was omitted.
- PMID 23818609 Fig. 2A directly prints primary sequences for Tyr tRNA_CUA candidates from `E. coli` and `Bacillus stearothermophilus`, and its pAcBac1.tR4 design uses two bacterial Tyr suppressor tRNAs in a two-copy cassette.
- PMID 31346230 should not be expanded to the Bacillus tRNA from PMID 23818609. The 2019 paper describes a separately synthesized `E. coli` tRNA^Tyr_CUA construct.
- Addgene #50831 sequence page exposes full-sequence visualization data for sequence ID `193569`. The anonymous GenBank file endpoint was not downloadable, but `sequence-lines.json` and `features.json` were accessible and saved locally.
- Reconstructing the top strand from `sequence-lines.json` yields a 11408 bp plasmid sequence. In this Addgene full sequence, the `E. coli` Tyr(CUA) tRNA starts at 1-based position 7491 and contains `...GACTCTAAATC...`; `...GACTGTAAATC...` is absent.
- 2026-06-07 check: the publisher PDF URL `https://www.nature.com/articles/s41598-019-47268-4.pdf` was downloadable and saved as `field-curation-workdir/full_tRNAtherapeutics/papers/31346230/31346230_s41598-019-47268-4_nature.pdf`. Its SHA-256 hash matches the PMC OA package PDF exactly, so it adds no new sequence evidence beyond the already downloaded article PDF.
- 2026-06-07 check: the Springer supplementary DOCX direct URL was also downloadable and matched the existing local supplement. Text inspection found `tRNA`/`Tyr`/`CUA` mentions but no `GeneScript`, `Addgene`, `plasmid`, `50831`, or nucleotide sequence evidence for the synthesized construct.

## Sequence issue

PMID 23818609 Fig. 2A labels the Ec sequence as Tyr tRNA_CUA, but the printed sequence appears to contain a `GTA` DNA anticodon segment:

```text
GGTGGGGTTCCCGAGCGGCCAAAGGGAGCAGACTGTAAATCTGCCGTCACAGACTTCGAAGGTTCGAATCCTTCCCCCACCACCA
```

The Addgene #50831 full-sequence visualization resolves this ambiguity. The actual Addgene full sequence contains the CUA-form Ec tRNA:

```text
GGTGGGGTTCCCGAGCGGCCAAAGGGAGCAGACTCTAAATCTGCCGTCACAGACTTCGAAGGTTCGAATCCTTCCCCCACCACCA
```

Length: 85 nt including encoded terminal `CCA`. RNA transcription:

```text
GGUGGGGUUCCCGAGCGGCCAAAGGGAGCAGACUCUAAAUCUGCCGUCACAGACUUCGAAGGUUCGAAUCCUUCCCCCACCACCA
```

PMID 31346230 says the encoded 3' acceptor `CCA` was omitted. Therefore the sequence matching the synthesized tRNA body would be:

```text
GGUGGGGUUCCCGAGCGGCCAAAGGGAGCAGACUCUAAAUCUGCCGUCACAGACUUCGAAGGUUCGAAUCCUUCCCCCACCA
```

Length: 82 nt.

## Recommendation

Sequence update for `ensure-852` can now be drafted from two linked pieces of evidence:

- Addgene #50831 full-sequence visualization data support the Ec Tyr(CUA) tRNA sequence with `GACTCTAAATC`.
- PMID 31346230 states that the encoded terminal `CCA` was omitted from the Genescript tRNA construct.

The final supported RNA sequence for the tRNA body is:

```text
GGUGGGGUUCCCGAGCGGCCAAAGGGAGCAGACUCUAAAUCUGCCGUCACAGACUUCGAAGGUUCGAAUCCUUCCCCCACCA
```

2026-06-06: the sequence decision was applied to the live `Engineered_sup_tRNA` row for `ensure-852`, together with `tRNAscan-SE -B` secondary structures and Sprinzl JSON. The pre-existing `pdbid=AFU` was not changed; the corresponding CIF/model should be separately checked for existence and sequence consistency.
