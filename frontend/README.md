# AapniSociety frontend

React 19 + TypeScript + Vite PWA. Built for `0.1.0-alpha.1` Foundations — a working
OTP sign-in → onboarding → dashboard flow with **minimal styling**. Intentional visual
design is a deliberate later milestone (functional scaffold first; see
[`docs/plans/0.1.0-alpha.1-foundations.md`](../docs/plans/0.1.0-alpha.1-foundations.md)).

## Run locally

```bash
cd frontend
npm install
npm run dev            # http://localhost:5173  (proxies /api -> http://localhost:8000)
```

Run the backend (`make backend-migrate && make backend-seed && cd backend && uv run python
manage.py runserver`) alongside. In dev the OTP code is shown on the verify screen, so no SMS
is needed.

## Structure

- `src/api/client.ts` — typed fetch client: bearer auth + one-shot refresh-on-401.
- `src/auth/` — `AuthProvider` (session bootstrap) + `useAuth` hook.
- `src/routes/` — `SignIn` (phone → OTP), `Onboarding` (worker/household profile), `Dashboard`.
- PWA: installable, auto-update service worker (`vite-plugin-pwa`).

## Scripts

```bash
npm run dev      # dev server
npm run build    # tsc -b && vite build (generates PWA service worker)
npm run lint     # eslint
npm run test     # vitest  (or: make frontend-test)
```
