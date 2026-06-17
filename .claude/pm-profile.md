---
repo: aapnisociety
cockpit: docs/STATUS.md
roadmap: docs/aapnisociety-roadmap.md
unit_of_progress: recovery and rebuild-planning artifacts for the AapniSociety cooperative PWA
---

## Stage Discipline

The repo currently progresses through documentation and planning gates before implementation:

1. legacy recovered
2. scope documented
3. SRS documented
4. roadmap documented
5. research notes documented
6. implementation plan written
7. software scaffolded
8. software verified

Do not count research or docs as software implementation.

## 1. Count Commands

```bash
find docs -maxdepth 2 -type f -name '*.md' | sort | wc -l
find docs/releases -maxdepth 1 -type f -name '*.md' 2>/dev/null | sort | wc -l
find docs/research -maxdepth 1 -type f -name '*.md' 2>/dev/null | sort | wc -l
/opt/homebrew/bin/rg -n '^### 0\\.|^### 1\\.0\\.0' docs/aapnisociety-roadmap.md
git log --oneline -6
```

## 1a. Integrity Check

```bash
git diff --check
git status --short
```

## 2. Freshness Gates

Freshness is research-driven:

- app-store and competitor data should be refreshed before investor/funding/product claims
- legal/government-scheme claims should be refreshed before grant applications
- Bharat Taxi should remain a watch case and be refreshed before using it as evidence
- no freshness gate blocks `0.1.0-alpha.1` scaffolding

## 3. Live-Ops Check

No dev server, crawler, or daemon is expected for this repo at the current stage.

## 4. Roadmap Source and Gates

Roadmap source: `docs/aapnisociety-roadmap.md`

Current gate:
- `0.0.1` is the recovery baseline
- next gate is `0.1.0-alpha.1 - Foundations`

Acceptance for the next gate is defined in the roadmap under `0.1.0-alpha.1`.

## 5. Report Template

```markdown
## /pm - aapnisociety

Integrity:
Progress units:
Current gate:
Next gate:
Roadmap-vs-actual:
Freshness:
Live ops:
Blocked:
Commit gap:
On track:
```

## Discipline

- Treat the old Android and Django code as archival.
- Build the modern product as worker-led cooperative infrastructure.
- Scope and research live in docs; implementation starts at `0.1.0-alpha.1`.
- Use `/opt/homebrew/bin/rg` when searching in this repo.
