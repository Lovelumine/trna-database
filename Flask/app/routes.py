# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify
from sqlalchemy import text, bindparam, Integer
import re
from . import db

from .logic.align import (
    search_in_csvs,  # 统一封装的业务逻辑入口
)

bp = Blueprint("routes", __name__)

# ---------------------- 通用工具 ----------------------

def _get_table_columns(table: str):
    insp = db.inspect(db.engine)
    if table not in insp.get_table_names():
        return None, None
    cols = insp.get_columns(table)  # [{'name':..., 'type':...}, ...]
    col_names = [c["name"] for c in cols]
    return cols, col_names

# ---------------------- 搜索/分页辅助 ----------------------

def _escape_like(s: str) -> str:
    return s.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

def _normalize_sort_order(order: str) -> str:
    o = str(order or "").lower()
    if o in ("desc", "descend", "descending"):
        return "desc"
    return "asc"

def _build_search_clause(search_text: str, search_column: str, columns: list, ci: bool):
    if not search_text:
        return "", {}
    collate = " COLLATE utf8mb4_general_ci" if ci else ""
    like_val = f"%{_escape_like(str(search_text))}%"
    if search_column:
        clauses = [
            f"CAST(`{search_column}` AS CHAR){collate} LIKE :search ESCAPE '\\\\'"
        ]
    else:
        clauses = [
            f"CAST(`{col}` AS CHAR){collate} LIKE :search ESCAPE '\\\\'"
            for col in columns
        ]
    if not clauses:
        return "", {}
    return "WHERE " + " OR ".join(clauses), {"search": like_val}

def _build_fulltext_query(search_text: str) -> str:
    tokens = re.findall(r"[A-Za-z0-9_]+", str(search_text))
    tokens = [t for t in tokens if len(t) >= 3]
    if not tokens:
        return ""
    return " ".join(f"+{t}*" for t in tokens)

def _get_fulltext_columns(table: str, index_name: str = "ft_all"):
    db_name = db.engine.url.database
    sql = text(
        "SELECT INDEX_NAME, COLUMN_NAME, SEQ_IN_INDEX "
        "FROM information_schema.statistics "
        "WHERE TABLE_SCHEMA = :db AND TABLE_NAME = :table "
        "AND INDEX_TYPE = 'FULLTEXT'"
    )
    with db.engine.connect() as conn:
        rows = conn.execute(sql, {"db": db_name, "table": table}).fetchall()
    if not rows:
        return []
    # Prefer a named index if present; otherwise take the first fulltext index.
    by_index = {}
    for idx_name, col, seq in rows:
        by_index.setdefault(idx_name, []).append((seq, col))
    if index_name in by_index:
        cols = by_index[index_name]
    else:
        first = next(iter(by_index.values()))
        cols = first
    return [col for seq, col in sorted(cols)]

def _build_search_filter(
    search_text: str,
    search_column: str,
    columns: list,
    ci: bool,
    use_fulltext: bool,
    fulltext_columns: list,
):
    if not search_text:
        return "", {}, False
    if use_fulltext and not search_column and fulltext_columns:
        ft_query = _build_fulltext_query(search_text)
        if ft_query:
            cols_sql = ", ".join(f"`{c}`" for c in fulltext_columns)
            return (
                f"WHERE MATCH({cols_sql}) AGAINST (:ft IN BOOLEAN MODE)",
                {"ft": ft_query},
                True,
            )
    where_sql, params = _build_search_clause(search_text, search_column, columns, ci)
    return where_sql, params, False

def _merge_where(where_sql: str, extra: str) -> str:
    if not extra:
        return where_sql
    if where_sql:
        return f"{where_sql} AND {extra}"
    return f"WHERE {extra}"

def _build_stat_filters(filters, columns: list, ci: bool):
    clauses = []
    params = {}
    if not filters:
        return "", params
    for idx, f in enumerate(filters):
        col = f.get("column")
        op = (f.get("op") or "eq").lower()
        val = f.get("value")
        if not col or col not in columns:
            raise ValueError(f"Invalid filter column '{col}'")
        collate = " COLLATE utf8mb4_general_ci" if ci else ""
        if op == "eq":
            clauses.append(f"CAST(`{col}` AS CHAR){collate} = :f{idx}")
            params[f"f{idx}"] = val
        elif op == "neq":
            clauses.append(f"CAST(`{col}` AS CHAR){collate} <> :f{idx}")
            params[f"f{idx}"] = val
        else:
            raise ValueError(f"Unsupported filter op '{op}'")
    return " AND ".join(clauses), params

