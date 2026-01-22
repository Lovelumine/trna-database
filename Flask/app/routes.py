# -*- coding: utf-8 -*-
from flask import (
    Blueprint,
    request,
    jsonify,
    send_file,
    current_app,
    Response,
    stream_with_context,
    after_this_request,
    redirect,
)
import csv
import json
import hashlib
import os
import threading
import time
import uuid
import zipfile
import math
import subprocess
from sqlalchemy import text, bindparam, Integer
import re
import requests
from . import db

from .logic.align import (
    search_in_csvs,
    search_in_mysql,
)

bp = Blueprint("routes", __name__)

EXPORT_TABLES = [
    "coding_variation_cancer",
    "coding_variation_genetic_disease",
    "nonsense_sup_rna",
    "frameshift_sup_trna",
    "Engineered_sup_tRNA",
    "function_and_modification",
    "aars_recognition",
    "ef_tu",
]

EXPORT_NAME_BY_TABLE = {
    "coding_variation_cancer": "Coding Variation in Cancer",
    "coding_variation_genetic_disease": "Coding Variation in Disease",
    "nonsense_sup_rna": "Nonsense Sup-RNA",
    "frameshift_sup_trna": "Frameshift sup-tRNA",
    "Engineered_sup_tRNA": "Engineered sup-tRNA",
    "function_and_modification": "Function of Modification",
    "aars_recognition": "aaRS Recognition",
    "ef_tu": "EF-Tu recognition site",
}

_EXPORT_TASK_LOCK = threading.Lock()
_EXPORT_TASKS = {}

_CHAT_LOCK = threading.Lock()
_CHAT_SESSIONS = {}
_EMBED_LOCK = threading.Lock()
_EMBED_INDEX = []
_EMBED_INDEX_MTIME = 0.0
_ALLOWED_CHAT_MODELS = {"qwen3:32b", "gemma3:27b"}

def _get_ollama_config():
    base = current_app.config.get("OLLAMA_BASE_URL") or "http://127.0.0.1:11434"
    model = current_app.config.get("OLLAMA_MODEL") or "qwen3:32b"
    timeout = current_app.config.get("OLLAMA_TIMEOUT") or 120
    system_prompt = current_app.config.get("OLLAMA_SYSTEM_PROMPT") or ""
    max_messages = current_app.config.get("OLLAMA_MAX_MESSAGES") or 20
    try:
        timeout = float(timeout)
    except Exception:
        timeout = 120
    try:
        max_messages = int(max_messages)
    except Exception:
        max_messages = 20
    return base, model, timeout, system_prompt, max_messages

def _select_ollama_model(requested: str, fallback: str) -> str:
    if not isinstance(requested, str):
        return fallback
    candidate = requested.strip()
    if not candidate:
        return fallback
    return candidate if candidate in _ALLOWED_CHAT_MODELS else fallback

def _get_chat_session(chat_id: str):
    with _CHAT_LOCK:
        session = _CHAT_SESSIONS.setdefault(chat_id, {"messages": [], "updated_at": time.time()})
        session["updated_at"] = time.time()
        return session

def _append_chat_message(chat_id: str, role: str, content: str, max_messages: int):
    if not content:
        return
    with _CHAT_LOCK:
        session = _CHAT_SESSIONS.setdefault(chat_id, {"messages": [], "updated_at": time.time()})
        session["messages"].append({"role": role, "content": content})
        if max_messages and len(session["messages"]) > max_messages:
            session["messages"] = session["messages"][-max_messages:]
        session["updated_at"] = time.time()

def _build_ollama_messages(session_messages, system_prompt: str, extra_system: str = ""):
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    if extra_system:
        messages.append({"role": "system", "content": extra_system})
    messages.extend(session_messages or [])
    return messages

def _ollama_stream(base: str, model: str, messages: list, timeout: float):
    url = base.rstrip("/") + "/api/chat"
    payload = {"model": model, "messages": messages, "stream": True}
    resp = requests.post(url, json=payload, stream=True, timeout=timeout)
    resp.raise_for_status()
    for line in resp.iter_lines(decode_unicode=True):
        if not line:
            continue
        data = json.loads(line)
        if data.get("error"):
            raise RuntimeError(data["error"])
        msg = data.get("message") or {}
        content = msg.get("content") or ""
        done = bool(data.get("done"))
        yield content, done

def _get_embedding_config():
    enable = current_app.config.get("EMBEDDING_ENABLE", True)
    model = current_app.config.get("EMBEDDING_MODEL") or "nomic-embed-text:latest"
    index_path = current_app.config.get("EMBEDDING_INDEX_PATH") or ""
    auto_build = current_app.config.get("EMBEDDING_AUTO_BUILD", False)
    max_rows = int(current_app.config.get("EMBEDDING_MAX_ROWS") or 8000)
    per_table = int(current_app.config.get("EMBEDDING_PER_TABLE") or 2000)
    docs_dir = current_app.config.get("EMBEDDING_DOCS_DIR") or ""
    docs_max_chunks = int(current_app.config.get("EMBEDDING_DOCS_MAX_CHUNKS") or 120)
    docs_chunk_size = int(current_app.config.get("EMBEDDING_DOCS_CHUNK_SIZE") or 1200)
    docs_chunk_overlap = int(current_app.config.get("EMBEDDING_DOCS_CHUNK_OVERLAP") or 150)
    return (
        enable,
        model,
        index_path,
        auto_build,
        max_rows,
        per_table,
        docs_dir,
        docs_max_chunks,
        docs_chunk_size,
        docs_chunk_overlap,
    )

