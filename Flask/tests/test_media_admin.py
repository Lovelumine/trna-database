from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from flask import Flask


FLASK_ROOT = Path(__file__).resolve().parents[1]
if str(FLASK_ROOT) not in sys.path:
    sys.path.insert(0, str(FLASK_ROOT))

from app import routes  # noqa: E402
from app import admin as admin_module  # noqa: E402
from app.admin import ADMIN_CSRF_KEY  # noqa: E402
from app.models import MediaAsset, MediaBinding  # noqa: E402


def build_media_admin_app() -> Flask:
    app = Flask(__name__)
    app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret",
    )
    app.register_blueprint(routes.bp)
    return app


class FakeSession:
    def __init__(self, asset=None, binding=None):
        self.asset = asset
        self.binding = binding
        self.added = []
        self.deleted = []

    def get(self, model, pk):
        if model is MediaAsset:
            if self.asset and int(pk) == int(getattr(self.asset, "id", 0) or 0):
                return self.asset
            return None
        if model is MediaBinding:
            if self.binding and int(pk) == int(getattr(self.binding, "id", 0) or 0):
                return self.binding
            return None
        return None

    def add(self, obj):
        self.added.append(obj)
        if isinstance(obj, MediaBinding):
            if not getattr(obj, "id", None):
                obj.id = 91
            self.binding = obj
        elif isinstance(obj, MediaAsset):
            if not getattr(obj, "id", None):
                obj.id = 17
            self.asset = obj

    def delete(self, obj):
        self.deleted.append(obj)

    def commit(self):
        return None

    def flush(self):
        return None

    def rollback(self):
        return None


