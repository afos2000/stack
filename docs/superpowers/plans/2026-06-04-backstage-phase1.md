# Backstage Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deploy Backstage (AndresKube Homelab Services) with PostgreSQL via managed CNPG, Keycloak SSO, and Cloudflare Tunnel ingress.

**Architecture:** Helm chart wrapper following the existing pattern (`applications/*`). PostgreSQL via `managed.databases` on the existing `keycloak-db` CNPG cluster. Auth via Keycloak `backstage` realm. Ingress via Cloudflare Tunnel (no Ingress resource). Secrets via Vault → External Secrets → K8s Secrets.

**Tech Stack:** Backstage (Helm chart 2.8.1), CloudNative PG 1.29.1, Keycloak 26.5.6, External Secrets, Reflector, Cloudflare Tunnel

---

### Task 1: Update CNPG Cluster — add managed databases

**Files:**
- Modify: `applications/postgres/cluster.yaml`

- [ ] **Step 1: Add managed databases and roles to the Cluster spec**

Edit `applications/postgres/cluster.yaml` to add `managed.databases` and `managed.roles`:

```yaml
spec:
  # ... existing config (instances, storage, bootstrap, resources, etc.) ...

  managed:
    databases:
      - name: backstage
        owner: backstage
    roles:
      - name: backstage
        login: true
        passwordSecret:
          name: backstage-db-app
```

This tells CNPG to ensure a database `backstage` exists with owner `backstage`, and auto-generate a Secret `backstage-db-app` in the `postgres` namespace with credentials.

- [ ] **Step 2: Commit**

```bash
git add applications/postgres/cluster.yaml
git commit -m "feat: add managed database backstage to CNPG cluster"
```

---

### Task 2: Create Backstage Helm chart wrapper

**Files:**
- Create: `applications/backstage/Chart.yaml`
- Create: `applications/backstage/README.md`

- [ ] **Step 1: Create Chart.yaml**

```yaml
apiVersion: v2
name: backstage
version: 0.1.0
dependencies:
  - name: backstage
    version: 2.8.1
    repository: https://backstage.github.io/charts
```

- [ ] **Step 2: Create README.md**

```markdown
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
```

- [ ] **Step 3: Commit**

```bash
git add applications/backstage/Chart.yaml applications/backstage/README.md
git commit -m "feat: add Backstage Helm chart wrapper"
```

---

### Task 3: Create Backstage values.yaml with app-config

**Files:**
- Create: `applications/backstage/values.yaml`

- [ ] **Step 1: Create values.yaml**

```yaml
backstage:
  replicas: 1

  image:
    registry: ghcr.io
    repository: backstage/backstage
    tag: 1.36.1
    pullPolicy: IfNotPresent

  service:
    type: ClusterIP
    ports:
      backend: 7007

  appConfig:
    app:
      title: AndresKube Homelab Services
      baseUrl: https://platform-apps.andreskube.uk

    backend:
      baseUrl: https://platform-apps.andreskube.uk
      listen:
        port: 7007
      database:
        client: pg
        connection:
          host: keycloak-db-rw.postgres.svc
          port: 5432
          user: backstage
          password: ${BACKSTAGE_DB_PASSWORD}
      cors:
        origin: https://platform-apps.andreskube.uk

    auth:
      environment: production
      providers:
        oidc:
          development:
            metadataUrl: http://keycloak.keycloak.svc.cluster.local:8080/realms/backstage/.well-known/openid-configuration
            clientId: backstage
            clientSecret: ${KEYCLOAK_CLIENT_SECRET}
            callbackUrl: https://platform-apps.andreskube.uk/api/auth/oidc/handler/frame

    catalog:
      locations: []
      rules:
        - allow:
          - Component
          - API
          - Group
          - User
          - Resource
          - System
          - Location
          - Template

  extraEnvVars:
    - name: BACKSTAGE_DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: backstage-db-backstage
          key: password
    - name: KEYCLOAK_CLIENT_SECRET
      valueFrom:
        secretKeyRef:
          name: backstage-keycloak-secret
          key: client-secret
    - name: AUTH_SECRET
      valueFrom:
        secretKeyRef:
          name: backstage-auth-secret
          key: session-secret

  podSecurityContext:
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 1000
    fsGroup: 1000

  containerSecurityContext:
    allowPrivilegeEscalation: false
    runAsNonRoot: true
    runAsUser: 1000
    capabilities:
      drop:
        - ALL
    readOnlyRootFilesystem: false

  resources:
    requests:
      cpu: 250m
      memory: 512Mi
    limits:
      cpu: 1
      memory: 1Gi

postgresql:
  enabled: false

ingress:
  enabled: false
```

