# Current

- Aakash: review, then push and merge the PR that records alpha.2 Met (release
  notes, roadmap flip) plus the alpha.3 plan.
- After that merge: start alpha.3 build per docs/plans/0.1.0-alpha.3-introductions.md —
  models and APIs first, then pages.
- Keep worker-led cooperative governance as the product center.

# Future

- `0.1.0-alpha.4 - References and Bargaining` per the roadmap after alpha.3.
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
- Recorded alpha.1 Met; built and merged all of 0.1.0-alpha.2 across PRs #2, #3, #4
  (membership approval, service needs, profile editors, moderator review).
- Aakash called the alpha.2 gate Met. Release notes written; alpha.3 plan opened.

## 2026-06-24

- Implemented + hardened `0.1.0-alpha.1`: 3 HIGH security fixes (OTP brute-force, JWT key floor,
  refresh rotation), created `infra/` stack + CI + release notes. All suites green. Compose validates.
- Refreshed `docs/STATUS.md` cockpit to alpha.1 criteria-met.

## 2026-06-17

- Recovered legacy Android/Django project intent.
- Created scope, formal SRS, roadmap, legacy audit, release notes, technology co-op research, PM status.
- Committed `0.0.1` recovery baseline and PM cockpit.
- Wrote `0.1.0-alpha.1` implementation plan; chose monorepo layout; scaffolded backend + frontend.
