# GitHub Actions Permissions Inventory

Permissions are part of the reusable workflow contract and must be
documented alongside secrets and inputs.

| Workflow | Permissions |
|---|---|
| `reusable-test.yml` | `contents: read` |
| `reusable-codeql.yml` | `actions: read`, `contents: read`, `security-events: write` |
| `reusable-sonarqube.yml` | `contents: read`, `actions: read` |
| `reusable-docker-build.yml` | `contents: read`, `packages: write` |
| `reusable-docker-push.yml` | `contents: read`, `packages: write` |
| `reusable-trivy.yml` | `contents: read`, `security-events: write` |
| `reusable-notification.yml` | `contents: read` |
| `reusable-deploy-docker-compose.yml` | Not explicitly declared in the workflow — the caller should grant `contents: read` |
| `reusable-deploy-kubernetes.yml` | Not explicitly declared — the caller should grant `contents: read` |
| `reusable-deploy-helm.yml` | Not explicitly declared — the caller should grant `contents: read` |
| `reusable-sync.yml` | `contents: read` |

## Recommendation for v1

Add explicit `permissions:` blocks to the three deployment workflows before
tagging `v1`. A reusable workflow that doesn't declare permissions inherits
whatever the caller grants, which makes the contract implicit rather than
documented — exactly the kind of inconsistency worth fixing before freezing
a public interface.

## Security rule

Use the smallest permission set required by each reusable workflow. Do not
add:

```yaml
permissions: write-all
```

or:

```yaml
permissions:
  contents: write
```

unless the workflow genuinely needs it.

## OIDC

If a future reusable workflow authenticates to a cloud provider using
GitHub OIDC (for example, pushing to a cloud container registry or
deploying to a cloud-managed Kubernetes cluster), that specific job should
additionally request:

```yaml
id-token: write
```

Keep this permission limited to the job that performs the OIDC exchange —
not the whole workflow.
