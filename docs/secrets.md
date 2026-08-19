# GitHub Actions Secrets Inventory

This file records **secret names and their purpose only**. It intentionally
does not contain secret values.

## Required/known secrets

| Secret | Workflow | Required | Purpose | Recommended scope | OIDC replacement |
|---|---|---:|---|---|---|
| `sonar-token` | `reusable-sonarqube.yml` | Yes | SonarQube authentication token | Environment or repository | No |
| `sonar-host-url` | `reusable-sonarqube.yml` | Yes | SonarQube server URL | Repository/environment; should be a variable, not a secret | No |
| `DEPLOY_KEY` | `reusable-sonarqube.yml` | Yes in current workflow | SSH key supplied to checkout | Repository/environment | No |
| `registry-password` | `reusable-docker-build.yml` | Yes | Container registry password/token | Repository/environment | Sometimes — yes for cloud registries (ECR/ACR/Artifact Registry) |
| `registry-password` | `reusable-docker-push.yml` | Yes | Container registry password/token | Repository/environment | Sometimes |
| `ssh-host` | `reusable-deploy-docker-compose.yml` | Yes | Remote Docker Compose host | Variable preferred; secret only if policy requires | No |
| `ssh-user` | `reusable-deploy-docker-compose.yml` | Yes | Remote SSH username | Variable preferred | No |
| `ssh-private-key` | `reusable-deploy-docker-compose.yml` | Yes | SSH private key for remote Docker Compose deployment | Environment | No — plain SSH has no OIDC verifier |
| `DEPLOY_KEY` | `reusable-deploy-kubernetes.yml` | Yes | SSH key passed to `actions/checkout` for manifest access | Repository/environment | No |
| `DEPLOY_KEY` | `reusable-deploy-helm.yml` | Yes | SSH key passed to `actions/checkout` for chart access | Repository/environment | No |
| `slack-webhook` | `reusable-notification.yml` | Optional | Slack notification webhook | Environment/repository | No |
| `teams-webhook` | `reusable-notification.yml` | Optional | Microsoft Teams webhook | Environment/repository | No |
| `discord-webhook` | `reusable-notification.yml` | Optional | Discord notification webhook | Environment/repository | No |
| `target-token` | `reusable-sync.yml` | Yes | Token used to push to target repository | Environment/repository | Prefer GitHub App/short-lived auth where practical |

## Important observations

### 1. `sonar-host-url` should be a variable, not a secret

The URL itself is not sensitive. A future revision should move it to
`vars.SONAR_HOST_URL` and keep only `secrets.SONAR_TOKEN` as the credential.

### 2. Two workflows reuse `DEPLOY_KEY` for two different purposes

`reusable-deploy-kubernetes.yml` and `reusable-deploy-helm.yml` both require
`DEPLOY_KEY`, but neither uses it to authenticate to Kubernetes itself —
it's an SSH key passed to `actions/checkout` so the workflow can clone the
manifest/chart. If that manifest lives in the *same* repository the
workflow is already running in, `actions/checkout` can normally use the
ambient `GITHUB_TOKEN` instead, and `DEPLOY_KEY` may be unnecessary. Confirm
this before committing to the requirement for `v1`.

### 3. GHCR

Prefer the automatically provided `GITHUB_TOKEN` for GHCR pushes instead of
a long-lived personal access token, where the workflow's `registry-password`
input accepts it.

### 4. Kubernetes / Helm credentials

Neither `reusable-deploy-kubernetes.yml` nor `reusable-deploy-helm.yml`
accepts a `kubeconfig` secret directly — both assume `kubectl`/`helm` are
already authenticated on the runner (e.g. a self-hosted `k3s` runner with a
local kubeconfig). If you move to a cloud-managed Kubernetes service,
you'll likely add an explicit kubeconfig or OIDC-based auth step — update
this table when that happens.

### 5. SSH (Docker Compose deployment)

OIDC does not replace `ssh-private-key`. A plain SSH-reachable server has no
identity system capable of verifying a GitHub OIDC token. Keep this as a
stored secret unless the deployment architecture changes (e.g. moving to a
cloud provider with an SSM/Session-Manager-style access model).

## Secret naming recommendation

Prefer consistent uppercase names for infrastructure-specific secrets in
future revisions:

```text
SONAR_TOKEN
REGISTRY_PASSWORD
SSH_PRIVATE_KEY
DEPLOY_KEY
DISCORD_WEBHOOK
SLACK_WEBHOOK
TEAMS_WEBHOOK
TARGET_REPOSITORY_TOKEN
```

Renaming secrets in an already-tagged reusable workflow is a breaking
contract change — do this before cutting `v1`, not after.

## What must never be stored here

- actual token values
- private keys
- kubeconfig contents
- passwords
- webhook URLs containing credentials
- PATs
- cloud access keys
