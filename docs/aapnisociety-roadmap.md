# AapniSociety Roadmap

Date: 2026-06-17
Status: Maintained
Maintainer: AapniSociety project

Reference documents:
- [Scope and Concept Note](./aapnisociety-scope.md)
- [Software Requirements Specification](./aapnisociety-srs-formal.md)

## 1. Roadmap Purpose

This file is the maintained roadmap for rebuilding AapniSociety as worker-led, worker-owned cooperative infrastructure.

The roadmap translates the scope and SRS into release gates. It should answer:
- what version we are building
- what that version proves
- what is in scope
- what is explicitly out of scope
- what must be true before the version is accepted
- what decisions are still open

## 2. Product Direction

AapniSociety is not a society-management clone, a booking marketplace, or a platform that extracts rent from workers.

The product direction is:
- worker-led
- worker-owned or cooperative-governed
- privacy-first
- tenant-supportive
- anti-caste and anti-surveillance by default
- built around trusted introductions, portable references, rate floors, and worker-authored city knowledge

Households are users, but workers and the cooperative are the center of gravity.

## 3. Version Strategy

### 0.0.x - Repository Recovery and Concept Stabilization

Goal: understand the 2012 codebase, recover the project intent, and document the modern product direction.

Status: complete.

Deliverables:
- legacy Android client reviewed
- legacy Django server reviewed
- current market and competitor notes gathered
- scope document created
- formal SRS created
- roadmap created

Exit criteria:
- one canonical SRS exists
- one canonical roadmap exists
- product direction is clear enough to start implementation
- worker-led cooperative direction is reflected in planning docs

### 0.0.1 - Recovery Baseline

Goal: create a committed documentation baseline that explains the legacy project, the rebuild decision, and the path to `0.1.0`.

Deliverables:
- README points to canonical docs
- legacy Android and Django audit exists
- scope document exists
- formal SRS exists
- maintained roadmap exists
- `0.1.0` target is defined as the Cooperative Trust Pilot

Exit criteria:
- the old codebase is treated as archival
- the modern stack direction is documented
- worker-led cooperative ownership is documented as the product center
- there is no ambiguity about which document owns scope, requirements, and release planning

### 0.1.0 - Cooperative Trust Pilot

Goal: prove that a worker-led cooperative can manage trusted household-work introductions, portable references, rate floors, and safety knowledge inside one Ahmedabad pilot cluster.

Primary pilot assumption:
- city: Ahmedabad
- locality pattern: Prahladnagar / apartment-cluster context
- first real-world test size: 20-50 workers and 50-100 households or tenants

The 0.1.0 release is successful only if workers can use the app to increase control over work terms, references, safety, and household access. It is not successful merely because households can find cheaper help.

## 4. 0.1.0 Scope

### Must Ship

#### Worker Member Onboarding

- phone OTP login
- worker profile
- service categories:
  - maid
  - cook
  - driver
  - plumber
  - electrician
  - caregiver
- languages
- localities served
- availability
- worker-defined rate floor
- contact and profile visibility settings
- consent record for every sensitive reveal

#### Household and Tenant Onboarding

- phone OTP login
- household profile
- building or locality membership
- service-need request
- privacy controls
- no public resident directory
- no public worker directory

#### Trusted Introduction Flow

- household creates a request for help
- cooperative moderator or trusted connector reviews the request
- worker receives the request without forced exposure
- worker can accept, reject, or ask for more context
- contact details are revealed only after consent
- introduction history is logged privately
- users can revoke or restrict future contact

#### Portable References

- worker can request a reference from a household
- household can submit a reference
- worker controls whether a reference is visible
- references are private by default
- no public star-rating marketplace
- no caste, religion, marital status, or relationship-status metadata is collected for ranking or filtering

#### Rate Floor and Bargaining Support

- worker can set minimum rates by service category
- cooperative can view aggregate rate-floor patterns
- requests below worker floor are flagged
- worker sees whether a request meets their stated minimum
- cooperative can use aggregate demand and rate data for bargaining, without exposing individual workers unnecessarily

#### Safety and Abuse Layer

