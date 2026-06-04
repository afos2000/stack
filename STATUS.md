# Stack Status

## Cluster
- k3s-master, k3s-worker1, k3s-worker2, afos2000-thinkpad-p52 — all **Ready**
- thinkpad node auth fixed: CA cert replaced, agent re-joined fresh
- kubeconfig perms fixed: `write-kubeconfig-mode: 644` in `/etc/rancher/k3s/config.yaml`

## OpenCode
- Conductor plugin removed, **superpowers** installed (obra/superpowers)
- Fresh session needed after plugin change

## Running Apps (via ArgoCD)
- Keycloak + postgres-db
- Cloudflare Tunnel (cloudflared)
- Vault + External Secrets Operator
- cert-manager, reflector, reloader
- postgres-operator, Longhorn
- ArgoCD + ApplicationSet

## Todo (next session)
1. Add `k` alias + kubectl autocomplete on master
2. Deploy Backstage as IDP (Helm chart, postgres-operator, cloudflared ingress)
3. Integrate Keycloak SSO with Backstage
4. Configure Backstage catalog with existing services

## Decisions
- GitOps via ArgoCD ApplicationSet → `applications/*` dirs
- Each app = Helm chart with Chart.yaml + values.yaml
- Secrets from Vault via External Secrets Operator
- CPU limits removed to avoid throttling
- Backstage from `backstage/backstage` Helm repo, external PostgreSQL
- All 4 nodes Ready (thinkpad re-joined)
