from uuid import uuid4

from fastapi.testclient import TestClient
from pydantic import ValidationError
import pytest

from competence_hub_api.main import create_app
from competence_hub_api.web.reservations import CreateReservation, ReviewReservation


def test_default_app_does_not_expose_reservation_data_or_writes():
    with TestClient(create_app()) as client:
        base = "/api/v1/portal/reservations"
        assert client.get(base + "/capabilities").json() == {}
        assert client.get(base).status_code == 404
        assert client.post(base + f"/offers/{uuid4()}", json={}).status_code == 404


@pytest.mark.parametrize("payload", [
    {"seats": True}, {"seats": "2"}, {"seats": 0}, {"seats": 501},
    {"revision_number": "1"}, {"contact_confirmed": "true"}, {"company_id": str(uuid4())},
    {"phone": "x" * 51}, {"message": "x" * 501},
])
def test_request_is_strict_bounded_and_cannot_choose_a_company(payload):
    with pytest.raises(ValidationError):
        CreateReservation.model_validate({
            "request_id": str(uuid4()), "revision_number": 1,
            "contact_confirmed": True, "seats": 2, **payload,
        })


@pytest.mark.parametrize(("outcome", "reason"), [("confirmed", "Demo"), ("approved", "  ")])
def test_review_never_accepts_contract_confirmation_or_blank_reasons(outcome, reason):
    with pytest.raises(ValidationError):
        ReviewReservation.model_validate({"request_id": str(uuid4()), "outcome": outcome, "reason": reason})
