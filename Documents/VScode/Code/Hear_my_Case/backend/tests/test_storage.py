"""Tests for storage helpers."""
from app.services.storage import build_storage_key, delete_stored_file


def test_build_storage_key_preserves_extension():
    key = build_storage_key("evidence", "document.pdf")
    assert key.startswith("evidence/")
    assert key.endswith(".pdf")


def test_delete_stored_file_removes_local_file(tmp_path, monkeypatch):
    uploads = tmp_path / "uploads"
    uploads.mkdir()
    file_path = uploads / "evidence" / "file.txt"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text("hello")

    monkeypatch.setattr("app.services.storage.settings.UPLOAD_DIR", str(uploads))
    delete_stored_file("/uploads/evidence/file.txt")

    assert not file_path.exists()
