# AapniSociety Software Requirements Specification

Date: 2026-06-17
Status: Active
Reference scope: [docs/aapnisociety-scope.md](./aapnisociety-scope.md)
Release roadmap: [docs/aapnisociety-roadmap.md](./aapnisociety-roadmap.md)

## 1. Purpose

AapniSociety is private, consent-gated cooperative infrastructure for domestic workers, support workers, and tenant households in Indian cities.

The system helps users:
- preserve trusted local knowledge across tenant churn
- request and offer introductions without public exposure
- carry worker reputation and references across buildings
- surface worker-authored city safety knowledge
- operate under worker-led cooperative governance rather than platform extraction

## 2. Scope

The conceptual and historical basis for the product is documented in `scope.md`. This SRS only defines software behavior, data, privacy, and deployment requirements.

### In Scope

- worker and tenant accounts
- building membership
- introduction flows
- portable references
- worker rate floors and preferences
- service memory
- city safety notes
- reporting, moderation, and blocking
- cooperative operator tools
- privacy controls

### Out of Scope

- payments
- bookings / fulfillment marketplace
- public social feed
- public resident search
- landlord/RWA administration
- delivery logistics
- ad-supported growth mechanics

## 3. Users and Roles

- Domestic worker
- Maid / cook / driver / plumber / electrician
- Support staff
- Worker cooperative member
- Worker cooperative operator
- Tenant household
- Long-term tenant
- Trusted connector
- Moderator
- System admin

## 4. Product Overview

The product is organized around four user-visible modules:

1. **Trust Transfer**
   - request and offer introductions
   - reveal contact details only with consent
   - preserve building-scoped memory

2. **Worker Portability**
   - worker-owned profiles
   - portable references
   - minimum rate floors
   - work preferences
   - grievance and block tools

3. **City Safety**
   - transit reliability
   - night-route risk
   - institutional trust notes
   - worker-authored locality intelligence

4. **Cooperative Operations**
   - moderation
   - audit trails
   - policy review
   - operator tools for the cooperative

## 5. Functional Requirements

### 5.1 Authentication and Membership

- The system shall support phone OTP and email OTP sign-in.
- The system shall allow users to join one or more buildings.
- Building membership shall be explicit and scoped.
- The system shall support profile visibility settings.

### 5.2 Introductions

- The system shall let a user request an introduction to a resident or service provider.
- The system shall let a user accept or decline an introduction request.
- The system shall reveal contact details only with consent.
- The system shall store introduction history privately and per building.

### 5.3 Service Memory

- The system shall let users store and retrieve trusted local service knowledge.
- Supported service categories shall include maids, cooks, drivers, doctors, plumbers, electricians, and local eateries.
- The system shall favor introductions and referrals over public ratings.

### 5.4 Worker Portability

- The system shall allow workers to maintain a worker-owned profile.
- The system shall let workers store minimum rate floors, availability, language preferences, and scope of work.
- The system shall let workers carry private references across buildings.
- The system shall let workers block abusive households and report harassment.
- The system shall preserve worker bargaining history.

### 5.5 City Safety Layer

- The system shall allow workers and tenants to report transit reliability.
- The system shall allow workers to report night-route safety risk.
- The system shall allow workers to add structured institutional trust notes.
- The system shall present aggregated safety patterns rather than raw rumor streams.

### 5.6 Moderation

- The system shall allow reports for harassment, stalking, doxxing, coercion, casteism, communal abuse, and classist exclusion.
- The system shall support moderation review queues.
- The system shall log all moderator and admin actions.

### 5.7 Notifications

- The system shall notify users of introduction requests, approvals, new trusted leads, and moderation updates.
- The system shall avoid leaking sensitive relationship data in previews.

## 6. Non-Functional Requirements

### 6.1 Privacy

