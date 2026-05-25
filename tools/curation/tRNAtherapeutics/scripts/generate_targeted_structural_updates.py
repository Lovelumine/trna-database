#!/usr/bin/env python3
"""Generate targeted structure/Sprinzl updates for evidence-resolved rows."""

from __future__ import annotations

import csv
import io
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path


csv.field_size_limit(sys.maxsize)

BASE = Path(__file__).resolve().parents[4] / "field-curation-workdir"
FULL = BASE / "full_tRNAtherapeutics"
BACKUPS = FULL / "backups"
OUT_TSV = FULL / "extractions" / "targeted_structural_updates.tsv"
OUT_SQL = FULL / "sql" / "targeted_structural_updates.sql"
OUT_REPORT = FULL / "reports" / "targeted_structural_update_review.md"
OUT_API_DIR = FULL / "extractions" / "targeted_llm_trna_api"

ALIGN_API = "https://llm-trna.lumoxuan.cn/api/align/"


def norm_rna(seq: str) -> str:
    return (seq or "").strip().upper().replace("T", "U").replace(" ", "").replace("\n", "")


def qident(name: str) -> str:
    return "`" + name.replace("`", "``") + "`"


def qval(value: object) -> str:
    if value is None or value == "":
        return "NULL"
    return "'" + str(value).replace("\\", "\\\\").replace("'", "''") + "'"


def latest_backup() -> Path:
    paths = sorted(BACKUPS.glob("Engineered_sup_tRNA_targeted_before_*.tsv"))
    if not paths:
        raise RuntimeError("No targeted backup found")
    return paths[-1]


def load_backup_rows(path: Path) -> dict[str, dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return {row["ENSURE_ID"]: row for row in csv.DictReader(handle, delimiter="\t")}


def dotbracket_to_parentheses(structure: str) -> str:
    return structure.replace(">", "(").replace("<", ")")


def safe_label(text: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in text)


def call_alignment(seq: str, anticodon: str, template_name: str, label: str) -> dict[str, object]:
    payload = json.dumps(
        {
            "target_seq": norm_rna(seq),
            "anticodon": anticodon,
            "use_llm": False,
            "template_name": template_name,
        }
    ).encode()
    request = urllib.request.Request(
        ALIGN_API,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            body = response.read().decode()
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"{label}: LLM-tRNA API HTTP {exc.code}: {exc.read().decode()}") from exc

    data = json.loads(body)
    rows = list(csv.reader(io.StringIO(data["csv_content"])))
    if len(rows) < 3:
        raise RuntimeError(f"{label}: expected three-line csv_content")
    ids = rows[0]
    aligned = rows[-1]
    if len(ids) != len(aligned):
        raise RuntimeError(f"{label}: id/aligned length mismatch")
    consumed = "".join(base for base in aligned if base != "-")
    if consumed != norm_rna(seq):
        raise RuntimeError(f"{label}: alignment does not preserve sequence")
    structure = dotbracket_to_parentheses(data["structure"]["secondary_structure"])
    if len(structure) != len(norm_rna(seq)):
        raise RuntimeError(f"{label}: structure length mismatch")

    OUT_API_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_API_DIR / f"{safe_label(label)}.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return {
        "template_name": data["template_name"],
        "ids": ids,
        "aligned": aligned,
        "structure": structure,
        "raw": data,
    }


def classify(base: str, sup_base: str) -> str:
    if base == "-" and sup_base == "-":
        return "gap"
    if base == "-":
        return "insertion"
    if sup_base == "-":
        return "deletion"
    if base == sup_base:
        return "match"
    return "mismatch"


