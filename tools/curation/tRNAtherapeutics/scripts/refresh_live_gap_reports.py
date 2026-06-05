#!/usr/bin/env python3
"""Refresh local curation gap reports from the live Engineered_sup_tRNA table."""

from __future__ import annotations

import csv
import os
import re
import subprocess
from collections import defaultdict
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "field-curation-workdir" / "full_tRNAtherapeutics"
SNAPSHOTS = BASE / "snapshots"
MANIFEST = BASE / "paper_manifest.tsv"
ROW_GAP_REPORT = BASE / "row_gap_report.tsv"
FIELD_GAP_REPORT = BASE / "field_gap_report.tsv"
TABLE = "Engineered_sup_tRNA"

HIGH_VALUE_FIELDS = [
    "pdbid",
    "Secondary structure",
    "Secondary structure of sup-trna",
    "Sequence_of_origin_tRNA",
    "Sequence_of_sup-tRNA",
]


def read_env() -> dict[str, str]:
    env: dict[str, str] = {}
    for rel in [".env", "Flask/.env"]:
        path = ROOT / rel
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", line):
                continue
            key, value = line.split("=", 1)
            env[key] = value.strip().strip("'\"")
    return env


def is_blank(value: str | None) -> bool:
    if value is None:
        return True
    text = str(value).strip()
    return text == "" or text.upper() == "NULL" or text == "[]"


def export_live_table() -> tuple[Path, list[dict[str, str]]]:
    env = read_env()
    missing = [key for key in ["MYSQL_HOST", "MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_DB"] if key not in env]
    if missing:
        raise RuntimeError(f"Missing env keys: {', '.join(missing)}")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    SNAPSHOTS.mkdir(parents=True, exist_ok=True)
    path = SNAPSHOTS / f"{TABLE}_{timestamp}.tsv"
    cmd_env = os.environ.copy()
    cmd_env["MYSQL_PWD"] = env["MYSQL_PASSWORD"]
    proc = subprocess.run(
        [
            "/usr/bin/mysql",
            "-h",
            env["MYSQL_HOST"],
            "-P",
            env.get("MYSQL_PORT") or "3306",
            "-u",
            env["MYSQL_USER"],
            env["MYSQL_DB"],
            "-B",
            "-e",
            f"SELECT * FROM {TABLE};",
        ],
        cwd=ROOT,
        env=cmd_env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr)
    path.write_text(proc.stdout, encoding="utf-8")
    rows = list(csv.DictReader(proc.stdout.splitlines(), delimiter="\t"))
    return path, rows


def write_tsv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def refresh_manifest(rows: list[dict[str, str]]) -> None:
    manifest_rows = list(csv.DictReader(MANIFEST.open(encoding="utf-8"), delimiter="\t"))
    by_pmid: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_pmid[str(row.get("PMID", "")).strip()].append(row)

    manifest_by_pmid = {
        row["PMID"]: row
        for row in manifest_rows
        if str(row.get("PMID", "")).strip() in by_pmid
    }
    for pmid, pmid_rows in by_pmid.items():
        row = manifest_by_pmid.setdefault(
            pmid,
            {
                key: ""
                for key in manifest_rows[0].keys()
            },
        )
        row["PMID"] = pmid
        row["row_count"] = str(len(pmid_rows))
        ensure_nums = [int(item["ENSURE_ID"]) for item in pmid_rows if str(item.get("ENSURE_ID", "")).isdigit()]
        row["min_ensure_id"] = str(min(ensure_nums)) if ensure_nums else row.get("min_ensure_id", "")
        row["max_ensure_id"] = str(max(ensure_nums)) if ensure_nums else row.get("max_ensure_id", "")
        counts = {field: sum(1 for item in pmid_rows if is_blank(item.get(field))) for field in HIGH_VALUE_FIELDS}
        row["missing_pdbid"] = str(counts["pdbid"])
        row["missing_origin_secondary_structure"] = str(counts["Secondary structure"])
        row["missing_sup_secondary_structure"] = str(counts["Secondary structure of sup-trna"])
        row["missing_origin_sequence"] = str(counts["Sequence_of_origin_tRNA"])
        row["missing_sup_sequence"] = str(counts["Sequence_of_sup-tRNA"])

    fieldnames = list(manifest_rows[0].keys())
    def pmid_sort_key(value: str):
        return (0, int(value)) if value.isdigit() else (1, value)

    ordered = [manifest_by_pmid[pmid] for pmid in sorted(manifest_by_pmid, key=pmid_sort_key)]
    write_tsv(MANIFEST, ordered, fieldnames)