- [ ] **Step 2: Commit**

```bash
git add applications/backstage/values.yaml
git commit -m "feat: add Backstage values with app-config, auth, security"
```

---

### Task 4: Create Backstage templates — reflector and secrets

**Files:**
- Create: `applications/backstage/templates/db-secret-reflect.yaml`
- Create: `applications/backstage/templates/backstage-secrets.yaml`

- [ ] **Step 1: Create db-secret-reflect.yaml**

Mirrors the auto-generated CNPG credentials from `postgres` namespace into the `backstage` namespace.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: backstage-db-backstage
  namespace: backstage
  annotations:
    reflector.v1.k8s.emberstack.com/reflects: "postgres/backstage-db-app"
type: Opaque
```

- [ ] **Step 2: Create backstage-secrets.yaml**

ExternalSecrets for the session secret and Keycloak client secret — both stored in Vault.

```yaml
apiVersion: external-secrets.io/v1
kind: ExternalSecret
metadata:
  name: backstage-auth-secret
  namespace: backstage
spec:
  refreshInterval: "1h"
  secretStoreRef:
    name: vault-store
    kind: ClusterSecretStore
  target:
    name: backstage-auth-secret
    creationPolicy: Owner
    deletionPolicy: Retain
  data:
    - secretKey: session-secret
      remoteRef:
        conversionStrategy: Default
        decodingStrategy: None
        key: secrets/data/backstage
        metadataPolicy: None
        nullBytePolicy: Ignore
        property: session-secret
---
apiVersion: external-secrets.io/v1
kind: ExternalSecret
metadata:
  name: keycloak-backstage
  namespace: backstage
spec:
  refreshInterval: "1h"
  secretStoreRef:
    name: vault-store
    kind: ClusterSecretStore
  target:
    name: backstage-keycloak-secret
    creationPolicy: Owner
    deletionPolicy: Retain
  data:
    - secretKey: client-secret
      remoteRef:
        conversionStrategy: Default
        decodingStrategy: None
        key: secrets/data/keycloak-backstage-client
        metadataPolicy: None
        nullBytePolicy: Ignore
        property: client-secret
```

- [ ] **Step 3: Commit**

```bash
git add applications/backstage/templates/db-secret-reflect.yaml applications/backstage/templates/backstage-secrets.yaml
git commit -m "feat: add Backstage reflector and ExternalSecrets"
```

---

### Task 5: Create Keycloak backstage realm ConfigMap

**Files:**
- Create: `applications/keycloak/templates/realm-backstage-configmap.yaml`
- Modify: `applications/keycloak/values.yaml`

- [ ] **Step 1: Create realm-backstage-configmap.yaml**

Keycloak realm definition for the `backstage` realm. This goes in `applications/keycloak/templates/` because Keycloak pods need to read this ConfigMap.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: keycloak-realm-backstage
  namespace: keycloak
  labels:
    app: keycloak
data:
  realm-backstage.json: |
    {
      "realm": "backstage",
      "enabled": true,
      "displayName": "Backstage",
      "registrationAllowed": false,
      "clients": [
        {
          "clientId": "backstage",
          "enabled": true,
          "protocol": "openid-connect",
          "clientAuthenticatorType": "client-secret",
          "standardFlowEnabled": true,
          "redirectUris": [
            "https://platform-apps.andreskube.uk/api/auth/oidc/handler/frame"
          ],
          "webOrigins": ["+"],
          "protocolMappers": [
            {
              "name": "realm-roles",
              "protocol": "openid-connect",
              "protocolMapper": "oidc-usermodel-realm-role-mapper",
              "config": {
                "multivalued": "true",
                "id.token.claim": "true",
                "access.token.claim": "true",
                "claim.name": "groups",
                "userinfo.token.claim": "true"
              }
            }
          ]
        }
      ],
      "roles": {
        "realm": [
          {
            "name": "backstage-admin"
          },
          {
            "name": "backstage-user"
          }
        ]
      }
    }
```