def build_json(origin_alignment: dict[str, object], sup_alignment: dict[str, object]) -> tuple[str, str]:
    origin_ids = origin_alignment["ids"]
    sup_ids = sup_alignment["ids"]
    if origin_ids != sup_ids:
        raise RuntimeError("Origin/sup alignment coordinate IDs differ")
    origin_aligned = origin_alignment["aligned"]
    sup_aligned = sup_alignment["aligned"]
    js_origin = [
        {"id": coord, "base": base}
        for coord, base in zip(origin_ids, origin_aligned)
    ]
    js_sup = [
        {
            "id": coord,
            "base": base,
            "sup_base": sup_base,
            "type": classify(base, sup_base),
        }
        for coord, base, sup_base in zip(origin_ids, origin_aligned, sup_aligned)
    ]
    return json.dumps(js_origin, ensure_ascii=False), json.dumps(js_sup, ensure_ascii=False)


def validate_update(row: dict[str, str], update: dict[str, str]) -> None:
    ensure_id = update["ENSURE_ID"]
    if norm_rna(row["Sequence_of_sup-tRNA"]) != update["existing_sup_sequence"]:
        raise RuntimeError(f"{ensure_id}: DB sup sequence does not match curated suppressor sequence")
    if len(update["new_origin_secondary_structure"]) != len(update["new_origin_sequence"]):
        raise RuntimeError(f"{ensure_id}: origin structure length mismatch")
    if len(update["new_sup_secondary_structure"]) != len(update["existing_sup_sequence"]):
        raise RuntimeError(f"{ensure_id}: sup structure length mismatch")
    js_origin = json.loads(update["new_js_origin_tRNA"])
    js_sup = json.loads(update["new_js_sup_tRNA"])
    if sum(1 for item in js_origin if item["base"] != "-") != len(update["new_origin_sequence"]):
        raise RuntimeError(f"{ensure_id}: origin JSON non-gap count mismatch")
    if sum(1 for item in js_sup if item["sup_base"] != "-") != len(update["existing_sup_sequence"]):
        raise RuntimeError(f"{ensure_id}: sup JSON non-gap count mismatch")
    if len(update["new_js_origin_tRNA"]) >= 4096:
        raise RuntimeError(f"{ensure_id}: js_origin_tRNA exceeds DB field budget")
    if len(update["new_js_sup_tRNA"]) >= 8192:
        raise RuntimeError(f"{ensure_id}: js_sup_tRNA exceeds DB field budget")


