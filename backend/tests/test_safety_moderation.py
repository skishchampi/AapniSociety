import json

import pytest

pytestmark = pytest.mark.django_db

WORKER_PHONE = "+919****0501"
HOUSEHOLD_PHONE = "+919****0502"
MOD_PHONE = "+919****0500"


def _auth(api, access):
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")


def _make_moderator(api, signin):
    from django.contrib.auth import get_user_model

    access, _ = signin(api, MOD_PHONE, role="household", full_name="Mod")
    get_user_model().objects.filter(phone=MOD_PHONE).update(primary_role="moderator")
    return access


def _make_worker(api, signin):
    from django.contrib.auth import get_user_model

    from apps.members.models import WorkerProfile

    access, _ = signin(api, WORKER_PHONE, role="worker", full_name="Kiran")
    user = get_user_model().objects.get(phone=WORKER_PHONE)
    worker, _ = WorkerProfile.objects.get_or_create(user=user)
    return access, worker


def _make_household(api, signin):
    from django.contrib.auth import get_user_model

    from apps.members.models import HouseholdProfile

    access, _ = signin(api, HOUSEHOLD_PHONE, role="household", full_name="Shah Family")
    user = get_user_model().objects.get(phone=HOUSEHOLD_PHONE)
    household, _ = HouseholdProfile.objects.get_or_create(user=user)
    return access, household


def test_worker_block_stops_introductions_and_routing(api, signin):
    mod_access = _make_moderator(api, signin)
    w_access, worker = _make_worker(api, signin)
    h_access, household = _make_household(api, signin)

    # Household files an open introduction before the block
    _auth(api, h_access)
    intro_id = api.post(
        "/api/v1/introductions/", {"worker": worker.id, "note": "Need help"}, format="json"
    ).json()["id"]

    # Worker blocks the household
    _auth(api, w_access)
    r = api.post(
        "/api/v1/blocks/",
        {"household": household.id, "reason": "Hostile behaviour"},
        format="json",
    )
    assert r.status_code == 201, r.content
    block_id = r.json()["id"]

    # Duplicate block -> 409
    dup = api.post("/api/v1/blocks/", {"household": household.id}, format="json")
    assert dup.status_code == 409

    # Household cannot see blocks -> 403
    _auth(api, h_access)
    assert api.get("/api/v1/blocks/").status_code == 403

    # Blocked household cannot file a new introduction -> 403
    assert (
        api.post("/api/v1/introductions/", {"worker": worker.id}, format="json").status_code == 403
    )

    # Moderator cannot route an existing open introduction for a blocked pair -> 409
    _auth(api, mod_access)
    assert api.post(f"/api/v1/moderation/introductions/{intro_id}/route/").status_code == 409

    # Worker unblocks -> household can file again
    _auth(api, w_access)
    assert api.delete(f"/api/v1/blocks/{block_id}/").status_code == 204
    _auth(api, h_access)
    assert (
        api.post("/api/v1/introductions/", {"worker": worker.id}, format="json").status_code == 201
    )


def test_abuse_report_confidential_and_moderated(api, signin):
    mod_access = _make_moderator(api, signin)
    w_access, _ = _make_worker(api, signin)
    h_access, household = _make_household(api, signin)

    # Worker reports caste abuse and non-payment
    _auth(api, w_access)
    r = api.post(
        "/api/v1/reports/",
        {
            "reported_household": household.id,
            "category": "caste_abuse",
            "details": "Refused water and withheld wages.",
        },
        format="json",
    )
    assert r.status_code == 201, r.content
    report_id = r.json()["id"]
    assert r.json()["status"] == "open"

    # Reported household never sees reports filed against them
    _auth(api, h_access)
    hh_reports = api.get("/api/v1/reports/").json()
    assert hh_reports == []

    # Worker cannot resolve their own report -> 403
    _auth(api, w_access)
    assert (
        api.post(
            f"/api/v1/moderation/reports/{report_id}/resolve/",
            {"status": "resolved"},
            format="json",
        ).status_code
        == 403
    )

    # Moderator resolves report and action is logged in AdminAuditLog
    _auth(api, mod_access)
    res = api.post(
        f"/api/v1/moderation/reports/{report_id}/resolve/",
        {"status": "resolved", "resolution_note": "Household suspended from routing."},
        format="json",
    )
    assert res.status_code == 200, res.content
    assert res.json()["status"] == "resolved"
    assert res.json()["resolution_note"] == "Household suspended from routing."