This realm needs to be imported into Keycloak. It will be done via the existing post-start hook pattern — update Keycloak's values to also import this realm.

- [ ] **Step 2: Update Keycloak values to import backstage realm**

Edit `applications/keycloak/values.yaml` to add the backstage realm volume and mount, and update the post-start hook.

Under `extraVolumes`, add the backstage realm ConfigMap:
```yaml
extraVolumes: |
    - name: realm-import
      configMap:
        name: keycloak-realm-argocd
    - name: realm-import-backstage
      configMap:
        name: keycloak-realm-backstage
```

Under `extraVolumeMounts`, add the backstage realm mount:
```yaml
extraVolumeMounts: |
    - name: realm-import
      mountPath: /opt/keycloak/data/import/
    - name: realm-import-backstage
      mountPath: /opt/keycloak/data/import-backstage/
```

Update the post-start hook to also import the backstage realm:
```yaml
lifecycleHooks: |
    postStart:
      exec:
        command:
          - /bin/bash
          - -c
          - |
            sleep 15
            /opt/keycloak/bin/kcadm.sh config credentials --server http://localhost:8080 --realm master --user "${KC_BOOTSTRAP_ADMIN_USERNAME}" --password "${KC_BOOTSTRAP_ADMIN_PASSWORD}" 2>/dev/null
            /opt/keycloak/bin/kcadm.sh update realms/argocd -f /opt/keycloak/data/import/realm-argocd.json 2>/dev/null || true
            /opt/keycloak/bin/kcadm.sh create realms -f /opt/keycloak/data/import-backstage/realm-backstage.json 2>/dev/null || true
```

- [ ] **Step 3: Commit**

```bash
git add applications/keycloak/templates/realm-backstage-configmap.yaml applications/keycloak/values.yaml
git commit -m "feat: add Keycloak backstage realm ConfigMap and import"
```

---

### Task 6: Add Vault secrets for Backstage

**Environment:** Run on any node with `vault` CLI and VAULT_ADDR configured.

- [ ] **Step 1: Add Backstage session secret to Vault**

```bash
vault kv put secrets/backstage session-secret="$(openssl rand -base64 32)"
```

- [ ] **Step 2: Generate and store Keycloak client secret for Backstage**

First, generate a secret:
```bash
BACKSTAGE_CLIENT_SECRET=$(openssl rand -base64 32)
vault kv put secrets/keycloak-backstage-client client-secret="$BACKSTAGE_CLIENT_SECRET"
```

Note: The same secret needs to be used when creating the `backstage` client in Keycloak's realm JSON. Since the realm JSON in the ConfigMap uses `clientAuthenticatorType: client-secret`, Keycloak will auto-generate a client secret. We'll need to update the Keycloak client secret after realm creation. This will be handled by the access management repo's Job in a later phase.

- [ ] **Step 3: Verify secrets are stored**

```bash
vault kv get secrets/backstage
vault kv get secrets/keycloak-backstage-client
```

---

### Task 7: Create Backstage access ArgoCD Application

**Files:**
- Create: `applications/backstage-access/application.yaml`

- [ ] **Step 1: Create the ArgoCD Application for the access repo**

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: backstage-access
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/afos2000/backstage-homelab-access.git
    targetRevision: HEAD
    path: chart
    helm:
      valueFiles:
        - ../users.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: backstage
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

