#!/usr/bin/env python3
"""Backup and apply PMID 9447966 curation SQL to the live database."""

from __future__ import annotations

import os
import re
import subprocess
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
BACKUPS = ROOT / "field-curation-workdir" / "full_tRNAtherapeutics" / "backups"
SQL_PATH = ROOT / "docs" / "curation" / "tRNAtherapeutics" / "sql" / "9447966_kondo_trp_updates.sql"
PMID = "9447966"
ENSURE_IDS = ["ensure-995", "ensure-996", "ensure-997", "ensure-998", "ensure-999"]


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


def mysql_base(env: dict[str, str]) -> tuple[list[str], dict[str, str]]:
    missing = [key for key in ["MYSQL_HOST", "MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_DB"] if key not in env]
    if missing:
        raise RuntimeError(f"Missing env keys: {', '.join(missing)}")
    cmd_env = os.environ.copy()
    cmd_env["MYSQL_PWD"] = env["MYSQL_PASSWORD"]
    return (
        [
            "/usr/bin/mysql",
            "-h",
            env["MYSQL_HOST"],
            "-P",
            env.get("MYSQL_PORT") or "3306",
            "-u",
            env["MYSQL_USER"],
            env["MYSQL_DB"],
        ],
        cmd_env,
    )


def run_mysql(base: list[str], cmd_env: dict[str, str], query: str | None = None, stdin: str | None = None) -> str:
    cmd = base if query is None else base + ["-B", "-e", query]
    proc = subprocess.run(
        cmd,
        cwd=ROOT,
        env=cmd_env,
        text=True,
        input=stdin,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr)
    return proc.stdout


def quoted_ids() -> str:
    return ",".join("'" + item.replace("'", "''") + "'" for item in ENSURE_IDS)


def main() -> None:
    env = read_env()
    base, cmd_env = mysql_base(env)
    BACKUPS.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_tsv = BACKUPS / f"Engineered_sup_tRNA_PMID9447966_before_{timestamp}.tsv"

    select_query = (
        f"SELECT * FROM Engineered_sup_tRNA "
        f"WHERE PMID='{PMID}' AND ENSURE_ID IN ({quoted_ids()}) "
        "ORDER BY `Index`;"
    )
    backup = run_mysql(base, cmd_env, query=select_query)
    row_count = max(0, len(backup.splitlines()) - 1)
    if row_count != len(ENSURE_IDS):
        raise RuntimeError(f"Expected {len(ENSURE_IDS)} backup rows, got {row_count}")
    backup_tsv.write_text(backup, encoding="utf-8")

    run_mysql(base, cmd_env, stdin=SQL_PATH.read_text(encoding="utf-8"))

    verify_query = (
        "SELECT ENSURE_ID, "
        "LENGTH(`Sequence_of_origin_tRNA`) AS origin_len, "
        "LENGTH(`Sequence_of_sup-tRNA`) AS sup_len, "
        "LENGTH(`Secondary structure`) AS origin_ss_len, "
        "LENGTH(`Secondary structure of sup-trna`) AS sup_ss_len, "
        "JSON_LENGTH(`js_origin_tRNA`) AS js_origin_len, "
        "JSON_LENGTH(`js_sup_tRNA`) AS js_sup_len, "
        "pdbid "
        "FROM Engineered_sup_tRNA "
        f"WHERE PMID='{PMID}' AND ENSURE_ID IN ({quoted_ids()}) "
        "ORDER BY `Index`;"
    )
    verify = run_mysql(base, cmd_env, query=verify_query)
    print(f"backup_tsv {backup_tsv}")
    print(verify)


if __name__ == "__main__":
    main()