def _value_counts(
    conn,
    table: str,
    column: str,
    where_sql: str,
    params: dict,
    split_regex: str = "",
    top_n: int = 0,
):
    if split_regex:
        sql = text(f"SELECT `{column}` FROM `{table}` {where_sql}")
        rows = conn.execute(sql, params).fetchall()
        counter = {}
        for row in rows:
            cell = row[0]
            if cell is None or cell == "":
                continue
            for part in re.split(split_regex, str(cell)):
                name = part.strip()
                if not name:
                    continue
                counter[name] = counter.get(name, 0) + 1
        items = sorted(counter.items(), key=lambda x: x[1], reverse=True)
        if top_n:
            items = items[:top_n]
        return [{"name": k, "value": int(v)} for k, v in items]

    sql = text(
        f"SELECT `{column}` AS name, COUNT(*) AS cnt "
        f"FROM `{table}` {where_sql} "
        f"GROUP BY `{column}`"
    )
    rows = conn.execute(sql, params).fetchall()
    items = sorted(((r[0] or "Unknown"), int(r[1])) for r in rows if r[0] not in (None, ""))
    if top_n:
        items = sorted(items, key=lambda x: x[1], reverse=True)[:top_n]
    return [{"name": k, "value": int(v)} for k, v in items]

def _matrix_counts(
    conn,
    table: str,
    x_column: str,
    y_column: str,
    where_sql: str,
    params: dict,
):
    sql = text(
        f"SELECT `{x_column}` AS x, `{y_column}` AS y, COUNT(*) AS cnt "
        f"FROM `{table}` {where_sql} "
        f"GROUP BY `{x_column}`, `{y_column}`"
    )
    rows = conn.execute(sql, params).fetchall()
    return [
        {"x": r[0], "y": r[1], "count": int(r[2])}
        for r in rows
        if r[0] not in (None, "") and r[1] not in (None, "")
    ]

def _codon_change_heatmap(
    conn,
    table: str,
    column: str,
    where_sql: str,
    params: dict,
    exclude_mut_regex: str = "",
):
    sql = text(f"SELECT `{column}` FROM `{table}` {where_sql}")
    rows = conn.execute(sql, params).fetchall()
    counter = {}
    for row in rows:
        cell = row[0]
        if cell is None or cell == "":
            continue
        parts = str(cell).split("-")
        if len(parts) < 2:
            continue
        orig = parts[0].strip()
        mut = parts[1].strip()
        if not orig or not mut:
            continue
        if exclude_mut_regex and re.search(exclude_mut_regex, mut):
            continue
        counter.setdefault(orig, {})
        counter[orig][mut] = counter[orig].get(mut, 0) + 1
    data = []
    for orig, row in counter.items():
        for mut, cnt in row.items():
            data.append({"orig": orig, "mut": mut, "count": int(cnt)})
    return data

# 针对 Engineered_sup_tRNA 提供简化 CRUD（行级编辑）
ENGINEERED_TABLE = "Engineered_sup_tRNA"

@bp.route("/engineered_sup_trna/columns", methods=["GET"])
def engineered_columns():
    cols, col_names = _get_table_columns(ENGINEERED_TABLE)
    if not cols:
        return jsonify({"error": f"Table '{ENGINEERED_TABLE}' does not exist"}), 400
    return jsonify({
        "table": ENGINEERED_TABLE,
        "columns": [{"name": c["name"], "type": str(c["type"])} for c in cols]
    })

