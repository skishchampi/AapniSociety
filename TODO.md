# Current

- Aakash: review, then push `reboot-13years-later` and merge PR #2. The branch now carries the
  0.0.x cleanup, the June coordination sync, and the alpha.2 membership + needs slice.
- Finish `0.1.0-alpha.2`: frontend onboarding forms (worker profile, household profile,
  membership request, service need) and a moderator queue view or an admin-only stopgap.
- Keep worker-led cooperative governance as the product center.

# Future

- `0.1.0-alpha.3 - Introductions` per the roadmap: introduction requests, review queue,
  worker accept/reject, contact-reveal consent, auditable history.
- Deferred (non-blocking) audit medium findings: Idempotency-Key on POST writes (SRS §7.4);
  cumulative per-phone failed-verify lockout beyond the issuance cap.
- Refresh app-store competitor data before external pitch/deck use.
- Refresh government funding scheme data before applications.
- Research Indian technology cooperatives and legal forms.
- Resolve worker verification and household verification authority.

# Archive

## 2026-08-24

- Closed every stale status marker on the 0.0.x recovery baseline; one canonical SRS now owns
  requirements.
- Recomputed the PM cockpit into local-only notes/STATUS.md; docs/STATUS.md stays a durable
  public snapshot.
- Recorded alpha.1 as Met after Aakash's go for alpha.2.
- Started alpha.2 per roadmap numbering: MembershipRequest approval workflow, ServiceNeed CRUD,
  privacy-exposure tests. Backend pytest 22/22, ruff clean.

## 2026-06-24

- Implemented + hardened `0.1.0-alpha.1`: 3 HIGH security fixes (OTP brute-force, JWT key floor,
  refresh rotation), created `infra/` stack + CI + release notes. All suites green. Compose validates.
- Refreshed `docs/STATUS.md` cockpit to alpha.1 criteria-met.

## 2026-06-17

- Recovered legacy Android/Django project intent.
- Created scope, formal SRS, roadmap, legacy audit, release notes, technology co-op research, PM status.
- Committed `0.0.1` recovery baseline and PM cockpit.
- Wrote `0.1.0-alpha.1` implementation plan; chose monorepo layout; scaffolded backend + frontend.
