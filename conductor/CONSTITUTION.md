# Constitution

## Principles
1. **GitOps-first** — all infrastructure changes go through ArgoCD via this repo
2. **ApplicationSet-driven** — new apps are added as directories under `applications/` with Chart.yaml + values.yaml
3. **Helm Charts with dependency pattern** — upstream charts are referenced as dependencies in Chart.yaml (never forked)
4. **Cluster resources** — namespaced by app; cluster-scoped resources live in `applications/<app>/templates/`
5. **Ingress** — Cloudflare Tunnel entrypoint (cloudflared); new public services route through it

## Track Naming Convention
- `conductor/tracks/<kebab-case-name>/`

## Track Structure
- `spec.yaml` — requirements, design decisions, constraints
- `plan.yaml` — ordered implementation steps
- `status.md` — current state, blockers, next actions
