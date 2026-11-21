from contextlib import asynccontextmanager
from datetime import UTC, date, datetime, timedelta
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from competence_hub_api.auth.session_repository import SessionPrincipal
from competence_hub_api.main import create_app
from competence_hub_api.portal import requests as operations
from competence_hub_api.portal.requests import CoachingRequestRepository, RequestError
from competence_hub_api.security.cookies import SESSION_COOKIE_NAME
from competence_hub_api.security.tokens import digest_token

BASE = "/api/v1/portal/requests"
ORIGIN = "https://portal.example.invalid"
CSRF = "synthetic-request-csrf-token"
HEADERS = {"Origin": ORIGIN, "X-CSRF-Token": CSRF}
NOW = datetime(2026, 11, 21, tzinfo=UTC)


def principal(role):
    return SessionPrincipal(
        uuid4(), uuid4(), "Synthetic", (role,), NOW,
        NOW + timedelta(minutes=30), NOW + timedelta(hours=8), digest_token(CSRF),
    )


def client(role, repository):
    sessions = AsyncMock()
    sessions.refresh_active_session.return_value = principal(role) if role else None
    return TestClient(
        create_app(
            calendar_session_repository=sessions, coaching_request_repository=repository,
            allowed_origin=ORIGIN, clock=lambda: NOW,
        ),
        base_url=ORIGIN,
        cookies={SESSION_COOKIE_NAME: "synthetic-request-session-token"},
    )


def repository_double():
    return AsyncMock(spec=CoachingRequestRepository)


def create_payload():
    return {"subject": "Synthetic request", "description": "Staff only", "company_id": str(uuid4())}


def test_default_off_capability_and_resource_routes():
    http = client("internal", None)
    response = http.get(BASE + "/capabilities")
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert response.json() == {"enabled": False, "can_read": False, "can_manage": False, "scope": None}
    assert http.get(BASE).status_code == 404
    assert http.get(BASE + "/options?bucket=coaches").status_code == 404


@pytest.mark.parametrize("role, expected", [(None, 401), ("coach", 403), ("company_contact", 403)])
def test_only_staff_can_use_options_or_write(role, expected):
    repository = repository_double()
    http = client(role, repository)
    request_id = uuid4()
    responses = (
        http.get(BASE + "/options?bucket=private_customers"),
        http.post(BASE, json=create_payload(), headers=HEADERS),
        http.patch(f"{BASE}/{request_id}", json={"version": 1, "status": "closed"}, headers=HEADERS),
        http.post(f"{BASE}/{request_id}/notes", json={"version": 1, "visibility": "coach", "body": "Test"},
                  headers=HEADERS),
    )
    assert all(response.status_code == expected and response.headers["cache-control"] == "no-store"
               for response in responses)
    assert repository.mock_calls == []


@pytest.mark.parametrize("role", ["internal", "admin", "calendar_reviewer"])
def test_staff_create_requires_exact_origin_and_session_csrf(role):
    repository = repository_double()
    repository.create.return_value = {"id": uuid4(), "version": 1}
    http = client(role, repository)
    payload = {**create_payload(), "follow_up_on": "2026-11-25"}
    for headers in ({}, {**HEADERS, "Origin": "https://other.example.invalid"}, {"Origin": ORIGIN},
                    {**HEADERS, "X-CSRF-Token": "incorrect-synthetic-csrf-token"}):
        assert http.post(BASE, json=payload, headers=headers).status_code == 403
    repository.create.assert_not_awaited()
    saved = http.post(BASE, json=payload, headers=HEADERS)
    assert saved.status_code == 201
    actor, data, timestamp = repository.create.await_args.args
    assert (actor.roles, timestamp) == ((role,), NOW)
    assert data["status"] == "open"
    assert str(data["company_id"]) == payload["company_id"]
    assert data["follow_up_on"] == date(2026, 11, 25)


def test_mutation_payloads_are_bounded_strict_and_do_not_echo_data():
    repository = repository_double()
    http = client("internal", repository)
    request_id = uuid4()
    payload = create_payload()
    for invalid in (
        {"description": None}, {"subject": " "}, {"subject": "x" * 161}, {"description": "x" * 4001},
        {"follow_up_on": "2026-11-25T00:00:00"}, {"coach_summary": "bad\x00text"},
        {"notes": "private-marker"}, {"coach_release_id": str(uuid4())},
    ):
        response = http.post(BASE, json={**payload, **invalid}, headers=HEADERS)
        assert response.status_code == 400
        assert "private-marker" not in response.text
    for invalid in ({"version": True, "status": "closed"}, {"version": 1},
                    {"version": 1, "status": None}, {"status": "closed"}, {"version": "1", "status": "closed"}):
        assert http.patch(f"{BASE}/{request_id}", json=invalid, headers=HEADERS).status_code == 400
    for invalid in (
        {"version": 1, "body": "test"}, {"version": 1, "visibility": "company", "body": "test"},
        {"version": 1, "visibility": "internal", "body": "x" * 2001},
        {"version": 1, "visibility": "coach", "body": " "},
    ):
        assert http.post(f"{BASE}/{request_id}/notes", json=invalid, headers=HEADERS).status_code == 400
    assert repository.mock_calls == []


