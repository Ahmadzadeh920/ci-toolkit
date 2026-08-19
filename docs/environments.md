# GitHub Environments

## Overview

GitHub Environments provide a way to separate deployment configuration and protect deployment targets such as:

```text
development
staging
production
```

An environment can provide:

- environment-specific secrets
- environment-specific variables
- deployment protection rules
- required reviewers
- deployment restrictions

GitHub supports using environments with reusable workflows, but there are important limitations around environment secrets and `workflow_call`.

---

# Current `ci-toolkit` environment model

Of the three deployment strategies supported by this toolkit:

1. Docker Compose
2. Kubernetes / k3s
3. Helm

the current Docker Compose workflow explicitly supports a GitHub Environment.

It defines:

```yaml
inputs:
  environment:
    description: "Deployment environment"
    required: true
    type: string
```

and applies it to the deployment job:

```yaml
environment: ${{ inputs.environment }}
```

The Docker Compose workflow therefore allows the caller to select the GitHub Environment used by the deployment job.

---

# Docker Compose environments

The Docker Compose workflow requires:

```yaml
environment:
  required: true
```

and then uses:

```yaml
environment: ${{ inputs.environment }}
```

at the job level.

A consuming repository can therefore call it like:

```yaml
jobs:
  deploy:
    uses: Ahmadzadeh920/ci-toolkit/.github/workflows/reusable-deploy-docker-compose.yml@v1
    with:
      environment: production
      compose-file: docker-compose/docker-compose.yml
      image: ghcr.io/my-org/my-app
      image-tag: ${{ github.sha }}
      remote-directory: /opt/my-app
    secrets:
      ssh-host: ${{ secrets.SSH_HOST }}
      ssh-user: ${{ secrets.SSH_USER }}
      ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}
      DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
      ghcr-username: ${{ secrets.GHCR_USERNAME }}
      ghcr-token: ${{ secrets.GHCR_TOKEN }}
```

The deployment job will target the `production` environment.

---

# Recommended environment structure

For applications with multiple deployment stages, use:

```text
development
    |
    v
staging
    |
    v
production
```

For example:

```text
GitHub repository
│
├── development
│   ├── variables
│   └── secrets
│
├── staging
│   ├── variables
│   └── secrets
│
└── production
    ├── variables
    └── secrets
```

The exact environments should match the application's actual deployment model.

Do not create environments simply because they are listed here.

---

# Production protection

Production should normally be the most protected environment.

Recommended controls include:

- required reviewers
- restricted deployment branches/tags
- environment-specific secrets
- environment-specific variables
- deployment history/auditing

A typical promotion model is:

```text
Pull Request
     |
     v
Tests / Lint / Security
     |
     v
Development
     |
     v
Staging
     |
     | approval
     v
Production
```

This prevents a successful CI run from automatically becoming an unrestricted production deployment.

---

# Environment secrets

Deployment secrets should be stored in the appropriate GitHub Environment when they differ between deployment targets.

For example:

```text
production
├── SSH_HOST
├── SSH_USER
└── SSH_PRIVATE_KEY
```

while staging may have:

```text
staging
├── SSH_HOST
├── SSH_USER
└── SSH_PRIVATE_KEY
```

The values can be different even though the logical secret names are the same.

This allows the reusable workflow to remain unchanged.

---

# Important reusable-workflow limitation

A caller workflow cannot pass an environment secret through `workflow_call` simply by defining an `environment` input.

GitHub's reusable workflow model does not support an `environment` keyword under `on.workflow_call` secrets. If an environment is declared at the job level inside the called workflow, the environment's secret is used there rather than a caller-passed secret with the same name.

This distinction is important:

```text
Caller repository
       |
       | workflow_call
       |
       +---- with: environment
       |
       +---- secrets: ...
       |
       v
Reusable workflow
       |
       +---- job.environment
```

The `environment` input is simply a string until the called workflow assigns it to the job's `environment`.

---

# `ci-toolkit` Docker Compose behavior

The current Docker Compose workflow does this:

```yaml
environment: ${{ inputs.environment }}
```

at the deployment job level.

Therefore, if the caller supplies:

```yaml
with:
  environment: production
```

the called job targets the GitHub `production` Environment.

This makes the Docker Compose workflow the current toolkit workflow with explicit GitHub Environment integration.

---

# Kubernetes / k3s environments

The current Kubernetes workflow does **not** define an `environment` input.

Its deployment configuration is based on:

```text
runner
application
namespace
manifest
image-repository
image-tag
timeout
```

and it runs on:

```yaml
runs-on: ${{ inputs.runner }}
```

with `k3s` as the default runner label.

Therefore, environment separation for Kubernetes is currently handled through the consuming repository's configuration, runner availability, namespaces, manifests, and cluster configuration rather than through a GitHub Environment inside this reusable workflow.

A common pattern is:

```text
k3s cluster
│
├── development namespace
├── staging namespace
└── production namespace
```

For example:

```yaml
with:
  runner: k3s
  namespace: production
  manifest: k8s/
```

The `namespace` is a Kubernetes namespace, not a GitHub Environment.

These two concepts should not be confused.

---

# Helm environments

The current Helm workflow similarly does not define a GitHub Environment input.

It receives:

