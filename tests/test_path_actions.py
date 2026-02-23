"""Tests for opening/closing user file and folder paths."""

from pathlib import Path

from personal_ai.actions import app_actions


def test_extract_path_query_prefers_quoted_path() -> None:
    query = app_actions._extract_path_query('open file "C:/Users/test/Documents/report.txt"')
    assert query == "C:/Users/test/Documents/report.txt"


def test_extract_path_query_from_plain_text() -> None:
    query = app_actions._extract_path_query("open folder projects")
    assert query == "projects"


def test_resolve_target_path_from_allowed_folder(tmp_path: Path, monkeypatch) -> None:
    docs = tmp_path / "Documents"
    docs.mkdir()
    target = docs / "report.txt"
    target.write_text("hello", encoding="utf-8")

    monkeypatch.setattr(app_actions, "load_permissions", lambda: {"allowed_apps": {}, "allowed_folders": [str(docs)]})

    resolved = app_actions._resolve_target_path("report.txt")

    assert resolved == target.resolve()


def test_ensure_folder_permission_accepts_and_saves(tmp_path: Path, monkeypatch) -> None:
    target = tmp_path / "notes" / "todo.txt"
    target.parent.mkdir()
    target.write_text("todo", encoding="utf-8")

    saved = {}
    monkeypatch.setattr(app_actions, "load_permissions", lambda: {"allowed_apps": {}, "allowed_folders": []})
    monkeypatch.setattr(app_actions, "save_permissions", lambda perms: saved.update(perms))
    monkeypatch.setattr(app_actions, "listen_text", lambda: "yes")
    monkeypatch.setattr(app_actions, "speak", lambda _msg: None)

    assert app_actions._ensure_folder_permission(target)
    assert str(target.parent) in saved["allowed_folders"]