def refresh_row_gap_report(rows: list[dict[str, str]]) -> None:
    out = []
    for row in rows:
        missing_origin_seq = is_blank(row.get("Sequence_of_origin_tRNA"))
        missing_sup_seq = is_blank(row.get("Sequence_of_sup-tRNA"))
        missing_origin_ss = is_blank(row.get("Secondary structure"))
        missing_sup_ss = is_blank(row.get("Secondary structure of sup-trna"))
        missing_pdbid = is_blank(row.get("pdbid"))
        if not any([missing_origin_seq, missing_sup_seq, missing_origin_ss, missing_sup_ss, missing_pdbid]):
            continue
        out.append(
            {
                "PMID": row.get("PMID", ""),
                "ENSURE_ID": row.get("ENSURE_ID", ""),
                "Index": row.get("Index", ""),
                "Related_disease": row.get("Related_disease", ""),
                "sup-tRNA_gene": row.get("sup-tRNA_gene", ""),
                "missing_origin_seq": int(missing_origin_seq),
                "missing_sup_seq": int(missing_sup_seq),
                "missing_origin_ss": int(missing_origin_ss),
                "missing_sup_ss": int(missing_sup_ss),
                "missing_pdbid": int(missing_pdbid),
                "origin_seq": row.get("Sequence_of_origin_tRNA", ""),
                "sup_seq": row.get("Sequence_of_sup-tRNA", ""),
            }
        )
    out.sort(key=lambda item: (int(item["PMID"]) if str(item["PMID"]).isdigit() else 10**12, int(item["Index"]) if str(item["Index"]).isdigit() else 10**12, item["ENSURE_ID"]))
    write_tsv(
        ROW_GAP_REPORT,
        out,
        [
            "PMID",
            "ENSURE_ID",
            "Index",
            "Related_disease",
            "sup-tRNA_gene",
            "missing_origin_seq",
            "missing_sup_seq",
            "missing_origin_ss",
            "missing_sup_ss",
            "missing_pdbid",
            "origin_seq",
            "sup_seq",
        ],
    )


def refresh_field_gap_report(rows: list[dict[str, str]]) -> None:
    manifest_rows = list(csv.DictReader(MANIFEST.open(encoding="utf-8"), delimiter="\t"))
    title_by_pmid = {row.get("PMID", ""): row.get("title", "") for row in manifest_rows}
    by_pmid: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_pmid[str(row.get("PMID", "")).strip()].append(row)

    out = []
    for pmid, pmid_rows in by_pmid.items():
        counts = {
            field: sum(1 for item in pmid_rows if is_blank(item.get(field)))
            for field in HIGH_VALUE_FIELDS
        }
        if not any(counts.values()):
            continue
        out.append(
            {
                "PMID": pmid,
                "row_count": len(pmid_rows),
                "title": title_by_pmid.get(pmid, ""),
                "missing_pdbid": counts["pdbid"],
                "missing_origin_secondary_structure": counts["Secondary structure"],
                "missing_sup_secondary_structure": counts["Secondary structure of sup-trna"],
                "missing_origin_sequence": counts["Sequence_of_origin_tRNA"],
                "missing_sup_sequence": counts["Sequence_of_sup-tRNA"],
            }
        )
    out.sort(key=lambda item: int(item["PMID"]) if str(item["PMID"]).isdigit() else 10**12)
    write_tsv(
        FIELD_GAP_REPORT,
        out,
        [
            "PMID",
            "row_count",
            "title",
            "missing_pdbid",
            "missing_origin_secondary_structure",
            "missing_sup_secondary_structure",
            "missing_origin_sequence",
            "missing_sup_sequence",
        ],
    )


def main() -> int:
    snapshot, rows = export_live_table()
    refresh_manifest(rows)
    refresh_row_gap_report(rows)
    refresh_field_gap_report(rows)
    print(snapshot)
    print(f"rows {len(rows)}")
    print(MANIFEST)
    print(ROW_GAP_REPORT)
    print(FIELD_GAP_REPORT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
