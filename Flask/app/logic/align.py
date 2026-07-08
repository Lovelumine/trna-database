# -*- coding: utf-8 -*-
import os
import io
import re
from datetime import date, datetime
from decimal import Decimal
from typing import Tuple, Optional, Iterable, Set, List, Dict, Any

import pandas as pd
import requests
from Bio.Align import PairwiseAligner
from sqlalchemy import text, inspect

# -----------------------------
# 工具函数（编码鲁棒读取 + 乱码修复）
# -----------------------------
def _read_csv_from_bytes(raw: bytes) -> pd.DataFrame:
    """按常见编码顺序尝试读取 CSV；失败则用 latin1 兜底，后续再做修复。"""
    encodings = ["utf-8-sig", "utf-8", "gb18030", "big5", "cp936", "cp1252", "latin1"]
    for enc in encodings:
        try:
            return pd.read_csv(io.BytesIO(raw), dtype=str, keep_default_na=False, encoding=enc)
        except UnicodeDecodeError:
            continue
    return pd.read_csv(io.BytesIO(raw), dtype=str, keep_default_na=False, encoding="latin1")

def _maybe_fix_mojibake(s: str) -> str:
    """只在检测到典型乱码痕迹时尝试 latin1->utf8 复原。"""
    if not isinstance(s, str) or not s:
        return s
    if ("Ã" in s) or ("Â" in s):
        try:
            return s.encode("latin1").decode("utf-8")
        except Exception:
            return s
    return s

