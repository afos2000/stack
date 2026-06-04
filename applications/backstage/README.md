# backstage

Deploys **Backstage** — Internal Developer Portal "AndresKube Homelab Services" at `platform-apps.andreskube.uk`.

## Dependencies
- **keycloak-db** (CNPG) — database `backstage` via managed databases
- **keycloak** — SSO via OIDC (realm `backstage`)
- **vault** — session secret, Keycloak client secret
- **reflector** — DB credentials reflected from `postgres` namespace
- **cloudflared** — ingress via `platform-apps.andreskube.uk`

## Key config
- **Title:** AndresKube Homelab Services
- **Image:** `ghcr.io/backstage/backstage:<pinned>`
- **Auth:** OIDC → Keycloak realm `backstage`
- **DB:** PostgreSQL on `keycloak-db-rw.postgres.svc:5432`

## Adding users
Users managed via `backstage-homelab-access.git` repo — creates users in Keycloak realm `backstage` with "change password on first login".
