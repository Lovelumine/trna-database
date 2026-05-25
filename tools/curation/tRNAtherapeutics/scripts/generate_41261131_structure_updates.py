import csv
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

csv.field_size_limit(sys.maxsize)

BASE = Path(__file__).resolve().parents[4] / "field-curation-workdir"
CANDIDATE_PATH = BASE / "backups" / "Engineered_sup_tRNA_PMID41261131_structure_before.tsv"
TEMPLATE_PATH = BASE / "backups" / "Engineered_sup_tRNA_structure_templates.tsv"
OUT_TSV = BASE / "extractions" / "41261131_structure_updates.tsv"
OUT_SQL = BASE / "sql" / "41261131_structure_updates.sql"
OUT_REVIEW = BASE / "notes" / "41261131_structure_update_review.md"


def normalize_seq(seq):
    return (seq or "").strip().upper().replace("T", "U")


def predict_structure(seq, name):
    seq = normalize_seq(seq)
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        fasta = tmpdir / "query.fa"
        out = tmpdir / "trnascan.out"
        fasta.write_text(f">{name}\n{seq}\n")
        subprocess.run(
            ["tRNAscan-SE", "-E", "-f", str(out), str(fasta)],
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        text = out.read_text()
    match = re.search(r"^Str:\s*(\S+)", text, flags=re.MULTILINE)
    if not match:
        raise RuntimeError(f"tRNAscan-SE did not return a structure for {name}")
    structure = match.group(1).replace(">", "(").replace("<", ")")
    if len(structure) != len(seq):
        raise RuntimeError(f"Structure/sequence length mismatch for {name}: {len(structure)} != {len(seq)}")
    return structure


def load_tsv(path):
    with path.open() as f:
        return list(csv.DictReader(f, delimiter="\t"))


def decode_json(value):
    return json.loads(value) if value else []


def non_gap_count(items, value_key):
    return sum(1 for item in items if item.get(value_key) != "-")


def template_spec_from_items(items, value_key):
    return [(item["id"], item.get(value_key, "-") == "-") for item in items]


def build_origin_json(seq, spec):
    seq = normalize_seq(seq)
    pos = 0
    out = []
    for coord, is_gap in spec:
        if is_gap:
            base = "-"
        else:
            base = seq[pos]
            pos += 1
        out.append({"id": coord, "base": base})
    if pos != len(seq):
        raise RuntimeError(f"Could not map all origin bases: consumed {pos}, sequence length {len(seq)}")
    return out


def build_sup_json(origin_seq, sup_seq, spec):
    origin_seq = normalize_seq(origin_seq)
    sup_seq = normalize_seq(sup_seq)
    origin_pos = 0
    sup_pos = 0
    out = []
    for coord, is_gap in spec:
        if is_gap:
            base = "-"
            sup_base = "-"
        else:
            base = origin_seq[origin_pos]
            sup_base = sup_seq[sup_pos]
            origin_pos += 1
            sup_pos += 1
        if base == "-" and sup_base == "-":
            kind = "gap"
        elif base == "-":
            kind = "insertion"
        elif sup_base == "-":
            kind = "deletion"
        elif base == sup_base:
            kind = "match"
        else:
            kind = "mismatch"
        out.append({"id": coord, "base": base, "sup_base": sup_base, "type": kind})
    if origin_pos != len(origin_seq) or sup_pos != len(sup_seq):
        raise RuntimeError(
            f"Could not map all alignment bases: origin {origin_pos}/{len(origin_seq)}, sup {sup_pos}/{len(sup_seq)}"
        )
    return out


def qident(name):
    return "`" + name.replace("`", "``") + "`"


def qval(value):
    if value is None or value == "":
        return "NULL"
    return "'" + str(value).replace("\\", "\\\\").replace("'", "''") + "'"


templates = load_tsv(TEMPLATE_PATH)
candidates = load_tsv(CANDIDATE_PATH)

origin_template_by_seq = {}
sup_template_by_seq = {}
templates_by_id = {}

for row in templates:
    templates_by_id[row["ENSURE_ID"]] = row
    origin_seq = normalize_seq(row.get("Sequence_of_origin_tRNA"))
    sup_seq = normalize_seq(row.get("Sequence_of_sup-tRNA"))
    if origin_seq and row.get("js_origin_tRNA"):
        origin_template_by_seq.setdefault(origin_seq, row)
    if sup_seq and row.get("js_sup_tRNA"):
        sup_template_by_seq.setdefault(sup_seq, row)

fallback_leu = origin_template_by_seq[
    "ACCAGGAUGGCCGAGUGGUUAAGGCGUUGGACUUAAGAUCCAAUGGACAUAUGUCCGCGUGGGUUCGAACCCCACUCCUGGUA"
]
fallback_tyr = templates_by_id["ensure-257"]

updates = []

for row in candidates:
    ensure_id = row["ENSURE_ID"]
    origin_seq = normalize_seq(row["Sequence_of_origin_tRNA"])
    sup_seq = normalize_seq(row["Sequence_of_sup-tRNA"])

    template_row = origin_template_by_seq.get(origin_seq)
    template_kind = "origin"
    if template_row:
        template_items = decode_json(template_row["js_origin_tRNA"])
        spec = template_spec_from_items(template_items, "base")
        template_id = template_row["ENSURE_ID"]
    elif sup_seq in sup_template_by_seq:
        template_row = sup_template_by_seq[sup_seq]
        template_items = decode_json(template_row["js_sup_tRNA"])
        spec = template_spec_from_items(template_items, "sup_base")
        template_id = template_row["ENSURE_ID"]
        template_kind = "sup"
    elif len(origin_seq) == 83 and "Leu-TAA" in (row.get("sup-tRNA_gene") or ""):
        template_row = fallback_leu
        template_items = decode_json(template_row["js_origin_tRNA"])
        spec = template_spec_from_items(template_items, "base")
        template_id = template_row["ENSURE_ID"]
        template_kind = "fallback_leu"
    elif len(origin_seq) == 94 and "Tyr-GTA" in (row.get("sup-tRNA_gene") or ""):
        template_row = fallback_tyr
        template_items = decode_json(template_row["js_sup_tRNA"])
        spec = template_spec_from_items(template_items, "sup_base")
        template_id = template_row["ENSURE_ID"]
        template_kind = "fallback_tyr_intron"
    else:
        raise RuntimeError(f"No Sprinzl template found for ENSURE_ID {ensure_id}")

    non_gap = sum(1 for _, is_gap in spec if not is_gap)
    if non_gap != len(origin_seq) or non_gap != len(sup_seq):
        raise RuntimeError(f"Template {template_id} non-gap count {non_gap} does not match {ensure_id} length")

    js_origin = build_origin_json(origin_seq, spec)
    js_sup = build_sup_json(origin_seq, sup_seq, spec)

    sec_origin = predict_structure(origin_seq, f"{ensure_id}_origin")
    sec_sup = predict_structure(sup_seq, f"{ensure_id}_sup")

    exact_model = sup_template_by_seq.get(sup_seq)
    pdbid = (exact_model or {}).get("pdbid") or ""

    updates.append(
        {
            "ENSURE_ID": ensure_id,
            "Secondary structure": sec_origin,
            "Secondary structure of sup-trna": sec_sup,
            "js_origin_tRNA": json.dumps(js_origin, ensure_ascii=False),
            "js_sup_tRNA": json.dumps(js_sup, ensure_ascii=False),
            "pdbid": pdbid,
            "sprinzl_template_id": template_id,
            "sprinzl_template_kind": template_kind,
            "pdbid_source": (exact_model or {}).get("ENSURE_ID", "") if pdbid else "",
        }
    )

OUT_TSV.parent.mkdir(parents=True, exist_ok=True)
with OUT_TSV.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(updates[0].keys()), delimiter="\t")
    writer.writeheader()
    writer.writerows(updates)

