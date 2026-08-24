# AapniSociety SRS

Date: 2026-06-17  
Status: Superseded draft — the formal SRS (aapnisociety-srs-formal.md) owns requirements.

## 1. Purpose

AapniSociety is a private resident trust-transfer system for apartment buildings and housing societies in Indian cities.

The product helps:
- renters preserve local knowledge across tenant churn
- residents get warm introductions to trusted people and services
- inter-caste couples, inter-religion couples, and unmarried couples navigate housing and local support with privacy
- buildings retain useful community memory without turning into a public social network

This is not a society-management suite, not a public directory, and not a ratings marketplace.

## 2. Problem Statement

Urban Indian housing is high-churn and trust-fragmented.

This product sits in Kalyan Sanyal's "need economy". That is the part of postcolonial capitalism where people sit outside stable wage labor. They still reproduce life through informal work, care labor, tenant mobility, and negotiated access to housing and services. In that world, the app should help people meet needs, bargain better, and move without losing dignity.

Common problems:
- new tenants do not know whom to trust for maids, cooks, drivers, plumbers, electricians, doctors, or local eateries
- local knowledge disappears when people move out
- landlords, brokers, and RWAs can become gatekeepers
- renters face large deposits, weak paperwork, eviction pressure, utility pressure, and discrimination
- private relationships can face social scrutiny in some cities and states

The app’s job is to preserve and transfer trust inside a building, not expose it publicly.

## 3. Product Goals

1. Let a resident join a building and understand what trusted local knowledge already exists.
2. Let a resident request a warm introduction instead of broadcasting personal details.
3. Let a resident offer trusted introductions without becoming a middleman.
4. Keep sensitive relationship and household data private by default.
5. Support an Ahmedabad-first rollout, then expand to similar urban markets.
6. Prevent caste/class enclosure from turning the app into a tool of exclusion.
7. Increase worker bargaining power rather than reducing labor to a hidden service layer.
8. Help tenants and domestic workers navigate the need economy with mobility, trust, and leverage.

## 4. Non-Goals

- public social feed
- open ratings marketplace
- RWA administration or compliance system
- payments or service booking marketplace
- delivery/logistics layer
- public resident search
- ad-driven growth mechanics
- in-app chat as the primary product
- caste-coded filtering or ranking of workers
- landlord or RWA surveillance of private resident relationships
- any product mechanic that turns “trust” into a euphemism for exclusion

## 5. Target Users

- tenant household
- long-term tenant
- trusted connector
- migrant professional
- inter-caste couple
- inter-religion couple
- unmarried couple
- domestic worker
- support staff
- cook
- maid
- driver
- plumber
- electrician
- worker cooperative member

## 6. Core Use Cases

1. A new tenant joins a building and asks for trusted help finding a maid, cook, plumber, or electrician.
2. A resident offers a warm introduction to a trusted service provider or neighbor.
3. A couple uses the app with limited visibility to avoid unnecessary exposure.
4. A resident reviews building memory for prior recommendations and introductions.
5. A moderator handles abuse, false reports, or coercive behavior.
6. A worker carries references and rate expectations across buildings without losing dignity or control.
7. A worker rejects abuse, blocks hostile households, and preserves portability of labor.
8. A worker compares demand across nearby buildings and raises rate floors based on real experience, not on elite labels.
9. A tenant household discovers trusted support without relying on a broker or RWA-controlled gate.

## 7. Functional Requirements

### 7.1 Account and Membership

- Users can create an account using phone or email verification.
- Users can join one or more buildings.
- Building membership must be explicit and scoped.
- Users can set profile visibility and sharing preferences.

### 7.2 Introductions

- Users can request an introduction to a resident or service provider.
- Users can accept, decline, or ignore introduction requests.
- Contact details are revealed only with consent.
- Introduction history is private and building-scoped.

### 7.3 Service Memory

- Users can store and retrieve trusted local service knowledge.
- Supported categories include maids, cooks, drivers, doctors, plumbers, electricians, and local eateries.
- The system should favor referrals and introductions over public reviews.
- Service memory must remain anti-caste in practice: no public ranking engine that can become a caste filter.