def _ollama_embed(base: str, model: str, text_value: str, timeout: float):
    url = base.rstrip("/") + "/api/embeddings"
    payload = {"model": model, "prompt": text_value}
    resp = requests.post(url, json=payload, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    embedding = data.get("embedding")
    if not isinstance(embedding, list):
        raise RuntimeError("embedding response missing vector")
    return embedding

def _cosine_similarity(a, b):
    if not a or not b:
        return 0.0
    if len(a) != len(b):
        return 0.0
    dot = 0.0
    na = 0.0
    nb = 0.0
    for i in range(len(a)):
        va = float(a[i])
        vb = float(b[i])
        dot += va * vb
        na += va * va
        nb += vb * vb
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (math.sqrt(na) * math.sqrt(nb))

def _split_text(text: str, chunk_size: int, overlap: int):
    s = str(text or "").strip()
    if not s:
        return []
    if chunk_size <= 0:
        return [s]
    if overlap < 0:
        overlap = 0
    chunks = []
    start = 0
    while start < len(s):
        end = min(len(s), start + chunk_size)
        chunks.append(s[start:end])
        if end >= len(s):
            break
        start = max(0, end - overlap)
    return chunks

def _markdown_to_text(markdown: str):
    s = str(markdown or "")
    # Keep image URLs so the assistant knows screenshots exist.
    s = re.sub(r"!\[[^\]]*\]\(([^)]+)\)", r"Image: \1", s)
    # Replace links with text + url.
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", s)
    # Strip code fences.
    s = re.sub(r"```[\s\S]*?```", "", s)
    # Basic cleanup.
    s = re.sub(r"[\t\r]+", " ", s)
    return s

def _read_pdf_text(path: str) -> str:
    try:
        from pypdf import PdfReader
    except Exception:
        try:
            from PyPDF2 import PdfReader
        except Exception:
            PdfReader = None
    try:
        if PdfReader:
            reader = PdfReader(path)
            parts = []
            for page in reader.pages:
                try:
                    parts.append(page.extract_text() or "")
                except Exception:
                    continue
            return "\n".join(parts)
    except Exception:
        pass
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", path, "-"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return result.stdout or ""
    except Exception:
        return ""

def _iter_doc_chunks(docs_dir: str, max_chunks: int, chunk_size: int, overlap: int):
    if not docs_dir or not os.path.isdir(docs_dir):
        return []
    items = []
    files = [f for f in os.listdir(docs_dir) if f.lower().endswith((".md", ".pdf"))]
    files.sort()
    for fname in files:
        fpath = os.path.join(docs_dir, fname)
        text = ""
        if fname.lower().endswith(".md"):
            try:
                with open(fpath, "r", encoding="utf-8") as handle:
                    raw = handle.read()
                text = _markdown_to_text(raw)
            except Exception:
                text = ""
        else:
            text = _read_pdf_text(fpath)
        if not text:
            continue
        header = f"Doc: {fname}\n"
        chunks = _split_text(header + text, chunk_size, overlap)
        for chunk in chunks:
            items.append({"source": f"public/docs/{fname}", "text": chunk})
            if max_chunks and len(items) >= max_chunks:
                return items
    return items

def _load_embedding_index(path: str):
    global _EMBED_INDEX, _EMBED_INDEX_MTIME
    if not path or not os.path.exists(path):
        return []
    mtime = os.path.getmtime(path)
    with _EMBED_LOCK:
        if _EMBED_INDEX and _EMBED_INDEX_MTIME == mtime:
            return _EMBED_INDEX
        items = []
        with open(path, "r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    items.append(json.loads(line))
                except Exception:
                    continue
        _EMBED_INDEX = items
        _EMBED_INDEX_MTIME = mtime
        return items

def _build_embedding_index(base: str, model: str, timeout: float):
    (
        enable,
        _,
        index_path,
        _,
        max_rows,
        per_table,
        docs_dir,
        docs_max_chunks,
        docs_chunk_size,
        docs_chunk_overlap,
    ) = _get_embedding_config()
    if not enable or not index_path:
        return []
    os.makedirs(os.path.dirname(index_path), exist_ok=True)

    rag_tables = current_app.config.get("RAG_TABLES") or ""
    if rag_tables:
        tables = [t.strip() for t in rag_tables.split(",") if t.strip()]
    else:
        tables = list(EXPORT_TABLES)

    written = 0
    items = []
    try:
        with db.engine.connect() as conn:
            for table in tables:
                cols, col_names = _get_table_columns(table)
                if not col_names:
                    continue
                limit = min(per_table, max_rows - written)
                if limit <= 0:
                    break
                sql = text(f"SELECT * FROM `{table}` LIMIT {int(limit)}")
                try:
                    rows = conn.execute(sql).fetchall()
                except Exception:
                    continue
                for row in rows:
                    fields = _pick_row_fields(row, col_names, 10, 300)
                    if not fields:
                        continue
                    text_parts = [f"{k}: {v}" for k, v in fields]
                    text_value = f"table: {table}\n" + "\n".join(text_parts)
                    try:
                        emb = _ollama_embed(base, model, text_value, timeout)
                    except Exception:
                        continue
                    record = {
                        "type": "row",
                        "table": table,
                        "fields": fields,
                        "embedding": emb,
                    }
                    items.append(record)
                    written += 1
                    if written >= max_rows:
                        break
                if written >= max_rows:
                    break
    except Exception:
        pass

    if written < max_rows:
        doc_chunks = _iter_doc_chunks(
            docs_dir,
            docs_max_chunks,
            docs_chunk_size,
            docs_chunk_overlap,
        )
        for chunk in doc_chunks:
            if written >= max_rows:
                break
            try:
                emb = _ollama_embed(base, model, chunk["text"], timeout)
            except Exception:
                continue
            record = {
                "type": "doc",
                "source": chunk["source"],
                "text": _compact_value(chunk["text"], 400),
                "embedding": emb,
            }
            items.append(record)
            written += 1

    with open(index_path, "w", encoding="utf-8") as handle:
        for item in items:
            handle.write(json.dumps(item, ensure_ascii=False) + "\n")

    with _EMBED_LOCK:
        _EMBED_INDEX[:] = items
        _EMBED_INDEX_MTIME = os.path.getmtime(index_path)
    return items

def _semantic_retrieve(question: str):
    enable, model, index_path, auto_build, _, _, _, _, _, _ = _get_embedding_config()
    if not enable:
        return "", ""
    base, _, timeout, _, _ = _get_ollama_config()

    index = _load_embedding_index(index_path)
    if not index and auto_build:
        index = _build_embedding_index(base, model, timeout)
    if not index:
        return "", ""

    qtext = _normalize_query_text(question, 200)
    if not qtext:
        return "", ""

    try:
        qvec = _ollama_embed(base, model, qtext, timeout)
    except Exception:
        return "", ""

    scored = []
    for item in index:
        sim = _cosine_similarity(qvec, item.get("embedding") or [])
        scored.append((sim, item))
    scored.sort(key=lambda x: x[0], reverse=True)

    max_results = int(current_app.config.get("RAG_MAX_RESULTS") or 6)
    top_items = [it for _, it in scored[:max_results] if _ > 0]
    if not top_items:
        return "", ""

    context_lines = []
    evidence_lines = []
    for idx, item in enumerate(top_items, 1):
        if item.get("type") == "doc":
            source = item.get("source") or "docs"
            snippet = item.get("text") or ""
            context_lines.append(f"[{idx}] doc: {source}; {snippet}")
            evidence_lines.append(f"{idx}. Doc `{source}` — {snippet}")
        else:
            fields = item.get("fields") or []
            context_lines.append(
                f"[{idx}] table: {item.get('table')}; "
                + "; ".join(f"{k}: {v}" for k, v in fields)
            )
            evidence_lines.append(
                f"{idx}. Table `{item.get('table')}` — "
                + "; ".join(f"{k}: {v}" for k, v in fields)
            )

    context = "Retrieved records (semantic match):\n" + "\n".join(context_lines)
    evidence = "\n".join(evidence_lines)
    return context, evidence

def _normalize_query_text(text: str, max_len: int = 200) -> str:
    s = str(text or "").strip()
    if len(s) > max_len:
        s = s[:max_len]
    return s

def _find_column(columns: list, keywords: list) -> str:
    for col in columns:
        low = str(col).lower()
        if any(k in low for k in keywords):
            return col
    return ""

def _compact_value(value, max_len: int) -> str:
    if value is None:
        return ""
    s = str(value)
    s = s.replace("\n", " ").replace("\r", " ").strip()
    if len(s) > max_len:
        return s[: max_len - 3] + "..."
    return s

def _doc_snippet(path: str, max_len: int = 600) -> str:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            raw = handle.read()
    except Exception:
        return ""
    text = _markdown_to_text(raw)
    text = text.strip()
    if not text:
        return ""
    if len(text) > max_len:
        return text[: max_len - 3] + "..."
    return text

def _natural_doc_context(question: str):
    if not re.search(r"natural|天然|sup-?trna|sup trna", str(question or ""), flags=re.IGNORECASE):
        return "", ""
    docs_dir = current_app.config.get("EMBEDDING_DOCS_DIR") or ""
    if not docs_dir:
        return "", ""
    path = os.path.join(docs_dir, "3-Natural Sup-tRNA.md")
    if not os.path.exists(path):
        return "", ""
    snippet = _doc_snippet(path, 700)
    if not snippet:
        return "", ""
    context = "Natural sup-tRNA definition and features (from Help docs):\n" + snippet
    evidence = f"Doc `public/docs/3-Natural Sup-tRNA.md` — {snippet}"
    return context, evidence

def _paper_meta_context(question: str):
    if not re.search(r"author|authors|作者|论文|paper|pmid|doi|发表", str(question or ""), flags=re.IGNORECASE):
        return "", ""
    docs_dir = current_app.config.get("EMBEDDING_DOCS_DIR") or ""
    if not docs_dir:
        return "", ""
    path = os.path.join(docs_dir, "0-ENSURE-Overview.md")
    if not os.path.exists(path):
        return "", ""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            content = handle.read()
    except Exception:
        return "", ""

    authors_match = re.search(r"^Authors:\\s*(.+)$", content, flags=re.MULTILINE)
    doi_match = re.search(r"DOI\\s+([^,\\n]+)", content, flags=re.IGNORECASE)
    pmid_match = re.search(r"PMID\\s+(\\d+)", content, flags=re.IGNORECASE)

    parts = []
    evidence = []
    if authors_match:
        authors = authors_match.group(1).strip()
        parts.append(f"Authors: {authors}")
        evidence.append(f"Doc `public/docs/0-ENSURE-Overview.md` — Authors: {authors}")
    if doi_match:
        doi = doi_match.group(1).strip()
        parts.append(f"DOI: {doi}")
        evidence.append(f"Doc `public/docs/0-ENSURE-Overview.md` — DOI: {doi}")
    if pmid_match:
        pmid = pmid_match.group(1).strip()
        parts.append(f"PMID: {pmid}")
        evidence.append(f"Doc `public/docs/0-ENSURE-Overview.md` — PMID: {pmid}")

    if not parts:
        return "", ""
    context = "ENSURE paper metadata:\n" + "\n".join(parts)
    return context, "\n".join(evidence)

def _is_count_question(text: str) -> bool:
    return bool(re.search(r"\bhow many\b|count|数量|多少|有几", str(text or ""), flags=re.IGNORECASE))

def _is_identity_question(text: str) -> bool:
    return bool(re.search(r"你是谁|你叫什么|名字|who are you|your name", str(text or ""), flags=re.IGNORECASE))

def _is_greeting(text: str) -> bool:
    return bool(re.search(r"\bhi\b|\bhello\b|你好|您好|hey", str(text or ""), flags=re.IGNORECASE))

def _mentions_platform(text: str) -> bool:
    return bool(re.search(r"\bensure\b|数据库|网站|平台|this site|this database", str(text or ""), flags=re.IGNORECASE))

def _evidence_required(text: str) -> bool:
    if _is_identity_question(text) or _is_greeting(text):
        return False
    if _is_count_question(text):
        return True
    if re.search(r"作者|authors|pmid|doi|发表|哪年|when was|published|publication", str(text or ""), flags=re.IGNORECASE):
        return True
    if re.search(r"条目|记录|统计|页面|功能|特点|特征|操作|帮助|文档|怎么用|如何使用|下载|搜索|blast|api|物种|species", str(text or ""), flags=re.IGNORECASE):
        return True
    if re.search(r"ENSURE[_-]?\\d+|\\bpmid\\b", str(text or ""), flags=re.IGNORECASE):
        return True
    if _mentions_platform(text):
        return True
    return False

def _strict_allowed_response(question: str) -> str:
    if _is_identity_question(question):
        return "我是Yingying（荧荧），ENSURE 数据库的助手。"
    if _is_greeting(question):
        return "你好，我是Yingying（荧荧）。可以帮你查询 ENSURE 的内容。"
    return ""

def _format_evidence_block(evidence: str) -> str:
    if evidence:
        return "\n\nSearch results:\n" + evidence
    return "\n\nSearch results:\nNo relevant records found."

def _count_table_rows(conn, table: str) -> int:
    sql = text(f"SELECT COUNT(*) FROM `{table}`")
    try:
        return int(conn.execute(sql).scalar() or 0)
    except Exception:
        return 0

def _rag_count(question: str):
    if not _is_count_question(question):
        return "", ""

    q = str(question or "").lower()
    targets = []
    include_natural = any(k in q for k in ["natural", "天然", "自然"])
    include_engineered = any(k in q for k in ["engineered", "工程", "人工", "设计"])
    include_nonsense = any(k in q for k in ["nonsense", "无义", "终止"])
    include_frameshift = any(k in q for k in ["frameshift", "移码"])

    if include_nonsense:
        targets.append("nonsense_sup_rna")
    if include_frameshift:
        targets.append("frameshift_sup_trna")
    if include_engineered:
        targets.append("Engineered_sup_tRNA")

    if include_natural and "nonsense_sup_rna" not in targets:
        targets.append("nonsense_sup_rna")
    if include_natural and "frameshift_sup_trna" not in targets:
        targets.append("frameshift_sup_trna")

    if ("sup-trna" in q or "sup trna" in q or "sup-tRNA".lower() in q) and not targets:
        targets = ["nonsense_sup_rna", "frameshift_sup_trna", "Engineered_sup_tRNA"]

    if not targets:
        return "", ""

    counts = {}
    with db.engine.connect() as conn:
        for table in targets:
            counts[table] = _count_table_rows(conn, table)

    context_lines = []
    evidence_lines = []

    if "nonsense_sup_rna" in counts or "frameshift_sup_trna" in counts:
        natural_total = counts.get("nonsense_sup_rna", 0) + counts.get("frameshift_sup_trna", 0)
        context_lines.append(f"Natural sup-tRNA total (nonsense + frameshift) = {natural_total}")
        evidence_lines.append(f"Natural sup-tRNA total = {natural_total} (nonsense_sup_rna + frameshift_sup_trna)")

    if "Engineered_sup_tRNA" in counts:
        context_lines.append(f"Engineered sup-tRNA total = {counts.get('Engineered_sup_tRNA', 0)}")
        evidence_lines.append(f"Table `Engineered_sup_tRNA` count = {counts.get('Engineered_sup_tRNA', 0)}")

    if len(counts) > 0:
        for table, count in counts.items():
            evidence_lines.append(f"Table `{table}` count = {count}")

    if not context_lines:
        return "", ""

    context = "Live counts from ENSURE database tables:\n" + "\n".join(context_lines)
    evidence = "\n".join(dict.fromkeys(evidence_lines))
    return context, evidence

def _parse_species_values(values: list):
    species = set()
    for val in values:
        if not val:
            continue
        raw = str(val)
        parts = re.split(r"[;,/|]|\\band\\b", raw, flags=re.IGNORECASE)
        for part in parts:
            name = part.strip()
            if not name:
                continue
            species.add(name)
    return sorted(species)

def _rag_species(question: str):
    if not re.search(r"物种|species", str(question or ""), flags=re.IGNORECASE):
        return "", ""
    if not re.search(r"natural|天然|sup-?trna|sup trna", str(question or ""), flags=re.IGNORECASE):
        return "", ""

    tables = ["nonsense_sup_rna", "frameshift_sup_trna"]
    max_items = int(current_app.config.get("RAG_SPECIES_MAX") or 30)
    all_species = set()
    evidence_lines = []

    with db.engine.connect() as conn:
        for table in tables:
            cols, col_names = _get_table_columns(table)
            if not col_names:
                continue
            col = _find_column(col_names, ["species", "organism"])
            if not col:
                continue
            sql = text(
                f"SELECT DISTINCT `{col}` FROM `{table}` "
                f"WHERE `{col}` IS NOT NULL AND `{col}` <> '' LIMIT 500"
            )
            try:
                rows = conn.execute(sql).fetchall()
            except Exception:
                continue
            values = [r[0] for r in rows]
            species = _parse_species_values(values)
            for s in species:
                all_species.add(s)
            sample = ", ".join(species[: min(len(species), max_items)])
            evidence_lines.append(f"Table `{table}` column `{col}` sample species: {sample}")

    if not all_species:
        return "", ""

    species_list = sorted(all_species)
    shown = species_list[: max_items]
    context = (
        "Species list for natural sup-tRNAs (sample):\n"
        + ", ".join(shown)
    )
    evidence = "\n".join(evidence_lines)
    return context, evidence

def _pick_row_fields(row, columns: list, max_fields: int, max_len: int):
    row_map = dict(row._mapping) if hasattr(row, "_mapping") else dict(row)
    priority = [
        "ENSURE_ID",
        "PMID",
        "Gene",
        "GENE",
        "GENE_NAME",
        "Variant",
        "VARIANT",
        "Mutation",
        "MUTATION",
        "Disease",
        "DISEASE",
        "Cancer",
        "CANCER",
        "Organism",
        "ORGANISM",
        "Species",
        "SPECIES",
        "tRNA",
        "TRNA",
        "AA",
        "Amino",
    ]
    picked = []
    seen = set()

    for key in priority:
        for col in columns:
            if col in seen:
                continue
            if str(col).lower() == str(key).lower() and row_map.get(col) not in (None, ""):
                picked.append((col, row_map.get(col)))
                seen.add(col)
        if len(picked) >= max_fields:
            break

    if len(picked) < max_fields:
        for col in columns:
            if col in seen:
                continue
            val = row_map.get(col)
            if val in (None, ""):
                continue
            picked.append((col, val))
            seen.add(col)
            if len(picked) >= max_fields:
                break

    return [(k, _compact_value(v, max_len)) for k, v in picked]

def _rag_retrieve(question: str):
    if not current_app.config.get("RAG_ENABLE", True):
        return "", ""

    count_context, count_evidence = _rag_count(question)
    paper_context, paper_evidence = _paper_meta_context(question)
    natural_context, natural_evidence = _natural_doc_context(question)
    species_context, species_evidence = _rag_species(question)
    semantic_context, semantic_evidence = _semantic_retrieve(question)

    search_text = _normalize_query_text(question, 200)
    if not search_text:
        context_parts = [
            c for c in [
                paper_context,
                count_context,
                natural_context,
                species_context,
                semantic_context
            ] if c
        ]
        evidence_parts = [
            e for e in [
                paper_evidence,
                count_evidence,
                natural_evidence,
                species_evidence,
                semantic_evidence
            ] if e
        ]
        return "\n\n".join(context_parts), "\n".join(evidence_parts)

    rag_tables = current_app.config.get("RAG_TABLES") or ""
    if rag_tables:
        tables = [t.strip() for t in rag_tables.split(",") if t.strip()]
    else:
        tables = list(EXPORT_TABLES)

    max_results = int(current_app.config.get("RAG_MAX_RESULTS") or 6)
    per_table = int(current_app.config.get("RAG_PER_TABLE") or 2)
    max_len = int(current_app.config.get("RAG_MAX_FIELD_LEN") or 160)
    max_fields = 6

    ensure_ids = re.findall(r"ENSURE[_-]?\d+", search_text, flags=re.IGNORECASE)
    pmids = re.findall(r"\b\d{6,9}\b", search_text)

    results = []
    context_lines = []

    with db.engine.connect() as conn:
        for table in tables:
            cols, col_names = _get_table_columns(table)
            if not col_names:
                continue

            search_column = ""
            search_values = None
            if ensure_ids:
                ensure_col = _find_column(col_names, ["ensure_id", "ensureid", "ensure"])
                if ensure_col:
                    search_column = ensure_col
                    search_values = ensure_ids
            if not search_column and pmids:
                pmid_col = _find_column(col_names, ["pmid", "pubmed"])
                if pmid_col:
                    search_column = pmid_col
                    search_values = pmids

            use_fulltext = True
            fulltext_cols = _get_fulltext_columns(table, "ft_all") if use_fulltext else []

            where_sql, params, used_fulltext = _build_search_filter(
                search_text,
                search_column,
                col_names,
                True,
                use_fulltext,
                fulltext_cols,
                search_values=search_values,
            )
            if not where_sql:
                continue

            order_sql = ""
            if used_fulltext and fulltext_cols:
                cols_sql = ", ".join(f"`{c}`" for c in fulltext_cols)
                order_sql = f" ORDER BY MATCH({cols_sql}) AGAINST (:ft IN BOOLEAN MODE) DESC"

            limit = max(1, per_table)
            sql = text(f"SELECT * FROM `{table}` {where_sql}{order_sql} LIMIT {limit}")
            try:
                rows = conn.execute(sql, params).fetchall()
            except Exception:
                continue

            for row in rows:
                fields = _pick_row_fields(row, col_names, max_fields, max_len)
                if not fields:
                    continue
                results.append({"table": table, "fields": fields})
                context_lines.append(
                    f"[{len(results)}] table: {table}; "
                    + "; ".join(f"{k}: {v}" for k, v in fields)
                )
                if len(results) >= max_results:
                    break
            if len(results) >= max_results:
                break

    if not results:
        context_parts = [
            c for c in [
                paper_context,
                count_context,
                natural_context,
                species_context,
                semantic_context
            ] if c
        ]
        evidence_parts = [
            e for e in [
                paper_evidence,
                count_evidence,
                natural_evidence,
                species_evidence,
                semantic_evidence
            ] if e
        ]
        return "\n\n".join(context_parts), "\n".join(evidence_parts)

    context = "Retrieved records (may be partial):\n" + "\n".join(context_lines)
    evidence_lines = [
        f"{idx}. Table `{item['table']}` — "
        + "; ".join(f"{k}: {v}" for k, v in item["fields"])
        for idx, item in enumerate(results, 1)
    ]
    evidence = "\n".join(evidence_lines)

    merged_contexts = [
        c for c in [
            paper_context,
            count_context,
            natural_context,
            species_context,
            semantic_context,
            context
        ] if c
    ]
    merged_evidence = [
        e for e in [
            paper_evidence,
            count_evidence,
            natural_evidence,
            species_evidence,
            semantic_evidence,
            evidence
        ] if e
    ]
    context = "\n\n".join(merged_contexts)
    evidence = "\n".join(merged_evidence)
    return context, evidence

# ---------------------- 通用工具 ----------------------

def _get_table_columns(table: str):
    insp = db.inspect(db.engine)
    if table not in insp.get_table_names():
        return None, None
    cols = insp.get_columns(table)  # [{'name':..., 'type':...}, ...]
    col_names = [c["name"] for c in cols]
    return cols, col_names

def _get_export_cache_dir() -> str:
    cache_dir = current_app.config.get("EXPORT_CACHE_DIR")
    if not cache_dir:
        cache_dir = os.path.join(os.path.dirname(__file__), "cache", "exports")
    return cache_dir

def _normalize_minio_endpoint(endpoint: str) -> str:
    if not endpoint:
        return ""
    return (
        endpoint.replace("https://", "")
        .replace("http://", "")
        .rstrip("/")
    )

def _get_minio_client():
    endpoint = current_app.config.get("MINIO_ENDPOINT") or ""
    access_key = current_app.config.get("MINIO_ACCESS_KEY") or ""
    secret_key = current_app.config.get("MINIO_SECRET_KEY") or ""
    if not (endpoint and access_key and secret_key):
        return None
    try:
        from minio import Minio
    except Exception as exc:  # pragma: no cover - environment-specific
        raise RuntimeError("minio package is not installed") from exc
    secure = current_app.config.get("MINIO_SECURE")
    if secure is None:
        secure = str(endpoint).startswith("https://")
    endpoint = _normalize_minio_endpoint(endpoint)
    return Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=secure)

def _minio_object_key(table: str, fmt: str, signature: str) -> str:
    prefix = current_app.config.get("MINIO_EXPORT_PREFIX") or "exports"
    prefix = prefix.strip("/")
    return f"{prefix}/{table}/{table}_{fmt}_{signature}.{fmt}"

def _get_minio_public_base() -> str:
    base = current_app.config.get("MINIO_PUBLIC_BASE") or ""
    if base:
        return base.rstrip("/")
    endpoint = current_app.config.get("MINIO_ENDPOINT") or ""
    bucket = current_app.config.get("MINIO_BUCKET") or ""
    if not (endpoint and bucket):
        return ""
    secure = current_app.config.get("MINIO_SECURE")
    scheme = "https" if secure is True or str(endpoint).startswith("https://") else "http"
    endpoint = _normalize_minio_endpoint(endpoint)
    return f"{scheme}://{endpoint}/{bucket}"

def _minio_public_url(key: str) -> str:
    base = _get_minio_public_base()
    if not base:
        return ""
    return f"{base}/{key}"

def _minio_stream_response(client, bucket: str, key: str, table: str, fmt: str):
    obj = client.get_object(bucket, key)

    def generate():
        try:
            for data in obj.stream(32 * 1024):
                yield data
        finally:
            obj.close()
            obj.release_conn()

    mimetype = (
        "text/csv; charset=utf-8"
        if fmt == "csv"
        else "text/tab-separated-values; charset=utf-8"
    )
    headers = {
        "Content-Disposition": f'attachment; filename="{table}.{fmt}"'
    }
    return Response(stream_with_context(generate()), mimetype=mimetype, headers=headers)

def _minio_object_status(client, bucket: str, key: str):
    try:
        client.stat_object(bucket, key)
        return True, None
    except Exception as exc:
        try:
            from minio.error import S3Error
            if isinstance(exc, S3Error):
                if exc.code in ("NoSuchKey", "NoSuchObject", "NoSuchBucket"):
                    return False, None
        except Exception:
            pass
        return False, str(exc)

def _get_table_signature(table: str) -> str:
    with db.engine.connect() as conn:
        try:
            meta = conn.execute(
                text("SELECT updated_at FROM table_meta WHERE table_name = :table"),
                {"table": table},
            ).fetchone()
            if meta and meta[0]:
                return hashlib.sha1(
                    f"{table}|{meta[0]}".encode("utf-8")
                ).hexdigest()
        except Exception:
            pass

        db_name = db.engine.url.database
        sql = text(
            "SELECT UPDATE_TIME, TABLE_ROWS, DATA_LENGTH, INDEX_LENGTH "
            "FROM information_schema.tables "
            "WHERE TABLE_SCHEMA = :db AND TABLE_NAME = :table"
        )
        row = conn.execute(sql, {"db": db_name, "table": table}).fetchone()
    if not row:
        return ""
    parts = [
        table,
        str(row[0] or ""),
        str(row[1] or 0),
        str(row[2] or 0),
        str(row[3] or 0),
    ]
    return hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()

def _csv_safe(value):
    if value is None:
        return ""
    if isinstance(value, (bytes, bytearray)):
        return value.decode("utf-8", errors="replace")
    return value

def _export_table_to_local(
    table: str,
    fmt: str,
    signature: str,
    export_dir: str,
    task_key: str = None,
) -> str:
    os.makedirs(export_dir, exist_ok=True)
    cache_name = f"{table}_{fmt}_{signature}.{fmt}"
    cache_path = os.path.join(export_dir, cache_name)
    delimiter = "," if fmt == "csv" else "\t"
    tmp_path = f"{cache_path}.tmp-{os.getpid()}"
    sql = text(f"SELECT * FROM `{table}`")
    total = None
    if task_key:
        try:
            with db.engine.connect() as conn:
                total = conn.execute(text(f"SELECT COUNT(*) FROM `{table}`")).scalar() or 0
            _update_task(task_key, progress=1, message="exporting rows")
        except Exception:
            total = None
    with db.engine.connect() as conn:
        result = conn.execution_options(stream_results=True).execute(sql)
        with open(tmp_path, "w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter=delimiter, lineterminator="\n")
            writer.writerow(result.keys())
            row_count = 0
            for row in result:
                writer.writerow([_csv_safe(v) for v in row])
                row_count += 1
                if task_key and total:
                    if row_count % 1000 == 0 or row_count == total:
                        progress = int((row_count / total) * 90)
                        _update_task(task_key, progress=progress)
    os.replace(tmp_path, cache_path)
    return cache_path

def _ensure_table_export(
    table: str,
    fmt: str,
    signature: str = None,
    task_key: str = None,
) -> str:
    if signature is None:
        signature = _get_table_signature(table)
    if not signature:
        raise RuntimeError("could not determine table signature")
    export_dir = _get_export_cache_dir()
    minio_client = _get_minio_client()
    bucket = current_app.config.get("MINIO_BUCKET")
    minio_key = _minio_object_key(table, fmt, signature)
    public_url = _minio_public_url(minio_key)
    if minio_client and bucket and public_url:
        exists, err = _minio_object_status(minio_client, bucket, minio_key)
        if err:
            raise RuntimeError(f"minio stat failed: {err}")
        if exists:
            if task_key:
                _update_task(task_key, progress=100, message="ready")
            return public_url
    cache_path = _export_table_to_local(table, fmt, signature, export_dir, task_key=task_key)
    if minio_client and bucket and public_url:
        if task_key:
            _update_task(task_key, progress=95, message="uploading")
        minio_client.fput_object(
            bucket,
            minio_key,
            cache_path,
            content_type="text/csv" if fmt == "csv" else "text/tab-separated-values",
        )
        try:
            os.remove(cache_path)
        except OSError:
            pass
        if task_key:
            _update_task(task_key, progress=100, message="ready")
        return public_url
    return cache_path

def _get_table_signature_map(tables: list) -> dict:
    signatures = {}
    for table in tables:
        signatures[table] = _get_table_signature(table)
    return signatures

def _bundle_signature_from_map(signature_map: dict, fmt: str) -> str:
    parts = [f"{table}:{signature_map[table]}" for table in sorted(signature_map)]
    raw = "|".join(parts + [fmt])
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()

def _get_bundle_signature(tables: list, fmt: str) -> str:
    signature_map = _get_table_signature_map(tables)
    return _bundle_signature_from_map(signature_map, fmt)

def _bundle_object_key(fmt: str, signature: str) -> str:
    prefix = current_app.config.get("MINIO_EXPORT_PREFIX") or "exports"
    prefix = prefix.strip("/")
    return f"{prefix}/bundles/all_{fmt}_{signature}.zip"

def _ensure_bundle_export(
    fmt: str,
    signature_map: dict = None,
    task_key: str = None,
) -> str:
    if signature_map is None:
        signature_map = _get_table_signature_map(EXPORT_TABLES)
    signature = _bundle_signature_from_map(signature_map, fmt)
    export_dir = _get_export_cache_dir()
    minio_client = _get_minio_client()
    bucket = current_app.config.get("MINIO_BUCKET")
    bundle_key = _bundle_object_key(fmt, signature)
    public_url = _minio_public_url(bundle_key)
    if minio_client and bucket and public_url:
        exists, err = _minio_object_status(minio_client, bucket, bundle_key)
        if err:
            raise RuntimeError(f"minio stat failed: {err}")
        if exists:
            if task_key:
                _update_task(task_key, progress=100, message="ready")
            return public_url
    os.makedirs(export_dir, exist_ok=True)
    zip_path = os.path.join(export_dir, f"all_{fmt}_{signature}.zip")
    tmp_zip = f"{zip_path}.tmp-{os.getpid()}"
    with zipfile.ZipFile(tmp_zip, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        total_tables = len(EXPORT_TABLES)
        for idx, table in enumerate(EXPORT_TABLES, start=1):
            if task_key:
                progress = int((idx - 1) / total_tables * 80)
                _update_task(task_key, progress=progress, message=f"exporting {table}")
            url_or_path = _ensure_table_export(table, fmt, signature_map.get(table))
            if url_or_path.startswith("http"):
                if not minio_client or not bucket:
                    raise RuntimeError("minio client not available for bundle")
                table_sig = signature_map.get(table)
                if not table_sig:
                    raise RuntimeError(f"missing signature for {table}")
                obj_key = _minio_object_key(table, fmt, table_sig)
                tmp_file = os.path.join(export_dir, f"{table}_{fmt}_{table_sig}.tmp")
                minio_client.fget_object(bucket, obj_key, tmp_file)
                name = EXPORT_NAME_BY_TABLE.get(table, table)
                bundle.write(tmp_file, arcname=f"{name}.{fmt}")
                try:
                    os.remove(tmp_file)
                except OSError:
                    pass
            else:
                name = EXPORT_NAME_BY_TABLE.get(table, table)
                bundle.write(url_or_path, arcname=f"{name}.{fmt}")
                try:
                    os.remove(url_or_path)
                except OSError:
                    pass
    os.replace(tmp_zip, zip_path)
    if minio_client and bucket and public_url:
        if task_key:
            _update_task(task_key, progress=95, message="uploading bundle")
        minio_client.fput_object(
            bucket,
            bundle_key,
            zip_path,
            content_type="application/zip",
        )
        try:
            os.remove(zip_path)
        except OSError:
            pass
        if task_key:
            _update_task(task_key, progress=100, message="ready")
        return public_url
    return zip_path

def _start_task(task_key: str, target, *args):
    with _EXPORT_TASK_LOCK:
        state = _EXPORT_TASKS.get(task_key)
        if state and state.get("status") == "running":
            return False
        _EXPORT_TASKS[task_key] = {
            "status": "running",
            "error": None,
            "progress": 0,
            "message": "starting",
        }
    thread = threading.Thread(target=target, args=args, daemon=True)
    thread.start()
    return True

def _update_task(task_key: str, progress: int = None, message: str = None):
    with _EXPORT_TASK_LOCK:
        state = _EXPORT_TASKS.get(task_key) or {}
        if progress is not None:
            state["progress"] = max(0, min(100, int(progress)))
        if message is not None:
            state["message"] = message
        _EXPORT_TASKS[task_key] = state

def _mark_task_done(task_key: str, status: str, error: str = None):
    with _EXPORT_TASK_LOCK:
        state = _EXPORT_TASKS.get(task_key) or {}
        state["status"] = status
        state["error"] = error
        if status == "done":
            state["progress"] = 100
            state["message"] = "ready"
        _EXPORT_TASKS[task_key] = state

def _run_table_export(app, table: str, fmt: str, signature: str, task_key: str):
    with app.app_context():
        try:
            _ensure_table_export(table, fmt, signature, task_key=task_key)
            _mark_task_done(task_key, "done")
        except Exception as exc:
            app.logger.exception("table export failed: %s %s", table, fmt)
            _mark_task_done(task_key, "error", str(exc))

def _run_bundle_export(app, fmt: str, signature_map: dict, task_key: str):
    with app.app_context():
        try:
            _ensure_bundle_export(fmt, signature_map, task_key=task_key)
            _mark_task_done(task_key, "done")
        except Exception as exc:
            app.logger.exception("bundle export failed: %s", fmt)
            _mark_task_done(task_key, "error", str(exc))

def start_export_warmup(app, tables=None, formats=None):
    tables = tables or EXPORT_TABLES
    formats = formats or ["csv"]

    def _warm():
        with app.app_context():
            for fmt in formats:
                for table in tables:
                    try:
                        _ensure_table_export(table, fmt)
                    except Exception:
                        continue
                try:
                    _ensure_bundle_export(fmt)
                except Exception:
                    continue

    threading.Thread(target=_warm, daemon=True).start()

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

def _build_search_clause_values(
    search_values: list,
    search_column: str,
    columns: list,
    ci: bool,
):
    if not search_values:
        return "", {}
    collate = " COLLATE utf8mb4_general_ci" if ci else ""
    if not search_column:
        return "", {}
    clauses = []
    params = {}
    for idx, value in enumerate(search_values):
        like_val = f"%{_escape_like(str(value))}%"
        clauses.append(
            f"CAST(`{search_column}` AS CHAR){collate} LIKE :search{idx} ESCAPE '\\\\'"
        )
        params[f"search{idx}"] = like_val
    if not clauses:
        return "", {}
    return "WHERE " + " OR ".join(clauses), params

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
    search_values=None,
):
    if not search_text:
        if not search_values:
            return "", {}, False
    if search_text and search_column:
        if search_column.lower() == "id" and re.fullmatch(r"\d+", str(search_text)):
            return (
                f"WHERE `{search_column}` = :search_exact",
                {"search_exact": int(search_text)},
                False,
            )
    if search_values and search_column:
        where_sql, params = _build_search_clause_values(
            search_values, search_column, columns, ci
        )
        return where_sql, params, False
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

def _build_filters_clause(filters, columns: list, ci: bool):
    if not filters:
        return "", {}
    collate = " COLLATE utf8mb4_general_ci" if ci else ""
    clauses = []
    params = {}
    for idx, f in enumerate(filters):
        col = f.get("column")
        values = f.get("values") or []
        if not col or col not in columns or not values:
            continue
        sub_clauses = []
        for jdx, value in enumerate(values):
            key = f"fv{idx}_{jdx}"
            like_val = f"%{_escape_like(str(value))}%"
            sub_clauses.append(
                f"CAST(`{col}` AS CHAR){collate} LIKE :{key} ESCAPE '\\\\'"
            )
            params[key] = like_val
        if sub_clauses:
            clauses.append("(" + " OR ".join(sub_clauses) + ")")
    if not clauses:
        return "", {}
    return " AND ".join(clauses), params

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


@bp.route("/chat/api/application/profile", methods=["GET"])
def chat_application_profile():
    return jsonify({"data": {"id": "ollama-local"}}), 200


@bp.route("/chat/api/open", methods=["GET"])
def chat_open():
    chat_id = uuid.uuid4().hex
    _get_chat_session(chat_id)
    return jsonify({"data": chat_id}), 200


@bp.route("/chat/api/title", methods=["POST"])
def chat_title():
    payload = request.get_json(silent=True) or {}
    items = payload.get("messages") or []
    if not isinstance(items, list):
        items = []

    parts = []
    user_parts = []
    for item in items:
        if not isinstance(item, dict):
            continue
        content = (item.get("content") or item.get("text") or "").strip()
        if not content:
            continue
        role = item.get("role") or item.get("sender") or "user"
        role = "User" if role == "user" else "Assistant"
        if role == "User":
            user_parts.append(content)
        parts.append(f"{role}: {content}")
        if len(parts) >= 10:
            break

    summary_input = "\n".join(parts).strip()
    if not summary_input:
        return jsonify({"title": "New chat"}), 200

    base, model, timeout, _, _ = _get_ollama_config()
    model = _select_ollama_model(payload.get("model"), model)
    user_text = " ".join(user_parts).strip()
    sample = user_text if user_text else summary_input
    cjk_count = len(re.findall(r"[\u4e00-\u9fff]", sample))
    latin_count = len(re.findall(r"[A-Za-z]", sample))
    use_chinese = cjk_count >= 6 and cjk_count >= latin_count
    if use_chinese:
        system_prompt = (
            "You are a title generator. Use Chinese only. "
            "Return only a short title (max 14 Chinese characters). No quotes."
        )
    else:
        system_prompt = (
            "You are a title generator. Use English only. "
            "Return only a short title (max 10 words). No quotes."
        )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": summary_input},
    ]
    title = ""
    try:
        for chunk, done in _ollama_stream(base, model, messages, timeout):
            if chunk:
                title += chunk
            if done:
                break
    except Exception:
        title = ""

    title = title.replace("\n", " ").strip().strip('"').strip()
    if len(title) > 60:
        title = title[:60].rstrip() + "..."
    if not title:
        title = "New chat"
    return jsonify({"title": title}), 200


@bp.route("/chat/api/chat_message/<chat_id>", methods=["POST"])
def chat_message(chat_id):
    payload = request.get_json(silent=True) or {}
    message = (payload.get("message") or "").strip()
    if not message:
        return jsonify({"error": "missing message"}), 400

    base, model, timeout, system_prompt, max_messages = _get_ollama_config()
    model = _select_ollama_model(payload.get("model"), model)
    rag_context, rag_evidence = _rag_retrieve(message)
    strict_evidence = bool(current_app.config.get("STRICT_EVIDENCE_MODE", False))
    _append_chat_message(chat_id, "user", message, max_messages)
    session = _get_chat_session(chat_id)
    messages = _build_ollama_messages(session.get("messages"), system_prompt, rag_context)

    def generate():
        complete = ""
        try:
            if strict_evidence and _evidence_required(message) and not rag_evidence:
                allowed = _strict_allowed_response(message)
                fallback = allowed or "当前数据中找不到"
                _append_chat_message(chat_id, "assistant", fallback, max_messages)
                data = json.dumps({"content": fallback}, ensure_ascii=False)
                yield f"data: {data}\n\n"
                evidence_text = _format_evidence_block(rag_evidence)
                data = json.dumps({"content": evidence_text}, ensure_ascii=False)
                yield f"data: {data}\n\n"
                yield "data: [DONE]\n\n"
                return
            for chunk, done in _ollama_stream(base, model, messages, timeout):
                if chunk:
                    complete += chunk
                    data = json.dumps({"content": chunk}, ensure_ascii=False)
                    yield f"data: {data}\n\n"
                if done:
                    break
            if complete:
                _append_chat_message(chat_id, "assistant", complete, max_messages)
            evidence_text = _format_evidence_block(rag_evidence)
            data = json.dumps({"content": evidence_text}, ensure_ascii=False)
            yield f"data: {data}\n\n"
        except Exception as exc:
            data = json.dumps({"content": f"Error: {exc}"}, ensure_ascii=False)
            yield f"data: {data}\n\n"
        yield "data: [DONE]\n\n"

    headers = {
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
    }
    return Response(stream_with_context(generate()), mimetype="text/event-stream", headers=headers)


@bp.route("/embedding/rebuild", methods=["POST"])
def embedding_rebuild():
    enable, model, index_path, _, _, _ = _get_embedding_config()
    if not enable:
        return jsonify({"error": "embedding disabled"}), 400
    base, _, timeout, _, _ = _get_ollama_config()
    items = _build_embedding_index(base, model, timeout)
    return jsonify({"ok": True, "count": len(items), "index_path": index_path}), 200

@bp.route("/search", methods=["GET", "POST"])
@bp.route("/search/", methods=["GET", "POST"])
def search():
    # 健康检查或简单监控
    if request.method == "GET":
        return "OK", 200

    # POST：实际搜索
    data = request.get_json(silent=True) or {}

    try:
        if data.get("tables"):
            topn = search_in_mysql(data, db.engine)
        else:
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
    search_values = data.get("search_values") or []
    if isinstance(search_values, str):
        search_values = [v for v in search_values.split(",") if v.strip()]
    search_values = [str(v) for v in search_values if v is not None and str(v).strip()]
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
        search_text,
        search_column,
        columns,
        ci,
        use_fulltext,
        fulltext_columns,
        search_values,
    )
    filters = data.get("filters") or []
    if not isinstance(filters, list):
        return jsonify({"error": "filters must be a list"}), 400
    for f in filters:
        col = f.get("column")
        if col and col not in columns:
            return jsonify({"error": f"Column '{col}' not in table '{table}'"}), 400
    filter_sql, filter_params = _build_filters_clause(filters, columns, ci)
    where_sql = _merge_where(where_sql, filter_sql)
    params = {**params, **filter_params}
    count_sql = text(f"SELECT COUNT(*) AS total FROM `{table}` {where_sql}")
    row_offset = (page - 1) * page_size
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
                {**params, "limit": page_size, "offset": row_offset},
            ).fetchall()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    try:
        results = [dict(r._mapping) for r in rows]
    except AttributeError:
        results = [dict(r) for r in rows]

    for idx, row in enumerate(results):
        if "__rowid" not in row:
            row["__rowid"] = row_offset + idx + 1

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
    search_values = data.get("search_values") or []
    if isinstance(search_values, str):
        search_values = [v for v in search_values.split(",") if v.strip()]
    search_values = [str(v) for v in search_values if v is not None and str(v).strip()]
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
        search_text,
        search_column,
        columns,
        ci,
        use_fulltext,
        fulltext_columns,
        search_values,
    )
    filters = data.get("filters") or []
    if not isinstance(filters, list):
        return jsonify({"error": "filters must be a list"}), 400
    for f in filters:
        col = f.get("column")
        if col and col not in columns:
            return jsonify({"error": f"Column '{col}' not in table '{table}'"}), 400
    filter_sql, filter_params = _build_filters_clause(filters, columns, ci)
    where_sql = _merge_where(where_sql, filter_sql)
    params = {**params, **filter_params}
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


