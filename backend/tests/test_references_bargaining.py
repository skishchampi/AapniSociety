import json
from decimal import Decimal

import pytest

pytestmark = pytest.mark.django_db

WORKER_PHONE = "+919****0401"
OTHER_WORKER_PHONE = "+919****0404"
HOUSEHOLD_PHONE = "+919****0402"
OTHER_HOUSEHOLD_PHONE = "+919****0403"
MOD_PHONE = "+919****0400"


def _auth(api, access):
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")


def _make_moderator(api, signin):
    from django.contrib.auth import get_user_model

    access, _ = signin(api, MOD_PHONE, role="household", full_name="Mod")
    get_user_model().objects.filter(phone=MOD_PHONE).update(primary_role="moderator")
    return access


def _make_worker(api, signin, phone=WORKER_PHONE, floor="5000.00"):
    from django.contrib.auth import get_user_model

    from apps.members.models import WorkerProfile

    access, _ = signin(api, phone, role="worker", full_name="Meera")
    user = get_user_model().objects.get(phone=phone)
    worker, _ = WorkerProfile.objects.get_or_create(user=user)
    if floor is not None:
        worker.default_rate_floor = Decimal(floor)
        worker.save(update_fields=["default_rate_floor"])
    return access, worker


def _make_household(api, signin, phone=HOUSEHOLD_PHONE):
    from django.contrib.auth import get_user_model

    from apps.members.models import HouseholdProfile

    access, _ = signin(api, phone, role="household", full_name="Patel Family")
    user = get_user_model().objects.get(phone=phone)
    household, _ = HouseholdProfile.objects.get_or_create(user=user)
    return access, household


def _make_accepted_intro(api, signin, offered_rate=None):
    mod_access = _make_moderator(api, signin)
    w_access, worker = _make_worker(api, signin)
    h_access, household = _make_household(api, signin)

    _auth(api, h_access)
    payload = {"worker": worker.id, "note": "Morning cooking"}
    if offered_rate is not None:
        payload["offered_rate"] = offered_rate
    r = api.post("/api/v1/introductions/", payload, format="json")
    assert r.status_code == 201, r.content
    intro_id = r.json()["id"]

    _auth(api, mod_access)
    assert api.post(f"/api/v1/moderation/introductions/{intro_id}/route/").status_code == 200

    _auth(api, w_access)
    assert api.post(f"/api/v1/introductions/{intro_id}/accept/").status_code == 200

    return mod_access, w_access, worker, h_access, household, intro_id


def test_reference_requires_accepted_introduction(api, signin):
    mod_access = _make_moderator(api, signin)
    _, worker = _make_worker(api, signin)
    h_access, _ = _make_household(api, signin)

    _auth(api, h_access)
    intro_id = api.post(
        "/api/v1/introductions/", {"worker": worker.id, "note": "Need cook"}, format="json"
    ).json()["id"]

    # Requested (not routed or accepted) -> 409
    r = api.post(
        "/api/v1/references/",
        {"introduction": intro_id, "body": "Punctual and skilled."},
        format="json",
    )
    assert r.status_code == 409

    # Routed (still not accepted) -> 409
    _auth(api, mod_access)
    api.post(f"/api/v1/moderation/introductions/{intro_id}/route/")

    _auth(api, h_access)
    r = api.post(
        "/api/v1/references/",
        {"introduction": intro_id, "body": "Punctual and skilled."},
        format="json",
    )
    assert r.status_code == 409


def test_reference_request_and_write_flow(api, signin):
    _, w_access, worker, h_access, household, intro_id = _make_accepted_intro(api, signin)

    # Worker requests a reference from the household
    _auth(api, w_access)
    req_resp = api.post(
        "/api/v1/reference-requests/",
        {"household": household.id, "introduction": intro_id},
        format="json",
    )
    assert req_resp.status_code == 201, req_resp.content
    req_id = req_resp.json()["id"]
    assert req_resp.json()["status"] == "pending"

    # Household writes the reference
    _auth(api, h_access)
    ref_resp = api.post(
        "/api/v1/references/",
        {"introduction": intro_id, "body": "Reliable cook for six months.", "rating": 5},
        format="json",
    )
    assert ref_resp.status_code == 201, ref_resp.content
    assert ref_resp.json()["visibility"] == "private"

    # Duplicate reference on same introduction -> 409
    dup_resp = api.post(
        "/api/v1/references/",
        {"introduction": intro_id, "body": "Second try."},
        format="json",
    )
    assert dup_resp.status_code == 409

    # Pending request flipped to written
    _auth(api, w_access)
    reqs = api.get("/api/v1/reference-requests/").json()
    row = next(r for r in reqs if r["id"] == req_id)
    assert row["status"] == "written"

    # Worker sees their own reference
    my_refs = api.get("/api/v1/me/references/").json()
    assert len(my_refs) == 1
    assert my_refs[0]["body"] == "Reliable cook for six months."
    assert my_refs[0]["visibility"] == "private"


