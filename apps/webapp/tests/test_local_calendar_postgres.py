import socket

import pytest

from scripts.local_calendar_postgres import LocalCalendarPostgres, ENV_NAMES, DOCKER


def test_local_container_has_explicit_local_engine_and_refuses_existing_database_configuration(monkeypatch):
    assert DOCKER[1:] == ["--host", "npipe:////./pipe/dockerDesktopLinuxEngine"]
    for name in ENV_NAMES:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv(ENV_NAMES[0], "must-not-be-read")
    fixture = LocalCalendarPostgres()
    monkeypatch.setattr(fixture,"command",lambda *args,**kwargs:pytest.fail("No Docker action permitted"))
    with pytest.raises(RuntimeError,match="Refusing existing"):
        fixture.__enter__()


def test_local_container_never_reuses_an_occupied_port(monkeypatch):
    for name in ENV_NAMES:
        monkeypatch.delenv(name, raising=False)
    with socket.socket() as existing:
        try:
            existing.bind(("127.0.0.1",55433))
        except OSError:
            pytest.skip("Dedicated local port is already occupied; do not touch its owner")
        existing.listen()
        fixture=LocalCalendarPostgres()
        monkeypatch.setattr(fixture,"command",lambda *args,**kwargs:pytest.fail("No Docker action permitted"))
        with pytest.raises(OSError):
            fixture.__enter__()


def test_cleanup_only_removes_confirmed_owned_container_identity(monkeypatch):
    fixture=LocalCalendarPostgres()
    fixture.container="unknown-untrusted-value"
    monkeypatch.setattr(fixture,"command",lambda *args,**kwargs:pytest.fail("Unknown container must not be removed"))
    fixture.__exit__(None,None,None)
    assert not fixture.removed
