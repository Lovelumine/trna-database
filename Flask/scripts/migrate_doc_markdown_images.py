from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

import requests
from PIL import Image
from werkzeug.utils import secure_filename

FLASK_ROOT = Path(__file__).resolve().parents[1]
if str(FLASK_ROOT) not in sys.path:
    sys.path.insert(0, str(FLASK_ROOT))

from app import create_app, db  # noqa: E402
from app.models import MediaAsset  # noqa: E402
from app import routes  # noqa: E402


MIGRATION_ACTOR = "doc-image-migration"


def _guess_filename_from_url(url: str) -> str:
    parsed = urlparse(str(url or "").strip())
    raw_name = unquote(Path(parsed.path).name or "").strip()
    safe_name = secure_filename(raw_name)
    if safe_name:
        return safe_name
    suffix = Path(raw_name).suffix or ".png"
    fallback_seed = hashlib.sha256(str(url or "").encode("utf-8")).hexdigest()[:16]
    return f"doc-image-{fallback_seed}{suffix}"


def _label_from_image_ref(ref: dict[str, Any], fallback_name: str) -> str:
    alt = str(ref.get("alt") or "").strip()
    if alt:
        return alt
    stem = Path(fallback_name).stem.strip()
    return stem or "image"


def _inspect_image_payload(payload: bytes, original_filename: str) -> dict[str, Any]:
    max_bytes = int(routes.current_app.config.get("MEDIA_UPLOAD_MAX_BYTES") or 0) or (10 * 1024 * 1024)
    if not payload:
        raise ValueError("downloaded image is empty")
    if len(payload) > max_bytes:
        raise ValueError(f"downloaded image exceeds {max_bytes // (1024 * 1024)} MB limit")
    with Image.open(io.BytesIO(payload)) as image:
        image.load()
        fmt = str(image.format or "").upper()
        width, height = image.size
    if fmt not in routes._MEDIA_FORMAT_INFO:
        raise ValueError(f"unsupported image format: {fmt or 'unknown'}")
    file_ext, mime_type = routes._MEDIA_FORMAT_INFO[fmt]
    return {
        "payload": payload,
        "size_bytes": len(payload),
        "width": int(width or 0),
        "height": int(height or 0),
        "mime_type": mime_type,
        "file_ext": file_ext,
        "original_filename": original_filename,
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def _download_image(url: str) -> bytes:
    response = requests.get(
        url,
        timeout=60,
        headers={"User-Agent": "ENSURE-doc-image-migration/1.0"},
    )
    response.raise_for_status()
    return response.content


def _load_local_doc_image_fallback(url: str) -> bytes | None:
    parsed = urlparse(str(url or "").strip())
    relative = unquote(parsed.path or "").lstrip("/")
    docs_dir = Path(routes._docs_dir())
    candidates = []
    if relative.startswith("docs/"):
        candidates.append(docs_dir / relative.removeprefix("docs/"))
    if relative:
        candidates.append(docs_dir / Path(relative).name)
    seen: set[Path] = set()
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        if resolved.exists() and resolved.is_file():
            return resolved.read_bytes()
    return None


def _create_docs_asset(image_info: dict[str, Any], label: str) -> MediaAsset:
    bucket = str(routes.current_app.config.get("MINIO_BUCKET") or "").strip()
    minio_client = routes._get_minio_client()
    if not bucket or not minio_client:
        raise RuntimeError("MinIO is not configured")

    object_key = routes._minio_media_object_key("docs", image_info["sha256"], image_info["file_ext"])
    public_url = routes._minio_public_url(object_key)
    if not public_url:
        raise RuntimeError("MinIO public base is not configured")

    minio_client.put_object(
        bucket,
        object_key,
        io.BytesIO(image_info["payload"]),
        length=image_info["size_bytes"],
        content_type=image_info["mime_type"],
    )

    asset = MediaAsset(
        bucket=bucket,
        object_key=object_key,
        public_url=public_url,
        mime_type=image_info["mime_type"],
        file_ext=image_info["file_ext"],
        size_bytes=image_info["size_bytes"],
        width=image_info["width"],
        height=image_info["height"],
        sha256=image_info["sha256"],
        title=label,
        alt_text=label,
        original_filename=image_info["original_filename"],
        source_type="docs",
        created_by=None,
        created_by_username=MIGRATION_ACTOR,
    )
    db.session.add(asset)
    db.session.commit()
    return asset


def _resolve_asset_for_ref(ref: dict[str, Any], cache: dict[str, dict[str, Any]]) -> dict[str, Any]:
    src = str(ref.get("src") or "").strip()
    if src in cache:
        return cache[src]

    by_src = routes._find_media_asset_for_doc_src(src)
    if by_src:
        payload = {"asset": by_src, "status": "existing_url"}
        cache[src] = payload
        return payload

    original_filename = _guess_filename_from_url(src)
    label = _label_from_image_ref(ref, original_filename)
    try:
        payload = _download_image(src)
    except Exception:
        payload = _load_local_doc_image_fallback(src)
        if payload is None:
            raise
    image_info = _inspect_image_payload(payload, original_filename)

    existing = (
        MediaAsset.query.filter_by(
            sha256=image_info["sha256"],
            size_bytes=image_info["size_bytes"],
        )
        .order_by(MediaAsset.id.desc())
        .first()
    )
    if existing:
        payload_info = {"asset": existing, "status": "existing_sha"}
        cache[src] = payload_info
        return payload_info

    created = _create_docs_asset(image_info, label)
    payload_info = {"asset": created, "status": "created"}
    cache[src] = payload_info
    return payload_info


def _escape_markdown_alt(value: str) -> str:
    return str(value or "").replace("\n", " ").replace("[", "\\[").replace("]", "\\]").strip()


def _render_markdown_image(asset: MediaAsset, original_alt: str) -> str:
    alt = _escape_markdown_alt(str(original_alt or "").strip() or str(asset.alt_text or asset.title or "").strip() or "image")
    return f"![{alt}]({str(asset.public_url or '').strip()})"


def _process_doc(path: Path, apply_changes: bool, cache: dict[str, dict[str, Any]]) -> dict[str, Any]:
    content = path.read_text(encoding="utf-8")
    refs = routes._extract_markdown_image_refs(content)
    doc_report: dict[str, Any] = {
        "filename": path.name,
        "image_refs": len(refs),
        "rewritten": 0,
        "created_assets": 0,
        "reused_assets_by_url": 0,
        "reused_assets_by_hash": 0,
        "failures": [],
        "updated": False,
    }
    if not refs:
        if apply_changes:
            routes._sync_doc_image_bindings(path.name, content, actor=None)
        return doc_report

    segments: list[str] = []
    cursor = 0
    updated_content = content
    if apply_changes:
        for ref in refs:
            src = str(ref.get("src") or "").strip()
            try:
                resolved = _resolve_asset_for_ref(ref, cache)
                asset = resolved["asset"]
                status = str(resolved["status"] or "")
                if status == "created":
                    doc_report["created_assets"] += 1
                elif status == "existing_sha":
                    doc_report["reused_assets_by_hash"] += 1
                else:
                    doc_report["reused_assets_by_url"] += 1
                replacement = str(ref.get("raw") or "")
                if str(asset.public_url or "").strip() != src:
                    replacement = _render_markdown_image(asset, str(ref.get("alt") or ""))
                    doc_report["rewritten"] += 1
                segments.append(content[cursor : int(ref["start"])])
                segments.append(replacement)
                cursor = int(ref["end"])
            except Exception as exc:
                doc_report["failures"].append({"src": src, "error": str(exc)})
                segments.append(content[cursor : int(ref["end"])])
                cursor = int(ref["end"])
        segments.append(content[cursor:])
        updated_content = "".join(segments)
        if updated_content != content:
            path.write_text(updated_content, encoding="utf-8")
            doc_report["updated"] = True
        routes._sync_doc_image_bindings(path.name, updated_content, actor=None)
        return doc_report

    for ref in refs:
        src = str(ref.get("src") or "").strip()
        try:
            by_src = routes._find_media_asset_for_doc_src(src)
            if by_src:
                doc_report["reused_assets_by_url"] += 1
                if str(by_src.public_url or "").strip() != src:
                    doc_report["rewritten"] += 1
                continue
            original_filename = _guess_filename_from_url(src)
            try:
                payload = _download_image(src)
            except Exception:
                payload = _load_local_doc_image_fallback(src)
                if payload is None:
                    raise
            image_info = _inspect_image_payload(payload, original_filename)
            existing = (
                MediaAsset.query.filter_by(
                    sha256=image_info["sha256"],
                    size_bytes=image_info["size_bytes"],
                )
                .order_by(MediaAsset.id.desc())
                .first()
            )
            if existing:
                doc_report["reused_assets_by_hash"] += 1
                doc_report["rewritten"] += 1
            else:
                doc_report["created_assets"] += 1
                doc_report["rewritten"] += 1
        except Exception as exc:
            doc_report["failures"].append({"src": src, "error": str(exc)})

    return doc_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrate historical Markdown document images into the media library.")
    parser.add_argument("--apply", action="store_true", help="Upload missing images, rewrite Markdown, and sync doc_image bindings.")
    parser.add_argument("--report", default="", help="Optional path to write the JSON migration report.")
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        docs_dir = Path(routes._docs_dir())
        docs = sorted(docs_dir.glob("*.md"))
        asset_cache: dict[str, dict[str, Any]] = {}
        report: dict[str, Any] = {
            "docs_dir": str(docs_dir),
            "apply": bool(args.apply),
            "doc_count": len(docs),
            "docs": [],
            "summary": {
                "image_refs": 0,
                "rewritten_refs": 0,
                "created_assets": 0,
                "reused_assets_by_url": 0,
                "reused_assets_by_hash": 0,
                "updated_docs": 0,
                "failures": 0,
            },
        }

        for doc_path in docs:
            item = _process_doc(doc_path, bool(args.apply), asset_cache)
            report["docs"].append(item)
            report["summary"]["image_refs"] += int(item["image_refs"])
            report["summary"]["rewritten_refs"] += int(item["rewritten"])
            report["summary"]["created_assets"] += int(item["created_assets"])
            report["summary"]["reused_assets_by_url"] += int(item["reused_assets_by_url"])
            report["summary"]["reused_assets_by_hash"] += int(item["reused_assets_by_hash"])
            report["summary"]["updated_docs"] += 1 if item["updated"] else 0
            report["summary"]["failures"] += len(item["failures"])

        if args.report:
            report_path = Path(args.report)
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if not report["summary"]["failures"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
