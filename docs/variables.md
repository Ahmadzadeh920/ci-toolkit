# GitHub Actions Variables Inventory

This document records non-sensitive configuration needed by the reusable
workflows.

## Recommended variables

| Variable | Current source/usage | Purpose | Recommended scope |
|---|---|---|---|
| `SONAR_HOST_URL` | Currently passed as `secrets.sonar-host-url` — should move here | SonarQube URL | Repository or environment |
| `REGISTRY` | `reusable-docker-build.yml` / `reusable-docker-push.yml` input, defaults to `ghcr.io` | Container registry | Repository/org variable if shared |
| `REGISTRY_USERNAME` | Workflow input | Registry owner/user | Repository/org variable |
| `K8S_NAMESPACE` | `reusable-deploy-kubernetes.yml` / `reusable-deploy-helm.yml` `namespace` input | Kubernetes namespace | Environment |
| `K8S_RUNNER` | Deployment input, default `k3s` | Self-hosted runner label | Repository/environment |
| `DEPLOYMENT_ENVIRONMENT` | `reusable-deploy-docker-compose.yml` `environment` input | GitHub environment name | Environment |
| `REMOTE_DIRECTORY` | `reusable-deploy-docker-compose.yml` input | Remote deployment directory | Environment |
| `COMPOSE_FILE` | `reusable-deploy-docker-compose.yml` input | Compose file path | Repository/environment |
| `HELM_RELEASE` | `reusable-deploy-helm.yml` `application` input | Helm release name | Environment |
| `HELM_CHART` | `reusable-deploy-helm.yml` `helm-chart` input | Helm chart path | Repository |
| `IMAGE_NAME` | `reusable-docker-build.yml` input | Container image name | Repository |
| `IMAGE_TAG` | Docker/deploy workflow inputs | Image tag | Workflow input (typically `${{ github.sha }}`) |
| `SONAR_PROJECT_BASE_DIR` | `reusable-sonarqube.yml` input | Sonar analysis directory | Repository |
| `NOTIFICATION_CHANNEL` | `reusable-notification.yml` input | slack / teams / discord | Environment |

## Current workflow inputs are preferred over global variables

Most reusable workflows already expose explicit `workflow_call.inputs`.
That's preferable to putting everything into `vars`. Use variables for
stable infrastructure configuration and inputs for values specific to a
particular invocation.

## Example configuration separation

Sensitive:

```text
secrets.SONAR_TOKEN
secrets.SSH_PRIVATE_KEY
secrets.DEPLOY_KEY
```

Non-sensitive:

```text
vars.SONAR_HOST_URL
vars.REGISTRY
vars.REGISTRY_USERNAME
vars.K8S_NAMESPACE
vars.REMOTE_DIRECTORY
```

Workflow-specific:

```text
with:
  image-name: my-app
  image-tag: ${{ github.sha }}
  namespace: my-namespace
```
