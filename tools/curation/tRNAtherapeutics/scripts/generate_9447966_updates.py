#!/usr/bin/env python3
"""Generate evidence-backed updates for PMID 9447966 C. elegans Trp suppressors."""

from __future__ import annotations

import csv
import io
import json
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path


csv.field_size_limit(sys.maxsize)

ROOT = Path(__file__).resolve().parents[4]
FULL = ROOT / "field-curation-workdir" / "full_tRNAtherapeutics"
SNAPSHOT = sorted((FULL / "snapshots").glob("Engineered_sup_tRNA_*.tsv"))[-1]
OUT_TSV = ROOT / "docs" / "curation" / "tRNAtherapeutics" / "extractions" / "9447966_kondo_trp_updates.tsv"
OUT_SQL = ROOT / "docs" / "curation" / "tRNAtherapeutics" / "sql" / "9447966_kondo_trp_updates.sql"
OUT_REPORT = ROOT / "docs" / "curation" / "tRNAtherapeutics" / "reports" / "9447966_kondo_trp_update_review.md"
OUT_API_DIR = FULL / "extractions" / "9447966_llm_trna_api"

ALIGN_API = "https://llm-trna.lumoxuan.cn/api/align/"
PMID = "9447966"

ORIGIN_SEQ = "GACUGCUUGGCGCAAUGGUAGCGCGUUCGACUCCAGAUCGAAAGGUUGGGCGUUCGAUCCGCUCAGUGGCUCA"
SUP_SEQ = "GACUGCUUGGCGCAAUGGUAGCGCGUUCGACUCUAGAUCGAAAGGUUGGGCGUUCGAUCCGCUCAGUGGCUCA"

TARGETS = {
    "ensure-995": "sup-5",
    "ensure-996": "sup-7",
    "ensure-997": "sup-24",
    "ensure-998": "sup-28",
    "ensure-999": "sup-29",
}


def norm(seq: str) -> str:
    return (seq or "").strip().upper().replace("T", "U").replace(" ", "").replace("\n", "")


def qident(name: str) -> str:
    return "`" + name.replace("`", "``") + "`"


def qval(value: object) -> str:
    if value is None:
        return "NULL"
    text = str(value)
    if text == "":
        return "NULL"
    return "'" + text.replace("\\", "\\\\").replace("'", "''") + "'"


def dotbracket_to_parentheses(structure: str) -> str:
    return structure.replace(">", "(").replace("<", ")")