- worker can block a household
- household can be reported for harassment, non-payment, caste abuse, communal abuse, coercion, stalking, or unsafe conduct
- worker can add city safety notes
- supported note types:
  - transit reliability
  - night-route risk
  - hostile institution
  - police-station or official-contact warning
  - non-payment pattern
  - unsafe building or household pattern
- safety notes must distinguish firsthand experience from secondhand reports
- raw notes are not exposed to employers, landlords, RWAs, or public search

#### Cooperative Admin

- approve worker members
- approve household or tenant membership
- review introduction requests
- review abuse reports
- manage service categories
- manage locality and building records
- view aggregate rate and demand summaries
- audit every admin action

### Should Ship

- installable PWA shell
- basic offline-read support for worker profile and accepted introductions
- export of cooperative member list
- export of aggregate demand/rate summaries
- internal seed data for Ahmedabad localities and service categories
- admin notes on unresolved disputes

### Explicitly Out of Scope for 0.1.0

- payments
- booking engine
- marketplace take-rate
- public worker search
- public resident search
- public ratings
- public social feed
- RWA tools
- visitor management
- ad system
- native Android app
- native iOS app
- algorithmic ranking
- automated dispatch
- landlord verification product
- employer-side surveillance dashboards

## 5. 0.1.0 Engineering Milestones

### 0.1.0-alpha.1 - Foundations

Goal: create the modern app skeleton and core identity model.

Status: Met. Recorded 2026-08-24 when Aakash ordered the alpha.2 start.

Deliverables:
- new frontend PWA scaffold
- new Django backend scaffold
- Docker Compose local environment
- PostgreSQL database
- user model
- role model
- worker profile model
- household profile model
- building/locality model
- development OTP flow
- basic admin login

Acceptance:
- worker and household users can sign in locally
- admin can view users and profiles
- test suite runs in CI/local command

### 0.1.0-alpha.2 - Cooperative Membership and Profiles

Goal: make worker and household records usable for a real pilot.

Status: In progress (started 2026-08-24).

Deliverables:
- worker onboarding flow
- household onboarding flow
- service category setup
- worker availability
- worker locality preferences
- worker rate floors
- privacy settings
- cooperative approval workflow

Acceptance:
- worker can create a complete profile
- household can create a service-need request
- moderator can approve or reject membership
- private fields are not exposed through normal APIs

### 0.1.0-alpha.3 - Introductions

Goal: implement consent-gated trusted introductions.

Deliverables:
- introduction request model
- request review queue
- worker accept/reject flow
- contact reveal consent
- introduction status history
- notification hooks

Acceptance:
- household can request an introduction
- cooperative moderator can route the request
- worker can accept or reject
- contact details are hidden until consent
- introduction history is auditable

### 0.1.0-alpha.4 - References and Bargaining

Goal: make worker reputation portable without creating a public ratings marketplace.

Deliverables:
- private worker reference model
- reference request flow
- reference visibility controls
- rate floor display
- below-floor request flag
- aggregate rate/demand admin view

Acceptance:
- worker can collect a reference
- worker can decide whether to show a reference
- household cannot browse public worker ratings
- below-floor requests are visible to worker and cooperative moderator

### 0.1.0-alpha.5 - Safety, Reports, and Moderation

Goal: give workers and tenants credible tools for abuse reporting and worker-authored city knowledge.

Deliverables:
- block household flow
- abuse report flow
- moderation queue
- safety note model
- evidence level
- note type taxonomy
- admin audit log

Acceptance:
- worker can block a household
- worker can report harassment, non-payment, caste abuse, communal abuse, or unsafe conduct
- safety notes can be entered without public exposure
- moderators can review and resolve reports
- admin actions are logged

### 0.1.0-beta.1 - Pilot Readiness

Goal: prepare for a controlled Ahmedabad pilot.

Deliverables:
- seeded Ahmedabad service categories
- seeded Ahmedabad pilot localities/buildings
- deployment checklist
- backup and restore checklist
- security review checklist
- pilot onboarding script
- lightweight usage analytics without sensitive identity leakage