class FakeBindingQuery:
    def __init__(self, items):
        self.items = items

    def filter_by(self, **kwargs):
        return self

    def filter(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def all(self):
        return list(self.items)


class FakeQueryResult:
    def __init__(self, items):
        self.items = list(items)

    def filter_by(self, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def all(self):
        return list(self.items)

    def first(self):
        return self.items[0] if self.items else None


class FakeFilterByRouter:
    def __init__(self, items):
        self.items = list(items)

    def filter_by(self, **kwargs):
        filtered = [
            item
            for item in self.items
            if all(getattr(item, key, None) == value for key, value in kwargs.items())
        ]
        return FakeQueryResult(filtered)


class FakeMediaListQuery:
    def __init__(self, items):
        self.items = list(items)
        self._offset = 0
        self._limit = None

    def filter(self, *args, **kwargs):
        return self

    def count(self):
        return len(self.items)

    def offset(self, value):
        self._offset = int(value or 0)
        return self

    def limit(self, value):
        self._limit = int(value or 0)
        return self

    def all(self):
        end = None if self._limit is None else self._offset + self._limit
        return list(self.items[self._offset:end])


class FakeBindingQueryRouter:
    def __init__(self, same_binding=None, slot_bindings=None):
        self.same_binding = same_binding
        self.slot_bindings = list(slot_bindings or [])

    def filter_by(self, **kwargs):
        if "asset_id" in kwargs:
            return FakeQueryResult([self.same_binding] if self.same_binding else [])
        return FakeQueryResult(self.slot_bindings)


class FakeAssetQueryRouter:
    def __init__(self, asset=None):
        self.asset = asset

    def filter_by(self, **kwargs):
        object_key = kwargs.get("object_key")
        if self.asset and object_key == getattr(self.asset, "object_key", None):
            return FakeQueryResult([self.asset])
        return FakeQueryResult([])


@pytest.fixture()
def media_app():
    return build_media_admin_app()


def _login_admin(client):
    with client.session_transaction() as session:
        session[ADMIN_CSRF_KEY] = "test-csrf-token"
    return "test-csrf-token"


def _mock_admin(monkeypatch: pytest.MonkeyPatch):
    admin_user = SimpleNamespace(id=7, username="media-admin", role="admin", is_active=True)
    monkeypatch.setattr(admin_module, "current_admin", lambda: admin_user)
    monkeypatch.setattr(routes, "current_admin", lambda: admin_user)
    monkeypatch.setattr(routes, "audit_admin_action", lambda *args, **kwargs: None)
    return admin_user


def _make_asset():
    return SimpleNamespace(
        id=11,
        bucket="ensure",
        object_key="library/test-image.png",
        public_url="https://example.com/library/test-image.png",
        mime_type="image/png",
        file_ext=".png",
        size_bytes=1234,
        width=320,
        height=240,
        sha256="abcd" * 16,
        title="Test image",
        alt_text="Before update",
        original_filename="test-image.png",
        source_type="library",
        created_by=7,
        created_by_username="media-admin",
        created_at=None,
    )


def test_find_media_asset_references_merges_binding_settings_and_docs(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    asset = _make_asset()
    binding = SimpleNamespace(
        id=5,
        asset_id=asset.id,
        binding_type="table_record_slot",
        resource_name="nonsense_sup_rna",
        field_name="pictureid",
        record_key="PMID:12345678",
        slot_key="structure_figure",
        created_at=None,
    )
    doc_path = tmp_path / "help.md"
    doc_path.write_text(f"![img]({asset.public_url})", encoding="utf-8")

    original_query = routes.MediaBinding.__dict__.get("query")
    type.__setattr__(routes.MediaBinding, "query", FakeBindingQuery([binding]))
    monkeypatch.setattr(
        routes,
        "get_setting",
        lambda key, default="": json.dumps(
            {
                "homepage.hero_logo": {
                    "asset_id": asset.id,
                    "public_url": asset.public_url,
                    "object_key": asset.object_key,
                }
            }
        )
        if key == "site_asset_slots_json"
        else default,
    )
    monkeypatch.setattr(routes, "_admin_list_docs", lambda: [{"filename": "help.md"}])
    monkeypatch.setattr(routes, "_admin_doc_allowed", lambda filename, allow_create=False: str(doc_path))
    monkeypatch.setattr(routes, "_admin_all_tables", lambda include_internal=False: [])

    try:
        references = routes._find_media_asset_references(asset)
    finally:
        if original_query is not None:
            type.__setattr__(routes.MediaBinding, "query", original_query)

    assert [ref["type"] for ref in references] == ["table_record_slot", "doc_image", "site_asset"]
    assert references[0]["resource"] == "nonsense_sup_rna"
    assert references[0]["field_name"] == "pictureid"
    assert references[0]["record_key"] == "PMID:12345678"
    assert references[0]["slot_key"] == "structure_figure"
    assert references[1]["resource"] == "help.md"
    assert references[2]["resource"] == "site_asset_slots_json"


def test_sync_doc_image_bindings_replaces_existing_bindings(
    monkeypatch: pytest.MonkeyPatch,
):
    asset = _make_asset()
    previous_binding = SimpleNamespace(
        id=12,
        asset_id=asset.id,
        binding_type="doc_image",
        resource_name="help.md",
        field_name="",
        record_key="",
        slot_key="image_999",
        extra_json=None,
        created_by=None,
        created_by_username="",
        created_at=None,
    )
    fake_session = FakeSession()
    original_session = routes.db.session
    original_binding_query = routes.MediaBinding.__dict__.get("query")
    original_asset_query = routes.MediaAsset.__dict__.get("query")
    type.__setattr__(routes.MediaBinding, "query", FakeBindingQuery([previous_binding]))
    type.__setattr__(routes.MediaAsset, "query", FakeFilterByRouter([asset]))
    monkeypatch.setattr(routes.db, "session", fake_session)

    try:
        bindings = routes._sync_doc_image_bindings(
            "help.md",
            f"![Overview image]({asset.public_url})",
            actor=None,
        )
    finally:
        monkeypatch.setattr(routes.db, "session", original_session)
        if original_binding_query is not None:
            type.__setattr__(routes.MediaBinding, "query", original_binding_query)
        if original_asset_query is not None:
            type.__setattr__(routes.MediaAsset, "query", original_asset_query)

    assert previous_binding in fake_session.deleted
    created_binding = next(obj for obj in fake_session.added if isinstance(obj, MediaBinding))
    assert created_binding.binding_type == "doc_image"
    assert created_binding.resource_name == "help.md"
    assert created_binding.slot_key == "image_001"
    assert bindings[0]["binding_type"] == "doc_image"
    assert bindings[0]["resource_name"] == "help.md"


def test_admin_media_detail_and_delete_are_blocked_by_references(
    media_app: Flask,
    monkeypatch: pytest.MonkeyPatch,
):
    _mock_admin(monkeypatch)
    asset = _make_asset()
    references = [
        {
            "type": "table_record_slot",
            "resource": "nonsense_sup_rna",
            "field_name": "pictureid",
            "record_key": "PMID:12345678",
            "slot_key": "structure_figure",
            "source": "binding",
            "binding_id": 5,
            "created_at": None,
        }
    ]
    fake_session = FakeSession(asset=asset)
    monkeypatch.setattr(routes, "db", SimpleNamespace(session=fake_session))
    monkeypatch.setattr(routes, "_find_media_asset_references", lambda current_asset: list(references))
    monkeypatch.setattr(routes, "_binding_counts_for_asset_ids", lambda asset_ids: {11: 1})

    client = media_app.test_client()
    csrf_token = _login_admin(client)

    detail = client.get("/admin/api/media/11")
    assert detail.status_code == 200
    detail_payload = detail.get_json()
    assert detail_payload["asset"]["id"] == 11
    assert detail_payload["asset"]["reference_count"] == 1
    assert detail_payload["references"] == references

    blocked = client.delete("/admin/api/media/11", headers={"X-CSRF-Token": csrf_token})
    assert blocked.status_code == 409
    blocked_payload = blocked.get_json()
    assert blocked_payload["error"] == "media asset is still referenced"
    assert blocked_payload["references"] == references


def test_admin_media_list_supports_binding_status_filter_and_returns_binding_count(
    media_app: Flask, monkeypatch: pytest.MonkeyPatch
):
    _mock_admin(monkeypatch)
    bound_asset = _make_asset()
    unbound_asset = _make_asset()
    unbound_asset.id = 12
    unbound_asset.title = "Unbound image"
    seen_status: list[str] = []

    def fake_filter(query, status):
        seen_status.append(status)
        if status == "bound":
            return FakeMediaListQuery([bound_asset])
        if status == "unbound":
            return FakeMediaListQuery([unbound_asset])
        return query

    monkeypatch.setattr(
        routes,
        "_media_asset_query",
        lambda: FakeMediaListQuery([bound_asset, unbound_asset]),
    )
    monkeypatch.setattr(routes, "_filter_media_query_by_binding_status", fake_filter)
    monkeypatch.setattr(routes, "_binding_counts_for_asset_ids", lambda asset_ids: {11: 2})

    client = media_app.test_client()
    _login_admin(client)

    response = client.get("/admin/api/media?binding_status=bound&page=1&page_size=10")
    assert response.status_code == 200
    payload = response.get_json()
    assert seen_status == ["bound"]
    assert payload["total"] == 1
    assert len(payload["items"]) == 1
    assert payload["items"][0]["id"] == 11
    assert payload["items"][0]["binding_count"] == 2


def test_admin_media_update_updates_metadata(media_app: Flask, monkeypatch: pytest.MonkeyPatch):
    _mock_admin(monkeypatch)
    asset = _make_asset()
    fake_session = FakeSession(asset=asset)
    monkeypatch.setattr(routes, "db", SimpleNamespace(session=fake_session))
    monkeypatch.setattr(routes, "_find_media_asset_references", lambda current_asset: [])
    monkeypatch.setattr(routes, "_binding_counts_for_asset_ids", lambda asset_ids: {11: 0})

    client = media_app.test_client()
    csrf_token = _login_admin(client)

    response = client.post(
        "/admin/api/media/11",
        headers={"X-CSRF-Token": csrf_token},
        json={
            "title": "Updated title",
            "alt_text": "Updated alt text",
            "source_type": "docs",
        },
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["ok"] is True
    assert payload["asset"]["title"] == "Updated title"
    assert payload["asset"]["alt_text"] == "Updated alt text"
    assert payload["asset"]["source_type"] == "docs"
    assert payload["references"] == []
    assert asset.title == "Updated title"
    assert asset.alt_text == "Updated alt text"
    assert asset.source_type == "docs"


def test_admin_media_binding_create_and_delete(media_app: Flask, monkeypatch: pytest.MonkeyPatch):
    _mock_admin(monkeypatch)
    asset = _make_asset()
    fake_session = FakeSession(asset=asset)
    monkeypatch.setattr(routes, "db", SimpleNamespace(session=fake_session))

    client = media_app.test_client()
    csrf_token = _login_admin(client)

    create = client.post(
        "/admin/api/media/11/bindings",
        headers={"X-CSRF-Token": csrf_token},
        json={
            "binding_type": "site_asset",
            "resource_name": "site_asset_slots_json",
            "slot_key": "homepage.hero_logo",
            "extra": {"scope": "homepage"},
        },
    )
    assert create.status_code == 200
    create_payload = create.get_json()
    assert create_payload["ok"] is True
    assert create_payload["binding"]["binding_type"] == "site_asset"
    assert create_payload["binding"]["slot_key"] == "homepage.hero_logo"

    binding_id = create_payload["binding"]["id"]
    assert binding_id == 91
    assert fake_session.binding is not None

    delete = client.delete(
        f"/admin/api/media/bindings/{binding_id}",
        headers={"X-CSRF-Token": csrf_token},
    )
    assert delete.status_code == 200
    assert delete.get_json()["ok"] is True
    assert fake_session.deleted == [fake_session.binding]


def test_admin_table_virtual_media_fields_update(media_app: Flask, monkeypatch: pytest.MonkeyPatch):
    _mock_admin(monkeypatch)
    monkeypatch.setattr(routes, "_admin_table_allowed", lambda table, include_internal=False: True)
    monkeypatch.setattr(routes, "_get_table_columns", lambda table: ([{"name": "PMID", "type": "VARCHAR"}], ["PMID"]))
    monkeypatch.setattr(
        routes,
        "save_table_virtual_media_fields",
        lambda table, fields: (
            [],
            [
                {
                    "key": "structure_figure",
                    "label": "Structure Figure",
                    "multiple": False,
                    "placement": "record",
                    "required": False,
                    "sort_order": 10,
                }
            ],
        ),
    )
    monkeypatch.setattr(routes, "audit_admin_action", lambda *args, **kwargs: None)

    client = media_app.test_client()
    csrf_token = _login_admin(client)

    response = client.post(
        "/admin/api/tables/nonsense_sup_rna/virtual_media_fields",
        headers={"X-CSRF-Token": csrf_token},
        json={
            "fields": [
                {
                    "key": "structure_figure",
                    "label": "Structure Figure",
                    "multiple": False,
                    "placement": "record",
                    "required": False,
                    "sort_order": 10,
                }
            ]
        },
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["ok"] is True
    assert payload["virtual_media_fields"][0]["key"] == "structure_figure"


def test_admin_table_record_media_slots_route_returns_payload(media_app: Flask, monkeypatch: pytest.MonkeyPatch):
    _mock_admin(monkeypatch)
    monkeypatch.setattr(routes, "_admin_table_allowed", lambda table, include_internal=False: True)
    monkeypatch.setattr(
        routes,
        "_admin_table_record_slot_payloads",
        lambda table, row: (
            {
                "table": table,
                "record_key": "PMID=12345678",
                "match_columns": ["PMID"],
                "row": {"PMID": "12345678"},
                "slots": [
                    {
                        "key": "structure_figure",
                        "label": "Structure Figure",
                        "multiple": False,
                        "placement": "record",
                        "required": False,
                        "sort_order": 10,
                        "bindings": [],
                    }
                ],
            },
            {"structure_figure": {"key": "structure_figure", "multiple": False}},
            None,
        ),
    )

    client = media_app.test_client()
    _login_admin(client)

    response = client.post(
        "/admin/api/tables/nonsense_sup_rna/record_media_slots",
        json={"original_row": {"PMID": "12345678"}},
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["record_key"] == "PMID=12345678"
    assert payload["slots"][0]["key"] == "structure_figure"


def test_admin_table_record_media_slot_bind_replaces_single_slot(media_app: Flask, monkeypatch: pytest.MonkeyPatch):
    _mock_admin(monkeypatch)
    asset = _make_asset()
    existing_binding = SimpleNamespace(
        id=44,
        asset_id=77,
        binding_type="table_record_slot",
        resource_name="nonsense_sup_rna",
        field_name="",
        record_key="PMID=12345678",
        slot_key="structure_figure",
        extra_json=None,
        created_by=None,
        created_by_username="",
        created_at=None,
    )
    fake_session = FakeSession(asset=asset)
    monkeypatch.setattr(routes, "db", SimpleNamespace(session=fake_session))
    monkeypatch.setattr(routes, "_admin_table_allowed", lambda table, include_internal=False: True)
    monkeypatch.setattr(
        routes,
        "_admin_table_record_slot_payloads",
        lambda table, row: (
            {
                "table": table,
                "record_key": "PMID=12345678",
                "match_columns": ["PMID"],
                "row": {"PMID": "12345678"},
                "slots": [],
            },
            {"structure_figure": {"key": "structure_figure", "multiple": False}},
            None,
        ),
    )
    original_query = routes.MediaBinding.__dict__.get("query")
    type.__setattr__(routes.MediaBinding, "query", FakeBindingQueryRouter(None, [existing_binding]))
    monkeypatch.setattr(routes, "audit_admin_action", lambda *args, **kwargs: None)

    client = media_app.test_client()
    csrf_token = _login_admin(client)

    try:
        response = client.post(
            "/admin/api/tables/nonsense_sup_rna/record_media_slots/bind",
            headers={"X-CSRF-Token": csrf_token},
            json={
                "original_row": {"PMID": "12345678"},
                "slot_key": "structure_figure",
                "asset_id": 11,
                "replace_existing": True,
            },
        )
    finally:
        if original_query is not None:
            type.__setattr__(routes.MediaBinding, "query", original_query)

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["ok"] is True
    assert payload["binding"]["slot_key"] == "structure_figure"
    assert fake_session.deleted == [existing_binding]


def test_admin_media_legacy_pictureid_migration_endpoints_are_removed(
    media_app: Flask,
    monkeypatch: pytest.MonkeyPatch,
):
    _mock_admin(monkeypatch)
    client = media_app.test_client()
    csrf_token = _login_admin(client)

    preview = client.get("/admin/api/media/legacy_pictureid/preview")
    execute = client.post(
        "/admin/api/media/legacy_pictureid/migrate",
        headers={"X-CSRF-Token": csrf_token},
        json={"dry_run": True},
    )

    assert preview.status_code == 404
    assert execute.status_code == 404


def test_attach_public_row_media_bindings_adds_bound_field_asset(
    media_app: Flask,
    monkeypatch: pytest.MonkeyPatch,
):
    asset = _make_asset()
    binding = SimpleNamespace(
        id=12,
        asset_id=11,
        binding_type="table_field",
        resource_name="nonsense_sup_rna",
        field_name="pictureid",
        record_key="id=1",
        slot_key="",
        extra_json=json.dumps({"legacy_pictureid": "914869"}),
        created_by=None,
        created_by_username="",
        created_at=None,
    )
    fake_session = FakeSession(asset=asset)
    monkeypatch.setattr(routes, "db", SimpleNamespace(session=fake_session))
    monkeypatch.setattr(routes, "_admin_build_record_key", lambda table, row, col_names: ("id=1", ["id"]))
    original_query = routes.MediaBinding.__dict__.get("query")
    type.__setattr__(routes.MediaBinding, "query", FakeBindingQuery([binding]))

    try:
        rows = routes._attach_public_row_media_bindings(
            "nonsense_sup_rna",
            [{"id": 1, "pictureid": "914869"}],
            ["id", "pictureid"],
        )
    finally:
        if original_query is not None:
            type.__setattr__(routes.MediaBinding, "query", original_query)

    assert rows[0]["__media"]["record_key"] == "id=1"
    assert rows[0]["__media"]["fields"]["pictureid"][0]["asset"]["public_url"] == asset.public_url


def test_attach_alignment_result_media_enriches_row_data_with_bound_asset(
    media_app: Flask,
    monkeypatch: pytest.MonkeyPatch,
):
    asset = _make_asset()
    binding = SimpleNamespace(
        id=12,
        asset_id=11,
        binding_type="table_field",
        resource_name="nonsense_sup_rna",
        field_name="pictureid",
        record_key="id=1",
        slot_key="",
        extra_json=json.dumps({"legacy_pictureid": "914869"}),
        created_by=None,
        created_by_username="",
        created_at=None,
    )
    fake_session = FakeSession(asset=asset)
    monkeypatch.setattr(routes, "db", SimpleNamespace(session=fake_session))
    monkeypatch.setattr(routes, "_admin_build_record_key", lambda table, row, col_names: ("id=1", ["id"]))
    original_query = routes.MediaBinding.__dict__.get("query")
    type.__setattr__(routes.MediaBinding, "query", FakeBindingQuery([binding]))

    try:
        results = routes._attach_alignment_result_media(
            [
                {
                    "file": "nonsense_sup_rna",
                    "columns": ["id", "pictureid"],
                    "row_data": {"id": 1, "pictureid": "914869"},
                }
            ]
        )
    finally:
        if original_query is not None:
            type.__setattr__(routes.MediaBinding, "query", original_query)

    row_data = results[0]["row_data"]
    assert row_data["__media"]["record_key"] == "id=1"
    assert row_data["__media"]["fields"]["pictureid"][0]["asset"]["public_url"] == asset.public_url


def test_sync_legacy_pictureid_field_binding_creates_asset_and_binding(
    media_app: Flask,
    monkeypatch: pytest.MonkeyPatch,
):
    _mock_admin(monkeypatch)
    media_app.config["MINIO_BUCKET"] = "ensure"
    fake_session = FakeSession(asset=None)
    monkeypatch.setattr(routes, "db", SimpleNamespace(session=fake_session))
    monkeypatch.setattr(
        routes,
        "_legacy_pictureid_row_summary",
        lambda table, row, col_names: {
            "table": table,
            "pictureid": "914869",
            "pictureid_normalized": "914869",
            "record_key": "PMID=12345678",
            "caption": "example caption",
            "object_key": "picture/914869.png",
            "public_url": "https://example.com/picture/914869.png",
        },
    )
    monkeypatch.setattr(routes, "_admin_build_record_key", lambda table, row, col_names: ("PMID=12345678", ["PMID"]))
    monkeypatch.setattr(routes, "_admin_display_name", lambda table: "Natural Nonsense sup-tRNA")
    original_asset_query = routes.MediaAsset.__dict__.get("query")
    original_binding_query = routes.MediaBinding.__dict__.get("query")
    type.__setattr__(routes.MediaAsset, "query", FakeAssetQueryRouter(None))
    type.__setattr__(routes.MediaBinding, "query", FakeFilterByRouter([]))

    try:
        with media_app.app_context():
            routes._sync_legacy_pictureid_field_binding(
                "nonsense_sup_rna",
                {"PMID": "12345678", "pictureid": "914869"},
                ["PMID", "pictureid"],
                actor=SimpleNamespace(id=7, username="media-admin"),
            )
    finally:
        if original_asset_query is not None:
            type.__setattr__(routes.MediaAsset, "query", original_asset_query)
        if original_binding_query is not None:
            type.__setattr__(routes.MediaBinding, "query", original_binding_query)

    assert any(isinstance(obj, MediaAsset) for obj in fake_session.added)
    assert any(isinstance(obj, MediaBinding) for obj in fake_session.added)


def test_sync_legacy_pictureid_field_binding_removes_existing_bindings_when_pictureid_cleared(
    media_app: Flask,
    monkeypatch: pytest.MonkeyPatch,
):
    binding = SimpleNamespace(
        id=44,
        asset_id=11,
        binding_type="table_field",
        resource_name="nonsense_sup_rna",
        field_name="pictureid",
        record_key="PMID=12345678",
        slot_key="",
    )
    fake_session = FakeSession(asset=None, binding=binding)
    monkeypatch.setattr(routes, "db", SimpleNamespace(session=fake_session))
    monkeypatch.setattr(routes, "_legacy_pictureid_row_summary", lambda table, row, col_names: None)
    monkeypatch.setattr(routes, "_admin_build_record_key", lambda table, row, col_names: ("PMID=12345678", ["PMID"]))
    original_binding_query = routes.MediaBinding.__dict__.get("query")
    type.__setattr__(routes.MediaBinding, "query", FakeFilterByRouter([binding]))

    try:
        with media_app.app_context():
            routes._sync_legacy_pictureid_field_binding(
                "nonsense_sup_rna",
                {"PMID": "12345678", "pictureid": ""},
                ["PMID", "pictureid"],
            )
    finally:
        if original_binding_query is not None:
            type.__setattr__(routes.MediaBinding, "query", original_binding_query)

    assert fake_session.deleted == [binding]


def test_clear_record_media_bindings_removes_field_and_slot_bindings(
    media_app: Flask,
    monkeypatch: pytest.MonkeyPatch,
):
    field_binding = SimpleNamespace(
        id=44,
        asset_id=11,
        binding_type="table_field",
        resource_name="nonsense_sup_rna",
        field_name="pictureid",
        record_key="PMID=12345678",
        slot_key="",
    )
    slot_binding = SimpleNamespace(
        id=45,
        asset_id=12,
        binding_type="table_record_slot",
        resource_name="nonsense_sup_rna",
        field_name="",
        record_key="PMID=12345678",
        slot_key="structure_figure",
    )
    unrelated_binding = SimpleNamespace(
        id=46,
        asset_id=13,
        binding_type="site_asset",
        resource_name="site_asset_slots_json",
        field_name="",
        record_key="PMID=12345678",
        slot_key="homepage.hero_logo",
    )
    fake_session = FakeSession()
    monkeypatch.setattr(routes, "db", SimpleNamespace(session=fake_session))
    monkeypatch.setattr(routes, "_admin_build_record_key", lambda table, row, col_names: ("PMID=12345678", ["PMID"]))
    original_binding_query = routes.MediaBinding.__dict__.get("query")
    type.__setattr__(routes.MediaBinding, "query", FakeFilterByRouter([field_binding, slot_binding, unrelated_binding]))

    try:
        with media_app.app_context():
            routes._clear_record_media_bindings(
                "nonsense_sup_rna",
                {"PMID": "12345678"},
                ["PMID", "pictureid"],
            )
    finally:
        if original_binding_query is not None:
            type.__setattr__(routes.MediaBinding, "query", original_binding_query)

    assert fake_session.deleted == [field_binding, slot_binding]
