# Current

- Aakash: review, then push and merge the PR recording alpha.3 Met plus the
  alpha.4 plan.
- After merge: start alpha.4 build per docs/plans/0.1.0-alpha.4-references-bargaining.md.
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

- Closed every stale status marker on the 0.0.x recovery baseline. One canonical SRS now owns
  requirements.
- Recorded alpha.1 Met.
- Built and merged 0.1.0-alpha.2 across PRs #2–#4. Aakash called it Met. Release notes written.
- Built and merged 0.1.0-alpha.3 across PRs #6–#7: introductions backend, events, contact
  reveal, frontend pages. Proven live in the browser. Aakash called it Met.
- /pm recomputed twice. Cockpit lives at local-only notes/STATUS.md.

## 2026-06-24

- Implemented + hardened `0.1.0-alpha.1`: 3 HIGH security fixes (OTP brute-force, JWT key floor,
  refresh rotation), created `infra/` stack + CI + release notes. All suites green. Compose validates.
- Refreshed `docs/STATUS.md` cockpit to alpha.1 criteria-met.

## 2026-06-17

- Recovered legacy Android/Django project intent.
- Created scope, formal SRS, roadmap, legacy audit, release notes, technology co-op research, PM status.
- Committed `0.0.1` recovery baseline and PM cockpit.
- Wrote `0.1.0-alpha.1` implementation plan; chose monorepo layout; scaffolded backend + frontend.