@bp.route("/engineered_sup_trna/create", methods=["POST"])
def engineered_create():
    """
    JSON: {<column>: <value>, ...}
    必须包含 ENSURE_ID（作为逻辑唯一键），其他字段可选。
    """
    payload = request.get_json(silent=True) or {}
    cols, col_names = _get_table_columns(ENGINEERED_TABLE)
    if not cols:
        return jsonify({"error": f"Table '{ENGINEERED_TABLE}' does not exist"}), 400

    if "ENSURE_ID" not in payload:
        return jsonify({"error": "ENSURE_ID is required"}), 400

    # 仅保留表中存在的字段
    data = {k: v for k, v in payload.items() if k in col_names}
    if not data:
        return jsonify({"error": "No valid columns to insert"}), 400

    col_sql = ", ".join(f"`{k}`" for k in data.keys())
    placeholders = []
    params = {}
    for idx, (k, v) in enumerate(data.items()):
        ph = f"p{idx}"
        placeholders.append(f":{ph}")
        params[ph] = v
    val_sql = ", ".join(placeholders)
    sql = text(f"INSERT INTO `{ENGINEERED_TABLE}` ({col_sql}) VALUES ({val_sql})")

    try:
        with db.engine.begin() as conn:
            conn.execute(sql, params)
        return jsonify({"ok": True, "inserted": 1}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@bp.route("/engineered_sup_trna/update", methods=["POST"])
def engineered_update():
    """
    JSON:
    {
      "ENSURE_ID": "...",   # 必填，作为更新条件
      "updates": { <column>: <value>, ... }  # 需要更新的字段
    }
    """
    payload = request.get_json(silent=True) or {}
    ensure_id = payload.get("ENSURE_ID")
    updates = payload.get("updates") or {}
    cols, col_names = _get_table_columns(ENGINEERED_TABLE)
    if not cols:
        return jsonify({"error": f"Table '{ENGINEERED_TABLE}' does not exist"}), 400
    if not ensure_id:
        return jsonify({"error": "ENSURE_ID is required"}), 400

    updates = {k: v for k, v in updates.items() if k in col_names}
    if not updates:
        return jsonify({"error": "No valid columns to update"}), 400

    set_parts = []
    params = {}
    for idx, (k, v) in enumerate(updates.items()):
        ph = f"p{idx}"
        set_parts.append(f"`{k}` = :{ph}")
        params[ph] = v
    params["pk"] = ensure_id
    sql = text(f"UPDATE `{ENGINEERED_TABLE}` SET {', '.join(set_parts)} WHERE `ENSURE_ID` = :pk")

    try:
        with db.engine.begin() as conn:
            res = conn.execute(sql, params)
        return jsonify({"ok": True, "updated": res.rowcount}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@bp.route("/engineered_sup_trna/delete", methods=["POST"])
def engineered_delete():
    """
    JSON: { "ENSURE_ID": "..." }
    """
    payload = request.get_json(silent=True) or {}
    ensure_id = payload.get("ENSURE_ID")
    if not ensure_id:
        return jsonify({"error": "ENSURE_ID is required"}), 400

    sql = text(f"DELETE FROM `{ENGINEERED_TABLE}` WHERE `ENSURE_ID` = :ENSURE_ID")
    try:
        with db.engine.begin() as conn:
            res = conn.execute(sql, {"ENSURE_ID": ensure_id})
        return jsonify({"ok": True, "deleted": res.rowcount}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@bp.route("/", methods=["GET"])
def index():
    return "OK", 200

@bp.route("/health", methods=["GET"])
def health():
    return "OK", 200

@bp.route("/search", methods=["GET", "POST"])
@bp.route("/search/", methods=["GET", "POST"])
def search():
    # 健康检查或简单监控
    if request.method == "GET":
        return "OK", 200

    # POST：实际搜索
    data = request.get_json(silent=True) or {}

    try:
        topn = search_in_csvs(data)
        return jsonify(topn), 200
    except Exception as e:
        # 尽量返回可读错误
        return jsonify({"error": str(e)}), 400


@bp.route("/table_info", methods=["GET"])
def table_info():
    """
    GET /table_info?table=Engineered_sup_tRNA
    列出表的列名与类型，方便核对
    """
    table = request.args.get("table")
    if not table:
        return jsonify({"error": "missing table"}), 400

    insp = db.inspect(db.engine)
    if table not in insp.get_table_names():
        return jsonify({"error": f"Table '{table}' does not exist"}), 400

    cols = insp.get_columns(table)  # [{'name':..., 'type':...}, ...]
    return jsonify({
        "table": table,
        "columns": [{"name": c["name"], "type": str(c["type"])} for c in cols]
    })


@bp.route("/table_rows", methods=["POST"])
def table_rows():
    """
    JSON:
    {
      "table": "coding_variation_cancer",
      "page": 1,
      "page_size": 10,
      "search_text": "tp53",
      "search_column": "GENE_NAME",   # 空字符串表示全列
      "sort_by": "GENE_NAME",
      "sort_order": "asc",            # asc | desc | ascend | descend
      "case_insensitive": true
    }
    """
    data = request.get_json(silent=True) or {}
    table = data.get("table")
    if not table:
        return jsonify({"error": "missing table"}), 400

    page = int(data.get("page") or 1)
    page_size = int(data.get("page_size") or 10)
    page = max(1, page)
    page_size = max(1, min(page_size, 500))

    search_text = (data.get("search_text") or "").strip()
    search_column = data.get("search_column") or ""
    sort_by = data.get("sort_by") or ""
    sort_order = _normalize_sort_order(data.get("sort_order"))
    ci = bool(data.get("case_insensitive", True))
    use_fulltext = bool(data.get("use_fulltext", True))
    fulltext_index = data.get("fulltext_index") or "ft_all"

    insp = db.inspect(db.engine)
    if table not in insp.get_table_names():
        return jsonify({"error": f"Table '{table}' does not exist"}), 400

    columns = [c["name"] for c in insp.get_columns(table)]
    if not columns:
        return jsonify({"error": f"Table '{table}' has no columns"}), 400
    if search_column and search_column not in columns:
        return jsonify({"error": f"Column '{search_column}' not in table '{table}'"}), 400
    if sort_by and sort_by not in columns:
        return jsonify({"error": f"Column '{sort_by}' not in table '{table}'"}), 400
    if not sort_by:
        sort_by = columns[0]

    fulltext_columns = _get_fulltext_columns(table, fulltext_index) if use_fulltext else []
    where_sql, params, _ = _build_search_filter(
        search_text, search_column, columns, ci, use_fulltext, fulltext_columns
    )
    count_sql = text(f"SELECT COUNT(*) AS total FROM `{table}` {where_sql}")
    query_sql = (
        text(
            f"SELECT * FROM `{table}` {where_sql} "
            f"ORDER BY `{sort_by}` {sort_order} "
            f"LIMIT :limit OFFSET :offset"
        )
        .bindparams(bindparam("limit", type_=Integer))
        .bindparams(bindparam("offset", type_=Integer))
    )

    try:
        with db.engine.connect() as conn:
            total = conn.execute(count_sql, params).scalar() or 0
            rows = conn.execute(
                query_sql,
                {**params, "limit": page_size, "offset": (page - 1) * page_size},
            ).fetchall()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    try:
        results = [dict(r._mapping) for r in rows]
    except AttributeError:
        results = [dict(r) for r in rows]

    return jsonify(
        {
            "table": table,
            "page": page,
            "page_size": page_size,
            "total": int(total),
            "rows": results,
        }
    )


@bp.route("/table_stats", methods=["POST"])
def table_stats():
    """
    JSON:
    {
      "table": "coding_variation_cancer",
      "stats": ["allele_heatmap", "disease_wordcloud"],
      "search_text": "",
      "search_column": "",
      "case_insensitive": true
    }
    """
    data = request.get_json(silent=True) or {}
    table = data.get("table")
    if not table:
        return jsonify({"error": "missing table"}), 400

    stats = data.get("stats") or []
    if isinstance(stats, str):
        stats = [stats]
    if not stats:
        return jsonify({"error": "stats is required"}), 400

    search_text = (data.get("search_text") or "").strip()
    search_column = data.get("search_column") or ""
    ci = bool(data.get("case_insensitive", True))
    use_fulltext = bool(data.get("use_fulltext", True))
    fulltext_index = data.get("fulltext_index") or "ft_all"

    insp = db.inspect(db.engine)
    if table not in insp.get_table_names():
        return jsonify({"error": f"Table '{table}' does not exist"}), 400

    columns = [c["name"] for c in insp.get_columns(table)]
    if search_column and search_column not in columns:
        return jsonify({"error": f"Column '{search_column}' not in table '{table}'"}), 400

    fulltext_columns = _get_fulltext_columns(table, fulltext_index) if use_fulltext else []
    where_sql, params, _ = _build_search_filter(
        search_text, search_column, columns, ci, use_fulltext, fulltext_columns
    )
    result = {"table": table}

    try:
        with db.engine.connect() as conn:
            # Backward-compatible string stats
            if "allele_heatmap" in stats:
                required_cols = ["GENOMIC_REF_ALLELE", "GENOMIC_MUT_ALLELE"]
                for col in required_cols:
                    if col not in columns:
                        return jsonify({"error": f"Column '{col}' not in table '{table}'"}), 400
                extra = (
                    "`GENOMIC_REF_ALLELE` IS NOT NULL AND `GENOMIC_REF_ALLELE` <> '' "
                    "AND `GENOMIC_MUT_ALLELE` IS NOT NULL AND `GENOMIC_MUT_ALLELE` <> ''"
                )
                heatmap_where = where_sql
                if heatmap_where:
                    heatmap_where = f"{heatmap_where} AND {extra}"
                else:
                    heatmap_where = f"WHERE {extra}"
                sql = text(
                    f"SELECT `GENOMIC_REF_ALLELE` AS ref, "
                    f"`GENOMIC_MUT_ALLELE` AS mut, "
                    f"COUNT(*) AS count "
                    f"FROM `{table}` {heatmap_where} "
                    f"GROUP BY `GENOMIC_REF_ALLELE`, `GENOMIC_MUT_ALLELE`"
                )
                rows = conn.execute(sql, params).fetchall()
                result["allele_heatmap"] = [
                    {"ref": r[0], "mut": r[1], "count": int(r[2])} for r in rows
                ]

            if "disease_wordcloud" in stats:
                if "DISEASE" not in columns:
                    return jsonify({"error": f"Column 'DISEASE' not in table '{table}'"}), 400
                extra = "`DISEASE` IS NOT NULL AND `DISEASE` <> ''"
                disease_where = where_sql
                if disease_where:
                    disease_where = f"{disease_where} AND {extra}"
                else:
                    disease_where = f"WHERE {extra}"
                sql = text(f"SELECT `DISEASE` FROM `{table}` {disease_where}")
                rows = conn.execute(sql, params).fetchall()

                counter = {}
                for row in rows:
                    cell = row[0]
                    if cell is None:
                        continue
                    for part in re.split(r"[;/]", str(cell)):
                        name = part.strip()
                        if not name:
                            continue
                        counter[name] = counter.get(name, 0) + 1
                items = sorted(counter.items(), key=lambda x: x[1], reverse=True)
                result["disease_wordcloud"] = [
                    {"name": k, "value": int(v)} for k, v in items
                ]

            # New generic stats (dict-based)
            for stat in stats:
                if isinstance(stat, str):
                    continue
                if not isinstance(stat, dict):
                    return jsonify({"error": "stats items must be string or object"}), 400
                stat_type = (stat.get("type") or "").lower()
                name = stat.get("name") or stat_type
                filters = stat.get("filters") or []

                try:
                    filter_sql, filter_params = _build_stat_filters(filters, columns, ci)
                except ValueError as e:
                    return jsonify({"error": str(e)}), 400

                stat_where = _merge_where(where_sql, filter_sql)
                stat_params = {**params, **filter_params}

                if stat_type == "value_counts":
                    column = stat.get("column")
                    if not column or column not in columns:
                        return jsonify({"error": f"Column '{column}' not in table '{table}'"}), 400
                    extra = f"`{column}` IS NOT NULL AND `{column}` <> ''"
                    stat_where = _merge_where(stat_where, extra)
                    split_regex = stat.get("split_regex") or ""
                    top_n = int(stat.get("top_n") or 0)
                    result[name] = _value_counts(
                        conn, table, column, stat_where, stat_params, split_regex, top_n
                    )
                elif stat_type == "matrix_counts":
                    x_col = stat.get("x_column")
                    y_col = stat.get("y_column")
                    if not x_col or x_col not in columns:
                        return jsonify({"error": f"Column '{x_col}' not in table '{table}'"}), 400
                    if not y_col or y_col not in columns:
                        return jsonify({"error": f"Column '{y_col}' not in table '{table}'"}), 400
                    extra = (
                        f"`{x_col}` IS NOT NULL AND `{x_col}` <> '' "
                        f"AND `{y_col}` IS NOT NULL AND `{y_col}` <> ''"
                    )
                    stat_where = _merge_where(stat_where, extra)
                    result[name] = _matrix_counts(
                        conn, table, x_col, y_col, stat_where, stat_params
                    )
                elif stat_type == "codon_change_heatmap":
                    column = stat.get("column")
                    if not column or column not in columns:
                        return jsonify({"error": f"Column '{column}' not in table '{table}'"}), 400
                    extra = f"`{column}` IS NOT NULL AND `{column}` <> ''"
                    stat_where = _merge_where(stat_where, extra)
                    exclude_regex = stat.get("exclude_mut_regex") or ""
                    result[name] = _codon_change_heatmap(
                        conn, table, column, stat_where, stat_params, exclude_regex
                    )
                else:
                    return jsonify({"error": f"unsupported stats type '{stat_type}'"}), 400

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/table_fulltext_rebuild", methods=["POST"])
def table_fulltext_rebuild():
    """
    JSON:
    {
      "table": "coding_variation_cancer",
      "index_name": "ft_all",
      "columns": ["GENE_NAME", "ENSEMBL_ID", ...]
    }
    """
    data = request.get_json(silent=True) or {}
    table = data.get("table")
    if not table:
        return jsonify({"error": "missing table"}), 400

    index_name = data.get("index_name") or "ft_all"
    cols = data.get("columns") or []

    insp = db.inspect(db.engine)
    if table not in insp.get_table_names():
        return jsonify({"error": f"Table '{table}' does not exist"}), 400

    table_columns = [c["name"] for c in insp.get_columns(table)]
    if not cols:
        cols = [c for c in table_columns if c != "search_blob"]
    for col in cols:
        if col not in table_columns:
            return jsonify({"error": f"Column '{col}' not in table '{table}'"}), 400

    try:
        with db.engine.begin() as conn:
            # Drop existing fulltext index if present
            check = conn.execute(
                text(
                    "SELECT COUNT(*) FROM information_schema.statistics "
                    "WHERE TABLE_SCHEMA = :db AND TABLE_NAME = :table "
                    "AND INDEX_NAME = :idx AND INDEX_TYPE = 'FULLTEXT'"
                ),
                {"db": db.engine.url.database, "table": table, "idx": index_name},
            ).scalar()
            if check and int(check) > 0:
                conn.execute(text(f"DROP INDEX `{index_name}` ON `{table}`"))

            if len(cols) > 16:
                # Use a single search_blob column for wide tables
                if "search_blob" not in table_columns:
                    conn.execute(text(f"ALTER TABLE `{table}` ADD COLUMN `search_blob` TEXT"))
                    table_columns.append("search_blob")

                cols_sql = ", ".join(f"COALESCE(`{c}`, '')" for c in cols)
                conn.execute(
                    text(
                        f"UPDATE `{table}` SET `search_blob` = CONCAT_WS(' ', {cols_sql})"
                    )
                )

                conn.execute(
                    text(
                        f"CREATE FULLTEXT INDEX `{index_name}` ON `{table}` (`search_blob`)"
                    )
                )

                # Refresh triggers to keep search_blob updated on insert/update
                trig_ins = f"trg_{table}_bi_ft"
                trig_upd = f"trg_{table}_bu_ft"
                conn.execute(text(f"DROP TRIGGER IF EXISTS `{trig_ins}`"))
                conn.execute(text(f"DROP TRIGGER IF EXISTS `{trig_upd}`"))

                expr = f"CONCAT_WS(' ', {cols_sql})"
                conn.execute(
                    text(
                        f"CREATE TRIGGER `{trig_ins}` BEFORE INSERT ON `{table}` "
                        f"FOR EACH ROW SET NEW.`search_blob` = {expr}"
                    )
                )
                conn.execute(
                    text(
                        f"CREATE TRIGGER `{trig_upd}` BEFORE UPDATE ON `{table}` "
                        f"FOR EACH ROW SET NEW.`search_blob` = {expr}"
                    )
                )
                return jsonify(
                    {"ok": True, "index": index_name, "columns": ["search_blob"]}
                ), 200

            cols_sql = ", ".join(f"`{c}`" for c in cols)
            conn.execute(
                text(
                    f"CREATE FULLTEXT INDEX `{index_name}` ON `{table}` ({cols_sql})"
                )
            )

        return jsonify({"ok": True, "index": index_name, "columns": cols}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/search_table", methods=["POST"])
def search_table():
    """
    JSON:
    {
      "table": "Engineered_sup_tRNA",
      "column": "PTC_codon",
      "value": "UAA",
      "mode": "like",        # exact | like | in
      "limit": 50,
      "case_insensitive": true
    }
    """
    data = request.get_json(silent=True) or {}
    table = data.get("table")
    column = data.get("column")
    value = data.get("value")
    mode = (data.get("mode") or "exact").lower()
    limit = int(data.get("limit") or 50)
    ci = bool(data.get("case_insensitive", True))  # 默认不区分大小写

    if not all([table, column]) or value is None:
        return jsonify({"error": "missing table/column/value"}), 400

    # 1) 表/列校验（防注入 & 防拼错）
    insp = db.inspect(db.engine)
    if table not in insp.get_table_names():
        return jsonify({"error": f"Table '{table}' does not exist"}), 400

    columns = [c["name"] for c in insp.get_columns(table)]
    if column not in columns:
        return jsonify({"error": f"Column '{column}' not in table '{table}'"}), 400

    # 2) LIKE 值转义（避免 %/_ 被当通配符）
    def escape_like(s: str) -> str:
        return s.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

    # 3) 大小写控制（MySQL 多为不区分大小写；保险起见附加 COLLATE）
    collate = " COLLATE utf8mb4_general_ci" if ci else ""

    try:
        if mode == "exact":
            sql = text(
                f"SELECT * FROM `{table}` "
                f"WHERE `{column}`{collate} = :val "
                f"LIMIT :limit"
            ).bindparams(bindparam("limit", type_=Integer))
            params = {"val": value, "limit": limit}

        elif mode == "like":
            # 统一 CAST 为 CHAR，避免目标列为数值/JSON/BLOB 时 LIKE 报错
            like_val = f"%{escape_like(str(value))}%"
            sql = text(
                f"SELECT * FROM `{table}` "
                f"WHERE CAST(`{column}` AS CHAR){collate} LIKE :val ESCAPE '\\\\' "
                f"LIMIT :limit"
            ).bindparams(bindparam("limit", type_=Integer))
            params = {"val": like_val, "limit": limit}

        elif mode == "in":
            if not isinstance(value, (list, tuple, set)):
                return jsonify({"error": "value must be a list for mode='in'"}), 400
            placeholders = ",".join([f":v{i}" for i in range(len(value))]) or "NULL"
            sql = text(
                f"SELECT * FROM `{table}` "
                f"WHERE `{column}` IN ({placeholders}) "
                f"LIMIT :limit"
            ).bindparams(bindparam("limit", type_=Integer))
            params = {f"v{i}": v for i, v in enumerate(value)}
            params["limit"] = limit

        else:
            return jsonify({"error": f"unsupported mode '{mode}'"}), 400

        # 4) 执行 + 返回（SQLAlchemy 2.x：用 row._mapping）
        with db.engine.connect() as conn:
            rows = conn.execute(sql, params).fetchall()

        if not rows:
            return jsonify({
                "table": table,
                "column": column,
                "mode": mode,
                "count": 0,
                "results": []
            })

        try:
            results = [dict(r._mapping) for r in rows]
        except AttributeError:
            results = [dict(r) for r in rows]

        return jsonify({
            "table": table,
            "column": column,
            "mode": mode,
            "count": len(results),
            "results": results
        })

    except Exception as e:
        # 关键：把真实错误抛给前端，便于诊断
        return jsonify({"error": str(e)}), 500
