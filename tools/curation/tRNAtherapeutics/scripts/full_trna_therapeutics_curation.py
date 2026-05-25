#!/usr/bin/env python3
"""Build a full evidence/download manifest for Engineered_sup_tRNA.

The script intentionally separates evidence collection from DB mutation.
It exports the live table, fetches PubMed metadata, downloads accessible
PMC/DOI materials, records failures, and writes one Markdown note per PMID.
"""

from __future__ import annotations

import csv
import html
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "field-curation-workdir" / "full_tRNAtherapeutics"
SNAPSHOTS = OUT / "snapshots"
PAPERS = OUT / "papers"
SUPP = OUT / "supplementary"
NOTES = OUT / "notes"
REPORTS = OUT / "reports"
METADATA = OUT / "metadata"
EXISTING = ROOT / "field-curation-workdir"

TABLE = "Engineered_sup_tRNA"
NCBI_TOOL = "ensure-trna-curation"
NCBI_EMAIL = os.environ.get("NCBI_EMAIL", "curation@example.com")


FIELD_NAMES = [
    "Index",
    "Related_disease",
    "PTC_gene",
    "Species_source_of_PTC_gene",
    "NCBI_ref_ID",
    "PTC(mutation_site)",
    "PTC_site",
    "Origin_aa_and_codon_of_PTC_site",
    "PTC_codon",
    "Delivery_as_vector_or_IVT_tRNA",
    "aa_and_anticodon_of_origin_tRNA",
    "aa_and_anticodon_of_sup-tRNA",
    "rnacentral_ID_of_origin_tRNA",
    "tRNAscan-SE_ID_of_origin_tRNA",
    "Species_source_of_origin_tRNA",
    "ENSURE_ID",
    "Sequence_of_origin_tRNA",
    "Sequence_of_sup-tRNA",
    "sup-tRNA_gene",
    "Modification",
    "Engineered_aaRS",
    "Reading_through_efficiency",
    "Measuring_of_efficiency",
    "Reaction_system",
    "Safety",
    "PMID",
    "Secondary structure",
    "Secondary structure of sup-trna",
    "js_origin_tRNA",
    "js_sup_tRNA",
    "pdbid",
]

HIGH_VALUE_FIELDS = [
    "Related_disease",
    "PTC_gene",
    "PTC(mutation_site)",
    "PTC_codon",
    "Delivery_as_vector_or_IVT_tRNA",
    "aa_and_anticodon_of_origin_tRNA",
    "aa_and_anticodon_of_sup-tRNA",
    "Species_source_of_origin_tRNA",
    "Sequence_of_origin_tRNA",
    "Sequence_of_sup-tRNA",
    "sup-tRNA_gene",
    "Modification",
    "Reading_through_efficiency",
    "Measuring_of_efficiency",
    "Reaction_system",
    "Safety",
    "Secondary structure",
    "Secondary structure of sup-trna",
    "js_origin_tRNA",
    "js_sup_tRNA",
    "pdbid",
]


@dataclass
class DownloadResult:
    status: str = "not_attempted"
    url: str = ""
    path: str = ""
    content_type: str = ""
    size: int = 0
    error: str = ""


@dataclass
class PaperMeta:
    pmid: str
    title: str = ""
    journal: str = ""
    year: str = ""
    doi: str = ""
    pmcid: str = ""
    pubmed_url: str = ""
    doi_url: str = ""
    row_count: int = 0
    min_ensure_id: str = ""
    max_ensure_id: str = ""
    field_missing_counts: dict[str, int] = field(default_factory=dict)
    local_existing_files: list[str] = field(default_factory=list)
    pubmed_xml: DownloadResult = field(default_factory=DownloadResult)
    pmc_html: DownloadResult = field(default_factory=DownloadResult)
    pmc_xml: DownloadResult = field(default_factory=DownloadResult)
    pmc_pdf: DownloadResult = field(default_factory=DownloadResult)
    doi_landing: DownloadResult = field(default_factory=DownloadResult)
    supplementary_files: list[DownloadResult] = field(default_factory=list)
    manual_reasons: list[str] = field(default_factory=list)