### 7.4 Worker Portability

- Workers can own a profile and carry it across buildings.
- Workers can set minimum rates, availability, language preferences, and scope of work.
- Workers can see private references and their own negotiation history.
- Workers can block abusive households, report harassment, and leave a building-level trust record.
- The system can recommend rate floors based on locality and realized demand, but the worker controls acceptance.
- The worker module should be structurally compatible with a cooperative governance model, not a pure platform-extraction model.

### 7.5 Privacy Controls

- Users can hide exact unit, full name, photo, and contact details.
- Users can choose what other residents can see.
- Users can delete or deactivate their account.
- Users can block or report abusive accounts.

### 7.6 Notifications

- The system sends notifications for introduction requests, approvals, new trusted leads, and moderation events.
- Notifications must not leak sensitive relationship data in lock screens or email previews.

### 7.7 Moderation

- Moderators can review abuse reports, false profiles, spam, harassment, stalking, doxxing, and hate content.
- Admin actions must be logged.
- Moderation must specifically catch casteism, communal abuse, classist exclusion, sexual harassment, and coercive landlord/RWA behavior.

## 8. UX/UI Requirements

### 8.1 Product Shape

- PWA-first
- mobile-first
- privacy-first
- building-scoped navigation
- no public profile graph
- no caste, religion, or marital-status surface area in default flows
- worker-facing flows must be as legible as household-facing flows

### 8.2 Main Screens

- sign-in / sign-up
- building join / verification
- home dashboard
- request introduction
- offer introduction
- service memory
- notifications
- privacy settings
- profile
- moderation/report flow

### 8.3 UX Principles

- expose the minimum needed to complete a trust transfer
- make consent obvious
- keep the main actions simple: join, ask, offer, introduce
- avoid social-feed behavior
- avoid public reputation scoring
- use non-judgmental language
- do not let “trust” become a filter for enclosure
- design for fraternity, not just convenience
- design for worker dignity, not just household convenience

## 9. Data Model

Core entities:
- User
- Profile
- City
- Building
- Unit
- Membership
- ServiceCategory
- ServiceNeed
- ServiceOffer
- IntroductionRequest
- Introduction
- Provider
- PrivacySetting
- ConsentRecord
- Notification
- Report
- BlockList
- AuditEvent
- WorkerProfile
- WorkerMembership
- WorkerRate
- WorkerReference
- WorkerBlock
- WorkerReport
- CoopMember
- CoopVote
- CoopPolicy

Legacy model mapping from the old codebase:
- `User_Wishes` -> `ServiceNeed`
- `User_Provides` -> `ServiceOffer`
- `Ratings` -> deprecate or fold into private trust metadata
- `Gossip` -> do not preserve as a core primitive
- `EnterAndReadGossip` -> replace with notifications or community updates only if needed

## 10. System Architecture

### 10.1 Recommended Stack

- Frontend: TypeScript + React + Vite
- Frontend state/data: TanStack Query, minimal client state
- Frontend styling: Tailwind CSS or equivalent restrained system
- Frontend mode: PWA
- Backend: Python 3.12+, Django 5.x, Django REST Framework
- Database: PostgreSQL
- Cache / queue: Redis
- Async jobs: Celery
- File/object storage: S3-compatible object storage
- Deployment: Docker, reverse proxy / load balancer, managed infrastructure where possible

### 10.2 Backend Shape

Use a modular monolith first.

Suggested domains:
- accounts
- buildings
- introductions
- service_graph
- notifications
- moderation
- search
- geo
- admin_ops

### 10.3 API Style

- REST-first
- versioned under `/api/v1/`
- idempotent writes where practical
- admin APIs isolated from resident APIs

## 11. Security and Privacy Requirements

