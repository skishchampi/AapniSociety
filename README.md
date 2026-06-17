# AapniSociety

AapniSociety began as a 2012 Android/Django prototype for crowdsourcing and geotagging community resources such as maids, cooks, grocery stores, laundry places, doctors, electricians, and other neighborhood services.

The 2026 rebuild is different in power and product direction: AapniSociety is now being re-scoped as worker-led, worker-owned cooperative infrastructure for trusted introductions, portable worker references, rate floors, tenant support, and worker-authored city knowledge.

## Current Status

This repository is in recovery and planning mode.

The legacy Android code is archival. It is useful for product memory, but it is not the production base for the rebuild.

Canonical project documents:

- [Scope and Concept Note](docs/aapnisociety-scope.md)
- [Formal SRS](docs/aapnisociety-srs-formal.md)
- [Roadmap](docs/aapnisociety-roadmap.md)
- [Legacy Audit](docs/aapnisociety-legacy-audit.md)
- [0.0.1 Release Notes](docs/releases/0.0.1.md)

## Release Direction

- `0.0.1`: recovery baseline and canonical documentation
- `0.1.0`: first cooperative trust pilot for Ahmedabad

## Rebuild Decision

Do not modernize the old Android project in place.

The modern rebuild should use:

- PWA-first frontend
- React + TypeScript + Vite
- Django 5 + Django REST Framework
- PostgreSQL with PostGIS-ready schema
- privacy-first data model
- cooperative governance and audit logging

The product should preserve the old insight that trust is local and relational, while rejecting public rating marketplaces, worker surveillance, and platform rent extraction.