@bp.route("/download_table", methods=["GET"])
def download_table():
    table = (request.args.get("table") or "").strip()
    fmt = (request.args.get("format") or "csv").strip().lower()
    force = str(request.args.get("force") or "").lower() in ("1", "true", "yes")
    direct = str(request.args.get("direct") or "").lower() in ("1", "true", "yes")
    async_mode = str(request.args.get("async") or "").lower() in ("1", "true", "yes")
    if fmt not in ("csv", "tsv"):
        return jsonify({"error": "format must be csv or tsv"}), 400
    if not table:
        return jsonify({"error": "table is required"}), 400
    if table in {"alembic_version", "table_meta"}:
        return jsonify({"error": "table not allowed"}), 400

    _, col_names = _get_table_columns(table)
    if not col_names:
        return jsonify({"error": f"table '{table}' not found"}), 404

    signature = _get_table_signature(table)
    if not signature:
        return jsonify({"error": "could not determine table signature"}), 500

    export_dir = _get_export_cache_dir()
    os.makedirs(export_dir, exist_ok=True)
    cache_name = f"{table}_{fmt}_{signature}.{fmt}"
    cache_path = os.path.join(export_dir, cache_name)

    minio_client = None
    bucket = current_app.config.get("MINIO_BUCKET")
    minio_key = _minio_object_key(table, fmt, signature)
    public_url = _minio_public_url(minio_key)
    try:
        minio_client = _get_minio_client()
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 500

    if minio_client and bucket and public_url and not force:
        exists, err = _minio_object_status(minio_client, bucket, minio_key)
        if err:
            return jsonify({"error": f"minio stat failed: {err}"}), 500
        if exists:
            if direct:
                return redirect(public_url, code=302)
            return _minio_stream_response(minio_client, bucket, minio_key, table, fmt)

    if async_mode and minio_client and bucket and public_url:
        task_key = f"table:{table}:{fmt}:{signature}"
        _start_task(
            task_key,
            _run_table_export,
            current_app._get_current_object(),
            table,
            fmt,
            signature,
            task_key,
        )
        return jsonify({"status": "generating"}), 202

    if os.path.exists(cache_path) and not force and not minio_client:
        return send_file(
            cache_path,
            as_attachment=True,
            download_name=f"{table}.{fmt}",
            mimetype="text/csv; charset=utf-8"
            if fmt == "csv"
            else "text/tab-separated-values; charset=utf-8",
        )

    delimiter = "," if fmt == "csv" else "\t"
    tmp_path = f"{cache_path}.tmp-{os.getpid()}"
    sql = text(f"SELECT * FROM `{table}`")
    with db.engine.connect() as conn:
        result = conn.execution_options(stream_results=True).execute(sql)
        with open(tmp_path, "w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter=delimiter, lineterminator="\n")
            writer.writerow(result.keys())
            for row in result:
                writer.writerow([_csv_safe(v) for v in row])
    os.replace(tmp_path, cache_path)

    if minio_client and bucket and public_url:
        try:
            minio_client.fput_object(
                bucket,
                minio_key,
                cache_path,
                content_type="text/csv" if fmt == "csv" else "text/tab-separated-values",
            )
            @after_this_request
            def _cleanup(response):
                try:
                    os.remove(cache_path)
                except OSError:
                    pass
                return response
            if direct:
                return redirect(public_url, code=302)
            return _minio_stream_response(minio_client, bucket, minio_key, table, fmt)
        except Exception as exc:
            return jsonify({"error": f"minio upload failed: {exc}"}), 500

    return send_file(
        cache_path,
        as_attachment=True,
        download_name=f"{table}.{fmt}",
        mimetype="text/csv; charset=utf-8"
        if fmt == "csv"
        else "text/tab-separated-values; charset=utf-8",
    )


@bp.route("/download_table_status", methods=["GET"])
def download_table_status():
    table = (request.args.get("table") or "").strip()
    fmt = (request.args.get("format") or "csv").strip().lower()
    if fmt not in ("csv", "tsv"):
        return jsonify({"error": "format must be csv or tsv"}), 400
    if not table:
        return jsonify({"error": "table is required"}), 400
    if table in {"alembic_version", "table_meta"}:
        return jsonify({"error": "table not allowed"}), 400

    signature = _get_table_signature(table)
    if not signature:
        return jsonify({"error": "could not determine table signature"}), 500

    try:
        minio_client = _get_minio_client()
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 500
    bucket = current_app.config.get("MINIO_BUCKET")
    minio_key = _minio_object_key(table, fmt, signature)
    public_url = _minio_public_url(minio_key)
    if minio_client and bucket and public_url:
        exists, err = _minio_object_status(minio_client, bucket, minio_key)
        if err:
            return jsonify({
                "status": "error",
                "error": err,
                "signature": signature,
                "key": minio_key,
                "url": public_url,
            }), 500
        if exists:
            return jsonify({"status": "ready", "url": public_url})

    task_key = f"table:{table}:{fmt}:{signature}"
    state = _EXPORT_TASKS.get(task_key)
    if state and state.get("status") == "error":
        return jsonify({
            "status": "error",
            "error": state.get("error"),
            "signature": signature,
            "key": minio_key,
            "url": public_url,
            "progress": state.get("progress", 0),
            "message": state.get("message"),
        }), 500
    _start_task(
        task_key,
        _run_table_export,
        current_app._get_current_object(),
        table,
        fmt,
        signature,
        task_key,
    )
    state = _EXPORT_TASKS.get(task_key) or {}
    return jsonify({
        "status": "generating",
        "signature": signature,
        "key": minio_key,
        "url": public_url,
        "progress": state.get("progress", 0),
        "message": state.get("message"),
    }), 202


@bp.route("/download_bundle_status", methods=["GET"])
def download_bundle_status():
    fmt = (request.args.get("format") or "csv").strip().lower()
    if fmt not in ("csv", "tsv"):
        return jsonify({"error": "format must be csv or tsv"}), 400

    signature_map = _get_table_signature_map(EXPORT_TABLES)
    signature = _bundle_signature_from_map(signature_map, fmt)
    try:
        minio_client = _get_minio_client()
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 500
    bucket = current_app.config.get("MINIO_BUCKET")
    bundle_key = _bundle_object_key(fmt, signature)
    public_url = _minio_public_url(bundle_key)
    if minio_client and bucket and public_url:
        exists, err = _minio_object_status(minio_client, bucket, bundle_key)
        if err:
            return jsonify({
                "status": "error",
                "error": err,
                "signature": signature,
                "key": bundle_key,
                "url": public_url,
            }), 500
        if exists:
            return jsonify({"status": "ready", "url": public_url})

    task_key = f"bundle:{fmt}:{signature}"
    state = _EXPORT_TASKS.get(task_key)
    if state and state.get("status") == "error":
        return jsonify({
            "status": "error",
            "error": state.get("error"),
            "signature": signature,
            "key": bundle_key,
            "url": public_url,
            "progress": state.get("progress", 0),
            "message": state.get("message"),
        }), 500
    _start_task(
        task_key,
        _run_bundle_export,
        current_app._get_current_object(),
        fmt,
        signature_map,
        task_key,
    )
    state = _EXPORT_TASKS.get(task_key) or {}
    return jsonify({
        "status": "generating",
        "signature": signature,
        "key": bundle_key,
        "url": public_url,
        "progress": state.get("progress", 0),
        "message": state.get("message"),
    }), 202


@bp.route("/export_warm", methods=["POST"])
def export_warm():
    data = request.get_json(silent=True) or {}
    tables = data.get("tables") or EXPORT_TABLES
    if isinstance(tables, str):
        tables = [t.strip() for t in tables.split(",") if t.strip()]
    formats = data.get("formats") or ["csv"]
    if isinstance(formats, str):
        formats = [f.strip() for f in formats.split(",") if f.strip()]
    start_export_warmup(current_app._get_current_object(), tables, formats)
    return jsonify({"status": "started", "tables": tables, "formats": formats}), 202


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