- Profiles shall be private by default.
- No public search indexing.
- No shareable resident profile URLs.
- No collection of caste, religion, marital status, or relationship status unless strictly required.
- No collection of caste or religion for worker ranking or household filtering.
- Sensitive data shall be redacted in logs and analytics.

### 6.2 Security

- Short-lived access tokens and rotating refresh tokens.
- Strong MFA for admin/support users.
- Rate limiting for login, OTP, invitations, and search.
- Block/report tools for abuse.
- Encrypted backups and controlled export access.
- India-region hosting preferred for primary data.

### 6.3 Reliability and Operations

- Daily backups with restore drills.
- Point-in-time recovery for the database.
- Structured logging, metrics, tracing, and alerting.
- CI with tests, dependency scanning, secret scanning, and container image scanning.
- Staging and production isolation.

### 6.4 Usability

- Mobile-first and PWA-first.
- Low-friction onboarding.
- Minimal cognitive load.
- Worker-facing and tenant-facing flows shall be equally legible.

## 7. System Architecture

### 7.1 Frontend

- TypeScript
- React
- Vite
- TanStack Query
- PWA support
- Minimal client state

### 7.2 Backend

- Python 3.12+
- Django 5.x
- Django REST Framework
- PostgreSQL
- Redis
- Celery
- Docker

### 7.3 Backend Structure

The backend shall use a modular monolith with domain modules for:
- accounts
- buildings
- introductions
- service_graph
- notifications
- moderation
- search
- geo
- admin_ops

### 7.4 API Style

- REST-first
- versioned under `/api/v1/`
- idempotent writes where practical
- admin endpoints separated from resident endpoints

## 8. Data Model

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

Legacy model mapping:
- `User_Wishes` -> `ServiceNeed`
- `User_Provides` -> `ServiceOffer`
- `Ratings` -> private trust metadata only, if retained
- `Gossip` -> not a core primitive
- `EnterAndReadGossip` -> notifications only, if relevant

## 9. UX Requirements

- Building-scoped navigation
- No public profile graph
- No default caste/religion/marital-status surface area
- Consent-first contact reveal
- Worker-facing flows as legible as tenant-facing flows
- No social-feed-first design
- No public reputation scoring

Primary screens:
- sign-in / sign-up
- building join / verification
- home dashboard
- request introduction
- offer introduction
- service memory
- notifications
- privacy settings
- worker profile
- city safety layer
- moderation/report flow
- coop admin console

## 10. Product Constraints

- The system shall not become a society-management clone.
- The system shall not become a transaction tollbooth on labor.
- The system shall not optimize for elite convenience over worker dignity.
- The system shall not expose worker-sourced safety notes to employers, landlords, or RWAs.
- The system shall not use trust as a filter for enclosure.

## 11. Deployment and Environment

- Containerized build and deployment
- Managed Postgres preferred
- Managed Redis preferred
- Object storage for files
- Reverse proxy or load balancer in front of the API
- Separate staging and production environments
- India-hosted primary data preferred

## 12. MVP Definition

The MVP shall include:
- sign-in
- building membership
- tenant profile
- worker profile
- portable references
- minimum rate floor setting
- introduction requests and approvals
- service memory
- city safety notes
- block/report moderation
- coop/admin console

The MVP shall exclude:
- payments
- bookings
- public feed
- open ratings
- public search
- logistics
- landlord/RWA tooling

## 13. Acceptance Criteria

The MVP is acceptable when:
1. a tenant can join a building and find trusted help without public exposure
2. a worker can move across buildings without losing references or rate expectations
3. users can add city-safety notes that aggregate without exposing contributors
4. moderation can handle harassment, caste/class exclusion, and coercion
5. the system operates as a privacy-first trust layer without requiring a marketplace cut

## 14. Open Questions

1. What is the verification standard for building membership?
2. How much of the resident graph should be visible to a newly joined resident?
3. Should service providers be first-class accounts or only trusted references?
4. Which notifications should be push vs in-app only?
5. What is the minimum data retained after account deletion?
