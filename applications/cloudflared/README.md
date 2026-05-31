# cloudflared

Deploys **cloudflared** (Cloudflare Tunnel) — secure outbound-only ingress into the cluster.

## Dependencies
- **vault** → **external-secrets** — tunnel token fetched from Vault at path `secrets/data/cloudflare-tunnel` (property: `token`)

## Key config
- **Image**: `cloudflare/cloudflared:latest`
- **Auth**: Token via env `TOKEN` from Kubernetes Secret `tunnel-token`
- **Replicas**: 1 (single tunnel connection)

## How it works
1. Create a tunnel in Cloudflare Zero Trust dashboard
2. Store the tunnel token in Vault: `vault kv put secrets/cloudflare-tunnel token="..."` 
3. cloudflared connects outbound to Cloudflare edge
4. Cloudflare routes traffic to the cluster based on ingress rules configured in the Cloudflare dashboard

## Adding a new service
In Cloudflare Zero Trust → Tunnels → your tunnel → Public Hostnames:
- **Subdomain**: e.g., `grafana`
- **Domain**: `andreskube.uk`
- **Type**: `HTTP`
- **URL**: `http://service-name.namespace.svc.cluster.local:port`

## Current services
- `keycloak.andreskube.uk` → Keycloak
- ArgoCD (hostname TBD, probably `argocd.andreskube.uk`)

## Operations
```bash
# Check tunnel status
kubectl logs -n cloudflared -l app.kubernetes.io/name=cloudflared

# Restart tunnel
kubectl rollout restart -n cloudflared deployment cloudflared
```
