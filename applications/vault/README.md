# vault

Deploys **HashiCorp Vault 1.21.2** — central secrets backend for the stack.

## Dependencies
- **Longhorn** — 10Gi PVC for Raft storage backend
- **k8s-objects** — MetalLB provides LB IP if needed (currently ClusterIP)

## Key config
- HA mode with Raft storage, single replica
- TLS disabled (internal cluster access only)
- Vault Agent injector disabled — secrets consumed via External Secrets Operator
- UI enabled at `ClusterIP:8200`
- No ingress — accessed via `kubectl port-forward` or Cloudflare Tunnel if needed

## Bootstrap
After initial deploy, you must unseal Vault and configure:
```bash
# Initialize (saves unseal keys + root token)
kubectl exec -n vault vault-0 -- vault operator init

# Unseal (repeat with 3 different keys)
kubectl exec -n vault vault-0 -- vault operator unseal

# Enable KV v2 engine
kubectl exec -n vault vault-0 -- vault secrets enable -path=secrets kv-v2

# Enable Kubernetes auth
kubectl exec -n vault vault-0 -- vault auth enable kubernetes
kubectl exec -n vault vault-0 -- vault write auth/kubernetes/config \
  token_reviewer_jwt="$(kubectl get secret vault-token-reviewer -n vault -o jsonpath='{.data.token}' | base64 -d)" \
  kubernetes_host="https://kubernetes.default.svc" \
  kubernetes_ca_cert="$(kubectl config view --raw --minify --flatten -o jsonpath='{.clusters[].cluster.certificate-authority-data}' | base64 -d)"

# Create role for External Secrets Operator
kubectl exec -n vault vault-0 -- vault write auth/kubernetes/role/eso \
  bound_service_account_names=external-secrets \
  bound_service_account_namespaces=external-secrets \
  policies=eso-policy \
  ttl=1h

# Create policy
kubectl exec -n vault vault-0 -- vault policy write eso-policy - <<EOF
path "secrets/data/*" {
  capabilities = ["read", "list"]
}
EOF
```

## Connected apps
| App | What it reads from Vault | Path |
|-----|-------------------------|------|
| external-secrets | (ClusterSecretStore points here) | `secrets/data/*` |
| cloudflared | Cloudflare Tunnel token | `secrets/data/cloudflare-tunnel` |
| keycloak | Admin password | `secrets/data/keycloak` |
| docker-registry | Docker Hub credentials | `secrets/data/dockerhub` |
