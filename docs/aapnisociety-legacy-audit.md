# AapniSociety Legacy Audit

Date: 2026-06-17
Status: Draft

Related repos:
- Android client: `skishchampi/AapniSociety`
- Django server: `skishchampi/django-btp`, cloned locally at `/Users/aakash/Developer/CommonerLLP/django-btp`

## 1. Summary

The legacy AapniSociety codebase is a 2012-era Android and Django prototype for crowdsourcing and geotagging community resources such as maids, cooks, doctors, local shops, laundry, groceries, and other neighborhood services.

The Android client contains the richer product intent. The Django server repo is much thinner and only has one route wired in the checked-in code.

The useful artifact is not the old implementation. The useful artifact is the product memory:
- users could suggest service providers from their contacts
- users could request service providers by category
- users could search/add neighborhood places
- users could use a gossip/chat-like building/community feed
- the app assumed service trust was social, local, and mediated by community knowledge

## 2. Android Client

### 2.1 Project Shape

- Package: `com.apdisociety`
- App label: `Aapdi Society`
- Build system: legacy Android/ADT project, not Gradle
- Target: `Google APIs:19`
- Minimum SDK: `8`
- Target SDK in manifest: `17`
- Google Play Services reference points to a dead local Linux SDK path in `project.properties`

### 2.2 Main Screens and Flows

The Android client includes these main activities:

- `MainActivity`
- `SignInActivity`
- `SignupActivity`
- `HomeActivity`
- `SelectPeopleActivity`
- `RequestServiceActivity`
- `ServiceProviderActivity`
- `SelectContactActivity`
- `NbhSelectActivity`
- `NbhActivity`
- `SearchNbhActivity`
- `SearchNActivity`
- `GossipActivity`
- `SettingsActivity`

The user-facing flows appear to be:

1. Sign up / sign in.
2. Enter a home dashboard.
3. Request a service.
4. Suggest a service provider from phone contacts.
5. Search or add neighborhood places.
6. Read/send gossip-style community messages.
7. Sign out.

### 2.3 Service Categories

The checked-in string resources include:
- Maid
- Cook
- Electrician
- Carpenter
- Doctor

The neighborhood-place categories include:
- Vegetables
- Laundry
- Groceries
- frozen food

These categories match the original survey direction: practical neighborhood labor and everyday support services rather than luxury services.

### 2.4 Backend Endpoints Called by Android

The Android client calls hardcoded HTTP endpoints under `http://jigar-btp.cloudapp.net/`:

- `/register/`
- `/login/`
- `/logout/`
- `/service_request/`
- `/suggest_service/`
- `/suggest_places/`
- `/request_places/`
- `/gossip_receive/`
- `/gossip_enter/`
- `/gossip_enter2/`

The server repo currently wires only `/register/`, so the deployed server that once backed the Android app was ahead of the checked-in Django code or lived elsewhere.

### 2.5 Data Collected by the Client

The client touches sensitive surfaces:
- phone contacts
- phone numbers
- location
- SMS sending
- service-provider suggestions
- ratings
- gossip/chat content
- login credentials stored in shared preferences

This is important for the rebuild: the original app solved a trust problem by using contacts and social proximity, but a 2026 rebuild must not repeat the same privacy pattern.

### 2.6 Security and Privacy Findings

Findings:

- Backend URLs are hardcoded and use plain HTTP.
- The app requests `READ_CONTACTS`.
- The app requests `SEND_SMS`.
- The app requests fine and coarse location.
- The app stores username/password-like values in shared preferences.
- The manifest contains a hardcoded Google Maps API key.
- The app parses server responses with fragile string-splitting in several places.
- Service suggestions upload contact names, phone numbers, service categories, and ratings.
- Public rating logic exists in the old flow, but the cooperative rebuild should not preserve public star-rating behavior.

Implication:

The old code should be treated as archival. It should not be modernized in place as the production base.

## 3. Django Server

### 3.1 Project Shape

- Django project name: `AapdiSociety`
- App name: `btp`
- Django version implied by code style: around Django 1.5
- Database: SQLite
- Checked-in database path in settings uses a Windows path
- `DEBUG = True`
- Admin app is commented out
- Only `/register/` is wired in `urls.py`

### 3.2 Server Models

The checked-in models are:

- `Gossip`
- `Services`
- `Data`
- `User_Provides`
- `User_Wishes`
- `Ratings`
- `EnterAndReadGossip`

Useful model-memory mapping for the rebuild:

- `User_Wishes` becomes `ServiceNeed`
- `User_Provides` becomes `ServiceOffer`
- `Data` becomes private service-reference metadata
- `Ratings` becomes private reference/reputation metadata only if retained
- `Gossip` does not survive as a primitive; its useful replacement is moderated city safety notes and cooperative announcements
- `EnterAndReadGossip` becomes notification/subscription behavior only if needed

### 3.3 Server Data Snapshot

The checked-in SQLite database has tables for the Django auth app and `btp` app.

Observed row counts:

- `auth_user`: 1
- `btp_services`: 0
- `btp_data`: 0
- `btp_user_provides`: 0
- `btp_user_wishes`: 0
- `btp_gossip`: 0
- `btp_ratings`: 0

There is no meaningful service, rating, provider, wish, or gossip seed data to migrate.

## 4. Product Memory Recovered

The 2012 product was already trying to solve a useful problem:

- a resident needs practical help inside a locality
- the best knowledge is held by other residents and workers
- a phone-contact recommendation is more meaningful than a generic listing
- service information should be local and geotagged
- apartment/neighborhood life needs a memory layer

The 2026 direction changes the power center:

- from resident convenience to worker and tenant power
- from public ratings to consent-gated portable references
- from gossip to moderated safety and city knowledge
- from phone-contact harvesting to explicit consent
- from platform marketplace to cooperative infrastructure

## 5. Rebuild Decision

Do not revive the old Android app directly.

For the modern rebuild:

- build a PWA instead of native Android/iOS first
- create a new Django 5 backend rather than updating the Django 1.x server in place
- keep PostgreSQL/PostGIS-ready architecture
- keep the old repo as a historical artifact
- migrate concepts, not code

## 6. 0.0.1 Conclusions

For `0.0.1`, the project is considered recovered when:

- the legacy intent is documented
- the privacy/security reasons for not reviving the old code directly are documented
- the canonical scope, SRS, and roadmap files exist
- the roadmap identifies `0.1.0` as the first build target
- the next implementation plan can start from the modern cooperative architecture
