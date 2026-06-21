import pytest

pytestmark = pytest.mark.django_db


def test_worker_and_household_can_sign_in(api, signin):
    """Roadmap acceptance: worker and household users can sign in locally."""
    w_access, w_user = signin(api, "+919900001111", role="worker", full_name="Asha")
    assert w_user["primary_role"] == "worker"

    h_access, h_user = signin(api, "+919900002222", role="household")
    assert h_user["primary_role"] == "household"
    assert w_access and h_access


def test_me_requires_auth(api):
    assert api.get("/api/v1/me/").status_code == 401


def test_me_returns_current_user(api, signin):
    access, _ = signin(api, "+919900003333", role="worker")
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    r = api.get("/api/v1/me/")
    assert r.status_code == 200
    assert r.json()["phone"] == "+919900003333"
    assert r.json()["primary_role"] == "worker"


def test_wrong_code_rejected(api):
    api.post("/api/v1/auth/otp/request/", {"phone": "+919900004444"}, format="json")
    r = api.post(
        "/api/v1/auth/otp/verify/",
        {"phone": "+919900004444", "code": "000000"},
        format="json",
    )
    # Vanishingly unlikely the random code is 000000; treat as rejection path.
    assert r.status_code in (400,)


def test_returning_user_logs_in_without_duplicate(api, signin):
    signin(api, "+919900005555", role="worker")
    _, user = signin(api, "+919900005555", role="worker")
    from apps.accounts.models import User

    assert User.objects.filter(phone="+919900005555").count() == 1