def main() -> None:
    backup_path = latest_backup()
    db_rows = load_backup_rows(backup_path)
    specs = [
        {
            "ENSURE_ID": "ensure-847",
            "PMID": "24386240",
            "sup_seq": "GGUGGCUAUAGCUCAGUUGGUAGAGCCCUGGAUUCUAAUUCCAGUUGUCGUGGGUUCGAAUCCCAUUAGCCACCCCA",
            "origin_seq": "GGUGGCUAUAGCUCAGUUGGUAGAGCCCUGGAUUGUGAUUCCAGUUGUCGUGGGUUCGAAUCCCAUUAGCCACCCCA",
            "origin_aa": "His(GUG)",
            "species": "Escherichia coli",
            "origin_anti": "GUG",
            "sup_anti": "CUA",
            "template": "eschColi_chr.trna38-HisGTG",
            "trnascan": "eschColi_chr.trna38",
            "evidence": (
                "PMID 24386240 Figure S1 lists the precursor tRNAHisCUA sequence with the mature tRNA "
                "in uppercase; the mature uppercase sequence exactly matches the DB suppressor sequence. "
                "The article describes an orthogonal Escherichia coli histidyl-tRNA synthetase/tRNAHis pair "
                "used for amber suppression in Caulobacter crescentus. Origin was computed by reverting the "
                "amber anticodon CUA to His anticodon GUG."
            ),
            "confidence": "high",
        },
        {
            "ENSURE_ID": "ensure-848",
            "PMID": "23379331",
            "sup_seq": "GGAAACCUGAUCAUGUAGAUCGAACGGACUCUAAAUCCGUUCAGCCGGGUUAGAUUCCCGGGGUUUCCGCCA",
            "origin_seq": "GGAAACCUGAUCAUGUAGAUCGAACGGACUGUAAAUCCGUUCAGCCGGGUUAGAUUCCCGGGGUUUCCGCCA",
            "origin_aa": "Tyr(GUA)",
            "species": "Methanocaldococcus jannaschii",
            "origin_anti": "GUA",
            "sup_anti": "CUA",
            "template": "methJann1_chr.trna20-TyrGTA",
            "trnascan": "",
            "evidence": (
                "PMID 23379331 states that pUltra used a proK-tRNA_CUA^MjTyr cassette amplified from pEVOL. "
                "The existing DB suppressor sequence is therefore treated as the study sequence; origin was "
                "computed by reverting the amber anticodon CUA to Tyr anticodon GUA. The exact source-gene "
                "identifier is not assigned because the forced llm-trna template is not an exact sequence source."
            ),
            "confidence": "medium-high",
        },
    ]

    updates: list[dict[str, str]] = []
    for spec in specs:
        ensure_id = spec["ENSURE_ID"]
        if ensure_id not in db_rows:
            raise RuntimeError(f"{ensure_id}: missing from targeted backup")
        row = db_rows[ensure_id]
        origin_alignment = call_alignment(
            spec["origin_seq"],
            spec["origin_anti"],
            spec["template"],
            f"{ensure_id}_origin",
        )
        sup_alignment = call_alignment(
            spec["sup_seq"],
            spec["sup_anti"],
            spec["template"],
            f"{ensure_id}_sup",
        )
        js_origin_s, js_sup_s = build_json(origin_alignment, sup_alignment)
        update = {
            "PMID": spec["PMID"],
            "ENSURE_ID": ensure_id,
            "Index": row["Index"],
            "current_origin_aa": row["aa_and_anticodon_of_origin_tRNA"],
            "new_origin_aa": spec["origin_aa"],
            "current_origin_species": row["Species_source_of_origin_tRNA"],
            "new_origin_species": spec["species"],
            "current_trnascan": row["tRNAscan-SE_ID_of_origin_tRNA"],
            "new_trnascan": spec["trnascan"],
            "current_origin_sequence": row["Sequence_of_origin_tRNA"],
            "new_origin_sequence": norm_rna(spec["origin_seq"]),
            "existing_sup_sequence": norm_rna(spec["sup_seq"]),
            "current_origin_secondary_structure": row["Secondary structure"],
            "new_origin_secondary_structure": origin_alignment["structure"],
            "current_sup_secondary_structure": row["Secondary structure of sup-trna"],
            "new_sup_secondary_structure": sup_alignment["structure"],
            "current_js_origin_tRNA": row["js_origin_tRNA"],
            "new_js_origin_tRNA": js_origin_s,
            "current_js_sup_tRNA": row["js_sup_tRNA"],
            "new_js_sup_tRNA": js_sup_s,
            "pdbid_current": row["pdbid"],
            "alignment_template_requested": spec["template"],
            "alignment_template_origin": origin_alignment["template_name"],
            "alignment_template_sup": sup_alignment["template_name"],
            "origin_len": str(len(norm_rna(spec["origin_seq"]))),
            "sup_len": str(len(norm_rna(spec["sup_seq"]))),
            "coord_count": str(len(origin_alignment["ids"])),
            "evidence": spec["evidence"]
            + " Sprinzl/alignment and secondary structures were generated by llm-trna.lumoxuan.cn /api/align with use_llm=false and a forced template.",
            "confidence": spec["confidence"],
        }
        validate_update(row, update)
        updates.append(update)

    OUT_TSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_TSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(updates[0].keys()), delimiter="\t")
        writer.writeheader()
        writer.writerows(updates)

    sql = [
        "-- Targeted structure/Sprinzl updates for evidence-resolved Engineered_sup_tRNA rows.",
        f"-- DB backup: {backup_path}",
        f"-- Review TSV: {OUT_TSV}",
        "START TRANSACTION;",
    ]
    for update in updates:
        assignments = [
            f"{qident('aa_and_anticodon_of_origin_tRNA')} = {qval(update['new_origin_aa'])}",
            f"{qident('Species_source_of_origin_tRNA')} = {qval(update['new_origin_species'])}",
            f"{qident('Sequence_of_origin_tRNA')} = {qval(update['new_origin_sequence'])}",
            f"{qident('Secondary structure')} = {qval(update['new_origin_secondary_structure'])}",
            f"{qident('Secondary structure of sup-trna')} = {qval(update['new_sup_secondary_structure'])}",
            f"{qident('js_origin_tRNA')} = {qval(update['new_js_origin_tRNA'])}",
            f"{qident('js_sup_tRNA')} = {qval(update['new_js_sup_tRNA'])}",
        ]
        if update["new_trnascan"]:
            assignments.append(f"{qident('tRNAscan-SE_ID_of_origin_tRNA')} = {qval(update['new_trnascan'])}")
        sql.append(
            "\nUPDATE Engineered_sup_tRNA\nSET\n  "
            + ",\n  ".join(assignments)
            + f"\nWHERE PMID = {qval(update['PMID'])} AND ENSURE_ID = {qval(update['ENSURE_ID'])};"
        )
    sql.append("\nCOMMIT;")
    OUT_SQL.parent.mkdir(parents=True, exist_ok=True)
    OUT_SQL.write_text("\n".join(sql) + "\n", encoding="utf-8")

    OUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT_REPORT.write_text(
        "\n".join(
            [
                "# Targeted structural/Sprinzl update review",
                "",
                "Accepted rows: 2",
                "",
                "Rows updated:",
                "",
                "- `ensure-847` / PMID `24386240`: origin set to `His(GUG)`, species corrected to `Escherichia coli`, origin sequence computed by reverting amber `CUA` to `GUG`, secondary structures and Sprinzl JSON generated with llm-trna forced template `eschColi_chr.trna38-HisGTG`; existing tertiary placeholder `pdbid=AFP` retained.",
                "- `ensure-848` / PMID `23379331`: origin set to `Tyr(GUA)`, species normalized to `Methanocaldococcus jannaschii`, origin sequence computed by reverting amber `CUA` to `GUA`, secondary structures and Sprinzl JSON generated with llm-trna forced template `methJann1_chr.trna20-TyrGTA`; existing tertiary placeholder `pdbid=AFQ` retained.",
                "",
                "Evidence chain:",
                "",
                "1. PMID 24386240 Figure S1 provides the precursor `tRNAHisCUA` sequence and marks the mature tRNA sequence in uppercase. That mature sequence exactly matches the database suppressor sequence for `ensure-847`.",
                "2. PMID 24386240 identifies the suppressor system as the orthogonal Escherichia coli histidyl-tRNA synthetase/tRNAHis pair used in Caulobacter crescentus, so the origin tRNA source is Escherichia coli and the host/reaction system remains Caulobacter/E. coli as already represented elsewhere in the row.",
                "3. PMID 23379331 states that the `proK-tRNA_CUA^MjTyr` cassette was amplified from pEVOL and used in pUltra. The row's existing MjTyr suppressor sequence is retained as the study sequence; only the cognate Tyr anticodon is inferred by single anticodon reversion.",
                "4. The llm-trna API was used only for coordinate alignment and secondary-structure projection. It is not used as the literature source for biological identity.",
                "",
                "Skipped rows:",
                "",
                "- `ensure-849` / PMID `23379331` was not updated. The article discusses an ochre Mm-tRNA_UUA^Pyl(U25C) / MbPylRS(opt) pair, but the current database row has a source/sequence/anticodon conflict that needs plasmid or supplementary sequence confirmation before updating.",
                "",
                f"Review TSV: `{OUT_TSV}`",
                f"SQL: `{OUT_SQL}`",
                f"Raw API responses: `{OUT_API_DIR}`",
                f"Backup: `{backup_path}`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(OUT_TSV)
    print(OUT_SQL)
    print(OUT_REPORT)
    print("accepted", len(updates))
    for update in updates:
        print(
            update["ENSURE_ID"],
            update["new_origin_aa"],
            "origin_len",
            update["origin_len"],
            "sup_len",
            update["sup_len"],
            "coords",
            update["coord_count"],
            "pdbid",
            update["pdbid_current"],
        )


if __name__ == "__main__":
    main()