- default profiles to private
- no public search indexing
- no shareable resident URLs
- no collection of caste, religion, marital status, or relationship status unless strictly required
- no collection of caste or religion for worker ranking or household filtering
- consent-gated contact reveal only
- short-lived tokens and rotating refresh tokens
- strong MFA for admin/support roles
- audit trails for admin actions and consent changes
- PII redaction in logs and analytics
- rate limiting for login, OTP, invitations, and search
- block/report flows for harassment, stalking, coercion, and hate
- encrypted backups and controlled access to exports
- resident/household access must not reveal worker location history beyond what is consented

## 12. DevOps Requirements

- containerized build and deployment
- staging and production isolation
- automated tests in CI
- dependency, secret, and container image scanning
- structured logging
- metrics, tracing, and alerting
- daily backups plus restore drills
- point-in-time recovery for the database
- managed secret storage only
- India-region hosting preferred for primary data

## 13. Why Django

Django is the right default here because the product needs to be small in team size, not fragile in security.

### Why Django over a thinner stack

1. **Security defaults**
   - Django gives mature auth, CSRF protection, ORM safety, middleware, and a long security track record.
   - A thinner framework usually shifts security work back onto the team, which is the wrong trade for a privacy-sensitive product.

2. **Less custom code**
   - The more you hand-roll identity, permissions, admin flows, migrations, and validation, the more attack surface you create.
   - Django reduces that surface by shipping the boring parts.

3. **Admin and moderation**
   - This product needs internal moderation, auditability, and support tooling.
   - Django admin is a real advantage here.

4. **Legacy alignment**
   - The old server side is already Django-shaped.
   - Reusing the framework family preserves domain memory without resurrecting the old code.

5. **Team velocity**
   - A modular Django monolith is faster to harden, easier to reason about, and easier to test than a custom microservice stack.

### Why not a lighter framework first

- **FastAPI**: excellent for APIs, but you must compose more of the security, auth, admin, and moderation stack yourself.
- **Node/NestJS**: workable, but the app does not need a JS backend and the team would be recreating mature Django functionality.
- **Barebones microframeworks**: too much custom glue for a product that carries privacy and safety risk.

### What “lightweight” should mean here

Not “fewest files at all costs.” It should mean:
- one backend repo
- one API service to start
- minimal dependencies
- modular monolith instead of microservices
- strict data model
- narrow surface area

If you want the system to be lightweight and secure, Django API-only is the right compromise.

## 13.1 Anti-Caste Design Constraint

This product must not become a neutral technical wrapper over graded inequality.

The app should assume:
- caste and class hierarchies are present in housing
- “community trust” can be used to exclude and surveil
- workers are often the least protected party in the system
- households may want convenience without moral responsibility

Therefore:
- worker profiles must be portable
- worker data must not be owned by a building
- public ratings must not become caste-coded sorting
- the app should support worker bargaining power, not just household convenience
- privacy defaults should protect the vulnerable, not merely the respectable
- the product should treat tenants and support workers as primary participants in the need economy, not as edge cases around owner-led society management

This is not an accessory requirement. It is a structural requirement.

## 13.2 Sanyal / Need-Economy Positioning

The product's economic category is not "home services marketplace" in the Urban Company sense.

It is:
- trust transfer across churn
- worker portability across buildings
- tenant mobility across neighborhoods
- bargaining support inside the need economy

That means the app should prioritize:
- direct resident-to-worker and tenant-to-worker trust transfer
- worker-controlled rate discovery
- portable references
- household onboarding
- anti-abuse controls

It should not prioritize:
- taking a cut from every transaction
- converting need into a pure platform margin stream
- making workers dependent on opaque ranking systems
- building an elite convenience layer that reproduces enclosure

## 13.3 MVP Scope

The MVP should prove the trust-transfer and worker-knowledge thesis without broad marketplace complexity.

### Must Have

- phone/email sign-in
- building join / membership verification
- tenant household profile with private visibility controls
- worker profile with portable references and minimum rate floor
- request / offer introduction flow
- service memory for maids, cooks, drivers, plumbers, electricians, doctors, and local eateries
- simple city-safety notes for transit reliability and night-route risk
- block / report / moderation flow
- basic coop/admin console for review and support

### Should Have

