import csv
import io
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path


csv.field_size_limit(sys.maxsize)

BASE = Path(__file__).resolve().parents[4] / "field-curation-workdir"
FULL = BASE / "full_tRNAtherapeutics"
BACKUPS = FULL / "backups"
SUPP_TXT = FULL / "extractions" / "39558163_supplemental_docx.txt"
OUT_TSV = FULL / "extractions" / "39558163_human_trna_updates.tsv"
OUT_SQL = FULL / "sql" / "39558163_human_trna_updates.sql"
OUT_REPORT = FULL / "reports" / "39558163_human_trna_update_review.md"
OUT_API_DIR = FULL / "extractions" / "39558163_llm_trna_api"

ALIGN_API = "https://llm-trna.lumoxuan.cn/api/align/"


def norm_rna(seq: str) -> str:
    return (seq or "").strip().upper().replace("T", "U").replace(" ", "").replace("\n", "")


def norm_dna(seq: str) -> str:
    return norm_rna(seq).replace("U", "T")


def qident(name: str) -> str:
    return "`" + name.replace("`", "``") + "`"


def qval(value):
    if value is None or value == "":
        return "NULL"
    return "'" + str(value).replace("\\", "\\\\").replace("'", "''") + "'"


def latest_backup() -> Path:
    paths = sorted(BACKUPS.glob("Engineered_sup_tRNA_PMID39558163_before_*.tsv"))
    if not paths:
        raise RuntimeError("No PMID 39558163 backup found")
    return paths[-1]