def run_trnascan(seq: str, label: str) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        fasta = tmpdir / "seq.fa"
        out = tmpdir / "out.txt"
        struct = tmpdir / "struct.txt"
        fasta.write_text(f">{label}\n{seq}\n", encoding="utf-8")
        subprocess.run(["tRNAscan-SE", "-E", "-o", str(out), "-f", str(struct), str(fasta)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        lines = struct.read_text(encoding="utf-8").splitlines()
    for line in lines:
        if line.startswith("Str:"):
            return dotbracket_to_parentheses(line.split(":", 1)[1].strip())
    raise RuntimeError(f"No tRNAscan-SE structure for {label}")


def call_alignment(seq: str, anticodon: str, label: str) -> dict[str, object]:
    payload = json.dumps({"target_seq": norm(seq), "anticodon": anticodon, "use_llm": False}).encode()
    request = urllib.request.Request(ALIGN_API, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(request, timeout=45) as response:
        data = json.loads(response.read().decode())
    rows = list(csv.reader(io.StringIO(data["csv_content"])))
    ids = rows[0]
    aligned = rows[-1]
    if "".join(base for base in aligned if base != "-") != norm(seq):
        raise RuntimeError(f"{label}: alignment does not preserve sequence")
    OUT_API_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_API_DIR / f"{label}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"template_name": data["template_name"], "ids": ids, "aligned": aligned}


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
    if origin_alignment["ids"] != sup_alignment["ids"]:
        raise RuntimeError("Origin/sup alignment coordinate IDs differ")
    ids = origin_alignment["ids"]
    origin_aligned = origin_alignment["aligned"]
    sup_aligned = sup_alignment["aligned"]
    js_origin = [{"id": coord, "base": base} for coord, base in zip(ids, origin_aligned)]
    js_sup = [
        {"id": coord, "base": base, "sup_base": sup_base, "type": classify(base, sup_base)}
        for coord, base, sup_base in zip(ids, origin_aligned, sup_aligned)
    ]
    return json.dumps(js_origin, ensure_ascii=False), json.dumps(js_sup, ensure_ascii=False)


def load_rows() -> dict[str, dict[str, str]]:
    with SNAPSHOT.open(newline="", encoding="utf-8") as handle:
        return {row["ENSURE_ID"]: row for row in csv.DictReader(handle, delimiter="\t") if row.get("PMID") == PMID}


def main() -> None:
    rows = load_rows()
    missing = set(TARGETS) - set(rows)
    if missing:
        raise RuntimeError(f"Missing expected rows: {sorted(missing)}")

    origin_structure = run_trnascan(ORIGIN_SEQ, "origin_Trp_CCA")
    sup_structure = run_trnascan(SUP_SEQ, "sup_Trp_CUA")
    origin_alignment = call_alignment(ORIGIN_SEQ, "CCA", "9447966_origin_Trp_CCA")
    sup_alignment = call_alignment(SUP_SEQ, "CUA", "9447966_sup_Trp_CUA")
    js_origin, js_sup = build_json(origin_alignment, sup_alignment)

    updates = []
    for ensure_id, sup_gene in TARGETS.items():
        row = rows[ensure_id]
        if row["sup-tRNA_gene"].strip() != sup_gene:
            raise RuntimeError(f"{ensure_id}: expected {sup_gene}, found {row['sup-tRNA_gene']!r}")
        updates.append(
            {
                "PMID": PMID,
                "ENSURE_ID": ensure_id,
                "Index": row["Index"],
                "sup-tRNA_gene": sup_gene,
                "new_aa_and_anticodon_of_origin_tRNA": "Trp(CCA)",
                "new_Sequence_of_origin_tRNA": ORIGIN_SEQ,
                "new_Sequence_of_sup-tRNA": SUP_SEQ,
                "new_Secondary structure": origin_structure,
                "new_Secondary structure of sup-trna": sup_structure,
                "new_js_origin_tRNA": js_origin,
                "new_js_sup_tRNA": js_sup,
                "pdbid_current": row["pdbid"],
                "origin_len": str(len(ORIGIN_SEQ)),
                "sup_len": str(len(SUP_SEQ)),
                "origin_alignment_template": origin_alignment["template_name"],
                "sup_alignment_template": sup_alignment["template_name"],
                "evidence": (
                    "PMID 9447966 states the five assayed suppressor genes are tRNA^Trp gene family members "
                    "and have identical coding sequences; PMID 3221861 Fig. 2b provides the mature tRNA^Trp "
                    "coding sequence and states all five suppressor genes encode identical tRNA(UAGTrp) "
                    "with a single CCA-to-CTA anticodon change. Fig. 2 caption says 3' CCA is not encoded, "
                    "so the stored sequence is the 73-nt coding body without appended CCA."
                ),
            }
        )

    OUT_TSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_SQL.parent.mkdir(parents=True, exist_ok=True)
    OUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    fields = list(updates[0])
    with OUT_TSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        writer.writerows(updates)

    sql = [
        "-- PMID 9447966 C. elegans Trp suppressor sequence/structure updates.",
        "-- Evidence: PMID 9447966 plus original molecular characterization PMID 3221861 Fig. 2.",
        "-- Backup live DB before execution.",
    ]
    for update in updates:
        assignments = [
            f"{qident('aa_and_anticodon_of_origin_tRNA')} = {qval(update['new_aa_and_anticodon_of_origin_tRNA'])}",
            f"{qident('Sequence_of_origin_tRNA')} = {qval(update['new_Sequence_of_origin_tRNA'])}",
            f"{qident('Sequence_of_sup-tRNA')} = {qval(update['new_Sequence_of_sup-tRNA'])}",
            f"{qident('Secondary structure')} = {qval(update['new_Secondary structure'])}",
            f"{qident('Secondary structure of sup-trna')} = {qval(update['new_Secondary structure of sup-trna'])}",
            f"{qident('js_origin_tRNA')} = {qval(update['new_js_origin_tRNA'])}",
            f"{qident('js_sup_tRNA')} = {qval(update['new_js_sup_tRNA'])}",
        ]
        sql.append(
            "\nUPDATE Engineered_sup_tRNA\nSET\n  "
            + ",\n  ".join(assignments)
            + f"\nWHERE ENSURE_ID = {qval(update['ENSURE_ID'])} AND PMID = {qval(PMID)};"
        )
    OUT_SQL.write_text("\n".join(sql) + "\n", encoding="utf-8")

    OUT_REPORT.write_text(
        "\n".join(
            [
                "# PMID 9447966 update review",
                "",
                "- Scope: five C. elegans tRNA^Trp amber suppressor rows `ensure-995` through `ensure-999`.",
                "- Main article evidence: PMID 9447966 reports that the assayed `sup-5`, `sup-7`, `sup-24`, `sup-28`, and `sup-29` genes are individual tRNA^Trp family suppressors with identical coding sequences and differential expression.",
                "- Sequence evidence: original molecular characterization PMID 3221861 Fig. 2b gives the mature tRNA^Trp coding sequence; the abstract/figure state all five suppressors carry a single anticodon change from `CCA` to `CTA`.",
                "- Sequence convention: Fig. 2 caption states the 3' `CCA` is not encoded, so the stored origin/suppressor sequences are 73 nt without appended terminal CCA.",
                "- Origin/suppressor relationship: origin RNA is Trp(CCA); suppressor RNA is Trp/Sup(CUA), generated only by the documented anticodon first-base change.",
                "- Secondary structures: computed with local `tRNAscan-SE -E`; origin is classified as Trp/CCA and suppressor as Sup/CTA, both score 63.8.",
                f"- Secondary structure: `{origin_structure}`.",
                f"- Sprinzl JSON: generated through `{ALIGN_API}` with `use_llm=false`; origin template `{origin_alignment['template_name']}`, suppressor template `{sup_alignment['template_name']}`.",
                "- `tRNAscan-SE_ID_of_origin_tRNA`, `rnacentral_ID_of_origin_tRNA`, and `pdbid` are intentionally not changed. The paper gives locus names and coding sequence but not a database genomic tRNAscan ID.",
                f"- TSV: `{OUT_TSV}`.",
                f"- SQL: `{OUT_SQL}`.",
                f"- Raw llm-trna responses: `{OUT_API_DIR}`.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"Wrote {OUT_TSV}")
    print(f"Wrote {OUT_SQL}")
    print(f"Wrote {OUT_REPORT}")


if __name__ == "__main__":
    main()