- neighborhood and building notes
- worker-locality preference layer
- consent-based contact reveal
- moderation queue for hate, coercion, harassment, and caste/class exclusion
- simple worker bargaining history

### Won’t Have in MVP

- payments
- booking and fulfillment marketplace
- public feed
- public resident search
- open ratings system
- delivery/logistics features
- landlord/RWA admin suite

## 13.4 Success Criteria

The MVP is successful if it can do all of the following:

1. a tenant can join a building and find trusted help without public exposure
2. a worker can carry references and rate expectations across buildings
3. users can leave useful city-safety notes without leaking identity
4. moderators can respond to abuse, exclusion, and harassment
5. the product can operate as a privacy-first trust layer without needing a marketplace cut

## 14. City Rollout

### Phase 1
- Ahmedabad

### Phase 2
- Bengaluru
- Mumbai
- Delhi NCR
- Pune

### Phase 3
- Hyderabad
- Chennai
- Kolkata

## 15. Risks

- turning into a society-management clone
- adding public ratings and losing the trust-transfer wedge
- privacy leakage through notifications, search, or logs
- weak moderation against harassment and stalking
- overfitting the product to one city’s norms
- underestimating how sensitive interfaith/inter-caste/unmarried-couple support is in real housing contexts
- reproducing caste/class enclosure under the language of trust
- building a worker marketplace that extracts labor while calling itself a cooperative
- drifting back into owner-first convenience instead of tenant/worker bargaining power

## 16. Open Questions

1. What is the exact onboarding verification standard for building membership?
2. How much of the resident graph should be visible to a newly joined resident?
3. Should service providers be first-class accounts or only trusted references?
4. Which notifications should be push vs in-app only?
5. What is the minimum data retained after account deletion?

## 17. Source Notes

This SRS was informed by:
- the legacy Android client in this repo
- the legacy Django server repo
- current market context on urban housing, telecom access, and inequality
- current legal and policy context in India
- Kalyan Sanyal's account of postcolonial capitalism, capital/not-capital, and the need economy
- Indian labor organizing history across tech, gig, domestic, informal, and beedi work
- the Blume India 1 / India 2 / India 3 framing
- city readiness context from SevenT4 for Ahmedabad-first rollout

## 18. Worker Movement Context

The worker module should be designed with the actual Indian labor movement in mind, not as a generic marketplace feature.

### 18.1 What the labor history says

- **Tech workers** have organized late and unevenly, with visible pressure centers in Bengaluru, Chennai, and Pune.
- **Gig workers** have organized faster and more publicly, especially around pay cuts, ID blocks, algorithmic punishment, and social security.
- **Domestic workers** remain heavily underprotected, often working inside private homes and apartment enclaves where surveillance and abuse risks are high.
- **Bidi and other informal workers** show the long-running reality of home-based, feminized, underpaid labor and the need for portability, social security, and cooperative forms.

### 18.2 What the product should learn from unions

- Workers need portable reputation and portable leverage.
- Workers need clear grievance paths and the ability to block abusive households.
- Worker organizations succeed when they combine membership, services, legal help, and collective voice.
- Pure protest is not enough; governance and ownership matter.
- Any trust system can become a surveillance or exclusion tool if workers do not control their own data.

### 18.3 What this means for AapniSociety

- The worker module should be worker-owned in spirit and compatible with cooperative governance in structure.
- Rate discovery should help workers raise floors, not help households shop for the cheapest labor.
- References, ratings, and history must be portable across buildings.
- The app should help workers move through the need economy with more bargaining power, not less.

### 18.4 City labor map

