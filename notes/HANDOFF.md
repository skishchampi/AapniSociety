# Handoff

Date: 2026-06-24

## What Changed

- Ran an ultracode workflow (audit → implement → verify) on the `0.1.0-alpha.1` scaffold.
  The audit returned (0 blockers, 3 HIGH, ~8 missing artifacts). The implement + verify phases
  died on an API session limit. The implementation was completed directly in the main loop.
- Fixed the 3 HIGH audit findings (all verified green):
  - **OTP brute-force** (`accounts/otp.py`, `views.py`, `settings/base.py`): per-phone issuance
    cap over a window + atomic invalidate/create; separate `otp` vs `otp_verify` throttle scopes;
    plaintext-code logging gated on `DEBUG`. Request view now returns 429 on cap.
  - **JWT key floor** (`settings/base.py`, `prod.py`, `backend/.env.example`): dev `SECRET_KEY`
    now ≥ 32 bytes (kills `InsecureKeyLengthWarning`); explicit `SIMPLE_JWT["SIGNING_KEY"]`;
    `prod` raises `ImproperlyConfigured` on the dev placeholder or a < 32-byte key.
  - **Refresh rotation** (`frontend/src/api/client.ts`): `tryRefresh()` now persists the rotated
    refresh token (was dropping it → silent logout ~15 min in).
- Created the missing Phase-3/4 artifacts:
  - `infra/docker-compose.yml` (PostGIS + redis + backend + frontend), `infra/backend.Dockerfile`,
    `infra/frontend.Dockerfile`, `infra/.env.example`. Made the Vite proxy target env-driven
    (`BACKEND_ORIGIN`) so the SPA reaches `backend:8000` inside compose (default unchanged locally).
  - `.github/workflows/ci.yml` (ruff+pytest on Postgres, eslint+vitest+build, gitleaks).
  - `docs/releases/0.1.0-alpha.1.md`.
- Confirmed the role-privilege guard + its regression test already existed (audit's "missing test"
  finding was wrong).
- Verified: backend `ruff` clean + `pytest` 10/10; frontend lint+vitest+build green;
  `docker compose -f infra/docker-compose.yml config` validates. `ci.yml` is valid YAML.
- Refreshed `docs/STATUS.md` (cockpit) to reflect alpha.1 criteria-met.

## Current State

- `0.1.0-alpha.1` acceptance criteria are **met against artifacts; awaiting Aakash's verdict.**
- Working tree is **uncommitted** (8 modified, 6 untracked). Nothing committed this session
  (no permission given).
- Branch `reboot-13years-later` is 10 commits ahead of `origin/master` (pre-session) + this work.

## Next Queue

1. **Aakash review + commit** this session's working tree. Recommended staged commits:
   (a) backend security fixes, (b) frontend refresh fix, (c) `infra/`, (d) CI, (e) release doc.
   Org rule: branch + PR. Do not push to master.
2. Optionally run the verify phase of the ultracode workflow once the API limit resets
   (~4:30am America/Toronto) as an independent adversarial check — though local verification
   already passed.
3. After commit + Aakash's verdict: flip roadmap §5 `0.1.0-alpha.1` status to *Met*.
4. Then begin `0.1.0-alpha.2` (introductions / service needs+offers) per roadmap.
5. Medium audit findings deferred (not blocking): Idempotency-Key support on POST writes
   (SRS §7.4). Cumulative per-phone failed-verify lockout beyond the issuance cap.
