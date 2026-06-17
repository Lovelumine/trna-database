#!/usr/bin/env python3
"""Generate PMID 31346230 update artifacts for ensure-852."""

from __future__ import annotations

import csv
import io
import json
import sys
import urllib.request
from pathlib import Path


csv.field_size_limit(sys.maxsize)

ROOT = Path(__file__).resolve().parents[4]
FULL = ROOT / "field-curation-workdir" / "full_tRNAtherapeutics"
DOCS = ROOT / "docs" / "curation" / "tRNAtherapeutics"
OUT_API = FULL / "extractions" / "31346230_llm_trna_api"
OUT_TSV = DOCS / "extractions" / "31346230_update.tsv"
OUT_SQL = DOCS / "sql" / "31346230_update.sql"
OUT_REPORT = DOCS / "reports" / "31346230_update_review.md"

ALIGN_API = "https://llm-trna.lumoxuan.cn/api/align/"
TEMPLATE = "eschColi_chr.trna45-TyrGTA"
PMID = "31346230"
ENSURE_ID = "ensure-852"
STRUCTURE = "(((((((..(((...........))).(((((.......))))).(((...)))...(((((.......))))))))))))."
ORIGIN_SEQ = "GGUGGGGUUCCCGAGCGGCCAAAGGGAGCAGACUGUAAAUCUGCCGUCACAGACUUCGAAGGUUCGAAUCCUUCCCCCACCA"
SUP_SEQ = "GGUGGGGUUCCCGAGCGGCCAAAGGGAGCAGACUCUAAAUCUGCCGUCACAGACUUCGAAGGUUCGAAUCCUUCCCCCACCA"


def norm_rna(seq: str) -> str:
    return (seq or "").strip().upper().replace("T", "U").replace(" ", "").replace("\n", "")


def qident(name: str) -> str:
    return "`" + name.replace("`", "``") + "`"


def qval(value: object) -> str:
    if value is None:
        return "NULL"
    return "'" + str(value).replace("\\", "\\\\").replace("'", "''") + "'"


def dotbracket_to_parentheses(structure: str) -> str:
    return structure.replace(">", "(").replace("<", ")")