```text
runner
application
namespace
helm-chart
image-repository
image-tag
values-file
timeout
atomic
```

and performs:

```bash
helm upgrade --install
```

against the Kubernetes cluster available to the runner.

Environment separation can therefore be represented using different Kubernetes namespaces and/or Helm values.

For example:

```text
helm/
└── my-app/
    ├── Chart.yaml
    ├── values.yaml
    └── ...
```

with environment-specific values supplied by the consuming repository.

---

# GitHub Environment vs Kubernetes namespace

These are different concepts.

## GitHub Environment

Example:

```text
production
```

provides GitHub Actions deployment controls such as:

- approvals
- secrets
- variables
- deployment protection

## Kubernetes namespace

Example:

```text
production
```

provides Kubernetes resource isolation.

They can have the same name, but they serve different purposes.

For example:

```text
GitHub
└── Environment: production
       |
       v
GitHub Actions
       |
       v
k3s
└── Namespace: production
       |
       ├── Deployment
       ├── Service
       └── Ingress
```

A production deployment can use both.

---

# Environment variables

Reusable workflows should not assume that environment variables defined at the workflow level in the caller are automatically available in the called workflow.

GitHub documents that workflow-level `env` values do not propagate between caller and called reusable workflows. Variables intended to be shared across workflows can instead be managed through repository, organization, or environment-level variables and accessed through the `vars` context.

Prefer explicit workflow inputs for values that are part of the reusable workflow contract:

```yaml
with:
  namespace: production
  image-tag: ${{ github.sha }}
```

Use environment/repository variables for shared non-secret configuration where appropriate.

---

# Environment-specific deployment example

A caller repository could select a deployment environment explicitly:

```yaml
name: Production deployment

on:
  push:
    tags:
      - "v*"

jobs:
  deploy:
    uses: Ahmadzadeh920/ci-toolkit/.github/workflows/reusable-deploy-docker-compose.yml@v1

    with:
      environment: production
      compose-file: docker-compose/docker-compose.yml
      image: ghcr.io/my-org/my-app
      image-tag: ${{ github.sha }}
      remote-directory: /opt/my-app

    secrets:
      ssh-host: ${{ secrets.SSH_HOST }}
      ssh-user: ${{ secrets.SSH_USER }}
      ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}
      DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
      ghcr-username: ${{ secrets.GHCR_USERNAME }}
      ghcr-token: ${{ secrets.GHCR_TOKEN }}
```

The production Environment should then contain the production-specific configuration and protection rules.

---

# Recommended environment strategy

For a production application, the recommended conceptual model is:

```text
                     CI
                     |
          +----------+----------+
          |                     |
          v                     v
      Security               Tests
          |                     |
          +----------+----------+
                     |
                     v
                Development
                     |
                     v
                  Staging
                     |
                Approval
                     |
                     v
                Production
```

However, the exact promotion model is application-specific.

---

# Environment strategy for the three deployment options

## Docker Compose

Use GitHub Environments directly with the current reusable workflow.

```text
development
staging
production
```

The `environment` input selects the target GitHub Environment.

## Kubernetes / k3s

Use Kubernetes namespaces and runner/cluster configuration.

```text
development namespace
staging namespace
production namespace
```

The current workflow does not expose a GitHub Environment input.

## Helm

Use Helm values and Kubernetes namespaces.

```text
development values
staging values
production values
```

The current workflow does not expose a GitHub Environment input.

---

# Security recommendations

## 1. Protect production

Production should use appropriate approval and branch/tag restrictions.

## 2. Keep secrets environment-specific

Do not use the same production credential for staging unless there is a deliberate reason.

## 3. Use least privilege

A staging deployment credential should not automatically have production access.

## 4. Avoid putting secrets in variables

Use GitHub Secrets for sensitive values.

Use Variables for non-sensitive configuration.

## 5. Do not confuse environment names with infrastructure targets

For example:

```text
production
```

is not itself a server address, Kubernetes cluster, or namespace.

It is a GitHub deployment environment.

---

# Current status

The current `ci-toolkit` environment support is:

| Capability | Current status |
|---|---|
| Docker Compose `environment` input | Supported |
| Docker Compose job-level GitHub Environment | Supported |
| Kubernetes GitHub Environment input | Not currently implemented |
| Helm GitHub Environment input | Not currently implemented |
| Kubernetes namespaces | Supported |
| Helm namespaces | Supported |
| Environment-specific secrets | Supported through GitHub's environment model |
| Environment-specific variables | Supported through GitHub's environment model |
| Production approvals | Configured in consuming repository |
| OIDC-based environment authentication | Not currently implemented |

The Docker Compose workflow is the only current deployment workflow that explicitly binds the `environment` input to a GitHub Actions job environment.

---

# Future improvements

Potential future improvements to `ci-toolkit` include:

- adding an explicit `environment` input to Kubernetes deployment;
- adding an explicit `environment` input to Helm deployment;
- integrating OIDC with supported cloud providers;
- replacing long-lived deployment credentials with short-lived identity;
- adding stronger environment protection conventions;
- supporting GitHub Environment-based deployment approvals consistently across all three deployment strategies.

Any such changes should preserve the reusable workflow contract and be introduced with appropriate versioning.