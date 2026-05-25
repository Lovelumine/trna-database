import csv
import json
from pathlib import Path


BASE = Path(__file__).resolve().parents[4] / "field-curation-workdir"
CANDIDATE_TSV = BASE / "backups" / "Engineered_sup_tRNA_PMID41261131_structure_before.tsv"
CSV_DIR = BASE / "extractions" / "41261131_llm_trna_csv"
OUT_TSV = BASE / "extractions" / "41261131_llm_trna_sprinzl_updates.tsv"
OUT_SQL = BASE / "sql" / "41261131_llm_trna_sprinzl_updates.sql"
OUT_NOTE = BASE / "notes" / "41261131_llm_trna_sprinzl_update_review.md"


def norm(seq: str) -> str:
    return (seq or "").strip().upper().replace("T", "U")


def load_tsv(path: Path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_alignment(path: Path):
    with path.open(newline="") as handle:
        rows = [row for row in csv.reader(handle) if row]
    if len(rows) < 2:
        raise RuntimeError(f"{path} has fewer than two CSV rows")
    nums = [str(x).strip() for x in rows[0]]
    bases = [str(x).strip().upper().replace("T", "U") for x in rows[-1]]
    if len(nums) != len(bases):
        raise RuntimeError(f"{path} width mismatch: {len(nums)} != {len(bases)}")
    return nums, bases


def non_gap_sequence(bases):
    return "".join(base for base in bases if base != "-")


def classify(base, sup_base):
    if base == "-" and sup_base == "-":
        return "gap"
    if base == "-":
        return "insertion"
    if sup_base == "-":
        return "deletion"
    if base == sup_base:
        return "match"
    return "mismatch"


def qident(name):
    return "`" + name.replace("`", "``") + "`"


def qval(value):
    if value is None or value == "":
        return "NULL"
    return "'" + str(value).replace("\\", "\\\\").replace("'", "''") + "'"


rows = []
for cand in sorted(load_tsv(CANDIDATE_TSV), key=lambda row: int(row["ENSURE_ID"])):
    ensure_id = cand["ENSURE_ID"]
    origin_nums, origin_bases = read_alignment(CSV_DIR / f"{ensure_id}_origin.csv")
    sup_nums, sup_bases = read_alignment(CSV_DIR / f"{ensure_id}_sup.csv")

    origin_seq = norm(cand["Sequence_of_origin_tRNA"])
    sup_seq = norm(cand["Sequence_of_sup-tRNA"])
    if non_gap_sequence(origin_bases) != origin_seq:
        raise RuntimeError(f"{ensure_id}: origin base preservation failed")
    if non_gap_sequence(sup_bases) != sup_seq:
        raise RuntimeError(f"{ensure_id}: sup base preservation failed")

    origin_map = dict(zip(origin_nums, origin_bases))
    sup_map = dict(zip(sup_nums, sup_bases))
    coord_order = list(dict.fromkeys(origin_nums + [coord for coord in sup_nums if coord not in origin_map]))

    js_origin = [{"id": coord, "base": origin_map.get(coord, "-")} for coord in coord_order]
    js_sup = [
        {
            "id": coord,
            "base": origin_map.get(coord, "-"),
            "sup_base": sup_map.get(coord, "-"),
            "type": classify(origin_map.get(coord, "-"), sup_map.get(coord, "-")),
        }
        for coord in coord_order
    ]

    rows.append(
        {
            "ENSURE_ID": ensure_id,
            "sup-tRNA_gene": cand.get("sup-tRNA_gene", ""),
            "coord_count": len(coord_order),
            "origin_non_gap_count": sum(1 for item in js_origin if item["base"] != "-"),
            "sup_non_gap_count": sum(1 for item in js_sup if item["sup_base"] != "-"),
            "js_origin_tRNA": json.dumps(js_origin, ensure_ascii=False),
            "js_sup_tRNA": json.dumps(js_sup, ensure_ascii=False),
        }
    )

max_origin_len = max(len(row["js_origin_tRNA"]) for row in rows)
max_sup_len = max(len(row["js_sup_tRNA"]) for row in rows)
if max_origin_len > 4096 or max_sup_len > 8192:
    raise RuntimeError(f"JSON field length would exceed DB limits: origin={max_origin_len}, sup={max_sup_len}")

OUT_TSV.parent.mkdir(parents=True, exist_ok=True)
with OUT_TSV.open("w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), delimiter="\t")
    writer.writeheader()
    writer.writerows(rows)

sql = [
    "-- Regenerate Sprinzl coordinate/alignment JSON for PMID 41261131 using local LLM-tRNAAlign output.",
    "-- Source CSV files: field-curation-workdir/extractions/41261131_llm_trna_csv/",
    "START TRANSACTION;",
]
for row in rows:
    sql.append(
        "\nUPDATE Engineered_sup_tRNA\nSET\n  "
        + f"{qident('js_origin_tRNA')} = {qval(row['js_origin_tRNA'])},\n  "
        + f"{qident('js_sup_tRNA')} = {qval(row['js_sup_tRNA'])}\n"
        + f"WHERE PMID = 41261131 AND ENSURE_ID = {qval(row['ENSURE_ID'])};"
    )
sql.append("\nCOMMIT;")
OUT_SQL.parent.mkdir(parents=True, exist_ok=True)
OUT_SQL.write_text("\n".join(sql) + "\n")

OUT_NOTE.write_text(
    "\n".join(
        [
            "# PMID 41261131 LLM-tRNAAlign Sprinzl JSON update",
            "",
            "This update regenerates only:",
            "",
            "- `js_origin_tRNA`",
            "- `js_sup_tRNA`",
            "",
            "Secondary structure fields and `pdbid` are unchanged.",
            "",
            "Source:",
            "",
            "- Online `https://llm-trna.lumoxuan.cn/api/*` returned nginx 504 during testing.",
            "- The local LLM-tRNAAlign source repo was supplied via `LLM_TRNA_REPO`, with `LLM_POSTCHECK=0`.",
            "- Raw alignment CSV files are under `field-curation-workdir/extractions/41261131_llm_trna_csv/`.",
            "",
            "Rationale:",
            "",
            "- The previous JSON used compact coordinates copied from existing database templates.",
            "- LLM-tRNAAlign emits fuller Sprinzl coordinate rows and assigns the long Leu/Tyr variable-arm positions differently.",
            "- Non-gap sequence preservation was verified for every origin and suppressor sequence before SQL generation.",
            "",
            f"Rows: {len(rows)}",
            f"Max `js_origin_tRNA` length: {max_origin_len}",
            f"Max `js_sup_tRNA` length: {max_sup_len}",
            "",
            f"Review TSV: `{OUT_TSV}`",
            f"SQL: `{OUT_SQL}`",
        ]
    )
    + "\n"
)

print(OUT_TSV)
print(OUT_SQL)
print(OUT_NOTE)
print("rows", len(rows))
print("max_origin_len", max_origin_len)
print("max_sup_len", max_sup_len)
