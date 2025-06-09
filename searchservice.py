#!/usr/bin/env python3
"""
Flask 搜索服务：在本地或远程 CSV 中按行筛选与 query_seq 最优对齐。

Endpoints:
  POST /search
  Request JSON:
    {
      "query_seq": "YOUR_SEQUENCE",
      "csv_paths": ["path_or_url1.csv", "path_or_url2.csv", ...],
      "number": 5,
      "match": 2.0,
      "mismatch": -0.5,
      "gap_open": -2.0,
      "gap_extend": -1.0
    }
  Response JSON: List of up to `number` best-matching rows, each:
    {
      "file": "...",
      "row": 1,
      "column": "...",
      "score": 123.4,
      "columns": [...],
      "row_data": { ... },
      "alignment": "target ACGT...\\n||| ...\\nquery ACGT..."
    }
"""
import os
import io
import json
import requests
import pandas as pd
from flask import Flask, request, jsonify
from Bio.Align import PairwiseAligner
from typing import Tuple
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def load_csv(path_or_url: str) -> pd.DataFrame:
    """加载 CSV：支持本地路径或 HTTP/HTTPS URL"""
    if path_or_url.startswith(('http://', 'https://')):
        resp = requests.get(path_or_url, timeout=15)
        resp.raise_for_status()
        return pd.read_csv(io.StringIO(resp.text), dtype=str, keep_default_na=False)
    else:
        return pd.read_csv(path_or_url, dtype=str, keep_default_na=False)

def alignment_score_and_str(
    seq1: str, seq2: str,
    match: float, mismatch: float,
    gap_open: float, gap_extend: float
) -> Tuple[float, str]:
    """使用 PairwiseAligner 做全局对齐；返回 (score, flattened_alignment)."""
    aligner = PairwiseAligner()
    aligner.mode = 'global'
    aligner.match_score      = match
    aligner.mismatch_score   = mismatch
    aligner.open_gap_score   = gap_open
    aligner.extend_gap_score = gap_extend

    # 获取对齐结果，不要用 `if not alns` 来判断空集合
    alns = aligner.align(seq1, seq2)
    try:
        best = alns[0]
    except IndexError:
        # 没有任何对齐结果
        return 0.0, ''

    score = best.score
    raw   = best.format()

    seqA_parts, seqB_parts = [], []
    for line in raw.splitlines():
        if line.startswith('target'):
            parts = line.split(maxsplit=2)
            if len(parts) == 3 and all(c in 'ACGTU-' for c in parts[2]):
                seqA_parts.append(parts[2])
        elif line.startswith('query'):
            parts = line.split(maxsplit=2)
            if len(parts) == 3 and all(c in 'ACGTU-' for c in parts[2]):
                seqB_parts.append(parts[2])

    flatA = ''.join(seqA_parts)
    flatB = ''.join(seqB_parts)
    L = min(len(flatA), len(flatB))
    match_line = ''.join('|' if flatA[i] == flatB[i] else ' ' for i in range(L))

    flat_alignment = f"target {flatA}\n{match_line}\nquery  {flatB}"
    return score, flat_alignment

@app.route('/search', methods=['POST'])
def search():
    data = request.json or {}
    query_seq = data.get('query_seq', '')
    csv_paths = data.get('csv_paths', [])
    number     = int(data.get('number', 5))
    match      = float(data.get('match', 2.0))
    mismatch   = float(data.get('mismatch', -0.5))
    gap_open   = float(data.get('gap_open', -2.0))
    gap_extend = float(data.get('gap_extend', -1.0))

    results = []
    for path in csv_paths:
        try:
            df = load_csv(path)
        except Exception as e:
            app.logger.warning(f"Cannot load {path}: {e}")
            continue

        cols = df.columns.tolist()
        for idx, row in df.iterrows():
            best_score = None
            best_col   = None
            best_align = ''
            for col in cols:
                cell = row[col]
                if not isinstance(cell, str) or not cell:
                    continue
                score, aln = alignment_score_and_str(
                    query_seq, cell,
                    match, mismatch,
                    gap_open, gap_extend
                )
                if best_score is None or score > best_score:
                    best_score = score
                    best_col   = col
                    best_align = aln
            if best_score is not None:
                results.append({
                    'file': os.path.basename(path),
                    'row': idx + 1,
                    'column': best_col,
                    'score': best_score,
                    'columns': cols,
                    'row_data': row.to_dict(),
                    'alignment': best_align.replace('\n', '\\n')
                })

    # 返回前 number 名
    topn = sorted(results, key=lambda x: x['score'], reverse=True)[:number]
    return jsonify(topn)

if __name__ == '__main__':
    # 开发模式多线程；生产请使用 Gunicorn 等 WSGI 容器
    app.run(host='0.0.0.0', port=8000, threaded=True)