- **Ahmedabad**: the core informal-worker and cooperative precedent is SEWA, rooted in the city's Gandhian labor history and the organization of women street vendors, head-loaders, home-based workers, and bidi rollers. Ahmedabad also has strong evidence of migrant construction-worker organizing and exclusion in urban governance.
- **Bengaluru**: strongest visible tech-worker union pressure point, especially around working hours, layoffs, self-certification, and forced retrenchment. It is also a site where domestic workers are increasingly being folded into state-level regulation debates.
- **Chennai**: strongest IT/ITES worker-memory in the corpus, with women IT workers describing long hours, precarity, and limited collective action. The city is also a major site for public-sector and sanitation-worker labor conflict.
- **Delhi NCR**: strong gig-worker and domestic-worker policy pressure point, especially around minimum floors, social security, and the legal visibility of precarious labor.
- **Hyderabad**: important gig-worker node where grievance breakdown, ID blocks, and weak support systems are documented clearly.
- **Mumbai**: historic union city, and the launch node for IFAT. Also important for transport, municipal, film, and domestic-worker organizing.
- **Pune**: important for IT layoffs and complaint-driven worker mobilization, especially around retrenchment pressure in TCS-linked disputes.
- **Kolkata**: long labor-memory city with current gig-worker wage struggles and a stronger legacy labor culture, including tram and municipal worker histories.

### 18.5 Union forms and design lessons

- **Tech-worker unions** show that white-collar labor is not outside precarity; the app should expect opaque management, layoffs, and retaliation even in privileged sectors.
- **Gig-worker unions** show that algorithmic management, pay opacity, and ID blocking are core design failures; the app should make bargaining transparent and portable.
- **Domestic-worker organizing** shows that workers inside private homes need the strongest privacy and anti-abuse protections because exploitation is hidden inside intimate space.
- **Bidi and informal-worker organizing** shows why home-based, feminized, and caste-marked labor needs collective ownership, not just visibility.
- **SEWA-style cooperatives** show that membership, services, credit, and collective voice can scale better than protest alone.
- **Kerala Dinesh** shows that worker ownership is possible as an economic form, not just a political aspiration.

## 19. City Safety Layer

The app should let workers and tenants describe the city as it is lived, not as it is marketed.

### 19.1 Purpose

This module helps workers foreground practical knowledge about:
- which buses are usually on time
- which trains are reliable
- which lanes or stretches feel unsafe at night
- which localities are friendly to women workers
- which police stations or institutional actors are hostile or unsafe
- which routes are worth taking because the pay, timing, or safety justifies them

The goal is not aesthetic mapping. The goal is worker-authored urban intelligence.

### 19.2 Core Features

#### Transit Reliability
- Workers can report bus and train reliability as simple structured signals.
- Reports should support labels such as `on time`, `usually late`, `crowded but reliable`, `avoid`, and `depends on time of day`.
- The product should surface aggregated reliability patterns by route, time, and day.

#### Night Route Risk
- Workers can flag lanes, crossings, stations, and approach roads by perceived safety at night.
- Signals should be time-aware and gender-aware where the user consents to that context.
- The product should support labels such as `safe`, `unsafe`, `escort recommended`, and `avoid after dark`.

#### Institutional Trust Notes
- Workers can leave structured notes about institutions they encounter repeatedly, including police stations, labor offices, hospitals, and building offices.
- The system should capture behavior patterns, not encourage unsupported accusations.
- Notes should be tied to time, place, and context, with confidence levels where appropriate.

#### Worker City Lens
- Each worker can maintain a personal preference layer for:
  - best commute windows
  - safer routes
  - preferred neighborhoods
  - avoided zones
  - high-yield zones
  - repeat-client zones

### 19.3 Evidence and Moderation

- Reports must be structured enough to support aggregation.
- Raw accusations should not be treated as truth by default.
- Severe allegations should route to moderation and, where relevant, formal escalation workflows.
- The UI must distinguish between:
  - direct firsthand experience
  - repeated worker consensus
  - inferred risk
  - confirmed administrative action

### 19.4 Privacy Rules

- Individual contributors should remain protected by default.
- Identity should be visible only with consent.
- Employer, landlord, and RWA access must not reveal worker-sourced safety notes in a way that exposes the contributor.
- Location history should be minimized and retained only as needed for safety, product function, and legal compliance.

### 19.5 Product Outcome

This layer turns the app into a majority-city navigation tool:
- workers see where the city is safe, fair, and usable
- tenants see how daily life actually works
- the coop gets a better picture of local labor conditions
- the app stops pretending the city is only the elite route map
