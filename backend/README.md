# AapniSociety backend

Django 5 + DRF modular monolith. Apps: `accounts` (phone-OTP auth, custom User,
AuditEvent), `geo` (City/Locality/Building/Unit), `members` (Worker/Household profiles,
ServiceCategory). Built for `0.1.0-alpha.1` — see
[`docs/plans/0.1.0-alpha.1-foundations.md`](../docs/plans/0.1.0-alpha.1-foundations.md).

## Run locally

```bash
cd backend
cp .env.example .env          # defaults to SQLite — zero external deps
uv sync
uv run python manage.py migrate
uv run python manage.py seed_dev        # demo worker/household + Ahmedabad pilot data + superuser
uv run python manage.py runserver
```

- Admin: http://127.0.0.1:8000/admin/  (dev superuser: `+919900000000` / `admin12345`)
- API docs (Swagger): http://127.0.0.1:8000/api/v1/docs/

## Dev OTP flow (no SMS gateway)

```
POST /api/v1/auth/otp/request/  {"phone": "+9199..."}        -> {"dev_code": "123456"}   # dev only
POST /api/v1/auth/otp/verify/   {"phone": "+9199...", "code": "123456", "primary_role": "worker"}
                                                              -> {access, refresh, user}
GET  /api/v1/me/                 (Bearer access)              -> current user + profile flags
PUT  /api/v1/me/worker-profile/      | /me/household-profile/
```

`dev_code` is returned only when `OTP_RETURN_CODE_IN_RESPONSE` is true (dev/test settings).
Production settings never return it.

## Tests / lint

```bash
uv run pytest          # or: make test   (from repo root)
uv run ruff check .    # or: make lint
```

Settings: `config.settings.{base,dev,prod,test}`. The DB is `DATABASE_URL`-driven —
SQLite by default; docker-compose (Phase 3) points it at `postgis/postgis` for parity.
