# -*- coding: utf-8 -*-
import os
import io
from typing import Tuple, Optional, Iterable, Set, List, Dict, Any

import pandas as pd
import requests
from Bio.Align import PairwiseAligner

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
# 对齐
# -----------------------------
def alignment_score_and_str(
    seq1: str,
    seq2: str,
    match: float,
    mismatch: float,
    gap_open: float,
    gap_extend: float,
) -> Tuple[float, str]:
    """全局对齐，只取第一个最优对齐；返回 (score, flattened_alignment)."""
    aligner = PairwiseAligner()
    aligner.mode = "global"
    aligner.match_score = match
    aligner.mismatch_score = mismatch
    aligner.open_gap_score = gap_open
    aligner.extend_gap_score = gap_extend

    alns = aligner.align(seq1, seq2)
    try:
        best = alns[0]
    except IndexError:
        return 0.0, ""

    score = best.score
    raw = best.format()

    lines = raw.splitlines()
    if len(lines) >= 3:
        flatA = lines[0]
        match_line = lines[1]
        flatB = lines[2]
    else:
        flatA = "".join(lines)
        match_line = ""
        flatB = ""

    flat_alignment = f"target {flatA}\n{match_line}\nquery  {flatB}"
    return score, flat_alignment

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

    pmids_filter = _parse_ids(data.get("pmids"))
    ensure_filter = _parse_ids(data.get("ensure_ids"))

    if not isinstance(csv_paths, (list, tuple)) or not csv_paths:
        raise ValueError("csv_paths 不能为空；请提供本地路径或 URL 列表。")
    if not isinstance(query_seq, str) or not query_seq:
        raise ValueError("query_seq 不能为空。")

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
        for idx, row in df.iterrows():
            best_score = None
            best_col = None
            best_align = ""
            for col in cols:
                cell = row[col]
                if not isinstance(cell, str) or not cell:
                    continue
                score, aln = alignment_score_and_str(
                    query_seq, cell, match, mismatch, gap_open, gap_extend
                )
                if best_score is None or score > best_score:
                    best_score, best_col, best_align = score, col, aln
            if best_score is not None:
                results.append(
                    {
                        "file": os.path.basename(path),
                        "row": idx + 1,
                        "column": best_col,
                        "score": best_score,
                        "columns": cols,
                        "row_data": row.to_dict(),
                        "alignment": best_align.replace("\n", "\\n"),
                    }
                )

    topn = sorted(results, key=lambda x: x["score"], reverse=True)[:number]
    return topn
