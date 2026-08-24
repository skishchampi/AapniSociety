import json

import pytest

pytestmark = pytest.mark.django_db

WORKER_PHONE = "+919****0201"
HOUSEHOLD_PHONE = "+919****0202"
OTHER_HOUSEHOLD_PHONE = "+919****0203"
MOD_PHONE = "+919****0200"


def _auth(api, access):
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")


def _make_moderator(api, signin):
    from django.contrib.auth import get_user_model

    access, _ = signin(api, MOD_PHONE, role="household", full_name="Mod")
    get_user_model().objects.filter(phone=MOD_PHONE).update(primary_role="moderator")
    return access


def _make_worker(api, signin):
    """Sign in a worker and return (access, worker_profile)."""
    from django.contrib.auth import get_user_model

    from apps.members.models import WorkerProfile

    access, _ = signin(api, WORKER_PHONE, role="worker", full_name="Asha")
    worker_user = get_user_model().objects.get(phone=WORKER_PHONE)
    worker = WorkerProfile.objects.get_or_create(user=worker_user)[0]
    _auth(api, access)
    return access, worker


def _file_introduction(api, signin, worker_id, note="Two hours daily"):
    access, _ = signin(api, HOUSEHOLD_PHONE, role="household")
    _auth(api, access)
    r = api.post(
        "/api/v1/introductions/",
        {"worker": worker_id, "note": note},
        format="json",
    )
    assert r.status_code == 201, r.content
    return r.json()["id"]


def test_household_files_introduction(api, signin):
    _, worker = _make_worker(api, signin)
    intro_id = _file_introduction(api, signin, worker.id)
    assert intro_id > 0


def test_worker_cannot_file_introduction(api, signin):
    _, worker = _make_worker(api, signin)
    w_access, _ = signin(api, WORKER_PHONE, role="worker")
    _auth(api, w_access)
    r = api.post("/api/v1/introductions/", {"worker": worker.id}, format="json")
    assert r.status_code == 403


def test_full_lifecycle_records_events_in_order(api, signin):
    mod_access = _make_moderator(api, signin)
    w_access, worker = _make_worker(api, signin)
    intro_id = _file_introduction(api, signin, worker.id)

    _auth(api, mod_access)
    r = api.post(f"/api/v1/moderation/introductions/{intro_id}/route/")
    assert r.status_code == 200, r.content

    _auth(api, w_access)
    assert api.post(f"/api/v1/introductions/{intro_id}/accept/").status_code == 200
    r = api.post(f"/api/v1/introductions/{intro_id}/reveal-contact/")
    assert r.status_code == 200, r.content
    body = r.json()
    assert body["revealed"] is True
    assert body["phone"] == WORKER_PHONE

    events = api.get(f"/api/v1/introductions/{intro_id}/events/").json()
    whats = [e["what"] for e in events]
    assert whats == ["requested", "routed", "accepted", "contact_revealed"]


def test_reveal_before_accept_conflicts(api, signin):
    mod_access = _make_moderator(api, signin)
    w_access, worker = _make_worker(api, signin)
    intro_id = _file_introduction(api, signin, worker.id)

    _auth(api, mod_access)
    api.post(f"/api/v1/moderation/introductions/{intro_id}/route/")

    _auth(api, w_access)
    r = api.post(f"/api/v1/introductions/{intro_id}/reveal-contact/")
    assert r.status_code == 409


def test_only_addressed_worker_can_decide_or_reveal(api, signin):
    mod_access = _make_moderator(api, signin)
    _, worker = _make_worker(api, signin)
    intro_id = _file_introduction(api, signin, worker.id)

    _auth(api, mod_access)
    api.post(f"/api/v1/moderation/introductions/{intro_id}/route/")

    stranger_access, _ = signin(api, OTHER_HOUSEHOLD_PHONE, role="worker")
    _auth(api, stranger_access)
    assert api.post(f"/api/v1/introductions/{intro_id}/accept/").status_code == 403
    assert api.post(f"/api/v1/introductions/{intro_id}/reveal-contact/").status_code == 403


def test_decline_reason_never_reaches_household(api, signin):
    mod_access = _make_moderator(api, signin)
    w_access, worker = _make_worker(api, signin)
    intro_id = _file_introduction(api, signin, worker.id)

    _auth(api, mod_access)
    api.post(f"/api/v1/moderation/introductions/{intro_id}/route/")

    _auth(api, w_access)
    r = api.post(f"/api/v1/introductions/{intro_id}/decline/", {"reason": "too far"}, format="json")
    assert r.status_code == 200

    h_access, _ = signin(api, HOUSEHOLD_PHONE, role="household")
    _auth(api, h_access)
    listing = api.get("/api/v1/introductions/mine/").json()
    row = next(row for row in listing if row["id"] == intro_id)
    assert row["status"] == "declined"
    assert "too far" not in json.dumps(listing)


def test_serializer_never_carries_phone_or_email(api, signin):
    mod_access = _make_moderator(api, signin)
    w_access, worker = _make_worker(api, signin)
    _file_introduction(api, signin, worker.id)

    _auth(api, mod_access)
    payload = api.get("/api/v1/introductions/mine/").json()
    text = json.dumps(payload)
    assert WORKER_PHONE not in text and HOUSEHOLD_PHONE not in text
    assert '"phone"' not in text and '"email"' not in text

    _auth(api, w_access)
    worker_view = api.get("/api/v1/introductions/mine/").json()
    assert WORKER_PHONE not in json.dumps(worker_view)


def test_stranger_gets_404_on_foreign_introduction(api, signin):
    mod_access = _make_moderator(api, signin)
    _, worker = _make_worker(api, signin)
    intro_id = _file_introduction(api, signin, worker.id)

    _auth(api, mod_access)
    api.post(f"/api/v1/moderation/introductions/{intro_id}/route/")

    other_access, _ = signin(api, OTHER_HOUSEHOLD_PHONE, role="household")
    _auth(api, other_access)
    assert api.get(f"/api/v1/introductions/{intro_id}/events/").status_code == 404


def test_household_can_withdraw_open_request(api, signin):
    mod_access = _make_moderator(api, signin)
    _, worker = _make_worker(api, signin)
    intro_id = _file_introduction(api, signin, worker.id)

    h_access, _ = signin(api, HOUSEHOLD_PHONE, role="household")
    _auth(api, h_access)
    r = api.post(f"/api/v1/introductions/{intro_id}/withdraw/")
    assert r.status_code == 200
    assert r.json()["status"] == "withdrawn"

    _auth(api, mod_access)
    r = api.post(f"/api/v1/moderation/introductions/{intro_id}/route/")
    assert r.status_code == 409


def test_double_route_conflicts(api, signin):
    mod_access = _make_moderator(api, signin)
    _, worker = _make_worker(api, signin)
    intro_id = _file_introduction(api, signin, worker.id)

    _auth(api, mod_access)
    first = api.post(f"/api/v1/moderation/introductions/{intro_id}/route/")
    second = api.post(f"/api/v1/moderation/introductions/{intro_id}/route/")
    assert first.status_code == 200
    assert second.status_code == 409