def _fix_df_mojibake(df: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(df, pd.DataFrame) or df.empty:
        return df
    try:
        has_moji = df.apply(lambda col: col.astype(str).str.contains(r"Ã|Â", na=False)).any().any()
    except Exception:
        has_moji = True
    if not has_moji:
        return df
    if hasattr(df, "map") and callable(getattr(df, "map")):
        return df.map(_maybe_fix_mojibake)
    else:
        return df.applymap(_maybe_fix_mojibake)

def load_csv(path_or_url: str) -> pd.DataFrame:
    """统一按字节读取，避免 requests 的 r.text 误判编码；读取后按需修复乱码。"""
    if path_or_url.startswith(("http://", "https://")):
        r = requests.get(path_or_url, timeout=20)
        r.raise_for_status()
        df = _read_csv_from_bytes(r.content)
    else:
        with open(path_or_url, "rb") as f:
            raw = f.read()
        df = _read_csv_from_bytes(raw)
    return _fix_df_mojibake(df)

# -----------------------------
# 类 BLAST 序列搜索：标准化 + k-mer 候选 + 精确对齐
# -----------------------------
CANONICAL_BASES = {"A", "C", "G", "U"}
AMBIGUOUS_BASES = set("RYSWKMBDHVNXI")
MODIFIED_BASE_MAP = {
    "T": "U",
    "D": "U",  # dihydrouridine in tRNA notation
    "P": "U",  # pseudouridine is often encoded as P in the source data
    "Ψ": "U",
    "I": "N",
}
SEQUENCE_SIGNAL_CHARS = CANONICAL_BASES | {"T", "D", "P", "Ψ", "I"} | AMBIGUOUS_BASES


def normalize_sequence(value: Any) -> str:
    """Normalize RNA/DNA/tRNA-modification notation to A/C/G/U/N."""
    if value is None:
        return ""
    seq: List[str] = []
    for ch in str(value).upper():
        if ch in MODIFIED_BASE_MAP:
            seq.append(MODIFIED_BASE_MAP[ch])
        elif ch in CANONICAL_BASES:
            seq.append(ch)
        elif ch in AMBIGUOUS_BASES:
            seq.append("N")
        elif ch.isalpha():
            seq.append("N")
    return "".join(seq)


def _looks_like_sequence(value: Any, min_length: int = 3) -> bool:
    if value is None:
        return False
    raw = str(value).strip()
    if not raw:
        return False
    normalized = normalize_sequence(raw)
    if len(normalized) < min_length:
        return False
    letters = [ch for ch in raw.upper() if ch.isalpha() or ch == "Ψ"]
    if not letters:
        return False
    signal = sum(1 for ch in letters if ch in SEQUENCE_SIGNAL_CHARS)
    return signal / len(letters) >= 0.75


def _choose_kmer_size(query: str) -> int:
    if len(query) < 8:
        return 3
    if len(query) < 30:
        return 4
    return 6


def _kmers(seq: str, k: int) -> Set[str]:
    if k <= 0 or len(seq) < k:
        return set()
    return {seq[i : i + k] for i in range(0, len(seq) - k + 1) if "N" not in seq[i : i + k]}


def _sql_kmer_variants(kmers: Set[str], limit: int = 24) -> List[str]:
    variants: List[str] = []
    for kmer in sorted(kmers):
        expanded = [""]
        for ch in kmer:
            replacements = ["U", "T", "D", "P", "Ψ"] if ch == "U" else [ch]
            expanded = [prefix + item for prefix in expanded for item in replacements]
            if len(expanded) > limit:
                expanded = expanded[:limit]
                break
        for variant in expanded:
            if variant not in variants:
                variants.append(variant)
            if len(variants) >= limit:
                break
        if len(variants) >= limit:
            break
    return variants


def _shared_kmer_count(query_kmers: Set[str], target: str, k: int) -> int:
    if not query_kmers:
        return 0
    return len(query_kmers & _kmers(target, k))


def _choose_alignment_mode(query: str, target: str, requested: str = "auto") -> str:
    mode = str(requested or "auto").lower()
    if mode in {"global", "local"}:
        return mode
    if len(query) <= 30 or (target and len(query) < len(target) * 0.7):
        return "local"
    return "global"


def _alignment_to_strings(seq1: str, seq2: str, alignment) -> Tuple[str, str]:
    coords = alignment.coordinates
    left: List[str] = []
    right: List[str] = []

    for i in range(coords.shape[1] - 1):
        a0, a1 = int(coords[0, i]), int(coords[0, i + 1])
        b0, b1 = int(coords[1, i]), int(coords[1, i + 1])
        a_len = abs(a1 - a0)
        b_len = abs(b1 - b0)

        if a_len and b_len:
            a_seg = seq1[min(a0, a1) : max(a0, a1)]
            b_seg = seq2[min(b0, b1) : max(b0, b1)]
            if len(a_seg) == len(b_seg):
                left.append(a_seg)
                right.append(b_seg)
            else:
                span = max(len(a_seg), len(b_seg))
                left.append(a_seg.ljust(span, "-"))
                right.append(b_seg.ljust(span, "-"))
        elif a_len:
            a_seg = seq1[min(a0, a1) : max(a0, a1)]
            left.append(a_seg)
            right.append("-" * len(a_seg))
        elif b_len:
            b_seg = seq2[min(b0, b1) : max(b0, b1)]
            left.append("-" * len(b_seg))
            right.append(b_seg)

    return "".join(left), "".join(right)


def _bases_match(a: str, b: str) -> bool:
    a = "U" if a == "T" else a
    b = "U" if b == "T" else b
    return a == b and a in CANONICAL_BASES


def _match_line(target_aln: str, query_aln: str) -> str:
    chars: List[str] = []
    for target_ch, query_ch in zip(target_aln, query_aln):
        if target_ch == "-" or query_ch == "-":
            chars.append(" ")
        elif _bases_match(target_ch, query_ch):
            chars.append("|")
        else:
            chars.append(".")
    return "".join(chars)


def _alignment_metrics(
    query_aln: str,
    target_aln: str,
    query_len: int,
    target_len: int,
    score: float,
    match: float,
    mode: str,
    shared_kmers: int = 0,
    query_kmer_count: int = 0,
) -> Dict[str, Any]:
    alignment_length = max(len(query_aln), len(target_aln))
    matches = 0
    mismatches = 0
    gaps = 0
    query_aligned = 0
    target_aligned = 0

    for query_ch, target_ch in zip(query_aln, target_aln):
        query_gap = query_ch == "-"
        target_gap = target_ch == "-"
        if not query_gap:
            query_aligned += 1
        if not target_gap:
            target_aligned += 1
        if query_gap or target_gap:
            gaps += 1
        elif _bases_match(query_ch, target_ch):
            matches += 1
        else:
            mismatches += 1

    identity = (matches / alignment_length * 100.0) if alignment_length else 0.0
    query_coverage = (query_aligned / query_len * 100.0) if query_len else 0.0
    target_coverage = (target_aligned / target_len * 100.0) if target_len else 0.0

    max_len = min(query_len, target_len) if mode == "local" else max(query_len, target_len)
    max_score = max_len * match if max_len and match > 0 else 0.0
    normalized_score = (score / max_score * 100.0) if max_score else 0.0
    normalized_score = max(0.0, min(100.0, normalized_score))
    kmer_recall = (shared_kmers / query_kmer_count * 100.0) if query_kmer_count else 0.0

    rank_score = (
        normalized_score * 0.45
        + identity * 0.35
        + query_coverage * 0.15
        + target_coverage * 0.05
    )

    return {
        "alignment_length": alignment_length,
        "matches": matches,
        "mismatches": mismatches,
        "gaps": gaps,
        "identity": round(identity, 2),
        "query_coverage": round(query_coverage, 2),
        "target_coverage": round(target_coverage, 2),
        "normalized_score": round(normalized_score, 2),
        "kmer_hits": shared_kmers,
        "kmer_recall": round(kmer_recall, 2),
        "rank_score": round(rank_score, 4),
    }


def alignment_result(
    query_seq: str,
    target_seq: str,
    match: float,
    mismatch: float,
    gap_open: float,
    gap_extend: float,
    mode: str = "auto",
    shared_kmers: int = 0,
    query_kmer_count: int = 0,
) -> Dict[str, Any]:
    query = normalize_sequence(query_seq)
    target = normalize_sequence(target_seq)
    align_mode = _choose_alignment_mode(query, target, mode)

    aligner = PairwiseAligner()
    aligner.mode = align_mode
    aligner.match_score = match
    aligner.mismatch_score = mismatch
    aligner.open_gap_score = gap_open
    aligner.extend_gap_score = gap_extend
    aligner.wildcard = "N"

    alns = aligner.align(query, target)
    try:
        best = alns[0]
    except IndexError:
        return {
            "score": 0.0,
            "alignment": "",
            "alignment_mode": align_mode,
            "query_normalized": query,
            "target_normalized": target,
            **_alignment_metrics("", "", len(query), len(target), 0.0, match, align_mode),
        }

    query_aln, target_aln = _alignment_to_strings(query, target, best)
    line = _match_line(target_aln, query_aln)
    flat_alignment = f"target {target_aln}\n       {line}\nquery  {query_aln}"
    metrics = _alignment_metrics(
        query_aln,
        target_aln,
        len(query),
        len(target),
        float(best.score),
        match,
        align_mode,
        shared_kmers,
        query_kmer_count,
    )
    return {
        "score": float(best.score),
        "alignment": flat_alignment,
        "alignment_mode": align_mode,
        "query_normalized": query,
        "target_normalized": target,
        **metrics,
    }


def alignment_score_and_str(
    seq1: str,
    seq2: str,
    match: float,
    mismatch: float,
    gap_open: float,
    gap_extend: float,
    mode: str = "auto",
) -> Tuple[float, str]:
    """Return raw alignment score and formatted alignment for compatibility."""
    result = alignment_result(seq1, seq2, match, mismatch, gap_open, gap_extend, mode)
    return result["score"], result["alignment"]

# -----------------------------
# 列名与参数解析（PMID / ENSURE_ID）
# -----------------------------
def _normalize_col_name(s: str) -> str:
    return "".join(str(s).strip().lower().split())

def _detect_pmid_column(df: pd.DataFrame) -> Optional[str]:
    """在 DataFrame 中智能识别 PMID 列名，兼容大小写/空格与常见别名。"""
    candidates = ["pmid", "pubmedid", "pubmed_id", "pmids"]
    norm_cols = [_normalize_col_name(c) for c in df.columns]
    for key in candidates:
        if key in norm_cols:
            i = norm_cols.index(key)
            return df.columns[i]
    for raw in df.columns:
        if "pmid" in _normalize_col_name(raw):
            return raw
    return None

def _detect_ensure_column(df: pd.DataFrame) -> Optional[str]:
    """识别 ENSURE_ID 列名，兼容大小写/空格与常见别名。"""
    candidates = ["ensure_id", "ensureid", "ensureids", "ensure_ids", "ensure"]
    norm_cols = [_normalize_col_name(c) for c in df.columns]
    for key in candidates:
        if key in norm_cols:
            i = norm_cols.index(key)
            return df.columns[i]
    for raw in df.columns:
        n = _normalize_col_name(raw)
        if "ensure" in n and "id" in n:
            return raw
    for raw in df.columns:
        if str(raw).upper() == "ENSURE_ID":
            return raw
    return None

def _parse_ids(v) -> Optional[Set[str]]:
    """
    通用 ID 解析：
    - "A,B,C" / ["A","B","C"] / 单个字符串
    返回去重集合；无法解析时返回 None。
    """
    if v is None:
        return None
    if isinstance(v, str):
        s = v.strip()
        if not s:
            return None
        parts = [x.strip() for x in s.split(",") if x.strip()]
        return set(parts) if parts else None
    try:
        # Iterable（list/tuple/set 等）
        parts = [str(x).strip() for x in v if str(x).strip()]
        return set(parts) if parts else None
    except Exception:
        return None

# -----------------------------
# 统一业务入口：search_in_csvs
# -----------------------------
def search_in_csvs(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    输入：与原 POST /search JSON 一致
    输出：排序后前 N 条 topn 结果（list of dict）
    """
    query_seq = data.get("query_seq", "")
    csv_paths = data.get("csv_paths", [])
    number = int(data.get("number", 5))
    match = float(data.get("match", 2.0))
    mismatch = float(data.get("mismatch", -0.5))
    gap_open = float(data.get("gap_open", -2.0))
    gap_extend = float(data.get("gap_extend", -1.0))
    alignment_mode = str(data.get("alignment_mode", "auto") or "auto")

    pmids_filter = _parse_ids(data.get("pmids"))
    ensure_filter = _parse_ids(data.get("ensure_ids"))

    if not isinstance(csv_paths, (list, tuple)) or not csv_paths:
        raise ValueError("csv_paths 不能为空；请提供本地路径或 URL 列表。")
    if not isinstance(query_seq, str) or not query_seq:
        raise ValueError("query_seq 不能为空。")
    query_norm = normalize_sequence(query_seq)
    if not query_norm or not _looks_like_sequence(query_seq):
        raise ValueError("query_seq 中没有可识别的核酸序列字符。")

    kmer_size = _choose_kmer_size(query_norm)
    query_kmers = _kmers(query_norm, kmer_size)

    results: List[Dict[str, Any]] = []

    for path in csv_paths:
        try:
            df = load_csv(path)
        except Exception as e:
            # 忽略读取失败的文件，但记录错误行
            # （在 Flask 层用 app.logger 也可以，此处保持纯逻辑）
            # print(f"[WARN] Cannot load {path}: {e}")
            continue

        # 可选：按 ENSURE_ID 过滤
        if ensure_filter:
            ensure_col = _detect_ensure_column(df)
            if ensure_col:
                df = df[df[ensure_col].astype(str).isin(ensure_filter)]

        # 可选：按 PMID 过滤
        if pmids_filter:
            pmid_col = _detect_pmid_column(df)
            if pmid_col:
                df = df[df[pmid_col].astype(str).isin(pmids_filter)]

        cols = df.columns.tolist()
        table_hint = _normalize_table_name(os.path.splitext(os.path.basename(path))[0])
        seq_cols = _pick_sequence_columns(table_hint, cols) or cols

        for idx, row in df.iterrows():
            best_result: Optional[Dict[str, Any]] = None
            best_col: Optional[str] = None

            for col in seq_cols:
                cell = row[col]
                if not isinstance(cell, str) or not _looks_like_sequence(cell):
                    continue

                target_norm = normalize_sequence(cell)
                shared_kmers = _shared_kmer_count(query_kmers, target_norm, kmer_size)
                if query_kmers and shared_kmers <= 0:
                    continue

                result = alignment_result(
                    query_seq,
                    cell,
                    match,
                    mismatch,
                    gap_open,
                    gap_extend,
                    alignment_mode,
                    shared_kmers,
                    len(query_kmers),
                )
                if best_result is None or (
                    result.get("rank_score", 0),
                    result.get("score", 0),
                ) > (
                    best_result.get("rank_score", 0),
                    best_result.get("score", 0),
                ):
                    best_result, best_col = result, col

            if best_result is not None:
                results.append(
                    {
                        "file": os.path.basename(path),
                        "row": idx + 1,
                        "column": best_col,
                        "columns": cols,
                        "row_data": row.to_dict(),
                        "method": "k-mer candidate search + pairwise alignment",
                        "kmer_size": kmer_size,
                        **{
                            key: (
                                value.replace("\n", "\\n")
                                if key == "alignment" and isinstance(value, str)
                                else value
                            )
                            for key, value in best_result.items()
                        },
                    }
                )

    topn = sorted(
        results,
        key=lambda x: (x.get("rank_score", 0), x.get("score", 0)),
        reverse=True,
    )[:number]
    return topn


# -----------------------------
# MySQL 搜索（按序列相关列对齐）
# -----------------------------

TABLE_NAME_ALIASES = {
    "Coding Variation in Cancer": "coding_variation_cancer",
    "Coding Variation in Disease": "coding_variation_genetic_disease",
    "Nonsense Sup-RNA": "nonsense_sup_rna",
    "Frameshift sup-tRNA": "frameshift_sup_trna",
    "Engineered sup-tRNA": "Engineered_sup_tRNA",
    "Function of Modification": "function_and_modification",
    "aaRS Recognition": "aars_recognition",
}

DEFAULT_SEQUENCE_COLUMNS = {
    "coding_variation_cancer": [
        "MUTATION_CDS",
    ],
    "coding_variation_genetic_disease": ["Codon Change"],
    "nonsense_sup_rna": [
        "tRNA sequence before mutation",
        "tRNA sequence after mutation",
        "Anticodon before mutation",
        "Anticodon after mutation",
        "Stop codon for readthrough",
    ],
    "frameshift_sup_trna": [
        "tRNA sequence before mutation",
        "tRNA sequence after mutation",
        "Anticodon before mutation",
        "Anticodon after mutation",
        "Codon for readthrough",
    ],
    "Engineered_sup_tRNA": [
        "Sequence_of_origin_tRNA",
        "Sequence_of_sup-tRNA",
        "PTC_codon",
    ],
    "aars_recognition": ["AnticodonArm"],
    "ef_tu": ["Anticodon branch"],
}

SEQUENCE_KEYWORDS = ("sequence", "seq", "anticodon", "codon")


def _normalize_table_name(name: str) -> str:
    return TABLE_NAME_ALIASES.get(name, name)


def _pick_sequence_columns(table: str, columns: List[str]) -> List[str]:
    if table in DEFAULT_SEQUENCE_COLUMNS:
        return [c for c in DEFAULT_SEQUENCE_COLUMNS[table] if c in columns]
    hits: List[str] = []
    for col in columns:
        lower = col.lower()
        if any(key in lower for key in SEQUENCE_KEYWORDS):
            hits.append(col)
    return hits


def _jsonify_value(value: Any) -> Any:
    if isinstance(value, (datetime, date, Decimal)):
        return str(value)
    if isinstance(value, (bytes, bytearray)):
        try:
            return value.decode("utf-8")
        except Exception:
            return value.decode("latin1", errors="ignore")
    return value


def search_in_mysql(data: Dict[str, Any], engine) -> List[Dict[str, Any]]:
    """
    输入：
      - tables: MySQL 表名列表（或显示名）
      - query_seq, number, match, mismatch, gap_open, gap_extend
    输出：排序后前 N 条结果
    """
    query_seq = data.get("query_seq", "")
    tables = data.get("tables", [])
    number = int(data.get("number", 5))
    match = float(data.get("match", 2.0))
    mismatch = float(data.get("mismatch", -0.5))
    gap_open = float(data.get("gap_open", -2.0))
    gap_extend = float(data.get("gap_extend", -1.0))
    alignment_mode = str(data.get("alignment_mode", "auto") or "auto")

    if not isinstance(tables, (list, tuple)) or not tables:
        raise ValueError("tables 不能为空；请提供 MySQL 表名列表。")
    if not isinstance(query_seq, str) or not query_seq:
        raise ValueError("query_seq 不能为空。")
    query_norm = normalize_sequence(query_seq)
    if not query_norm or not _looks_like_sequence(query_seq):
        raise ValueError("query_seq 中没有可识别的核酸序列字符。")

    kmer_size = _choose_kmer_size(query_norm)
    query_kmers = _kmers(query_norm, kmer_size)
    sql_kmers = _sql_kmer_variants(query_kmers)

    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    results: List[Dict[str, Any]] = []

    with engine.connect() as conn:
        for raw_table in tables:
            table = _normalize_table_name(raw_table)
            if table not in existing_tables:
                continue

            columns = [c["name"] for c in inspector.get_columns(table)]
            seq_cols = _pick_sequence_columns(table, columns)
            if not seq_cols:
                continue

            select_sql = ", ".join([f"`{c}`" for c in columns])
            where_sql = ""
            params: Dict[str, Any] = {}
            if sql_kmers:
                like_clauses: List[str] = []
                for idx, kmer in enumerate(sql_kmers):
                    param = f"kmer_{idx}"
                    params[param] = kmer
                    like_clauses.extend(
                        f"INSTR(UPPER(CAST(`{c}` AS CHAR)), :{param}) > 0" for c in seq_cols
                    )
                where_sql = " WHERE " + " OR ".join(like_clauses)

            attempts = [(where_sql, params)]
            if where_sql:
                attempts.append(("", {}))

            table_results: List[Dict[str, Any]] = []
            for active_where_sql, active_params in attempts:
                sql = text(f"SELECT {select_sql} FROM `{table}`{active_where_sql}")
                res = conn.execution_options(stream_results=True).execute(sql, active_params)

                row_num = 0
                for row in res.mappings():
                    row_num += 1
                    row_data = {k: _jsonify_value(v) for k, v in row.items()}

                    best_result: Optional[Dict[str, Any]] = None
                    best_col: Optional[str] = None

                    for col in seq_cols:
                        cell = row_data.get(col)
                        if not isinstance(cell, str) or not _looks_like_sequence(cell):
                            continue

                        target_norm = normalize_sequence(cell)
                        shared_kmers = _shared_kmer_count(query_kmers, target_norm, kmer_size)
                        if query_kmers and shared_kmers <= 0:
                            continue

                        result = alignment_result(
                            query_seq,
                            cell,
                            match,
                            mismatch,
                            gap_open,
                            gap_extend,
                            alignment_mode,
                            shared_kmers,
                            len(query_kmers),
                        )
                        if best_result is None or (
                            result.get("rank_score", 0),
                            result.get("score", 0),
                        ) > (
                            best_result.get("rank_score", 0),
                            best_result.get("score", 0),
                        ):
                            best_result, best_col = result, col

                    if best_result is not None:
                        table_results.append(
                            {
                                "file": table,
                                "row": row_num,
                                "column": best_col,
                                "columns": columns,
                                "row_data": row_data,
                                "method": "k-mer candidate search + pairwise alignment",
                                "kmer_size": kmer_size,
                                **{
                                    key: (
                                        value.replace("\n", "\\n")
                                        if key == "alignment" and isinstance(value, str)
                                        else value
                                    )
                                    for key, value in best_result.items()
                                },
                            }
                        )

                if table_results or not active_where_sql:
                    break

            results.extend(table_results)

    topn = sorted(
        results,
        key=lambda x: (x.get("rank_score", 0), x.get("score", 0)),
        reverse=True,
    )[:number]
    return topn
