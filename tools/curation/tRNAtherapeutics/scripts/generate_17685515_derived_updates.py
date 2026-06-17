#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
FULL = ROOT / "field-curation-workdir" / "full_tRNAtherapeutics"
DOCS = ROOT / "docs" / "curation" / "tRNAtherapeutics"
SNAPSHOT = sorted((FULL / "snapshots").glob("Engineered_sup_tRNA_*.tsv"))[-1]
OUT_TSV = DOCS / "extractions" / "17685515_derived_sequence_updates.tsv"
OUT_SQL = DOCS / "sql" / "17685515_derived_sequence_updates.sql"
OUT_REPORT = DOCS / "reports" / "17685515_derived_sequence_update_review.md"

ORIGIN_RNA = "GCGGACUUAGCUCAGUUGGGAGAGCGCCAGACUGAAGAUCUGGAGGUCCUGUGUUCGAUCCACAGAGUUCGCACCA"
SUP_RNA = "GCGGACUUAGCUCAGUUGGGAGAGCGCCAUACUCUAAAUGUGGAGGUCCUGUGUUCGAUCCACAGAGUUCGCACCA"
STRUCTURE = "(((((((..((((........)))).(((((.......))))).....(((((.......))))))))))))...."


def qident(value: str) -> str:
    return "`" + value.replace("`", "``") + "`"


def qval(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "''") + "'"


def main() -> None:
    rows = []
    with SNAPSHOT.open(newline="") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            if row.get("PMID") == "17685515":
                rows.append(row)

    rows.sort(key=lambda r: int(r["Index"]))
    OUT_TSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_SQL.parent.mkdir(parents=True, exist_ok=True)
    OUT_REPORT.parent.mkdir(parents=True, exist_ok=True)

    fields = [
        "ENSURE_ID",
        "Index",
        "aa_and_anticodon_of_sup-tRNA",
        "pdbid",
        "new_Origin_species",
        "new_Origin_tRNA",
        "new_tRNAscan-SE_ID_of_origin_tRNA",
        "new_Sequence_of_origin_tRNA",
        "new_Sequence_of_sup-tRNA",
        "new_sup-tRNA_gene",
        "new_Mutation_description",
        "new_Secondary structure",
        "new_Secondary structure of sup-trna",
        "evidence_level",
        "evidence_note",
    ]

    with OUT_TSV.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "ENSURE_ID": row["ENSURE_ID"],
                    "Index": row["Index"],
                    "aa_and_anticodon_of_sup-tRNA": row["aa_and_anticodon_of_sup-tRNA"],
                    "pdbid": row["pdbid"],
                    "new_Origin_species": "Saccharomyces cerevisiae",
                    "new_Origin_tRNA": "tRNA-Phe-GAA-1-1/1-2",
                    "new_tRNAscan-SE_ID_of_origin_tRNA": "Furter1998_Kwon2006",
                    "new_Sequence_of_origin_tRNA": ORIGIN_RNA,
                    "new_Sequence_of_sup-tRNA": SUP_RNA,
                    "new_sup-tRNA_gene": "ytRNAPheCUA_UG",
                    "new_Mutation_description": "GAA->CUA anticodon edit; G37A; G30U/C40G (30U-40G wobble pair)",
                    "new_Secondary structure": STRUCTURE,
                    "new_Secondary structure of sup-trna": STRUCTURE,
                    "evidence_level": "direct_furter_sequence_plus_kwon_mutagenesis",
                    "evidence_note": "Furter 1998 gives the yeast amber suppressor tRNA gene sequence and G37A note; Kwon 2006 gives ytRNAPheCUA_UG 30U/40G construction, 76-mer transcript, and primer exact-match.",
                }
            )

    lines = [
        "-- PMID 17685515 sequence update draft.",
        "-- Do not execute before manual review of derived-sequence evidence.",
        "-- Source review: docs/curation/tRNAtherapeutics/notes/17685515.md",
        "START TRANSACTION;",
    ]
    for row in rows:
        assignments = {
            "Species_source_of_origin_tRNA": "Saccharomyces cerevisiae",
            "tRNAscan-SE_ID_of_origin_tRNA": "Furter1998_Kwon2006",
            "Sequence_of_origin_tRNA": ORIGIN_RNA,
            "Sequence_of_sup-tRNA": SUP_RNA,
            "sup-tRNA_gene": "ytRNAPheCUA_UG",
            "Secondary structure": STRUCTURE,
            "Secondary structure of sup-trna": STRUCTURE,
        }
        set_clause = ",\n  ".join(f"{qident(k)} = {qval(v)}" for k, v in assignments.items())
        lines.append(
            f"\nUPDATE `Engineered_sup_tRNA`\nSET {set_clause}\nWHERE `ENSURE_ID` = {qval(row['ENSURE_ID'])} AND `PMID` = '17685515';"
        )
    lines.append("\n-- COMMIT;")
    OUT_SQL.write_text("\n".join(lines) + "\n")

    report = f"""# PMID 17685515 Derived Sequence Update Review

This is a draft only; no database update has been executed.

## Rows

- Rows reviewed: {len(rows)}
- ENSURE_IDs: {", ".join(row["ENSURE_ID"] for row in rows)}
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

## Manual Review Needed

- Kwon 2006 SI was not available in the supplied files. The main article is sufficient for the tRNA sequence/mutation evidence used here.
- Before execution, review whether the database convention for this table should store encoded 3' `CCA`; Kwon 2006 explicitly describes 76-mer transcripts, so this draft includes CCA and appends `...` to the tRNAscan core structure.
"""
    OUT_REPORT.write_text(report)


if __name__ == "__main__":
    main()
