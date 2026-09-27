# SMS Number · OTP Market

A mobile app for purchasing virtual phone numbers and receiving OTPs for online service verification. Branded as **SMS Number** (display) / **OTP Market** (platform).

## Run & Operate

- `pnpm --filter @workspace/api-server run dev` — run the API server (port 8080)
- `pnpm --filter @workspace/mobile run dev` — run the Expo mobile app (port 18115)
- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from the OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only; run after any schema edit)
- Required env: `DATABASE_URL` — Postgres connection string (runtime-managed by Replit)

## Stack

- pnpm workspaces, Node.js 24, TypeScript 5.9
- API: Express 5
- DB: PostgreSQL + Drizzle ORM
- Validation: Zod (`zod/v4`), `drizzle-zod`
- API codegen: Orval (from OpenAPI spec)
- Build: esbuild (CJS bundle)
- Mobile: Expo / React Native

## Where things live

- `artifacts/api-server/src/routes/` — all 40+ Express route handlers
- `artifacts/api-server/src/middleware/auth.ts` — JWT middleware (`requireAuth`, `requireAdmin`)
- `artifacts/api-server/src/lib/seed.ts` — seeds all default data + admin user on startup
- `artifacts/api-server/src/lib/email.ts` — all email functions (verification, reset, login alert, logout alert, **account locked**)
- `artifacts/api-server/src/index.ts` — server entry point; calls `seedDatabase()` on boot
- `lib/db/src/schema/` — 14 Drizzle ORM schema files (one per table)
- `lib/api-spec/openapi.yaml` — source-of-truth OpenAPI spec (40+ endpoints)
- `artifacts/mobile/lib/api.ts` — fetch wrapper used by all mobile API calls
- `artifacts/mobile/context/AuthContext.tsx` — auth state + API-based login/register/verify
- `artifacts/mobile/context/AppContext.tsx` — app-wide state (services, orders, etc.) fetched from API
- `artifacts/mobile/app/_layout.tsx` — ConnectedAppProvider bridges AuthContext token → AppContext

## Architecture decisions

- JWT auth (30-day tokens), stored in `@otpmarket_token` in AsyncStorage
- JWT secret: `process.env.JWT_SECRET ?? process.env.SESSION_SECRET` (set SESSION_SECRET in Replit Secrets)
- Admin credentials seeded on startup: `tiegmicheal@gmail.com` / `333556`
- All numeric DB fields (`numeric` Drizzle type) serialized via `parseFloat()` in route handlers
- AppContext receives `token` + `userRole` props from ConnectedAppProvider; public data loads without auth, user/admin data loads when token is present
- Mobile API base URL: `https://${process.env.EXPO_PUBLIC_DOMAIN}/api`
- **Login lockout**: 5 failed attempts → 10-minute lock (`loginAttempts` + `lockedUntil` columns in `users`)
- **Security email**: `sendAccountLockedEmail()` fires automatically when the 5th failed attempt triggers a lock

## Security features

- Max 5 failed login attempts per account (backend-enforced, not just frontend)
- 10-minute lockout after 5 failures — stored in DB (`lockedUntil` timestamp)
- Lockout check runs before password comparison on every login attempt
- Automatic unlock: lock expires naturally when `lockedUntil` passes
- Security email sent to user when account is locked (via active email provider)
- Passwords hashed with bcrypt (cost 12) — never stored or returned in plaintext
- Login/logout alert emails sent on every successful auth event

## Email functions (artifacts/api-server/src/lib/email.ts)

| Function | Trigger |
|---|---|
| `sendVerificationCode` | User registers |
| `sendPasswordResetCode` | User requests reset |
| `sendLoginAlert` | Successful login |
| `sendLogoutAlert` | Logout |
| `sendAccountLockedEmail` | 5th failed login attempt (lockout triggered) |

## Product

- Users register, verify email, log in, and top up a wallet (USD/NGN)
- Browse 30+ services (WhatsApp, Telegram, Gmail, etc.) across multiple countries
- Purchase a virtual phone number, wait for OTP, receive it in-app
- Star system: ⭐ 1 = $0.10; users buy star packages to pay for numbers
- Admin panel: manage users, services, countries, providers, banners, support tickets, audit logs

## User preferences

- Branding: display name is **SMS Number**, platform name is **OTP Market**

## Gotchas

- `pnpm --filter @workspace/db run push` must be re-run after schema changes (dev only)
- Run `pnpm --filter @workspace/api-spec run codegen` after any OpenAPI spec change
- Express 5: async handlers return `Promise<void>`; use `res.status().json(); return;` pattern; wildcard routes use `/{*splat}`
- Never use `console.log` in server code — use `req.log` in handlers, singleton `logger` elsewhere
- After editing `lib/db/src/schema/`, run `pnpm --filter @workspace/db run push` then `cd lib/db && npx tsc -b` to regenerate `.d.ts` files consumed by api-server project references
- The `SESSION_SECRET` env var doubles as the JWT secret when `JWT_SECRET` is not set

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details
