# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify
from sqlalchemy import text, bindparam, Integer
from . import db

from .logic.align import (
    search_in_csvs,  # 统一封装的业务逻辑入口
)

bp = Blueprint("routes", __name__)

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