Note: This Application references a repo that doesn't exist yet. It can be created after the repo is set up.

- [ ] **Step 2: Commit**

```bash
git add applications/backstage-access/application.yaml
git commit -m "feat: add Backstage access ArgoCD Application"
```

---

### Task 8: Create backstage-homelab-access repo

This creates the initial structure in the new repo.

- [ ] **Step 1: Create repo and initial structure**

```bash
# Outside this repo — create on GitHub first
gh repo create afos2000/backstage-homelab-access --private --clone

# Create chart directory
mkdir -p chart/templates
```

- [ ] **Step 2: Create Chart.yaml**

```yaml
apiVersion: v2
name: backstage-access
version: 0.1.0
```

- [ ] **Step 3: Create users.yaml**

```yaml
users: []
```

(Empty by default — users are added via PRs.)

- [ ] **Step 4: Create chart/templates/job.yaml**

A Job that runs `kcadm.sh` to manage Keycloak users in the `backstage` realm.

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: backstage-sync-users
  namespace: backstage
spec:
  template:
    spec:
      containers:
        - name: kcadm
          image: quay.io/keycloak/keycloak:26.5.6
          command:
            - /bin/bash
            - -c
            - |
              /opt/keycloak/bin/kcadm.sh config credentials \
                --server http://keycloak.keycloak.svc.cluster.local:8080 \
                --realm master \
                --user admin \
                --password "$(cat /etc/keycloak-admin/password)" \
                --client admin-cli

              for user in "${USERS[@]}"; do
                IFS=':' read -r username role <<< "$user"
                # Check if user exists
                existing=$(/opt/keycloak/bin/kcadm.sh get users -r backstage -q username="$username" 2>/dev/null)
                if [ "$existing" = "[]" ]; then
                  # Create user with temp password
                  password=$(openssl rand -base64 12)
                  /opt/keycloak/bin/kcadm.sh create users -r backstage \
                    -s username="$username" \
                    -s enabled=true \
                    -s "credentials=[{\"type\":\"password\",\"value\":\"$password\",\"temporary\":true}]" \
                    -s "requiredActions=[\"UPDATE_PASSWORD\"]"
                  # Assign role
                  /opt/keycloak/bin/kcadm.sh add-roles -r backstage \
                    --uusername "$username" \
                    --rolename "$role"
                  echo "Created user $username with role $role"
                else
                  echo "User $username already exists, skipping"
                fi
              done
          env:
            - name: USERS
              valueFrom:
                configMapKeyRef:
                  name: backstage-users
                  key: users
            - name: ADMIN_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: keycloak-admin-password
                  key: password
          volumeMounts:
            - name: admin-password
              mountPath: /etc/keycloak-admin
              readOnly: true
      volumes:
        - name: admin-password
          secret:
            secretName: keycloak-admin
      restartPolicy: Never
  backoffLimit: 3
```

- [ ] **Step 5: Create chart/templates/configmap.yaml**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: backstage-users
  namespace: backstage
data:
  users: |-
{{- range .Values.users }}
    {{ .name }}:{{ .role }}
{{- end }}
```

- [ ] **Step 6: Create chart/templates/admin-password-secret.yaml**

```yaml
apiVersion: external-secrets.io/v1
kind: ExternalSecret
metadata:
  name: keycloak-admin-password
  namespace: backstage
spec:
  refreshInterval: "1h"
  secretStoreRef:
    name: vault-store
    kind: ClusterSecretStore
  target:
    name: keycloak-admin
    creationPolicy: Owner
    deletionPolicy: Retain
  data:
    - secretKey: password
      remoteRef:
        conversionStrategy: Default
        decodingStrategy: None
        key: secrets/data/keycloak
        metadataPolicy: None
        nullBytePolicy: Ignore
        property: admin-pw
```

---

### Task 9: Commit and push the main repo

- [ ] **Step 1: Commit all remaining changes**

```bash
git add -A
git commit -m "feat: deploy Backstage Phase 1 — chart, config, realm, secrets"
git push
```