def test_safety_notes_hidden_from_households_and_strip_author_identity(api, signin):
    from apps.geo.models import City, Locality

    city = City.objects.create(name="Ahmedabad", slug="ahmedabad")
    loc = Locality.objects.create(city=city, name="Prahladnagar", slug="prahladnagar")

    mod_access = _make_moderator(api, signin)
    w_access, _ = _make_worker(api, signin)
    h_access, _ = _make_household(api, signin)

    # Worker adds a firsthand city safety note
    _auth(api, w_access)
    r = api.post(
        "/api/v1/safety-notes/",
        {
            "locality": loc.id,
            "note_type": "night_route_risk",
            "evidence_level": "firsthand",
            "body": "Streetlights out near the bus stop after 9pm.",
        },
        format="json",
    )
    assert r.status_code == 201, r.content

    # Worker and moderator can read notes, with zero author identity leakage
    for access in (w_access, mod_access):
        _auth(api, access)
        notes = api.get("/api/v1/safety-notes/").json()
        assert len(notes) == 1
        assert notes[0]["evidence_level"] == "firsthand"
        dump = json.dumps(notes)
        assert WORKER_PHONE not in dump
        assert "Kiran" not in dump
        assert '"author"' not in dump

    # Households cannot read or create safety notes -> 403
    _auth(api, h_access)
    assert api.get("/api/v1/safety-notes/").status_code == 403
    assert (
        api.post(
            "/api/v1/safety-notes/",
            {
                "note_type": "transit_reliability",
                "evidence_level": "secondhand",
                "body": "Bus 42 delayed.",
            },
            format="json",
        ).status_code
        == 403
    )


def test_admin_audit_log_records_moderator_actions(api, signin):
    mod_access = _make_moderator(api, signin)
    w_access, worker = _make_worker(api, signin)
    h_access, household = _make_household(api, signin)

    # File an introduction and route it
    _auth(api, h_access)
    intro_id = api.post(
        "/api/v1/introductions/", {"worker": worker.id, "note": "Daily cook"}, format="json"
    ).json()["id"]

    _auth(api, mod_access)
    assert api.post(f"/api/v1/moderation/introductions/{intro_id}/route/").status_code == 200

    # File a report and resolve it
    _auth(api, w_access)
    report_id = api.post(
        "/api/v1/reports/",
        {
            "reported_household": household.id,
            "category": "non_payment",
            "details": "Two months unpaid.",
        },
        format="json",
    ).json()["id"]

    _auth(api, mod_access)
    assert (
        api.post(
            f"/api/v1/moderation/reports/{report_id}/resolve/",
            {"status": "resolved", "resolution_note": "Follow-up logged."},
            format="json",
        ).status_code
        == 200
    )

    # Non-moderators get 403 on audit log
    _auth(api, w_access)
    assert api.get("/api/v1/moderation/audit-log/").status_code == 403
    _auth(api, h_access)
    assert api.get("/api/v1/moderation/audit-log/").status_code == 403

    # Moderator sees both actions recorded in the audit log
    _auth(api, mod_access)
    logs = api.get("/api/v1/moderation/audit-log/").json()
    actions = {(entry["action"], entry["target_type"], entry["target_id"]) for entry in logs}
    assert ("introduction_routed", "IntroductionRequest", intro_id) in actions
    assert ("report_resolved", "AbuseReport", report_id) in actions
