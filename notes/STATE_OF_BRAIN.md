# State of Brain

Date: 2026-06-24

## Active Frame

AapniSociety is worker-led, worker-owned cooperative technology infrastructure for the Indian
urban need economy — not a society/RWA app or services marketplace. The worker is the first-class
subject of the data model. Households participate but do not control worker visibility, rates, or
discipline. This session's anti-caste schema audit confirmed the schema holds that line: zero
caste/religion/marital/relationship fields, and `WorkerProfile` is not subordinate to
`HouseholdProfile`.

## This Session's Engineering Posture

- The scaffold (Phases 0–2) was already functional; the real work was Phase 3–4 completion plus
  security hardening surfaced by audit. The product is now "off the ground": both halves run,
  tests pass, the local stack and CI exist.
- Security treated as foundational, not deferred: OTP brute-force backstop, a JWT key floor that
  fails prod boot on a weak key, and a refresh-rotation fix. These are alpha-appropriate. Full
  SMS gateway, httponly-cookie hardening, and idempotency keys remain explicitly later-milestone.

## Unresolved Tensions

- Whether the tech team becomes a worker-owned tech co-op or stays CommonerLLP as steward.
- Which legal form best protects worker control in India.
- How much governance surface ships in `0.1.0` vs `0.2.0`.
- Preventing NGO/RWA/state/founder capture while still securing pilot funding/support.
- (New, operational) The ultracode workflow's implement/verify phases are vulnerable to API
  session limits. For large self-contained builds, prefer main-loop execution or resumable
  workflows. Avoid a single long fan-out.

## Next Thinking Task

Aakash commits alpha.1 and calls the gate. Then design the next gate per the roadmap:
`0.1.0-alpha.2` Membership and Profiles. Keep trust transfer consent-gated and mediated.
Do not use public rating-driven mechanics.