Acceptance:
- app can be deployed to a staging environment
- pilot data can be seeded
- backup and restore have been tested
- privacy and moderation flows pass manual QA
- first pilot users can be onboarded without developer intervention

### 0.1.0 - First Cooperative Pilot

Goal: run the first real pilot with workers, tenant households, and cooperative moderators.

Acceptance:
- 20-50 workers can onboard
- 50-100 households or tenants can onboard
- at least 25 introduction requests can be processed end-to-end
- at least 10 portable references can be collected
- workers can reject or block households
- reports can be moderated
- aggregate rate-floor data can be reviewed by the cooperative
- no public worker rating or public household graph exists
- no household can access raw safety notes that expose workers

## 6. Technical Direction

### Frontend

- React
- TypeScript
- Vite
- TanStack Query
- PWA support
- minimal client state
- mobile-first layouts

### Backend

- Python 3.12+
- Django 5.x
- Django REST Framework
- PostgreSQL
- PostGIS-ready schema
- Redis
- Celery
- Docker

### Architecture Shape

- modular monolith
- REST-first API under `/api/v1/`
- separate admin and member permissions
- privacy-first data model
- audit logs for sensitive actions
- India-hosted primary data preferred when production begins

## 7. Governance Requirements

The roadmap assumes the cooperative is not a decorative admin role.

By 0.1.0, the system must support:
- cooperative approval of worker members
- cooperative review of household access
- cooperative moderation of abuse reports
- cooperative visibility into aggregate rate floors and demand
- cooperative export of non-sensitive operational summaries

The system must not support:
- investor-side worker performance dashboards
- employer-side surveillance feeds
- RWA-controlled worker blacklists
- public worker ranking
- secret admin edits without audit records

## 8. Research Backlog

These research items inform product decisions but should not block 0.1.0 unless they affect safety or legality.

- Ahmedabad domestic-worker organizations and informal worker networks
- SEWA-linked cooperative lessons relevant to domestic and care work
- Gujarat cooperative registration and governance options
- domestic-worker legal protections in Gujarat and India
- harassment, non-payment, and abuse escalation pathways
- data-protection implications under Indian privacy law
- risks of storing worker safety notes about households, institutions, or police stations
- app-store review mining for Mygate, NoBrokerHood, Urban Company, and relevant home-service apps

## 9. Open Product Decisions

These must be resolved before 0.1.0-beta.1:

1. Who can verify a worker member for the pilot?
2. Who can verify a household or tenant?
3. Is the cooperative a legal entity at pilot time, or an operating committee first?
4. Are household requests reviewed manually by default?
5. What is the minimum evidence level required before safety patterns are aggregated?
6. How long should abuse reports and blocked-contact records be retained?
7. What data can be exported by the cooperative without exposing workers?
8. What should happen when a household disputes a worker report?

## 10. Future Versions

### 0.2.0 - Cooperative Operations

Likely scope:
- stronger member governance
- cooperative policy records
- member voting or consent workflows
- better analytics for rate bargaining
- better offline support
- Ahmedabad pilot iteration

### 0.3.0 - Multi-Cluster Ahmedabad

Likely scope:
- multiple localities
- stronger geospatial support
- building cluster maps
- worker mobility patterns
- stronger moderation tooling
- external partner reporting

### 0.4.0 - Second City Preparation

Likely scope:
- city configuration
- local language support
- city-specific safety taxonomy
- city-specific legal/support referrals
- partner onboarding playbook

### 1.0.0 - Stable Cooperative Platform

Likely scope:
- production-grade cooperative governance
- audited privacy/security posture
- mature moderation system
- multiple city support
- robust backup/restore and incident response
- clear cooperative ownership and revenue model

## 11. Maintenance Rules

Update this file when:
- a release scope changes
- a milestone is completed
- an acceptance criterion changes
- a product decision is resolved
- research changes the roadmap
- implementation exposes a wrong assumption

Do not use this file as a dumping ground. Detailed conceptual material belongs in `aapnisociety-scope.md`. Detailed requirements belong in `aapnisociety-srs-formal.md`. This file should remain the maintained release plan.
