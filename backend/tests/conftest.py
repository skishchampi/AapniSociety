import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api():
    return APIClient()


def sign_in(api, phone, role="household", full_name=""):
    """Run the full dev OTP flow and return (access_token, user_dict)."""
    r = api.post("/api/v1/auth/otp/request/", {"phone": phone}, format="json")
    assert r.status_code == 200, r.content
    code = r.json()["dev_code"]
    r = api.post(
        "/api/v1/auth/otp/verify/",
        {"phone": phone, "code": code, "primary_role": role, "full_name": full_name},
        format="json",
    )
    assert r.status_code == 200, r.content
    body = r.json()
    return body["access"], body["user"]


@pytest.fixture
def signin():
    return sign_in
