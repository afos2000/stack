# keycloak

Deploys **Keycloak 26.5.6** — SSO/OIDC identity provider, configured to authenticate ArgoCD users.

## Dependencies
- **postgres** — external database (`keycloak-db-rw.postgres.svc`)
- **vault** — admin password fetched from `secrets/data/keycloak` (property: `admin-pw`)
- **reflector** — database credentials reflected from `postgres` namespace
- **cloudflared** — ingress via `keycloak.andreskube.uk`

## Key config
- **Image**: `quay.io/keycloak/keycloak:26.5.6`
- **Hostname**: `https://keycloak.andreskube.uk`
- **Args**: `start --import-realm` — imports `realm-argocd.json` on startup
- **Bootstrap admin**: username `admin`, password from Vault
- **Post-start hook**: re-imports realm JSON via `kcadm.sh` after 15s

## Realm: `argocd`
Pre-configured in `templates/realm-configmap.yaml`:
- OIDC client `argocd` with redirect to `https://argocd.andreskube.uk/auth/callback`
- Realm roles `argocd-admin` and `argocd-readonly`
- Groups claim mapper from realm roles

## ArgoCD SSO setup
1. In Keycloak realm `argocd`, create users and assign `argocd-admin` or `argocd-readonly` roles
2. ArgoCD is configured with OIDC pointing to this Keycloak instance

## Adding users
Access Keycloak admin console at `https://keycloak.andreskube.uk`, login with admin credentials from Vault.
