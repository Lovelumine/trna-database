#!/usr/bin/env python3
"""
Flask 搜索服务：在本地或远程 CSV 中按行筛选与 query_seq 最优对齐。

Endpoints:
  GET  /health    健康检查接口，返回 200 OK
  GET  /          首页，返回 200 OK
  POST /search    实际查询接口
  GET  /search    返回 200 OK，用于监控/测试
"""

import os, io, requests, pandas as pd
import threading
import sys
from flask          import Flask, request, jsonify
from Bio.Align      import PairwiseAligner
from typing         import Tuple
from flask_cors     import CORS

app = Flask(__name__)
CORS(app)

# -----------------------------
# 工具函数
# -----------------------------
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

    # 拆成三行：seqA / match_line / seqB
    lines = raw.splitlines()
    if len(lines) >= 3:
        flatA     = lines[0]
        match_line= lines[1]
        flatB     = lines[2]
    else:
        flatA  = ''.join(lines)
        match_line = ''
        flatB  = ''

    flat_alignment = f"target {flatA}\n{match_line}\nquery  {flatB}"
    return score, flat_alignment

# -----------------------------
# 路由
# -----------------------------
@app.route('/', methods=['GET'])
def index():
    return 'OK', 200

@app.route('/health', methods=['GET'])
def health():
    return 'OK', 200

@app.route('/search', methods=['GET', 'POST'])
@app.route('/search/', methods=['GET', 'POST'])
def search():
    # 健康检查或手工测试时 GET
    if request.method == 'GET':
        return 'OK', 200

    # POST 查询逻辑
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

# -----------------------------
# 自动重启（可选）
# -----------------------------
def schedule_restart(interval_sec: float = 1800):
    """在 interval_sec 秒后重启当前进程。"""
    def _restart():
        os.execv(sys.executable, [sys.executable] + sys.argv)
    t = threading.Timer(interval_sec, _restart)
    t.setDaemon(True)
    t.start()

# -----------------------------
# 主入口
# -----------------------------
if __name__ == '__main__':
    # 如果要开启定时重启，取消注释：
    # schedule_restart(1800)

    # 单线程，避免 Biopython 崩溃
    app.run(host='0.0.0.0', port=8000, threaded=False)
