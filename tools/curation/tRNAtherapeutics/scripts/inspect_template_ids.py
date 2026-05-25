import csv
import json
import sys
from pathlib import Path

csv.field_size_limit(sys.maxsize)
path = Path(__file__).resolve().parents[4] / "field-curation-workdir" / "backups" / "Engineered_sup_tRNA_structure_templates.tsv"
want = {"ensure-358", "ensure-326", "ensure-329", "ensure-257"}
with path.open() as f:
    rows = csv.DictReader(f, delimiter="\t")
    for row in rows:
        if row["ENSURE_ID"] not in want:
            continue
        origin = json.loads(row["js_origin_tRNA"])
        sup = json.loads(row["js_sup_tRNA"])
        print("\n", row["ENSURE_ID"], "origin len", len(row["Sequence_of_origin_tRNA"]), "sup len", len(row["Sequence_of_sup-tRNA"]))
        print("origin js", len(origin), "origin non-gap", sum(1 for item in origin if item.get("base") != "-"))
        print("origin ids", [item["id"] for item in origin])
        print("sup js", len(sup), "sup non-gap", sum(1 for item in sup if item.get("sup_base") != "-"))