def test_writes_use_same_version_contract_and_report_stale_without_payload():
    repository = repository_double()
    http = client("internal", repository)
    request_id = uuid4()
    stale = RequestError("request_version_conflict", 409)
    repository.update.side_effect = stale
    repository.add_note.side_effect = stale
    note = {"version": 4, "visibility": "internal", "body": "private-marker"}
    for response in (
        http.patch(f"{BASE}/{request_id}", json={"version": 4, "follow_up_on": None}, headers=HEADERS),
        http.post(f"{BASE}/{request_id}/notes", json=note, headers=HEADERS),
    ):
        assert response.status_code == 409
        assert response.json()["code"] == "request_version_conflict"
        assert "private-marker" not in response.text
    assert repository.update.await_args.args[1:4] == (request_id, 4, {"follow_up_on": None})
    assert repository.add_note.await_args.args[1:5] == (request_id, 4, "internal", note["body"])


class TransactionEngine:
    @asynccontextmanager
    async def begin(self):
        yield object()


@pytest.mark.parametrize("existing", ["company_id", "private_customer_id"])
@pytest.mark.parametrize("attempt", ["replace", "clear", "switch"])
def test_patch_cannot_transfer_a_request_to_another_customer(monkeypatch, existing, attempt):
    request_id, customer_id = uuid4(), uuid4()
    other = "private_customer_id" if existing == "company_id" else "company_id"
    current = {existing: customer_id, other: None, "subject": "Original"}
    changes = {"replace": {existing: str(uuid4())}, "clear": {existing: None},
               "switch": {existing: None, other: str(uuid4())}}[attempt]
    lock = AsyncMock(return_value=current)
    event = AsyncMock()
    write = AsyncMock()
    monkeypatch.setattr(operations, "_lock_current", lock)
    monkeypatch.setattr(operations, "_event", event)
    repository = CoachingRequestRepository(TransactionEngine())
    monkeypatch.setattr(repository, "_update_row", write)
    http = client("internal", repository)
    response = http.patch(f"{BASE}/{request_id}", json={"version": 2, "subject": "Edited", **changes}, headers=HEADERS)
    assert response.status_code == 400
    assert response.json()["code"] == "request_customer_immutable"
    assert lock.await_args.args[1:] == (request_id, 2)
    write.assert_not_awaited()
    event.assert_not_awaited()


@pytest.mark.parametrize("new_summary", [None, "Old released summary", "Explicit new summary"])
def test_assignment_rotation_cannot_carry_forward_old_release(monkeypatch, new_summary):
    request_id, new_coach, company, previous_release = uuid4(), uuid4(), uuid4(), uuid4()
    current = {
        "company_id": company, "private_customer_id": None, "coach_id": uuid4(),
        "coach_summary": "Old released summary", "coach_release_id": previous_release,
    }
    write = AsyncMock(return_value={"id": request_id, "version": 3})
    validate = AsyncMock()
    monkeypatch.setattr(operations, "_lock_current", AsyncMock(return_value=current))
    monkeypatch.setattr(operations, "_validate_changes", validate)
    monkeypatch.setattr(operations, "_event", AsyncMock())
    monkeypatch.setattr(operations, "_detail", AsyncMock(return_value={"version": 3}))
    repository = CoachingRequestRepository(TransactionEngine())
    monkeypatch.setattr(repository, "_update_row", write)
    http = client("internal", repository)
    payload = {"version": 2, "coach_id": str(new_coach), "company_id": str(company)}
    if new_summary is not None:
        payload["coach_summary"] = new_summary
    response = http.patch(f"{BASE}/{request_id}", json=payload, headers=HEADERS)
    assert response.status_code == 200
    fields = write.await_args.args[-1]
    assert fields["coach_id"] == new_coach
    assert fields["coach_release_id"] not in {None, previous_release}
    assert fields["coach_summary"] == (new_summary if new_summary == "Explicit new summary" else None)
    assert "company_id" not in fields
