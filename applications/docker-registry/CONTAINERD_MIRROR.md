# Containerd Mirror Configuration for Docker Hub Cache

After deploying the docker-registry, configure each node's containerd to use
the local registry as a mirror for `docker.io`.

## Option A: Manual per-node (simple, not GitOps)

Edit `/etc/containerd/config.toml` on each node and add:

```toml
version = 2

[plugins."io.containerd.grpc.v1.cri".registry]
  [plugins."io.containerd.grpc.v1.cri".registry.mirrors."docker.io"]
    endpoint = ["http://docker-registry.docker-registry.svc.cluster.local:5000"]
  [plugins."io.containerd.grpc.v1.cri".registry.configs."docker-registry.docker-registry.svc.cluster.local:5000".tls]
    insecure_skip_verify = true
```

Then restart containerd:
```bash
systemctl restart containerd
```

## Option B: DaemonSet + host mount (GitOps-friendly)

Create a DaemonSet in `applications/docker-registry/templates/` that:
1. Mounts `/etc/containerd/config.toml` from the host
2. Patches it to add the mirror endpoint
3. Restarts containerd

This is more complex but fully GitOps-managed.

## Option C: Config file per cluster bootstrap

If nodes are provisioned via PXE/Ansible/Terraform, include the mirror
config in the containerd config template at bootstrap time.

---

**Recommended for now**: Option A for initial setup, then migrate to
Option C when nodes are reprovisioned.
