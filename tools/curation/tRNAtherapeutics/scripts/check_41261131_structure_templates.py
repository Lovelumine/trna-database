import csv
import sys
from pathlib import Path

csv.field_size_limit(sys.maxsize)

base = Path(__file__).resolve().parents[4] / "field-curation-workdir"
cand_path = base / "backups" / "Engineered_sup_tRNA_PMID41261131_structure_before.tsv"
templ_path = base / "backups" / "Engineered_sup_tRNA_structure_templates.tsv"

with cand_path.open() as f:
    candidates = list(csv.DictReader(f, delimiter="\t"))

with templ_path.open() as f:
    templates = list(csv.DictReader(f, delimiter="\t"))

seq_to_ids = {}
for template in templates:
    for column in ("Sequence_of_origin_tRNA", "Sequence_of_sup-tRNA"):
        seq = (template.get(column) or "").strip().upper()
        if not seq:
            continue
        seq_to_ids.setdefault(seq, []).append(
            (
                template.get("ENSURE_ID", ""),
                template.get("PMID", ""),
                template.get("sup-tRNA_gene", ""),
                column,
                len(template.get("js_origin_tRNA") or ""),
                len(template.get("js_sup_tRNA") or ""),
                template.get("pdbid", ""),
            )
        )

for row in candidates:
    print(f"\nCAND {row['ENSURE_ID']} {row.get('sup-tRNA_gene', '')}")
    for column in ("Sequence_of_origin_tRNA", "Sequence_of_sup-tRNA"):
        seq = (row.get(column) or "").strip().upper()
        hits = seq_to_ids.get(seq, [])
        print(f"  {column} len={len(seq)} hits={len(hits)}")
        for hit in hits[:5]:
            print(f"    {hit}")
