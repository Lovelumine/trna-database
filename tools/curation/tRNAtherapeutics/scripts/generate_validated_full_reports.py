#!/usr/bin/env python3
"""Generate validated curation reports after PMC/OA downloads."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "field-curation-workdir" / "full_tRNAtherapeutics"
MANIFEST = BASE / "paper_manifest.tsv"
OA_REPORT = BASE / "reports" / "oa_package_download_report.tsv"
NOTES = BASE / "notes"
REPORTS = BASE / "reports"
PAPERS = BASE / "papers"
SUPP = BASE / "supplementary"
INVALID = BASE / "invalid_downloads_pmc_challenge"


def read_tsv(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.open(encoding="utf-8"), delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def pubmed_link(pmid: str) -> str:
    return f"[PMID {pmid}](<https://pubmed.ncbi.nlm.nih.gov/{pmid}/>)"


def doi_link(doi: object) -> str:
    doi_text = str(doi or "").strip()
    if not doi_text:
        return "Not found"
    return f"[{doi_text}](<https://doi.org/{doi_text}>)"


def pmc_link(pmcid: object) -> str:
    pmcid_text = str(pmcid or "").strip()
    if not pmcid_text:
        return "Not found"
    return f"[{pmcid_text}](<https://pmc.ncbi.nlm.nih.gov/articles/{pmcid_text}/>)"


def local_report_link(label: str, relative_path: str) -> str:
    return f"[{label}]({relative_path})"


def valid_supp_files(pmid: str) -> list[Path]:
    folder = SUPP / pmid
    if not folder.exists():
        return []
    files = []
    for path in sorted(folder.iterdir()):
        if path.is_file() and path.name != "urls.txt":
            files.append(path)
    return files


def valid_paper_files(pmid: str) -> list[Path]:
    folder = PAPERS / pmid
    if not folder.exists():
        return []
    return sorted(
        path
        for path in folder.iterdir()
        if path.is_file()
        and (
            path.name.endswith("_oa.pdf")
            or path.name.endswith("_oa.nxml")
            or path.name.endswith("_oa.xml")
            or path.name.endswith(".html")
            or path.name.endswith("_pubmed.xml")
        )
    )


def source_status(row: dict[str, str], oa: dict[str, str]) -> str:
    if oa.get("status") == "oa_package_downloaded":
        return "pmc_oa_package_fulltext"
    if row.get("pmcid") and row.get("pmc_html"):
        return "pmc_html_fulltext_no_oa_package"
    if row.get("doi_landing"):
        return "doi_landing_only_no_verified_fulltext"
    return "pubmed_only_manual_fulltext_needed"


def manual_reasons(row: dict[str, str], oa: dict[str, str], supp_count: int) -> list[str]:
    reasons: list[str] = []
    if not row.get("pmcid"):
        reasons.append("No PMCID; full text PDF/HTML and supplementary files were not automatically obtained.")
    elif oa.get("status") == "not_in_oa_subset":
        reasons.append("PMC HTML/XML was downloaded, but the article is not in the PMC Open Access package subset; PDF/supplement binaries need manual confirmation if required.")
    elif oa.get("status") not in {"oa_package_downloaded", ""}:
        reasons.append(f"OA package status: {oa.get('status')} {oa.get('error', '')}".strip())
    if row.get("pmcid") and supp_count == 0:
        reasons.append("No valid supplementary files found after PMC/OA package pass; manually confirm whether the article has no supplements.")
    for key, label in [
        ("missing_pdbid", "pdbid"),
        ("missing_origin_secondary_structure", "origin secondary structure"),
        ("missing_sup_secondary_structure", "suppressor secondary structure"),
        ("missing_origin_sequence", "origin tRNA sequence"),
        ("missing_sup_sequence", "suppressor tRNA sequence"),
    ]:
        try:
            value = int(row.get(key) or 0)
        except ValueError:
            value = 0
        if value:
            reasons.append(f"Database has {value} row(s) missing {label}.")
    return reasons


def main() -> int:
    rows = read_tsv(MANIFEST)
    oa_rows = {row["PMID"]: row for row in read_tsv(OA_REPORT)}
    validated_rows: list[dict[str, object]] = []
    supp_inventory: list[dict[str, object]] = []
    field_gap_rows: list[dict[str, object]] = []

    for row in rows:
        pmid = row["PMID"]
        oa = oa_rows.get(pmid, {})
        supp_files = valid_supp_files(pmid)
        paper_files = valid_paper_files(pmid)
        status = source_status(row, oa)
        reasons = manual_reasons(row, oa, len(supp_files))
        validated_rows.append(
            {
                "PMID": pmid,
                "row_count": row["row_count"],
                "year": row["year"],
                "title": row["title"],
                "doi": row["doi"],
                "pmcid": row["pmcid"],
                "source_status": status,
                "oa_package_status": oa.get("status", ""),
                "valid_paper_files": len(paper_files),
                "valid_supplementary_files": len(supp_files),
                "missing_pdbid": row["missing_pdbid"],
                "missing_origin_secondary_structure": row["missing_origin_secondary_structure"],
                "missing_sup_secondary_structure": row["missing_sup_secondary_structure"],
                "missing_origin_sequence": row["missing_origin_sequence"],
                "missing_sup_sequence": row["missing_sup_sequence"],
                "manual_reasons": " | ".join(reasons),
            }
        )
        for path in supp_files:
            supp_inventory.append(
                {
                    "PMID": pmid,
                    "filename": path.name,
                    "bytes": path.stat().st_size,
                    "path": rel(path),
                }
            )
        gap_keys = [
            "missing_pdbid",
            "missing_origin_secondary_structure",
            "missing_sup_secondary_structure",
            "missing_origin_sequence",
            "missing_sup_sequence",
        ]
        if any(int(row.get(key) or 0) for key in gap_keys):
            field_gap_rows.append(
                {
                    "PMID": pmid,
                    "row_count": row["row_count"],
                    "title": row["title"],
                    **{key: row[key] for key in gap_keys},
                }
            )

    write_tsv(
        BASE / "paper_manifest_validated.tsv",
        validated_rows,
        [
            "PMID",
            "row_count",
            "year",
            "title",
            "doi",
            "pmcid",
            "source_status",
            "oa_package_status",
            "valid_paper_files",
            "valid_supplementary_files",
            "missing_pdbid",
            "missing_origin_secondary_structure",
            "missing_sup_secondary_structure",
            "missing_origin_sequence",
            "missing_sup_sequence",
            "manual_reasons",
        ],
    )
    write_tsv(BASE / "supplementary_inventory_validated.tsv", supp_inventory, ["PMID", "filename", "bytes", "path"])
    write_tsv(
        BASE / "field_gap_report.tsv",
        field_gap_rows,
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

    status_counts = Counter(row["source_status"] for row in validated_rows)
    oa_counts = Counter(row["oa_package_status"] for row in validated_rows)
    total_supp = sum(int(row["valid_supplementary_files"]) for row in validated_rows)
    invalid_count = sum(1 for path in INVALID.rglob("*") if path.is_file()) if INVALID.exists() else 0
    rows_total = sum(int(row["row_count"]) for row in validated_rows)
    pmids_manual_fulltext = [
        row for row in validated_rows if row["source_status"] in {"doi_landing_only_no_verified_fulltext", "pubmed_only_manual_fulltext_needed"}
    ]
    pmids_supp_check = [row for row in validated_rows if int(row["valid_supplementary_files"]) == 0]
    pmids_field_gaps = [row for row in validated_rows if any(int(row[key] or 0) for key in ["missing_pdbid", "missing_origin_secondary_structure", "missing_sup_secondary_structure", "missing_origin_sequence", "missing_sup_sequence"])]

    lines = [
        "# tRNAtherapeutics 全量整理状态",
        "",
        "范围：`Engineered_sup_tRNA` 整张表。",
        "",
        "## 总览",
        "",
        f"- 数据库行数：{rows_total}",
        f"- PMID 数：{len(validated_rows)}",
        f"- 已验证真实 supplementary 文件：{total_supp}",
        f"- 已隔离 PMC challenge 假下载文件：{invalid_count}",
        "",
        "## 全文/来源状态",
        "",
    ]
    for key, count in sorted(status_counts.items()):
        lines.append(f"- `{key}`：{count} 篇")
    lines.extend(["", "## OA Package 状态", ""])
    for key, count in sorted(oa_counts.items()):
        lines.append(f"- `{key or 'n/a'}`：{count} 篇")
    lines.extend(
        [
            "",
            "## 需要用户帮忙下载全文的 PMID",
            "",
            "这些文章没有 PMCID，或只保存到 DOI landing page，未得到可验证全文 PDF/HTML。",
            "",
        ]
    )
    if pmids_manual_fulltext:
        lines.append("| PMID | Rows | DOI | Title |")
        lines.append("| --- | ---: | --- | --- |")
        for row in pmids_manual_fulltext:
            lines.append(f"| {row['PMID']} | {row['row_count']} | {row['doi']} | {row['title']} |")
    else:
        lines.append("- 无。")
    lines.extend(
        [
            "",
            "## 需要人工确认 supplementary 的 PMID",
            "",
            "这些文章没有找到有效 supplementary 文件。老文章可能本来没有补充数据；如果有，需人工下载后放入对应 PMID 目录。",
            "",
        ]
    )
    if pmids_supp_check:
        lines.append("| PMID | Source status | PMCID | Title |")
        lines.append("| --- | --- | --- | --- |")
        for row in pmids_supp_check:
            lines.append(f"| {row['PMID']} | {row['source_status']} | {row['pmcid']} | {row['title']} |")
    else:
        lines.append("- 无。")
    lines.extend(
        [
            "",
            "## 数据库缺失字段 PMID",
            "",
            "| PMID | Rows | missing pdbid | missing origin SS | missing sup SS | missing origin seq | missing sup seq |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in pmids_field_gaps:
        lines.append(
            f"| {row['PMID']} | {row['row_count']} | {row['missing_pdbid']} | {row['missing_origin_secondary_structure']} | {row['missing_sup_secondary_structure']} | {row['missing_origin_sequence']} | {row['missing_sup_sequence']} |"
        )
    lines.extend(
        [
            "",
            "## 生成文件",
            "",
            "- `field-curation-workdir/full_tRNAtherapeutics/paper_manifest_validated.tsv`",
            "- `field-curation-workdir/full_tRNAtherapeutics/supplementary_inventory_validated.tsv`",
            "- `field-curation-workdir/full_tRNAtherapeutics/field_gap_report.tsv`",
            "- `field-curation-workdir/full_tRNAtherapeutics/reports/manual_action_required_validated.md`",
            "- 每篇 PMID 的说明：`field-curation-workdir/full_tRNAtherapeutics/notes/{PMID}.md`",
            "",
        ]
    )
    (REPORTS / "tRNAtherapeutics_full_curation_status_validated.md").write_text("\n".join(lines), encoding="utf-8")

    manual = [
        "# 需要人工处理的论文和补充数据",
        "",
        "这里不包含已经拿到 PMC HTML/XML 的普通 DOI 403 问题，只列真正影响全文/附件证据链的事项。",
        "",
        "## 需要人工下载全文",
        "",
    ]
    if pmids_manual_fulltext:
        for row in pmids_manual_fulltext:
            pmid = str(row["PMID"])
            manual.extend(
                [
                    f"### {pubmed_link(pmid)}",
                    "",
                    f"- Title: {row['title']}",
                    f"- DOI: {doi_link(row['doi'])}",
                    f"- PubMed: {pubmed_link(pmid)}",
                    f"- Rows: {row['row_count']}",
                    f"- Current status: {row['source_status']}",
                    f"- Local note: {local_report_link(f'{pmid}.md', f'../notes/{pmid}.md')}",
                    f"- Local paper folder: {local_report_link('papers', f'../papers/{pmid}/')}",
                    f"- Local supplementary folder: {local_report_link('supplementary', f'../supplementary/{pmid}/')}",
                    "",
                ]
            )
    else:
        manual.append("- 无。")
    manual.extend(["", "## 需要人工确认是否有 supplementary", ""])
    for row in pmids_supp_check:
        pmid = str(row["PMID"])
        manual.extend(
            [
                f"### {pubmed_link(pmid)}",
                "",
                f"- Title: {row['title']}",
                f"- DOI: {doi_link(row['doi'])}",
                f"- PMCID: {pmc_link(row['pmcid'])}",
                f"- PubMed: {pubmed_link(pmid)}",
                f"- Status: {row['source_status']}",
                f"- Reason: no valid supplementary file after automated PMC/OA pass.",
                f"- Local note: {local_report_link(f'{pmid}.md', f'../notes/{pmid}.md')}",
                f"- Local paper folder: {local_report_link('papers', f'../papers/{pmid}/')}",
                f"- Local supplementary folder: {local_report_link('supplementary', f'../supplementary/{pmid}/')}",
                "",
            ]
        )
    (REPORTS / "manual_action_required_validated.md").write_text("\n".join(manual), encoding="utf-8")

    for row in validated_rows:
        pmid = str(row["PMID"])
        paper_files = valid_paper_files(pmid)
        supp_files = valid_supp_files(pmid)
        note = [
            f"# PMID {pmid}",
            "",
            f"- Title: {row['title']}",
            f"- Year: {row['year']}",
            f"- DOI: {row['doi'] or 'Not found'}",
            f"- PMCID: {row['pmcid'] or 'Not found'}",
            f"- Database rows: {row['row_count']}",
            f"- Source status: `{row['source_status']}`",
            f"- OA package status: `{row['oa_package_status'] or 'n/a'}`",
            "",
            "## Source Links",
            "",
            f"- PubMed: https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            f"- DOI: {('https://doi.org/' + row['doi']) if row['doi'] else 'Not found'}",
            f"- PMC: {('https://pmc.ncbi.nlm.nih.gov/articles/' + row['pmcid'] + '/') if row['pmcid'] else 'Not found'}",
            "",
            "## Verified Paper Files",
            "",
        ]
        if paper_files:
            for path in paper_files:
                note.append(f"- `{rel(path)}` ({path.stat().st_size} bytes)")
        else:
            note.append("- No verified full-text file beyond PubMed XML was downloaded.")
        note.extend(["", "## Verified Supplementary Files", ""])
        if supp_files:
            for path in supp_files:
                note.append(f"- `{rel(path)}` ({path.stat().st_size} bytes)")
        else:
            note.append("- No valid supplementary file downloaded automatically.")
        note.extend(["", "## Database Gaps / Manual Tasks", ""])
        reasons = str(row["manual_reasons"])
        if reasons:
            for reason in reasons.split(" | "):
                note.append(f"- {reason}")
        else:
            note.append("- No source-access blocker or high-priority structural field gap detected in this pass.")
        note.append("")
        (NOTES / f"{pmid}.md").write_text("\n".join(note), encoding="utf-8")

    print(f"Wrote {REPORTS / 'tRNAtherapeutics_full_curation_status_validated.md'}")
    print(f"Validated supplementary files: {total_supp}")
    print(f"Manual fulltext PMIDs: {len(pmids_manual_fulltext)}")
    print(f"Supplement check PMIDs: {len(pmids_supp_check)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