def load_backup_rows(path: Path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def parse_table_s1_sequences():
    text = SUPP_TXT.read_text()
    match = re.search(
        r"E\. coli sup-tRNAAla(?P<ecoli>[ACGT]+)"
        r"Human sup-tRNAAla(?P<ala>[ACGT]+)"
        r"Human sup-tRNATyr(?P<tyr>[ACGT]+)"
        r"Table S2",
        text,
    )
    if not match:
        raise RuntimeError("Could not parse Table S1 human sup-tRNA sequences")
    return {
        "Human sup-tRNAAla": match.group("ala"),
        "Human sup-tRNATyr": match.group("tyr"),
    }


def replace_unique(seq: str, old: str, new: str) -> str:
    hits = [m.start() for m in re.finditer(old, seq)]
    if len(hits) != 1:
        raise RuntimeError(f"Expected one {old} in {seq}, found {len(hits)}")
    pos = hits[0]
    return seq[:pos] + new + seq[pos + len(old):]


def dotbracket_to_parentheses(structure: str) -> str:
    return structure.replace(">", "(").replace("<", ")")


def call_alignment(seq: str, anticodon: str, template_name: str, label: str):
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
    (OUT_API_DIR / f"{label}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
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


def build_json(origin_alignment, sup_alignment):
    if origin_alignment["ids"] != sup_alignment["ids"]:
        raise RuntimeError("Origin/sup alignment coordinate IDs differ")
    js_origin = [
        {"id": coord, "base": base}
        for coord, base in zip(origin_alignment["ids"], origin_alignment["aligned"])
    ]
    js_sup = [
        {
            "id": coord,
            "base": base,
            "sup_base": sup_base,
            "type": classify(base, sup_base),
        }
        for coord, base, sup_base in zip(
            origin_alignment["ids"],
            origin_alignment["aligned"],
            sup_alignment["aligned"],
        )
    ]
    return js_origin, js_sup


def main():
    backup_path = latest_backup()
    db_rows = {row["ENSURE_ID"]: row for row in load_backup_rows(backup_path)}
    table_s1 = parse_table_s1_sequences()

    specs = [
        {
            "ids": ["ensure-1034", "ensure-1050"],
            "table_name": "Human sup-tRNAAla",
            "origin_aa": "Ala(AGC)",
            "sup_aa": "Ala(CUA)",
            "origin_anticodon_dna": "AGC",
            "sup_anticodon_dna": "CTA",
            "align_template": "hg19_chr6.trna112-AlaAGC",
            "trnascan": "chr6.trna112",
            "rnacentral": "URS000063E4FD_9606",
            "source_note": "GtRNAdb hg19 tRNA-Ala-AGC-1-1 / chr6.trna112; RNAcentral URS000063E4FD_9606",
            "confidence": "high",
        },
        {
            "ids": ["ensure-1052"],
            "table_name": "Human sup-tRNATyr",
            "origin_aa": "Tyr(GUA)",
            "sup_aa": "Tyr(CUA)",
            "origin_anticodon_dna": "GTA",
            "sup_anticodon_dna": "CTA",
            "align_template": "hg19_chr6.trna14-TyrGTA",
            "trnascan": "tRNA-Tyr-GTA-2-1",
            "rnacentral": "URS0000636E2A_9606",
            "source_note": "RNAcentral exact Homo sapiens tRNA-Tyr(GTA) 2-1 / URS0000636E2A_9606; GtRNAdb listed as an expert database",
            "confidence": "high",
        },
    ]

    updates = []
    for spec in specs:
        sup_dna = table_s1[spec["table_name"]]
        sup_rna = norm_rna(sup_dna)
        origin_dna = replace_unique(sup_dna, spec["sup_anticodon_dna"], spec["origin_anticodon_dna"])
        origin_rna = norm_rna(origin_dna)

        origin_alignment = call_alignment(
            origin_rna,
            spec["origin_anticodon_dna"].replace("T", "U"),
            spec["align_template"],
            f"{spec['table_name']}_origin",
        )
        sup_alignment = call_alignment(
            sup_rna,
            spec["sup_anticodon_dna"].replace("T", "U"),
            spec["align_template"],
            f"{spec['table_name']}_sup",
        )
        js_origin, js_sup = build_json(origin_alignment, sup_alignment)
        js_origin_s = json.dumps(js_origin, ensure_ascii=False)
        js_sup_s = json.dumps(js_sup, ensure_ascii=False)

        if sum(1 for item in js_origin if item["base"] != "-") != len(origin_rna):
            raise RuntimeError(f"{spec['table_name']}: origin JSON non-gap count mismatch")
        if sum(1 for item in js_sup if item["sup_base"] != "-") != len(sup_rna):
            raise RuntimeError(f"{spec['table_name']}: sup JSON non-gap count mismatch")

        for ensure_id in spec["ids"]:
            row = db_rows[ensure_id]
            if norm_rna(row["Sequence_of_sup-tRNA"]) != sup_rna:
                raise RuntimeError(f"{ensure_id}: DB sup sequence does not match Table S1")
            updates.append(
                {
                    "ENSURE_ID": ensure_id,
                    "Index": row["Index"],
                    "table_s1_name": spec["table_name"],
                    "current_origin_aa": row["aa_and_anticodon_of_origin_tRNA"],
                    "new_origin_aa": spec["origin_aa"],
                    "current_rnacentral": row["rnacentral_ID_of_origin_tRNA"],
                    "new_rnacentral": spec["rnacentral"],
                    "current_trnascan": row["tRNAscan-SE_ID_of_origin_tRNA"],
                    "new_trnascan": spec["trnascan"],
                    "current_species": row["Species_source_of_origin_tRNA"],
                    "new_species": "Homo sapiens",
                    "new_origin_sequence": origin_rna,
                    "existing_sup_sequence": sup_rna,
                    "new_sup_tRNA_gene": sup_dna,
                    "new_origin_secondary_structure": origin_alignment["structure"],
                    "new_sup_secondary_structure": sup_alignment["structure"],
                    "new_js_origin_tRNA": js_origin_s,
                    "new_js_sup_tRNA": js_sup_s,
                    "alignment_template": spec["align_template"],
                    "alignment_api_template_origin": origin_alignment["template_name"],
                    "alignment_api_template_sup": sup_alignment["template_name"],
                    "coord_count": str(len(js_origin)),
                    "origin_non_gap": str(sum(1 for item in js_origin if item["base"] != "-")),
                    "sup_non_gap": str(sum(1 for item in js_sup if item["sup_base"] != "-")),
                    "evidence": (
                        "PMID 39558163 Supplementary Table S1 sequence; "
                        "article methods state tRNA sequences are listed in Supplementary Tables S1/S2; "
                        + spec["source_note"]
                        + "; Sprinzl/alignment and CCA-unpaired secondary structure generated by llm-trna.lumoxuan.cn /api/align with forced template"
                    ),
                    "confidence": spec["confidence"],
                }
            )

    OUT_TSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_TSV.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(updates[0].keys()), delimiter="\t")
        writer.writeheader()
        writer.writerows(updates)

    sql = [
        "-- PMID 39558163 human sup-tRNA origin/structure/Sprinzl updates.",
        f"-- DB backup: {backup_path}",
        f"-- Review TSV: {OUT_TSV}",
        "START TRANSACTION;",
    ]
    for row in updates:
        assignments = [
            f"{qident('aa_and_anticodon_of_origin_tRNA')} = {qval(row['new_origin_aa'])}",
            f"{qident('rnacentral_ID_of_origin_tRNA')} = {qval(row['new_rnacentral'])}",
            f"{qident('tRNAscan-SE_ID_of_origin_tRNA')} = {qval(row['new_trnascan'])}",
            f"{qident('Species_source_of_origin_tRNA')} = {qval(row['new_species'])}",
            f"{qident('Sequence_of_origin_tRNA')} = {qval(row['new_origin_sequence'])}",
            f"{qident('sup-tRNA_gene')} = {qval(row['new_sup_tRNA_gene'])}",
            f"{qident('Secondary structure')} = {qval(row['new_origin_secondary_structure'])}",
            f"{qident('Secondary structure of sup-trna')} = {qval(row['new_sup_secondary_structure'])}",
            f"{qident('js_origin_tRNA')} = {qval(row['new_js_origin_tRNA'])}",
            f"{qident('js_sup_tRNA')} = {qval(row['new_js_sup_tRNA'])}",
        ]
        sql.append(
            "\nUPDATE Engineered_sup_tRNA\nSET\n  "
            + ",\n  ".join(assignments)
            + f"\nWHERE PMID = 39558163 AND ENSURE_ID = {qval(row['ENSURE_ID'])};"
        )
    sql.append("\nCOMMIT;")
    OUT_SQL.parent.mkdir(parents=True, exist_ok=True)
    OUT_SQL.write_text("\n".join(sql) + "\n")

    OUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT_REPORT.write_text(
        "\n".join(
            [
                "# PMID 39558163 human tRNA update review",
                "",
                "Accepted rows: 3",
                "",
                "Rows updated:",
                "",
                "- `ensure-1034`, `ensure-1050`: Human sup-tRNAAla; origin set to `Ala(AGC)`, RNAcentral `URS000063E4FD_9606`, tRNAscan-SE `chr6.trna112`.",
                "- `ensure-1052`: Human sup-tRNATyr; origin set to `Tyr(GUA)`, RNAcentral `URS0000636E2A_9606`, GtRNAdb/RNAcentral gene symbol `tRNA-Tyr-GTA-2-1`.",
                "",
                "Evidence chain:",
                "",
                "1. PMID 39558163 / PMCID PMC11662663 methods state that nucleic acid sequences of tRNAs and reporters are listed in Supplementary Tables S1 and S2.",
                "2. Supplementary Table S1 lists the exact `Human sup-tRNAAla` and `Human sup-tRNATyr` nucleotide sequences used in the study.",
                "3. The origin tRNA sequence is obtained by reverting the unique amber suppressor anticodon `CTA`/`CUA` to the cognate anticodon: `AGC` for Ala and `GTA`/`GUA` for Tyr. The terminal CCA present in the study sequence is retained so origin and suppressor sequences have the same mature-tRNA length used by the database row.",
                "4. Ala core sequence without terminal CCA matches GtRNAdb hg19 `tRNA-Ala-AGC-1-1` / `chr6.trna112`, RNAcentral `URS000063E4FD_9606`.",
                "5. Tyr core sequence without terminal CCA matches RNAcentral `URS0000636E2A_9606`, described as Homo sapiens tRNA-Tyr(GTA) 2-1 and annotated by GtRNAdb among other expert databases.",
                "6. `Secondary structure`, `Secondary structure of sup-trna`, `js_origin_tRNA`, and `js_sup_tRNA` were generated through `https://llm-trna.lumoxuan.cn/api/align/` with `use_llm=false` and forced human templates. The added terminal CCA is represented as unpaired dots in the secondary structure.",
                "",
                f"Review TSV: `{OUT_TSV}`",
                f"SQL: `{OUT_SQL}`",
                f"Raw API responses: `{OUT_API_DIR}`",
                f"Backup: `{backup_path}`",
            ]
        )
        + "\n"
    )

    print(OUT_TSV)
    print(OUT_SQL)
    print(OUT_REPORT)
    print("accepted", len(updates))
    for row in updates:
        print(
            row["ENSURE_ID"],
            row["new_origin_aa"],
            row["new_trnascan"],
            row["new_rnacentral"],
            "origin_len",
            len(row["new_origin_sequence"]),
            "coords",
            row["coord_count"],
        )


if __name__ == "__main__":
    main()
