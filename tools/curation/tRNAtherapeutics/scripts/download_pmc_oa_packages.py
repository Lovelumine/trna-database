#!/usr/bin/env python3
"""Download PMC Open Access packages and replace false PMC challenge files.

PMC binary endpoints now often return a small "Preparing to download" HTML
challenge page. The OA package service is the reliable route for articles that
are in the PMC Open Access subset.
"""

from __future__ import annotations

import csv
import gzip
import os
import re
import shutil
import subprocess
import tarfile
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "field-curation-workdir" / "full_tRNAtherapeutics"
MANIFEST = BASE / "paper_manifest.tsv"
OA_DIR = BASE / "oa_packages"
EXTRACTED = OA_DIR / "extracted"
SUPP = BASE / "supplementary"
PAPERS = BASE / "papers"
REPORT = BASE / "reports" / "oa_package_download_report.tsv"
INVALID_DIR = BASE / "invalid_downloads_pmc_challenge"

USER_AGENT = "ensure-trna-curation/1.0"


def fetch_text(url: str, timeout: int = 45) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            time.sleep(1 + attempt)
    raise RuntimeError(str(last_error))


def download(url: str, dest: Path, timeout: int = 180) -> tuple[bool, str, int]:
    dest.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [
            "curl",
            "-L",
            "--fail",
            "--retry",
            "3",
            "--connect-timeout",
            "30",
            "--speed-time",
            "90",
            "--speed-limit",
            "1024",
            "-A",
            USER_AGENT,
            "-C",
            "-",
            "-o",
            str(dest),
            url,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return False, proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else f"curl exit {proc.returncode}", 0
    return True, "", dest.stat().st_size


def normalize_ftp_url(url: str) -> str:
    if url.startswith("ftp://ftp.ncbi.nlm.nih.gov/"):
        path = url[len("ftp://ftp.ncbi.nlm.nih.gov/") :]
        if path.startswith("pub/pmc/oa_package/"):
            path = path.replace("pub/pmc/oa_package/", "pub/pmc/deprecated/oa_package/", 1)
        return "https://ftp.ncbi.nlm.nih.gov/" + path
    return url


def get_oa_tgz_url(pmcid: str) -> tuple[str, str]:
    url = f"https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id={pmcid}"
    try:
        text = fetch_text(url)
    except Exception as exc:  # noqa: BLE001
        return "", f"oa_service_failed: {exc}"
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        return "", "oa_xml_parse_failed"
    error = root.find(".//error")
    if error is not None:
        return "", f"{error.attrib.get('code', 'oa_error')}: {''.join(error.itertext()).strip()}"
    for link in root.findall(".//link"):
        if (link.attrib.get("format") or "").lower() == "tgz":
            return normalize_ftp_url(link.attrib.get("href", "")), ""
    return "", "no_tgz_link"


def looks_like_challenge(path: Path) -> bool:
    if not path.exists() or path.stat().st_size > 4096:
        return False
    head = path.read_text(encoding="utf-8", errors="ignore")[:1000].lower()
    return "preparing to download" in head or "pow_challenge" in head or "cloudpmc-viewer-pow" in head


def quarantine_challenge_files() -> int:
    count = 0
    for base in [SUPP, PAPERS]:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            if looks_like_challenge(path):
                rel = path.relative_to(BASE)
                dest = INVALID_DIR / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                if dest.exists():
                    dest.unlink()
                shutil.move(str(path), str(dest))
                count += 1
    return count


def safe_copy(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        dest.unlink()
    shutil.copy2(src, dest)


def classify_member(name: str) -> str:
    lower = name.lower()
    filename = Path(name).name
    if lower.endswith((".nxml", ".xml")):
        return "xml"
    if lower.endswith(".pdf") and not re.search(r"supp|suppl|moesm|si|appendix|table|data|dataset|mmc", filename, re.I):
        return "paper_pdf"
    if re.search(r"supp|suppl|moesm|si|appendix|table|data|dataset|mmc|additional|source", filename, re.I):
        return "supplement"
    if lower.endswith((".xlsx", ".xls", ".csv", ".tsv", ".doc", ".docx", ".ppt", ".pptx", ".zip", ".gz", ".txt")):
        return "supplement"
    return "other"


def extract_and_copy(pmid: str, pmcid: str, tgz_path: Path) -> tuple[int, int, int]:
    out_dir = EXTRACTED / f"{pmid}_{pmcid}"
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    with tarfile.open(tgz_path, "r:gz") as tf:
        tf.extractall(out_dir)

    paper_files = 0
    supp_files = 0
    other_files = 0
    for src in out_dir.rglob("*"):
        if not src.is_file():
            continue
        kind = classify_member(src.name)
        if kind == "xml":
            safe_copy(src, PAPERS / pmid / f"{pmid}_{pmcid}_oa{src.suffix}")
            paper_files += 1
        elif kind == "paper_pdf":
            safe_copy(src, PAPERS / pmid / f"{pmid}_{pmcid}_oa.pdf")
            paper_files += 1
        elif kind == "supplement":
            safe_copy(src, SUPP / pmid / src.name)
            supp_files += 1
        else:
            other_files += 1
    return paper_files, supp_files, other_files


def main() -> int:
    OA_DIR.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(MANIFEST.open(encoding="utf-8"), delimiter="\t"))
    quarantined = quarantine_challenge_files()
    report_rows = []
    for row in rows:
        pmid = row["PMID"]
        pmcid = row["pmcid"]
        if not pmcid:
            report_rows.append(
                {
                    "PMID": pmid,
                    "PMCID": pmcid,
                    "status": "no_pmcid",
                    "tgz_url": "",
                    "tgz_path": "",
                    "paper_files": 0,
                    "supplement_files": 0,
                    "other_files": 0,
                    "error": "No PMCID in PubMed metadata",
                }
            )
            continue
        tgz_url, err = get_oa_tgz_url(pmcid)
        if not tgz_url:
            report_rows.append(
                {
                    "PMID": pmid,
                    "PMCID": pmcid,
                    "status": "not_in_oa_subset",
                    "tgz_url": "",
                    "tgz_path": "",
                    "paper_files": 0,
                    "supplement_files": 0,
                    "other_files": 0,
                    "error": err,
                }
            )
            time.sleep(0.2)
            continue
        tgz_path = OA_DIR / f"{pmid}_{pmcid}.tar.gz"
        if not tgz_path.exists() or tgz_path.stat().st_size == 0:
            ok, error, _ = download(tgz_url, tgz_path)
            if not ok:
                report_rows.append(
                    {
                        "PMID": pmid,
                        "PMCID": pmcid,
                        "status": "download_failed",
                        "tgz_url": tgz_url,
                        "tgz_path": "",
                        "paper_files": 0,
                        "supplement_files": 0,
                        "other_files": 0,
                        "error": error,
                    }
                )
                time.sleep(0.2)
                continue
        try:
            with gzip.open(tgz_path, "rb") as fh:
                fh.read(2)
            paper_files, supp_files, other_files = extract_and_copy(pmid, pmcid, tgz_path)
            status = "oa_package_downloaded"
            error = ""
        except Exception as exc:  # noqa: BLE001
            paper_files, supp_files, other_files = 0, 0, 0
            status = "extract_failed"
            error = str(exc)
        report_rows.append(
            {
                "PMID": pmid,
                "PMCID": pmcid,
                "status": status,
                "tgz_url": tgz_url,
                "tgz_path": str(tgz_path.relative_to(ROOT)),
                "paper_files": paper_files,
                "supplement_files": supp_files,
                "other_files": other_files,
                "error": error,
            }
        )
        time.sleep(0.2)

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    with REPORT.open("w", encoding="utf-8", newline="") as fh:
        fieldnames = [
            "PMID",
            "PMCID",
            "status",
            "tgz_url",
            "tgz_path",
            "paper_files",
            "supplement_files",
            "other_files",
            "error",
        ]
        writer = csv.DictWriter(fh, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(report_rows)
    print(f"Quarantined challenge files: {quarantined}")
    print(f"Wrote {REPORT.relative_to(ROOT)}")
    print(f"OA downloaded: {sum(1 for r in report_rows if r['status'] == 'oa_package_downloaded')}")
    print(f"Not OA subset: {sum(1 for r in report_rows if r['status'] == 'not_in_oa_subset')}")
    print(f"No PMCID: {sum(1 for r in report_rows if r['status'] == 'no_pmcid')}")
    print(f"Supp files copied: {sum(int(r['supplement_files']) for r in report_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