def test_visibility_controls_and_post_routing_sharing(api, signin):
    mod_access, w_access, worker, h_access, _, intro_id = _make_accepted_intro(api, signin)

    _auth(api, h_access)
    ref_id = api.post(
        "/api/v1/references/",
        {"introduction": intro_id, "body": "Always on time.", "rating": 4},
        format="json",
    ).json()["id"]

    # Another household files a second introduction for the same worker
    h2_access, _ = _make_household(api, signin, phone=OTHER_HOUSEHOLD_PHONE)
    _auth(api, h2_access)
    intro2_id = api.post(
        "/api/v1/introductions/", {"worker": worker.id, "note": "Evening help"}, format="json"
    ).json()["id"]

    # Private reference is invisible before and after routing
    _auth(api, mod_access)
    api.post(f"/api/v1/moderation/introductions/{intro2_id}/route/")

    _auth(api, h2_access)
    listing = api.get("/api/v1/introductions/mine/").json()
    row = next(r for r in listing if r["id"] == intro2_id)
    assert row["shared_references"] == []
    assert "Always on time." not in json.dumps(listing)

    # Household cannot toggle visibility -> 403
    assert (
        api.patch(
            f"/api/v1/references/{ref_id}/visibility/", {"visibility": "shared"}, format="json"
        ).status_code
        == 403
    )

    # Another worker cannot toggle visibility -> 403
    w2_access, _ = _make_worker(api, signin, phone=OTHER_WORKER_PHONE)
    _auth(api, w2_access)
    assert (
        api.patch(
            f"/api/v1/references/{ref_id}/visibility/", {"visibility": "shared"}, format="json"
        ).status_code
        == 403
    )

    # Owning worker flips visibility to shared
    _auth(api, w_access)
    patch_resp = api.patch(
        f"/api/v1/references/{ref_id}/visibility/", {"visibility": "shared"}, format="json"
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["visibility"] == "shared"

    # Routed introduction now carries the shared reference text (no rating!)
    _auth(api, h2_access)
    listing = api.get("/api/v1/introductions/mine/").json()
    row = next(r for r in listing if r["id"] == intro2_id)
    assert len(row["shared_references"]) == 1
    assert row["shared_references"][0]["body"] == "Always on time."
    assert "rating" not in row["shared_references"][0]

    # Unrouted introduction still hides shared references
    intro3_id = api.post(
        "/api/v1/introductions/", {"worker": worker.id, "note": "Unrouted"}, format="json"
    ).json()["id"]
    listing = api.get("/api/v1/introductions/mine/").json()
    row3 = next(r for r in listing if r["id"] == intro3_id)
    assert row3["shared_references"] == []


def test_household_endpoints_never_expose_ratings_or_below_floor(api, signin):
    from apps.members.models import ServiceCategory

    cat = ServiceCategory.objects.create(key="cook", label="Cook")
    mod_access, w_access, worker, h_access, _, intro_id = _make_accepted_intro(
        api, signin, offered_rate="3500.00"
    )

    _auth(api, h_access)
    ref_id = api.post(
        "/api/v1/references/",
        {"introduction": intro_id, "body": "Great meals.", "rating": 5},
        format="json",
    ).json()["id"]

    _auth(api, w_access)
    api.patch(f"/api/v1/references/{ref_id}/visibility/", {"visibility": "shared"}, format="json")

    _auth(api, h_access)
    need_resp = api.post(
        "/api/v1/needs/",
        {"category": cat.id, "title": "Lunch cook", "offered_rate": "3000.00"},
        format="json",
    )
    assert need_resp.status_code == 201, need_resp.content

    for url in [
        "/api/v1/introductions/mine/",
        "/api/v1/needs/",
        "/api/v1/reference-requests/",
    ]:
        data = api.get(url).json()
        dump = json.dumps(data)
        assert '"rating"' not in dump, f"rating leaked in {url}"
        assert '"avg_rating"' not in dump, f"avg_rating leaked in {url}"
        assert '"below_floor"' not in dump, f"below_floor leaked in {url}"
        assert WORKER_PHONE not in dump, f"phone leaked in {url}"


def test_below_floor_flag_visible_to_worker_and_moderator_only(api, signin):
    from apps.members.models import ServiceCategory, ServiceNeed

    cat = ServiceCategory.objects.create(key="maid", label="Maid")
    mod_access, w_access, worker, h_access, household, intro_id = _make_accepted_intro(
        api, signin, offered_rate="3500.00"
    )

    # Worker sees below_floor=True (3500 < 5000)
    _auth(api, w_access)
    w_rows = api.get("/api/v1/introductions/mine/").json()
    w_row = next(r for r in w_rows if r["id"] == intro_id)
    assert w_row["below_floor"] is True

    # Moderator sees below_floor=True
    _auth(api, mod_access)
    m_rows = api.get("/api/v1/introductions/mine/").json()
    m_row = next(r for r in m_rows if r["id"] == intro_id)
    assert m_row["below_floor"] is True

    # Household never sees below_floor
    _auth(api, h_access)
    h_rows = api.get("/api/v1/introductions/mine/").json()
    h_row = next(r for r in h_rows if r["id"] == intro_id)
    assert "below_floor" not in h_row

    # ServiceNeed.below_floor computes against matched_worker.default_rate_floor
    need = ServiceNeed.objects.create(
        household=household,
        category=cat,
        title="Morning cleaning",
        offered_rate=Decimal("4000.00"),
        matched_worker=worker,
    )
    assert need.below_floor is True

    _auth(api, mod_access)
    mod_needs = api.get("/api/v1/needs/").json()
    mod_need = next(n for n in mod_needs if n["id"] == need.id)
    assert mod_need["below_floor"] is True

    _auth(api, h_access)
    hh_needs = api.get("/api/v1/needs/").json()
    hh_need = next(n for n in hh_needs if n["id"] == need.id)
    assert "below_floor" not in hh_need


def test_bargaining_summary_moderator_only(api, signin):
    from apps.geo.models import City, Locality
    from apps.members.models import ServiceCategory, ServiceNeed

    city = City.objects.create(name="Ahmedabad", slug="ahmedabad")
    loc = Locality.objects.create(city=city, name="Prahladnagar", slug="prahladnagar")
    cat = ServiceCategory.objects.create(key="driver", label="Driver")

    mod_access = _make_moderator(api, signin)
    w_access, worker = _make_worker(api, signin, floor="15000.00")
    worker.service_categories.add(cat)
    worker.localities_served.add(loc)
    h_access, household = _make_household(api, signin)

    ServiceNeed.objects.create(
        household=household,
        category=cat,
        locality=loc,
        title="Office commute driver",
        offered_rate=Decimal("12000.00"),
        matched_worker=worker,
    )

    # Household and worker are blocked
    _auth(api, h_access)
    assert api.get("/api/v1/moderation/bargaining-summary/").status_code == 403
    _auth(api, w_access)
    assert api.get("/api/v1/moderation/bargaining-summary/").status_code == 403

    # Moderator gets aggregates with zero personal/rating leakage
    _auth(api, mod_access)
    r = api.get("/api/v1/moderation/bargaining-summary/")
    assert r.status_code == 200, r.content
    body = r.json()
    cat_row = next(c for c in body["by_category"] if c["category_id"] == cat.id)
    assert cat_row["worker_count"] == 1
    assert cat_row["need_count"] == 1
    assert cat_row["below_floor_count"] == 1
    assert cat_row["min_rate_floor"] == "15000.00"

    loc_row = next(row for row in body["by_locality"] if row["locality_id"] == loc.id)
    assert loc_row["worker_count"] == 1
    assert loc_row["need_count"] == 1

    dump = json.dumps(body)
    assert WORKER_PHONE not in dump
    assert "Meera" not in dump
    assert "rating" not in dump