def run(cmd: list[str], *, input_text: str | None = None) -> str:
    proc = subprocess.run(
        cmd,
        input=input_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=ROOT,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{proc.stderr}")
    return proc.stdout


def read_env_files() -> dict[str, str]:
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


def mysql_args(env: dict[str, str]) -> list[str]:
    return [
        "/usr/bin/mysql",
        "-h",
        env["MYSQL_HOST"],
        "-P",
        env.get("MYSQL_PORT") or "3306",
        "-u",
        env["MYSQL_USER"],
        env["MYSQL_DB"],
    ]


def export_table(env: dict[str, str], timestamp: str) -> list[dict[str, str]]:
    SNAPSHOTS.mkdir(parents=True, exist_ok=True)
    query = f"SELECT * FROM {TABLE};"
    cmd_env = os.environ.copy()
    cmd_env["MYSQL_PWD"] = env.get("MYSQL_PASSWORD", "")
    proc = subprocess.run(
        mysql_args(env) + ["-B", "-e", query],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=ROOT,
        env=cmd_env,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr)
    path = SNAPSHOTS / f"{TABLE}_{timestamp}.tsv"
    path.write_text(proc.stdout, encoding="utf-8")
    rows = list(csv.DictReader(proc.stdout.splitlines(), delimiter="\t"))
    return rows


def is_blank(value: str | None) -> bool:
    if value is None:
        return True
    text = str(value).strip()
    return text == "" or text.upper() == "NULL"


def normalize_pmid(value: str) -> str:
    return str(value or "").strip()


def text_from_element(elem: ET.Element | None) -> str:
    if elem is None:
        return ""
    return " ".join("".join(elem.itertext()).split())


def request_url(url: str, dest: Path, *, accept: str = "*/*", timeout: int = 45) -> DownloadResult:
    result = DownloadResult(url=url)
    headers = {
        "User-Agent": f"{NCBI_TOOL}/1.0 ({NCBI_EMAIL})",
        "Accept": accept,
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
            ctype = resp.headers.get("Content-Type", "")
            final_url = resp.geturl()
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        result.status = "downloaded"
        result.url = final_url
        result.path = str(dest.relative_to(ROOT))
        result.content_type = ctype
        result.size = len(data)
        if len(data) == 0:
            result.status = "empty"
    except urllib.error.HTTPError as exc:
        result.status = "http_error"
        result.error = f"HTTP {exc.code}: {exc.reason}"
    except urllib.error.URLError as exc:
        result.status = "url_error"
        result.error = str(exc.reason)
    except Exception as exc:  # noqa: BLE001
        result.status = "error"
        result.error = str(exc)
    return result


def fetch_pubmed_xml(pmids: list[str]) -> str:
    chunks: list[str] = []
    for i in range(0, len(pmids), 100):
        ids = ",".join(pmids[i : i + 100])
        params = urllib.parse.urlencode(
            {
                "db": "pubmed",
                "id": ids,
                "retmode": "xml",
                "tool": NCBI_TOOL,
                "email": NCBI_EMAIL,
            }
        )
        url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?{params}"
        with urllib.request.urlopen(
            urllib.request.Request(url, headers={"User-Agent": f"{NCBI_TOOL}/1.0"}),
            timeout=60,
        ) as resp:
            chunks.append(resp.read().decode("utf-8", errors="replace"))
        time.sleep(0.35)
    if len(chunks) == 1:
        return chunks[0]
    bodies = []
    for chunk in chunks:
        body = re.sub(r"^.*?<PubmedArticleSet[^>]*>", "", chunk, flags=re.S)
        body = re.sub(r"</PubmedArticleSet>.*$", "", body, flags=re.S)
        bodies.append(body.strip())
    return "<?xml version='1.0' encoding='UTF-8'?><PubmedArticleSet>" + "\n".join(bodies) + "</PubmedArticleSet>"


def parse_pubmed(xml_text: str) -> dict[str, PaperMeta]:
    metas: dict[str, PaperMeta] = {}
    root = ET.fromstring(xml_text)
    for article in root.findall(".//PubmedArticle"):
        pmid = text_from_element(article.find(".//MedlineCitation/PMID"))
        if not pmid:
            continue
        meta = PaperMeta(pmid=pmid)
        meta.pubmed_url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        meta.title = html.unescape(text_from_element(article.find(".//ArticleTitle")))
        meta.journal = html.unescape(text_from_element(article.find(".//Journal/Title")))
        year = text_from_element(article.find(".//JournalIssue/PubDate/Year"))
        if not year:
            medline = text_from_element(article.find(".//JournalIssue/PubDate/MedlineDate"))
            year_match = re.search(r"\b(19|20)\d{2}\b", medline)
            year = year_match.group(0) if year_match else ""
        meta.year = year
        for aid in article.findall(".//PubmedData/ArticleIdList/ArticleId"):
            id_type = (aid.attrib.get("IdType") or "").lower()
            value = text_from_element(aid)
            if id_type == "doi":
                meta.doi = value
                meta.doi_url = f"https://doi.org/{value}"
            elif id_type == "pmc":
                meta.pmcid = value if value.startswith("PMC") else f"PMC{value}"
        metas[pmid] = meta
    return metas


def discover_existing_files(pmid: str) -> list[str]:
    matches: list[Path] = []
    for sub in ["papers", "extractions", "notes"]:
        base = EXISTING / sub
        if not base.exists():
            continue
        matches.extend(base.rglob(f"{pmid}*"))
        matches.extend(base.rglob(f"*{pmid}*"))
    unique = sorted({p for p in matches if p.is_file()})
    return [str(p.relative_to(ROOT)) for p in unique]


SUPP_EXT_RE = re.compile(
    r"""(?i)\b(?:href|src)=["']([^"']+(?:supp|suppl|supplement|MOESM|SD|Dataset|Data|Table|Appendix|media)[^"']*)["']"""
)
BIN_RE = re.compile(r"""(?i)\b(?:href|src)=["']([^"']*/(?:bin|media)/[^"']+)["']""")
FILE_EXT_RE = re.compile(r"(?i)\.(?:pdf|xlsx?|csv|tsv|txt|docx?|pptx?|zip|gz|tar|fasta|fa|xml)(?:[?#].*)?$")
XLINK = "{http://www.w3.org/1999/xlink}href"


def clean_url(base_url: str, href: str) -> str:
    href = html.unescape(href).strip()
    return urllib.parse.urljoin(base_url, href)


def discover_supplement_urls(pmcid: str, html_text: str, xml_text: str) -> list[str]:
    base = f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/"
    urls: set[str] = set()
    for text in [html_text, xml_text]:
        for regex in [SUPP_EXT_RE, BIN_RE]:
            for match in regex.finditer(text or ""):
                href = match.group(1)
                if FILE_EXT_RE.search(href) or "/bin/" in href or "/media/" in href:
                    urls.add(clean_url(base, href))
    if xml_text.strip():
        try:
            root = ET.fromstring(xml_text)
            for elem in root.iter():
                for attr_name, attr_value in elem.attrib.items():
                    if attr_name == XLINK or attr_name.endswith("href"):
                        href = attr_value
                        if FILE_EXT_RE.search(href) or "sup" in href.lower() or "MOESM" in href:
                            urls.add(clean_url(base, href))
        except ET.ParseError:
            pass
    return sorted(urls)


def safe_filename_from_url(url: str, fallback: str) -> str:
    path = urllib.parse.urlparse(url).path
    name = Path(path).name or fallback
    name = re.sub(r"[^A-Za-z0-9._+-]+", "_", name)
    return name[:180] or fallback


def download_for_meta(meta: PaperMeta) -> None:
    pmid = meta.pmid
    pmid_dir = PAPERS / pmid
    supp_dir = SUPP / pmid

    meta.pubmed_xml = request_url(
        f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=xml&tool={NCBI_TOOL}&email={urllib.parse.quote(NCBI_EMAIL)}",
        pmid_dir / f"{pmid}_pubmed.xml",
        accept="application/xml,text/xml",
    )
    time.sleep(0.2)

    html_text = ""
    xml_text = ""
    if meta.pmcid:
        meta.pmc_html = request_url(
            f"https://pmc.ncbi.nlm.nih.gov/articles/{meta.pmcid}/",
            pmid_dir / f"{pmid}_{meta.pmcid}.html",
            accept="text/html",
        )
        if meta.pmc_html.status == "downloaded" and meta.pmc_html.path:
            html_text = (ROOT / meta.pmc_html.path).read_text(encoding="utf-8", errors="ignore")
        time.sleep(0.2)

        meta.pmc_xml = request_url(
            f"https://pmc.ncbi.nlm.nih.gov/articles/{meta.pmcid}/?report=xml",
            pmid_dir / f"{pmid}_{meta.pmcid}.xml",
            accept="application/xml,text/xml,text/html",
        )
        if meta.pmc_xml.status == "downloaded" and meta.pmc_xml.path:
            xml_text = (ROOT / meta.pmc_xml.path).read_text(encoding="utf-8", errors="ignore")
        time.sleep(0.2)

        pdf = request_url(
            f"https://pmc.ncbi.nlm.nih.gov/articles/{meta.pmcid}/pdf/",
            pmid_dir / f"{pmid}_{meta.pmcid}.pdf",
            accept="application/pdf,text/html",
        )
        if pdf.status == "downloaded" and pdf.path:
            pdf_path = ROOT / pdf.path
            header = pdf_path.read_bytes()[:5]
            if header != b"%PDF-":
                pdf.status = "not_pdf"
                pdf.error = "PMC PDF endpoint did not return a PDF file"
        meta.pmc_pdf = pdf
        time.sleep(0.2)

        supp_urls = discover_supplement_urls(meta.pmcid, html_text, xml_text)
        for index, url in enumerate(supp_urls, start=1):
            filename = safe_filename_from_url(url, f"supplement_{index}")
            result = request_url(url, supp_dir / filename)
            if result.status == "downloaded" and result.size == 0:
                result.status = "empty"
            meta.supplementary_files.append(result)
            time.sleep(0.15)
    else:
        meta.manual_reasons.append("No PMCID in PubMed metadata; full text and supplements may require publisher access.")

    if meta.doi:
        meta.doi_landing = request_url(
            meta.doi_url,
            pmid_dir / f"{pmid}_doi_landing.html",
            accept="text/html,application/pdf",
        )
        if meta.doi_landing.status != "downloaded":
            meta.manual_reasons.append(f"DOI landing page download failed: {meta.doi_landing.error or meta.doi_landing.status}")
        time.sleep(0.2)
    else:
        meta.manual_reasons.append("No DOI found in PubMed metadata.")

    if meta.pmcid and meta.pmc_html.status != "downloaded":
        meta.manual_reasons.append(f"PMC HTML download failed: {meta.pmc_html.error or meta.pmc_html.status}")
    if meta.pmcid and meta.pmc_pdf.status not in {"downloaded", "not_pdf"}:
        meta.manual_reasons.append(f"PMC PDF download failed: {meta.pmc_pdf.error or meta.pmc_pdf.status}")
    if meta.pmcid and not meta.supplementary_files:
        meta.manual_reasons.append("No supplementary links were discovered automatically on the PMC page/XML.")


def summarize_rows(rows: list[dict[str, str]], metas: dict[str, PaperMeta]) -> None:
    by_pmid: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_pmid[normalize_pmid(row["PMID"])].append(row)
    for pmid, pmid_rows in by_pmid.items():
        meta = metas.setdefault(pmid, PaperMeta(pmid=pmid))
        meta.row_count = len(pmid_rows)
        ensure_ids = []
        for row in pmid_rows:
            value = row.get("ENSURE_ID", "")
            if value.isdigit():
                ensure_ids.append(int(value))
        if ensure_ids:
            meta.min_ensure_id = str(min(ensure_ids))
            meta.max_ensure_id = str(max(ensure_ids))
        counts: dict[str, int] = {}
        for field_name in HIGH_VALUE_FIELDS:
            counts[field_name] = sum(1 for row in pmid_rows if is_blank(row.get(field_name)))
        meta.field_missing_counts = counts
        meta.local_existing_files = discover_existing_files(pmid)


def copy_existing_41261131(meta: PaperMeta) -> None:
    """Preserve existing non-PMC Nature files in the full curation layout."""
    if meta.pmid != "41261131":
        return
    pmid_dir = PAPERS / meta.pmid
    pmid_dir.mkdir(parents=True, exist_ok=True)
    src_pdf = EXISTING / "papers" / "41261131_s41586-025-09732-2.pdf"
    if src_pdf.exists():
        dest = pmid_dir / src_pdf.name
        if not dest.exists():
            shutil.copy2(src_pdf, dest)
    src_supp = EXISTING / "papers" / "41261131_supplementary"
    if src_supp.exists():
        dest_dir = SUPP / meta.pmid
        dest_dir.mkdir(parents=True, exist_ok=True)
        for src in src_supp.iterdir():
            if src.is_file():
                dest = dest_dir / src.name
                if not dest.exists():
                    shutil.copy2(src, dest)


def status_for(meta: PaperMeta) -> str:
    if meta.pmc_html.status == "downloaded":
        return "pmc_downloaded"
    if meta.local_existing_files:
        return "local_existing"
    if meta.doi_landing.status == "downloaded":
        return "doi_landing_only"
    return "manual_required"


def write_manifest(metas: dict[str, PaperMeta]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "paper_manifest.tsv"
    columns = [
        "PMID",
        "row_count",
        "min_ensure_id",
        "max_ensure_id",
        "year",
        "journal",
        "title",
        "doi",
        "pmcid",
        "status",
        "pubmed_url",
        "doi_url",
        "pmc_html",
        "pmc_xml",
        "pmc_pdf",
        "supplementary_downloaded",
        "supplementary_attempted",
        "missing_pdbid",
        "missing_origin_secondary_structure",
        "missing_sup_secondary_structure",
        "missing_origin_sequence",
        "missing_sup_sequence",
        "manual_reasons",
    ]
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns, delimiter="\t")
        writer.writeheader()
        for pmid in sorted(metas, key=lambda x: int(x) if x.isdigit() else x):
            meta = metas[pmid]
            supp_downloaded = sum(1 for item in meta.supplementary_files if item.status == "downloaded")
            writer.writerow(
                {
                    "PMID": pmid,
                    "row_count": meta.row_count,
                    "min_ensure_id": meta.min_ensure_id,
                    "max_ensure_id": meta.max_ensure_id,
                    "year": meta.year,
                    "journal": meta.journal,
                    "title": meta.title,
                    "doi": meta.doi,
                    "pmcid": meta.pmcid,
                    "status": status_for(meta),
                    "pubmed_url": meta.pubmed_url,
                    "doi_url": meta.doi_url,
                    "pmc_html": meta.pmc_html.path,
                    "pmc_xml": meta.pmc_xml.path,
                    "pmc_pdf": meta.pmc_pdf.path if meta.pmc_pdf.status == "downloaded" else "",
                    "supplementary_downloaded": supp_downloaded,
                    "supplementary_attempted": len(meta.supplementary_files),
                    "missing_pdbid": meta.field_missing_counts.get("pdbid", 0),
                    "missing_origin_secondary_structure": meta.field_missing_counts.get("Secondary structure", 0),
                    "missing_sup_secondary_structure": meta.field_missing_counts.get("Secondary structure of sup-trna", 0),
                    "missing_origin_sequence": meta.field_missing_counts.get("Sequence_of_origin_tRNA", 0),
                    "missing_sup_sequence": meta.field_missing_counts.get("Sequence_of_sup-tRNA", 0),
                    "manual_reasons": " | ".join(meta.manual_reasons),
                }
            )


def md_link(path: str) -> str:
    return f"`{path}`" if path else ""


def write_pmid_notes(metas: dict[str, PaperMeta]) -> None:
    NOTES.mkdir(parents=True, exist_ok=True)
    for pmid in sorted(metas, key=lambda x: int(x) if x.isdigit() else x):
        meta = metas[pmid]
        supp_downloaded = [item for item in meta.supplementary_files if item.status == "downloaded"]
        missing = {k: v for k, v in meta.field_missing_counts.items() if v}
        lines = [
            f"# PMID {pmid}",
            "",
            f"- Title: {meta.title or 'Unknown'}",
            f"- Journal/year: {meta.journal or 'Unknown'}; {meta.year or 'Unknown'}",
            f"- DOI: {meta.doi or 'Not found'}",
            f"- PMCID: {meta.pmcid or 'Not found'}",
            f"- Database rows: {meta.row_count}",
            f"- ENSURE_ID range: {meta.min_ensure_id or 'n/a'}-{meta.max_ensure_id or 'n/a'}",
            "",
            "## Source Links",
            "",
            f"- PubMed: {meta.pubmed_url or 'Not found'}",
            f"- DOI: {meta.doi_url or 'Not found'}",
            f"- PMC: {f'https://pmc.ncbi.nlm.nih.gov/articles/{meta.pmcid}/' if meta.pmcid else 'Not found'}",
            "",
            "## Downloaded Files",
            "",
            f"- PubMed XML: {md_link(meta.pubmed_xml.path)} ({meta.pubmed_xml.status})",
            f"- PMC HTML: {md_link(meta.pmc_html.path)} ({meta.pmc_html.status})",
            f"- PMC XML: {md_link(meta.pmc_xml.path)} ({meta.pmc_xml.status})",
            f"- PMC PDF: {md_link(meta.pmc_pdf.path)} ({meta.pmc_pdf.status})",
            f"- DOI landing page: {md_link(meta.doi_landing.path)} ({meta.doi_landing.status})",
            "",
            "## Supplementary Files",
            "",
        ]
        if supp_downloaded:
            for item in supp_downloaded[:200]:
                lines.append(f"- {md_link(item.path)} ({item.size} bytes)")
        else:
            lines.append("- No supplementary files downloaded automatically.")
        failed = [item for item in meta.supplementary_files if item.status != "downloaded"]
        if failed:
            lines.extend(["", "Failed supplementary downloads:"])
            for item in failed[:100]:
                lines.append(f"- {item.url}: {item.status} {item.error}".rstrip())
        lines.extend(["", "## Existing Local Files From Earlier Work", ""])
        if meta.local_existing_files:
            for path in meta.local_existing_files:
                lines.append(f"- `{path}`")
        else:
            lines.append("- None found before this full pass.")
        lines.extend(["", "## Database Field Gaps", ""])
        if missing:
            for key, value in sorted(missing.items()):
                lines.append(f"- `{key}` missing in {value} row(s)")
        else:
            lines.append("- No high-value field gaps detected by blank-field scan.")
        lines.extend(["", "## Manual Follow-Up", ""])
        if meta.manual_reasons:
            for reason in meta.manual_reasons:
                lines.append(f"- {reason}")
        else:
            lines.append("- No manual access blocker detected in this pass.")
        lines.append("")
        (NOTES / f"{pmid}.md").write_text("\n".join(lines), encoding="utf-8")


def write_reports(metas: dict[str, PaperMeta], timestamp: str) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    status_counts = Counter(status_for(meta) for meta in metas.values())
    pmc_count = sum(1 for meta in metas.values() if meta.pmcid)
    total_supp = sum(sum(1 for item in meta.supplementary_files if item.status == "downloaded") for meta in metas.values())
    total_rows = sum(meta.row_count for meta in metas.values())
    field_gap_totals: dict[str, int] = defaultdict(int)
    for meta in metas.values():
        for key, value in meta.field_missing_counts.items():
            field_gap_totals[key] += value

    lines = [
        "# tRNAtherapeutics Full Curation Status",
        "",
        f"Generated: {timestamp}",
        "",
        "## Scope",
        "",
        f"- Table: `{TABLE}`",
        f"- Total rows: {total_rows}",
        f"- Unique PMIDs: {len(metas)}",
        "",
        "## Source Download Summary",
        "",
        f"- PMIDs with PMCID: {pmc_count}",
        f"- Supplementary files downloaded automatically: {total_supp}",
    ]
    for key, value in sorted(status_counts.items()):
        lines.append(f"- `{key}`: {value} PMID(s)")
    lines.extend(["", "## Field Gap Totals", ""])
    for key, value in sorted(field_gap_totals.items(), key=lambda kv: (-kv[1], kv[0])):
        if value:
            lines.append(f"- `{key}` missing in {value} row(s)")
    if all(value == 0 for value in field_gap_totals.values()):
        lines.append("- No missing high-value fields detected.")

    lines.extend(["", "## Manual Required PMIDs", ""])
    manual_metas = [meta for meta in metas.values() if status_for(meta) == "manual_required" or meta.manual_reasons]
    if manual_metas:
        lines.append("| PMID | Rows | DOI | PMCID | Reason |")
        lines.append("| --- | ---: | --- | --- | --- |")
        for meta in sorted(manual_metas, key=lambda m: int(m.pmid) if m.pmid.isdigit() else m.pmid):
            reason = "; ".join(meta.manual_reasons) or status_for(meta)
            lines.append(f"| {meta.pmid} | {meta.row_count} | {meta.doi or ''} | {meta.pmcid or ''} | {reason} |")
    else:
        lines.append("- None.")

    lines.extend(["", "## Per-PMID Notes", ""])
    lines.append("Each PMID has a note under `field-curation-workdir/full_tRNAtherapeutics/notes/`.")
    lines.append("")
    (REPORTS / "tRNAtherapeutics_full_curation_status.md").write_text("\n".join(lines), encoding="utf-8")

    manual_lines = [
        "# Manual Access / Manual Curation Required",
        "",
        f"Generated: {timestamp}",
        "",
    ]
    for meta in sorted(manual_metas, key=lambda m: int(m.pmid) if m.pmid.isdigit() else m.pmid):
        manual_lines.extend(
            [
                f"## PMID {meta.pmid}",
                "",
                f"- Title: {meta.title or 'Unknown'}",
                f"- DOI: {meta.doi or 'Not found'}",
                f"- PMCID: {meta.pmcid or 'Not found'}",
                f"- Rows: {meta.row_count}",
                f"- Note: `field-curation-workdir/full_tRNAtherapeutics/notes/{meta.pmid}.md`",
            ]
        )
        for reason in meta.manual_reasons:
            manual_lines.append(f"- Manual reason: {reason}")
        manual_lines.append("")
    (REPORTS / "manual_required.md").write_text("\n".join(manual_lines), encoding="utf-8")


def main() -> int:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    for path in [OUT, SNAPSHOTS, PAPERS, SUPP, NOTES, REPORTS, METADATA]:
        path.mkdir(parents=True, exist_ok=True)

    env = read_env_files()
    required = ["MYSQL_HOST", "MYSQL_USER", "MYSQL_DB"]
    missing = [key for key in required if not env.get(key)]
    if missing:
        raise RuntimeError(f"Missing DB env values: {', '.join(missing)}")

    rows = export_table(env, timestamp)
    pmids = sorted({normalize_pmid(row["PMID"]) for row in rows if normalize_pmid(row["PMID"])}, key=int)

    pubmed_xml = fetch_pubmed_xml(pmids)
    (METADATA / f"pubmed_efetch_{timestamp}.xml").write_text(pubmed_xml, encoding="utf-8")
    metas = parse_pubmed(pubmed_xml)
    summarize_rows(rows, metas)

    for pmid in pmids:
        meta = metas.setdefault(pmid, PaperMeta(pmid=pmid))
        copy_existing_41261131(meta)
        download_for_meta(meta)

    json_path = METADATA / f"paper_metadata_{timestamp}.json"
    serializable = {
        pmid: {
            "pmid": meta.pmid,
            "title": meta.title,
            "journal": meta.journal,
            "year": meta.year,
            "doi": meta.doi,
            "pmcid": meta.pmcid,
            "row_count": meta.row_count,
            "status": status_for(meta),
            "manual_reasons": meta.manual_reasons,
        }
        for pmid, meta in metas.items()
    }
    json_path.write_text(json.dumps(serializable, indent=2, ensure_ascii=False), encoding="utf-8")

    write_manifest(metas)
    write_pmid_notes(metas)
    write_reports(metas, timestamp)

    print(f"Wrote {OUT.relative_to(ROOT)}")
    print(f"PMIDs: {len(pmids)}")
    print(f"Rows: {len(rows)}")
    print(f"Manifest: {(OUT / 'paper_manifest.tsv').relative_to(ROOT)}")
    print(f"Report: {(REPORTS / 'tRNAtherapeutics_full_curation_status.md').relative_to(ROOT)}")
    print(f"Manual: {(REPORTS / 'manual_required.md').relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
