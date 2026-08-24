# Changelog

## 2026-06-24 · alpha1-implement · create/edit

- `backend/apps/accounts/otp.py` — per-phone issuance cap + atomic invalidate/create; DEBUG-gated code log.
- `backend/apps/accounts/views.py` — OTPRequest returns 429 on cap; OTPVerify own throttle scope.
- `backend/config/settings/base.py` — ≥32-byte dev SECRET_KEY; explicit JWT SIGNING_KEY; otp_verify rate; OTP issuance settings.
- `backend/config/settings/prod.py` — ImproperlyConfigured guard on weak/short/default SECRET_KEY.
- `backend/.env.example` — SECRET_KEY bumped to ≥32 bytes.
- `frontend/src/api/client.ts` — persist rotated refresh token on refresh.
- `frontend/vite.config.ts` — env-driven proxy target (BACKEND_ORIGIN) + host:true.
- `infra/docker-compose.yml`, `infra/backend.Dockerfile`, `infra/frontend.Dockerfile`, `infra/.env.example` — new local stack.
- `.github/workflows/ci.yml` — new (ruff+pytest/Postgres, eslint+vitest+build, gitleaks).
- `docs/releases/0.1.0-alpha.1.md` — new release notes.
- `docs/STATUS.md` — cockpit refreshed to alpha.1 criteria-met.
- `notes/HANDOFF.md`, `notes/STATE_OF_BRAIN.md` — rewritten (prior versions archived in local
  private archive folders).
- `WORKING.md`, `TODO.md` — session close + priorities updated.

## 2026-06-17 · closeout · create/edit

- `README.md` — updated project entrypoint and canonical docs.
- `docs/aapnisociety-scope.md` — added concept, market, and technology-coop links.
- `docs/aapnisociety-srs.md` — added expanded SRS draft.
- `docs/aapnisociety-srs-formal.md` — added formal SRS and cooperative operator framing.
- `docs/aapnisociety-roadmap.md` — added maintained roadmap through `1.0.0`.
- `docs/aapnisociety-legacy-audit.md` — added legacy Android/Django audit.
- `docs/releases/0.0.1.md` — added recovery baseline release notes.
- `docs/research/technology-coops.md` — added global technology/platform co-op research synthesis.
- `.claude/pm-profile.md` — added repo PM profile.
- `docs/STATUS.md` — added PM cockpit.
- `WORKING.md` — closed active session row.
- `notes/HANDOFF.md` — added closeout handoff.
- `notes/STATE_OF_BRAIN.md` — added conceptual closeout state.
- `TODO.md` — added current/future/archive queue.
- `memory/MEMORY.md` — added memory index.
- `memory/changelog.md` — added file-level session changelog.
- `memory/session-log.md` — added session summary.
