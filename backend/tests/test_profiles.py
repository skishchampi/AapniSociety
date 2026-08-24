import pytest

pytestmark = pytest.mark.django_db


def test_worker_can_create_profile(api, signin):
    access, _ = signin(api, "+919900010001", role="worker")
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    r = api.put(
        "/api/v1/me/worker-profile/",
        {"display_name": "Asha", "languages": ["gu", "hi"], "default_rate_floor": "8000.00"},
        format="json",
    )
    assert r.status_code == 200, r.content
    assert r.json()["display_name"] == "Asha"
    assert r.json()["languages"] == ["gu", "hi"]


def test_household_can_create_profile(api, signin):
    access, _ = signin(api, "+919900010002", role="household")
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    r = api.put(
        "/api/v1/me/household-profile/",
        {"display_name": "Sharma household"},
        format="json",
    )
    assert r.status_code == 200, r.content
    assert r.json()["display_name"] == "Sharma household"


def test_me_reflects_profile_presence(api, signin):
    access, _ = signin(api, "+919900010003", role="worker")
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    assert api.get("/api/v1/me/").json()["has_worker_profile"] is False
    api.put("/api/v1/me/worker-profile/", {"display_name": "X"}, format="json")
    assert api.get("/api/v1/me/").json()["has_worker_profile"] is True


def test_service_categories_public(api):
    from apps.members.models import ServiceCategory

    ServiceCategory.objects.create(key="maid", label="Maid")
    r = api.get("/api/v1/service-categories/")
    assert r.status_code == 200
    assert any(c["key"] == "maid" for c in r.json())
