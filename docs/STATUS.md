# AapniSociety Status

Last recomputed: 2026-06-24T22:30:00-04:00
Branch: `reboot-13years-later`

## Current Gate

`0.1.0-alpha.1 - Foundations`: **criteria met against artifacts, awaiting Aakash's verdict.**

The modern scaffold exists and is verified locally: backend `pytest` 10/10, frontend
lint+vitest+build green, `docker compose config` validates, CI defined. The recovery
baseline `0.0.1` is complete.

> "Done" is a human verdict, not the cockpit's. Criteria are met; Aakash calls the gate.

## Progress Units

| Unit | Count | Evidence |
|---|---:|---|
| Markdown docs under `docs/` | 10 | `find docs -maxdepth 2 -type f -name '*.md'` |
| Release notes | 2 | `docs/releases/0.0.1.md`, `docs/releases/0.1.0-alpha.1.md` |
| Research notes | 1 | `docs/research/technology-coops.md` |
| Backend apps scaffolded + verified | 3 | `accounts`, `geo`, `members` — models/serializers/views/admin/migrations |
| Backend tests passing | 10 | `cd backend && uv run pytest` |
| Frontend routes | 3 | SignIn, Onboarding, Dashboard (lint+vitest+build green) |
| Infra / CI artifacts | 5 | `infra/{docker-compose.yml,backend.Dockerfile,frontend.Dockerfile,.env.example}`, `.github/workflows/ci.yml` |

Stage: software **scaffolded → verified** (profile stages 7–8 reached this session).

## Roadmap vs Actual

| Gate | Status | Evidence |
|---|---|---|
| `0.0.1` recovery baseline | Met | release notes, README, legacy audit, SRS, roadmap, research |
| `0.1.0-alpha.1` foundations | Criteria met (awaiting verdict) | OTP→JWT sign-in, worker/household onboarding, `/me/`, Django admin, `make test`, infra stack, CI |

Acceptance (roadmap §5): all three criteria met — see `docs/releases/0.1.0-alpha.1.md`.

## Hardening applied this session (from audit)

- OTP brute-force backstop: per-phone issuance cap + separate issue/verify throttle scopes.
- JWT key floor: HS256 key ≥ 32 bytes; `prod` refuses to boot on dev/short key.
- Refresh-rotation fix: SPA persists the rotated refresh token (no silent logout).
- Role privilege guard + regression test confirmed present (self-assign limited to worker/household).
- Privacy: zero caste/religion/marital/relationship fields in the schema (confirmed).

## Freshness

No freshness gate blocks `0.1.0-alpha.1`. Refresh before external claims: app-store/competitor
data, government funding schemes, Bharat Taxi governance claims, city/legal research.

## Live Ops

None expected. (Local stack runs on demand via `make up`.)

## Blocked

No technical blocker. Product decisions to resolve before `0.1.0-beta.1` remain in the roadmap:
worker verification authority, household/tenant verification authority, pilot cooperative legal
form, safety-note evidence level, data-export boundaries, household dispute process.

## Commit Gap

- branch: `reboot-13years-later` (10 commits ahead of `origin/master`, plus this session uncommitted)
- modified (tracked): 8 — `.gitignore`, `backend/.env.example`, `accounts/otp.py`, `accounts/views.py`, `settings/base.py`, `settings/prod.py`, `frontend/src/api/client.ts`, `frontend/vite.config.ts`
- untracked: 6 — `infra/*` (4), `.github/workflows/ci.yml`, `docs/releases/0.1.0-alpha.1.md`
- pre-commit hook: installed. Recommend **staged commits** (security fixes / infra / CI / release doc as separate commits); not yet committed (no permission this turn).

## On Track

Yes. The gate's deciding question — convert `0.1.0-alpha.1` from plan to a verified modern
PWA + Django scaffold — is answered: it builds, tests pass, and the stack/CI exist. The one
remaining step is Aakash's review + commit of this session's working tree, then his verdict
on the gate.