sql = [
    "-- Structure/Sprinzl/alignment update for PMID 41261131",
    "START TRANSACTION;",
]

for row in updates:
    assignments = [
        f"{qident('Secondary structure')} = {qval(row['Secondary structure'])}",
        f"{qident('Secondary structure of sup-trna')} = {qval(row['Secondary structure of sup-trna'])}",
        f"{qident('js_origin_tRNA')} = {qval(row['js_origin_tRNA'])}",
        f"{qident('js_sup_tRNA')} = {qval(row['js_sup_tRNA'])}",
        f"{qident('pdbid')} = {qval(row['pdbid'])}",
    ]
    sql.append(
        "\nUPDATE Engineered_sup_tRNA\nSET\n  "
        + ",\n  ".join(assignments)
        + f"\nWHERE PMID = 41261131 AND ENSURE_ID = {qval(row['ENSURE_ID'])};"
    )

sql.append("\nCOMMIT;")
OUT_SQL.parent.mkdir(parents=True, exist_ok=True)
OUT_SQL.write_text("\n".join(sql) + "\n")

OUT_REVIEW.write_text(
    """# PMID 41261131 structure/Sprinzl update

Generated fields:

- `Secondary structure` and `Secondary structure of sup-trna`: predicted with local `tRNAscan-SE -E -f`.
- `js_origin_tRNA`: Sprinzl coordinate JSON generated from existing database Sprinzl templates with matching sequence/coordinate class.
- `js_sup_tRNA`: alignment JSON generated from the same Sprinzl coordinate template plus the curated origin/sup sequences.
- `pdbid`: copied only when the exact same sup-tRNA sequence already had an existing structure/model id in the database. Rows without exact sequence model evidence remain NULL.

Template policy:

- Human Leu-TAA rows use exact-origin Sprinzl templates where available.
- Mouse Leu-TAA-2-1 rows use the homologous 83-nt Leu-TAA coordinate template because no exact mouse mapping existed in the database.
- Tyr-GTA-7-1 includes a tRNAscan-SE predicted intron; the existing database Tyr-GTA suppressor template with `37i1`-style intron insertion coordinates was used.
"""
)

print(OUT_TSV)
print(OUT_SQL)
print(OUT_REVIEW)
print("rows", len(updates))
for row in updates:
    print(
        row["ENSURE_ID"],
        "sec",
        len(row["Secondary structure"]),
        len(row["Secondary structure of sup-trna"]),
        "js",
        len(json.loads(row["js_origin_tRNA"])),
        len(json.loads(row["js_sup_tRNA"])),
        "template",
        row["sprinzl_template_id"],
        row["sprinzl_template_kind"],
        "pdbid",
        row["pdbid"] or "-",
    )
