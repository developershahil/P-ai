import json

from personal_ai.security import permissions


def test_load_permissions_returns_defaults_when_file_missing(tmp_path, monkeypatch):
    fake_perm_file = tmp_path / "app_permissions.json"
    monkeypatch.setattr(permissions, "PERM_FILE", fake_perm_file)

    assert permissions.load_permissions() == {"allowed_apps": {}, "allowed_folders": []}


def test_load_permissions_handles_corrupt_json(tmp_path, monkeypatch):
    fake_perm_file = tmp_path / "app_permissions.json"
    fake_perm_file.write_text("{not-valid-json", encoding="utf-8")
    monkeypatch.setattr(permissions, "PERM_FILE", fake_perm_file)

    assert permissions.load_permissions() == {"allowed_apps": {}, "allowed_folders": []}


def test_load_permissions_normalizes_bad_types(tmp_path, monkeypatch):
    fake_perm_file = tmp_path / "app_permissions.json"
    fake_perm_file.write_text(
        json.dumps({"allowed_apps": [], "allowed_folders": "C:/Users"}),
        encoding="utf-8",
    )
    monkeypatch.setattr(permissions, "PERM_FILE", fake_perm_file)

    assert permissions.load_permissions() == {"allowed_apps": {}, "allowed_folders": []}


def test_blocked_exe_list_includes_powershell_variants():
    assert permissions.is_blocked_exe("powershell.exe")
    assert permissions.is_blocked_exe("pwsh.exe")
    assert permissions.is_blocked_exe("powershell_ise.exe")