def call_align(seq: str, anticodon: str, label: str) -> dict[str, object]:
    payload = json.dumps(
        {
            "target_seq": norm_rna(seq),
            "anticodon": anticodon,
            "use_llm": False,
            "template_name": TEMPLATE,
        }
    ).encode()
    request = urllib.request.Request(
        ALIGN_API,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        data = json.loads(response.read().decode())
    OUT_API.mkdir(parents=True, exist_ok=True)
    (OUT_API / f"{label}.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    rows = list(csv.reader(io.StringIO(data["csv_content"])))
    ids = rows[0]
    aligned = rows[-1]
    consumed = "".join(base for base in aligned if base != "-")
    if consumed != norm_rna(seq):
        raise RuntimeError(f"{label}: aligned sequence does not preserve input")
    structure = dotbracket_to_parentheses(data["structure"]["secondary_structure"])
    if structure != STRUCTURE:
        raise RuntimeError(f"{label}: unexpected secondary structure")
    if data.get("warnings"):
        raise RuntimeError(f"{label}: unexpected warnings: {data['warnings']}")
    return {"ids": ids, "aligned": aligned, "template": data["template_name"], "structure": structure}


def classify(origin_base: str, sup_base: str) -> str:
    if origin_base == "-" and sup_base == "-":
        return "gap"
    if origin_base == "-":
        return "insertion"
    if sup_base == "-":
        return "deletion"
    if origin_base == sup_base:
        return "match"
    return "mismatch"


def build_json(origin: dict[str, object], sup: dict[str, object]) -> tuple[str, str]:
    ids = origin["ids"]
    if ids != sup["ids"]:
        raise RuntimeError("origin/sup coordinate IDs differ")
    origin_aligned = origin["aligned"]
    sup_aligned = sup["aligned"]
    js_origin = [{"id": coord, "base": base} for coord, base in zip(ids, origin_aligned)]
    js_sup = [
        {
            "id": coord,
            "base": base,
            "sup_base": sup_base,
            "type": classify(base, sup_base),
        }
        for coord, base, sup_base in zip(ids, origin_aligned, sup_aligned)
    ]
    return json.dumps(js_origin, ensure_ascii=False), json.dumps(js_sup, ensure_ascii=False)


def main() -> None:
    origin_align = call_align(ORIGIN_SEQ, "GUA", "origin")
    sup_align = call_align(SUP_SEQ, "CUA", "sup")
    js_origin, js_sup = build_json(origin_align, sup_align)
    update = {
        "ENSURE_ID": ENSURE_ID,
        "PMID": PMID,
        "aa_and_anticodon_of_origin_tRNA": "Tyr(GUA)",
        "Sequence_of_origin_tRNA": ORIGIN_SEQ,
        "Sequence_of_sup-tRNA": SUP_SEQ,
        "Secondary structure": STRUCTURE,
        "Secondary structure of sup-trna": STRUCTURE,
        "js_origin_tRNA": js_origin,
        "js_sup_tRNA": js_sup,
        "sprinzl_template": TEMPLATE,
        "evidence_summary": (
            "PMID 31346230 states the E. coli Tyr_CUA construct omitted encoded 3' CCA; "
            "Addgene #50831 sequence visualization supports the CUA body sequence; "
            "origin sequence is derived by reverting CUA to GUA."
        ),
    }
    if len(ORIGIN_SEQ) != 82 or len(SUP_SEQ) != 82 or len(STRUCTURE) != 82:
        raise RuntimeError("sequence/structure length mismatch")
    if sum(1 for item in json.loads(js_origin) if item["base"] != "-") != len(ORIGIN_SEQ):
        raise RuntimeError("js_origin non-gap count mismatch")
    if sum(1 for item in json.loads(js_sup) if item["sup_base"] != "-") != len(SUP_SEQ):
        raise RuntimeError("js_sup non-gap count mismatch")

    OUT_TSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_SQL.parent.mkdir(parents=True, exist_ok=True)
    OUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    with OUT_TSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(update), delimiter="\t")
        writer.writeheader()
        writer.writerow(update)

    db_cols = [
        "aa_and_anticodon_of_origin_tRNA",
        "Sequence_of_origin_tRNA",
        "Sequence_of_sup-tRNA",
        "Secondary structure",
        "Secondary structure of sup-trna",
        "js_origin_tRNA",
        "js_sup_tRNA",
    ]
    assignments = ",\n  ".join(f"{qident(col)} = {qval(update[col])}" for col in db_cols)
    OUT_SQL.write_text(
        "\n".join(
            [
                "-- PMID 31346230 update for ensure-852.",
                "-- Backup must be created from live DB before execution.",
                f"-- Review TSV: {OUT_TSV}",
                f"UPDATE {qident('Engineered_sup_tRNA')}",
                "SET",
                f"  {assignments}",
                f"WHERE {qident('ENSURE_ID')} = {qval(ENSURE_ID)} AND {qident('PMID')} = {PMID};",
                "",
            ]
        ),
        encoding="utf-8",
    )
    OUT_REPORT.write_text(
        "\n".join(
            [
                "# PMID 31346230 update review",
                "",
                f"- Row: `{ENSURE_ID}` / PMID `{PMID}`.",
                f"- `Sequence_of_sup-tRNA`: 82 nt E. coli Tyr(CUA) body, supported by Addgene #50831 sequence visualization and the PMID 31346230 CCA-omission statement.",
                "- `Sequence_of_origin_tRNA`: 82 nt derived Tyr(GUA) body, generated by reverting the suppressor anticodon from `CUA` to `GUA`; no genomic locus ID is assigned.",
                "- Secondary structures: generated with `tRNAscan-SE -B`; both origin and suppressor have the same 82-character structure.",
                f"- Sprinzl JSON: generated with `llm-trna.lumoxuan.cn /api/align/`, `use_llm=false`, forced template `{TEMPLATE}`.",
                "- `tRNAscan-SE_ID_of_origin_tRNA`, `rnacentral_ID_of_origin_tRNA`, `sup-tRNA_gene`, and `pdbid` are intentionally not changed.",
                f"- TSV: `{OUT_TSV}`.",
                f"- SQL: `{OUT_SQL}`.",
                f"- Raw llm-trna responses: `{OUT_API}`.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(OUT_TSV)
    print(OUT_SQL)
    print(OUT_REPORT)


if __name__ == "__main__":
    main()
