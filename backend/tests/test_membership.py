import pytest

pytestmark = pytest.mark.django_db


def _auth(api, access):
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")


def _make_moderator(api, signin, phone="+919****0100"):
    """Sign in as a normal user, then elevate in the DB.

    The OTP verify endpoint refuses self-assigned moderator roles by design.
    """
    from django.contrib.auth import get_user_model

    access, _ = signin(api, phone, role="household", full_name="Mod")
    get_user_model().objects.filter(phone=phone).update(primary_role="moderator")
    return access


def _make_category(key="maid", label="Maid"):
    from apps.members.models import ServiceCategory

    return ServiceCategory.objects.create(key=key, label=label)


def test_membership_request_created_pending(api, signin):
    access, _ = signin(api, "+919****0101", role="household")
    _auth(api, access)
    r = api.post("/api/v1/membership/request/", {"role_sought": "worker"}, format="json")
    assert r.status_code == 201, r.content
    assert r.json()["status"] == "pending"
    assert r.json()["role_sought"] == "worker"


def test_duplicate_pending_request_conflicts(api, signin):
    access, _ = signin(api, "+919****0102", role="household")
    _auth(api, access)
    api.post("/api/v1/membership/request/", {"role_sought": "worker"}, format="json")
    r = api.post("/api/v1/membership/request/", {"role_sought": "worker"}, format="json")
    assert r.status_code == 409


def test_request_for_held_role_conflicts(api, signin):
    access, _ = signin(api, "+919****0103", role="household")
    _auth(api, access)
    r = api.post("/api/v1/membership/request/", {"role_sought": "household"}, format="json")
    assert r.status_code == 409


def test_invalid_role_rejected(api, signin):
    access, _ = signin(api, "+919****0104", role="household")
    _auth(api, access)
    r = api.post("/api/v1/membership/request/", {"role_sought": "admin"}, format="json")
    assert r.status_code == 400


def test_non_moderator_cannot_see_queue_or_review(api, signin):
    access, _ = signin(api, "+919****0105", role="household")
    _auth(api, access)
    assert api.get("/api/v1/membership/queue/").status_code == 403
    r = api.post("/api/v1/membership/requests/1/review/", {"action": "approve"}, format="json")
    assert r.status_code == 403


def test_moderator_sees_only_pending_in_queue(api, signin):
    mod_access = _make_moderator(api, signin, phone="+919****0106")
    h_access, _ = signin(api, "+919****0107", role="household")

    _auth(api, h_access)
    api.post("/api/v1/membership/request/", {"role_sought": "worker"}, format="json")

    _auth(api, mod_access)
    r = api.get("/api/v1/membership/queue/")
    assert r.status_code == 200
    assert len(r.json()) == 1
    assert r.json()[0]["status"] == "pending"


def test_moderator_approves_and_role_flips(api, signin):
    from django.contrib.auth import get_user_model

    User = get_user_model()
    mod_access = _make_moderator(api, signin, phone="+919****0108")
    h_access, _ = signin(api, "+919****0109", role="household")

    _auth(api, h_access)
    r = api.post("/api/v1/membership/request/", {"role_sought": "worker"}, format="json")
    request_id = r.json()["id"]

    _auth(api, mod_access)
    r = api.post(
        f"/api/v1/membership/requests/{request_id}/review/", {"action": "approve"}, format="json"
    )
    assert r.status_code == 200, r.content
    assert r.json()["status"] == "approved"

    requester = User.objects.get(phone="+919****0109")
    assert requester.primary_role == "worker"


def test_moderator_reject_stores_reason(api, signin):
    mod_access = _make_moderator(api, signin, phone="+919****0110")
    h_access, _ = signin(api, "+919****0111", role="household")

    _auth(api, h_access)
    r = api.post("/api/v1/membership/request/", {"role_sought": "worker"}, format="json")
    request_id = r.json()["id"]

    _auth(api, mod_access)
    r = api.post(
        f"/api/v1/membership/requests/{request_id}/review/",
        {"action": "reject", "reason": "Incomplete verification"},
        format="json",
    )
    assert r.status_code == 200, r.content
    body = r.json()
    assert body["status"] == "rejected"
    assert body["rejection_reason"] == "Incomplete verification"

    r2 = api.post(
        f"/api/v1/membership/requests/{request_id}/review/", {"action": "approve"}, format="json"
    )
    assert r2.status_code == 409


def test_household_creates_service_need(api, signin):
    cat = _make_category("maid", "Maid")
    access, _ = signin(api, "+919****0112", role="household")
    _auth(api, access)
    r = api.post(
        "/api/v1/needs/",
        {"category": cat.id, "title": "Morning help", "details": "Two hours, daily"},
        format="json",
    )
    assert r.status_code == 201, r.content
    assert r.json()["status"] == "open"
    assert r.json()["household"] is not None


def test_worker_cannot_create_need(api, signin):
    cat = _make_category("cook", "Cook")
    access, _ = signin(api, "+919****0113", role="worker")
    _auth(api, access)
    r = api.post("/api/v1/needs/", {"category": cat.id, "title": "X"}, format="json")
    assert r.status_code == 403


def test_needs_are_owner_scoped(api, signin):
    from django.contrib.auth import get_user_model

    from apps.members.models import HouseholdProfile, ServiceNeed

    User = get_user_model()
    cat = _make_category("cleaning", "Cleaning")

    access_a, _ = signin(api, "+919****0114", role="household")
    owner_a = User.objects.get(phone="+919****0114")
    hh_a = HouseholdProfile.objects.get_or_create(user=owner_a)[0]
    need = ServiceNeed.objects.create(household=hh_a, category=cat, title="Private need")

    access_b, _ = signin(api, "+919****0115", role="household")
    _auth(api, access_b)
    assert api.get(f"/api/v1/needs/{need.id}/").status_code == 404
    assert api.get("/api/v1/needs/").json() == []

    _auth(api, access_a)
    assert api.get(f"/api/v1/needs/{need.id}/").status_code == 200
    assert len(api.get("/api/v1/needs/").json()) == 1


def test_profile_responses_expose_no_contact_fields(api, signin):
    access, _ = signin(api, "+919****0116", role="worker")
    _auth(api, access)
    body = api.get("/api/v1/me/worker-profile/").json()
    assert "phone" not in body
    assert "email" not in body
