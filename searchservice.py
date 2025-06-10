#!/usr/bin/env python3
"""
Flask 搜索服务：在本地或远程 CSV 中按行筛选与 query_seq 最优对齐。

Endpoints:
  POST /search
  Request JSON:
    {
      "query_seq": "YOUR_SEQUENCE",
      "csv_paths": ["...csv", ...],
      "number": 5,
      "match": 2.0,
      "mismatch": -0.5,
      "gap_open": -2.0,
      "gap_extend": -1.0
    }
  Response JSON: List of best-matching rows with 'alignment' 字段包含 target/match/query 三行。
"""
import os, io, requests, pandas as pd
from flask          import Flask, request, jsonify
from Bio.Align      import PairwiseAligner
from typing         import Tuple
from flask_cors     import CORS

app = Flask(__name__)
CORS(app)

def load_csv(path_or_url: str) -> pd.DataFrame:
    if path_or_url.startswith(('http://','https://')):
        r = requests.get(path_or_url, timeout=15)
        r.raise_for_status()
        return pd.read_csv(io.StringIO(r.text), dtype=str, keep_default_na=False)
    return pd.read_csv(path_or_url, dtype=str, keep_default_na=False)

def alignment_score_and_str(
    seq1: str, seq2: str,
    match: float, mismatch: float,
    gap_open: float, gap_extend: float
) -> Tuple[float, str]:
    """全局对齐，只取第一个最优对齐；返回 (score, flattened_alignment)."""
    aligner = PairwiseAligner()
    aligner.mode             = 'global'
    aligner.match_score      = match
    aligner.mismatch_score   = mismatch
    aligner.open_gap_score   = gap_open
    aligner.extend_gap_score = gap_extend

    alns = aligner.align(seq1, seq2)
    try:
        best = alns[0]
    except IndexError:
        return 0.0, ''

    score = best.score
    raw   = best.format()

    # 直接拆成三行：seqA / match_line / seqB
    lines = raw.splitlines()
    if len(lines) >= 3:
        flatA     = lines[0]
        match_line= lines[1]
        flatB     = lines[2]
    else:
        # 万一不是三行，退回最简单拼接
        flatA  = ''.join(lines)
        match_line = ''
        flatB  = ''

    # 构造最终字符串
    flat_alignment = f"target {flatA}\n{match_line}\nquery  {flatB}"
    return score, flat_alignment

@app.route('/search', methods=['POST'])
def search():
    data       = request.json or {}
    query_seq  = data.get('query_seq','')
    csv_paths  = data.get('csv_paths',[])
    number     = int(data.get('number',5))
    match      = float(data.get('match',2.0))
    mismatch   = float(data.get('mismatch',-0.5))
    gap_open   = float(data.get('gap_open',-2.0))
    gap_extend = float(data.get('gap_extend',-1.0))

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
                if not isinstance(cell,str) or not cell:
                    continue
                score, aln = alignment_score_and_str(
                    query_seq, cell,
                    match, mismatch,
                    gap_open, gap_extend
                )
                if best_score is None or score > best_score:
                    best_score, best_col, best_align = score, col, aln
            if best_score is not None:
                results.append({
                    'file':      os.path.basename(path),
                    'row':       idx+1,
                    'column':    best_col,
                    'score':     best_score,
                    'columns':   cols,
                    'row_data':  row.to_dict(),
                    'alignment': best_align.replace('\n','\\n')
                })

    topn = sorted(results, key=lambda x: x['score'], reverse=True)[:number]
    return jsonify(topn)

if __name__ == '__main__':
    # 单线程下跑，避免多线程下 Biopython 崩溃
    app.run(host='0.0.0.0', port=8000, threaded=False)