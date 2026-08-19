# ci-toolkit

**Versioned, portable reusable GitHub Actions workflows for standardized CI/CD.**

`ci-toolkit` is a reusable GitHub Actions workflow library for centralizing CI/CD, testing, static analysis, security scanning, Docker image workflows, deployment, notifications, and repository synchronization.

Instead of duplicating similar GitHub Actions workflows across multiple repositories, application repositories can call the workflows from this repository using GitHub Actions `workflow_call`.

> **Application code, deployment configuration, infrastructure credentials, and secret values remain in the consuming repository. `ci-toolkit` provides the reusable CI/CD workflow contracts.**

---

## Why this exists?

CI/CD workflows are often copied from one repository to another. Over time, those copies become different:

- different tool versions
- different security settings
- different permissions
- different Docker configurations
- different deployment logic
- different notification mechanisms
- different secret requirements

Maintaining those duplicated workflows becomes increasingly difficult as the number of repositories grows.

`ci-toolkit` centralizes the reusable pipeline logic and exposes it through explicit:

- `inputs`
- `secrets`
- `outputs`
- permissions
- runner configuration
- deployment contracts

A consuming repository can therefore use a stable workflow such as:

```yaml
jobs:
  test:
    uses: Ahmadzadeh920/ci-toolkit/.github/workflows/reusable-test.yml@v1
```

instead of maintaining its own copy of the complete workflow.

The toolkit is designed to separate:

```text
Application repository
        |
        | application code
        | deployment configuration
        | secrets
        | environment configuration
        |
        v
+--------------------------------+
|          ci-toolkit            |
|                                |
| Test / Lint                    |
| CodeQL                         |
| SonarQube                      |
| Docker Build                   |
| Docker Push                    |
| Trivy                          |
| Notifications                  |
| Deployment                     |
| Repository Sync                |
+--------------------------------+
```

---

## Use cases

`ci-toolkit` is intended for repositories that want to standardize GitHub Actions without copying pipeline implementations between projects.

Typical use cases include:

- Multi-repository CI/CD standardization
- Python and general application testing
- Linting and test execution
- CodeQL static analysis
- SonarQube analysis and quality gates
- Docker image building
- Docker image publishing
- Trivy security scanning
- Slack, Microsoft Teams, and Discord notifications
- Docker Compose deployments
- Kubernetes/k3s deployments
- Helm deployments
- Repository mirroring or branch synchronization

The test workflow is configurable rather than being tied to one specific application structure, while Docker and deployment workflows expose repository-specific paths and configuration through inputs.

---

## Applications

The toolkit can be used by:

- Python applications
- Django applications
- FastAPI services
- backend services
- microservices
- Dockerized applications
- Kubernetes applications
- Helm-based applications
- Docker Compose applications
- internal tools
- repositories requiring CodeQL or Trivy
- repositories requiring SonarQube quality gates

The toolkit is not intended to own application-specific configuration.

The consuming repository remains responsible for its own:

- source code
- Dockerfiles
- Docker Compose files
- Kubernetes manifests
- Helm charts
- environment configuration
- GitHub Environments
- secrets
- infrastructure credentials

---

# Critical structural constraint

GitHub reusable workflows must physically exist under:

```text
.github/workflows/
```

in the source repository.

Therefore, this repository must keep reusable workflows here:

```text
ci-toolkit/
└── .github/
    └── workflows/
        └── reusable-test.yml
```

A consuming repository references them using:

```yaml
uses: Ahmadzadeh920/ci-toolkit/.github/workflows/reusable-test.yml@v1
```

Do **not** move reusable workflows to:

```text
workflows/
```

or:

```text
.github/reusable-workflows/
```

or another directory.

The reusable workflow files must remain under:

```text
.github/workflows/
```

GitHub resolves reusable workflows from that location.

---

# Repository structure

The current repository structure is:

```text
ci-toolkit/
│
├── .github/
│   └── workflows/
│       ├── caller-ci.yml
│       ├── reusable-codeql.yml
│       ├── reusable-deploy-docker-compose.yml
│       ├── reusable-deploy-helm.yml
│       ├── reusable-deploy-kubernetes.yml
│       ├── reusable-docker-build.yml
│       ├── reusable-docker-push.yml
│       ├── reusable-notification.yml
│       ├── reusable-sonarqube.yml
│       ├── reusable-sync.yml
│       ├── reusable-test.yml
│       └── reusable-trivy.yml
│
├── docs/
│   ├── migration-checklist.md
│   ├── permissions.md
│   ├── reusable-workflows.md
│   ├── secrets.md
│   └── variables.md
│
├── docker-compose/
│
├── helm/
│
├── k8s/
│
├── CHANGELOG.md
├── LICENSE.md
└── README.md
```

The repository currently contains 11 reusable workflows plus `caller-ci.yml`, which serves as a caller/example workflow.

### `docker-compose/`

Contains Docker Compose deployment/example configuration.

### `helm/`

Contains Helm-related example configuration.

### `k8s/`

Contains Kubernetes-related example configuration.

### `docs/`

Contains the configuration contracts and migration documentation for consuming repositories.

---

# Quick start

Create a workflow in your application repository:

```text
.github/workflows/ci.yml
```

Then reference the reusable workflows from `ci-toolkit`.

For example:

```yaml
name: CI/CD

on:
  push:
    branches:
      - main

  pull_request:

jobs:
  test:
    uses: Ahmadzadeh920/ci-toolkit/.github/workflows/reusable-test.yml@v1
    with:
      python-versions: '["3.11", "3.12"]'
      working-directory: services/api

  codeql:
    needs: test
    uses: Ahmadzadeh920/ci-toolkit/.github/workflows/reusable-codeql.yml@v1
    permissions:
      actions: read
      contents: read
      security-events: write
```

The complete workflow contract, including inputs, secrets, permissions, and outputs, is documented in:

[`docs/reusable-workflows.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/reusable-workflows.md).

### Recommended adoption sequence

1. Choose the reusable workflows required by your repository.
2. Pin them to a release tag.
3. Configure their required inputs.
4. Create only the required secrets.
5. Configure repository/environment variables where necessary.
6. Configure required GitHub Actions permissions.
7. Select one deployment strategy if deployment is required.
8. Test the pipeline in a non-production environment.
9. Promote the tested version to production.

The migration checklist documents this process.

---

# Deployment strategies

A consuming repository has **three deployment strategy options**:

```text
                    Application
                         |
                 Choose ONE strategy
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
   Docker Compose   Kubernetes / k3s    Helm
          |              |              |
          v              v              v
        SSH           kubectl           helm
          |              |              |
          v              v              v
    Remote host      Kubernetes        Kubernetes
                      cluster            cluster
```

## Important: choose exactly one

For a given application deployment, select exactly one of:

1. **Docker Compose**
2. **Kubernetes / k3s**
3. **Helm**

The toolkit does **not** provide a generic deployment dispatcher. The consuming repository directly calls the workflow corresponding to its infrastructure.

---

## Deployment option 1 — Docker Compose

Use Docker Compose when the application runs on a remote Docker host or VM.

Workflow:

```text
reusable-deploy-docker-compose.yml
```

The workflow connects to the remote host through SSH and runs Docker Compose. Its configurable inputs include:

```text
runner
environment
compose-file
image
image-tag
remote-directory
compose-service
timeout-minutes
```

and its deployment secrets are:

```text
ssh-host
ssh-user
ssh-private-key
```



Example:

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
      compose-service: api
    secrets:
      ssh-host: ${{ secrets.SSH_HOST }}
      ssh-user: ${{ secrets.SSH_USER }}
      ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}
```

The Compose file belongs to the consuming repository.

---

## Deployment option 2 — Kubernetes / k3s

Use the Kubernetes workflow when the application is deployed using Kubernetes manifests.

Workflow:

```text
reusable-deploy-kubernetes.yml
```

The workflow performs `kubectl apply` and waits for the application rollout.

Its main inputs include:

```text
runner
application
namespace
manifest
image-repository
image-tag
timeout
```

The default runner is:

```text
k3s
```

The workflow assumes that `kubectl` is already configured on the runner, for example through a self-hosted k3s runner with an appropriate local kubeconfig.

Example:

```yaml
jobs:
  deploy:
    uses: Ahmadzadeh920/ci-toolkit/.github/workflows/reusable-deploy-kubernetes.yml@v1
    with:
      runner: k3s
      application: my-app
      namespace: production
      manifest: k8s/
      image-repository: ghcr.io/my-org/my-app
      image-tag: ${{ github.sha }}
```

The consuming repository owns the Kubernetes manifests:

```text
my-app/
└── k8s/
    ├── deployment.yaml
    ├── service.yaml
    └── ingress.yaml
```

The toolkit does not assume that every application has the same Kubernetes directory.

---

## Deployment option 3 — Helm

Use Helm when the application is packaged as a Helm chart.

Workflow:

```text
reusable-deploy-helm.yml
```

The workflow performs:

```text
helm upgrade --install
```

with optional automatic rollback.

Its inputs include:

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

The default runner is also:

```text
k3s
```



Example:

```yaml
jobs:
  deploy:
    uses: Ahmadzadeh920/ci-toolkit/.github/workflows/reusable-deploy-helm.yml@v1
    with:
      runner: k3s
      application: my-app
      namespace: production
      helm-chart: helm/my-app
      values-file: helm/my-app/values.yaml
      image-repository: ghcr.io/my-org/my-app
      image-tag: ${{ github.sha }}
```

The consuming repository owns the Helm chart:

```text
my-app/
└── helm/
    └── my-app/
        ├── Chart.yaml
        ├── values.yaml
        └── templates/
```

---

# Workflow catalog

`ci-toolkit` currently provides **11 reusable `workflow_call` workflows**.

| Workflow | Purpose |
|---|---|
| `reusable-test.yml` | Install dependencies, lint, run tests, collect coverage, and upload artifacts |
| `reusable-codeql.yml` | GitHub CodeQL static analysis |
| `reusable-sonarqube.yml` | SonarQube analysis and quality gate |
| `reusable-docker-build.yml` | Build Docker images and optionally push/save them |
| `reusable-docker-push.yml` | Load a saved image artifact and push it |
| `reusable-trivy.yml` | Filesystem, image, configuration, or SBOM vulnerability scanning |
| `reusable-notification.yml` | Slack, Microsoft Teams, or Discord notifications |
| `reusable-deploy-docker-compose.yml` | Docker Compose deployment over SSH |
| `reusable-deploy-kubernetes.yml` | Kubernetes deployment using `kubectl` |
| `reusable-deploy-helm.yml` | Helm-based Kubernetes deployment |
| `reusable-sync.yml` | Synchronize a branch into another repository |

`caller-ci.yml` is present in `.github/workflows`, but it is a caller/example workflow and is not part of the 11 reusable workflow contracts.

For the complete contract of every workflow, including inputs, secrets, permissions, and outputs, see:

[`docs/reusable-workflows.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/reusable-workflows.md).

---

# Configuration reference

All configuration documentation is maintained under:

[`docs/`](https://github.com/Ahmadzadeh920/ci-toolkit/tree/main/docs)

## Reusable workflow contracts

[`docs/reusable-workflows.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/reusable-workflows.md)

Defines:

- workflow purposes
- inputs
- secrets
- permissions
- outputs
- deployment behavior



## Permissions

[`docs/permissions.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/permissions.md)

Documents the minimum GitHub Actions `GITHUB_TOKEN` permissions required by the workflows.

## Secrets

[`docs/secrets.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/secrets.md)

Documents:

- secret names
- which workflows use them
- their purpose
- secret-management considerations

Secret **values must never be committed** to the repository.

## Variables

[`docs/variables.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/variables.md)

Documents recommended non-sensitive repository and environment variables.

## Migration checklist

[`docs/migration-checklist.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/migration-checklist.md)

Provides the step-by-step process for adopting `ci-toolkit` in an existing repository.

The current checklist specifically covers selecting the required workflows, configuring inputs and secrets, permissions, runner configuration, and selecting exactly one deployment workflow.

---

# Configuration ownership

A central principle of this toolkit is:

> **Reusable workflow logic belongs in `ci-toolkit`; application-specific configuration belongs in the consuming repository.**

For example, `ci-toolkit` should not assume that every application has:

```text
services/api/
k8s/
helm/my-app/
docker-compose/docker-compose.yml
```

Instead, the consuming repository supplies its own paths.

### Kubernetes

```yaml
with:
  manifest: k8s/
```

### Helm

```yaml
with:
  helm-chart: helm/my-app
  values-file: helm/my-app/values.yaml
```

### Docker Compose

```yaml
with:
  compose-file: docker-compose/docker-compose.yml
```

This makes the workflows portable between repositories.

---

# Versioning

Production repositories should **not** consume workflows directly from `main`.

Use release tags such as:

```text
v1
v1.1.0
v1.2.0
```

Then reference a stable release:

```yaml
uses: Ahmadzadeh920/ci-toolkit/.github/workflows/reusable-test.yml@v1
```

## Major versions

Increment the major version for breaking contract changes such as:

- removing an input
- renaming an input
- removing a required secret
- renaming a secret
- removing an output
- changing workflow behavior in a way that requires caller changes

Example:

```text
v1 → v2
```

## Minor and patch versions

Use minor or patch releases for backward-compatible changes such as:

- adding optional inputs with defaults
- bug fixes
- documentation improvements
- internal workflow improvements that do not change the caller contract

The migration checklist also requires consuming repositories to pin workflow references to a release tag rather than `main`.

---

# Security notes

Security-sensitive configuration belongs in the consuming repository, not in `ci-toolkit`.

## Never commit secret values

Never commit:

- private keys
- passwords
- access tokens
- kubeconfigs
- SSH credentials
- webhook URLs
- registry credentials
- SonarQube tokens

The repository should document secret **names and purposes**, not secret values.

## Use least-privilege permissions

Grant only the permissions required by each workflow.

For example, CodeQL requires:

```yaml
permissions:
  actions: read
  contents: read
  security-events: write
```

Do not use:

```yaml
permissions: write-all
```

unless there is a specific and justified requirement.

## Protect deployment secrets

Use GitHub Actions secrets and, where appropriate, GitHub Environments for deployment credentials.

Production environments can be protected with:

- required reviewers
- environment-specific secrets
- deployment restrictions

## Self-hosted Kubernetes/k3s runners

Kubernetes and Helm workflows can run on a self-hosted runner labeled:

```text
k3s
```

The runner must have the required Kubernetes tooling and access to the target cluster.

The workflow itself should not contain cluster-specific credentials or hard-coded infrastructure addresses.

## Docker Compose SSH deployment

Docker Compose deployment requires SSH credentials supplied by the consuming repository:

```text
ssh-host
ssh-user
ssh-private-key
```

These values must be stored as GitHub Actions secrets and never committed to Git.

---

# Migrating an existing repo onto this toolkit

Use the complete migration checklist:

[`docs/migration-checklist.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/migration-checklist.md)

The migration process is:

1. Confirm that the repository can access `ci-toolkit`.
2. Pin workflow references to a release tag.
3. Identify the workflows actually required.
4. Configure all required `workflow_call` inputs.
5. Create only the required secrets.
6. Configure non-sensitive variables.
7. Configure GitHub Environments where required.
8. Select **exactly one deployment strategy**.
9. Keep the application's own manifest, Helm chart, or Compose file in the consuming repository.
10. Configure the correct self-hosted runner where required.
11. Configure the required GitHub Actions permissions.
12. Verify registry, SonarQube, deployment, and notification credentials as applicable.
13. Test in a non-production environment.
14. Promote the tested workflow version to production.

The repository's migration checklist explicitly recommends choosing one of:

```text
reusable-deploy-docker-compose.yml
reusable-deploy-kubernetes.yml
reusable-deploy-helm.yml
```

for deployment.

---

# Contributing

Contributions are welcome.

When adding or modifying a reusable workflow:

1. Keep reusable workflows under `.github/workflows/`.
2. Keep workflows generic and repository-independent.
3. Avoid hard-coded application paths.
4. Avoid hard-coded infrastructure addresses.
5. Never commit secrets.
6. Define explicit `workflow_call` inputs.
7. Define required secrets clearly.
8. Document required permissions.
9. Update `docs/reusable-workflows.md` when the workflow contract changes.
10. Update the relevant documentation.
11. Update `CHANGELOG.md`.
12. Test the workflow before creating a release.

## Breaking changes

Changes such as these are breaking changes:

- renaming an input
- removing an input
- renaming a secret
- removing a required secret
- removing an output
- changing a required workflow behavior

Breaking changes should receive a new major version.

Backward-compatible changes should use a minor or patch release.

---

# License

This project is licensed under the [MIT License](LICENSE.md).

---

# Documentation

| Resource | Description |
|---|---|
| [`docs/`](https://github.com/Ahmadzadeh920/ci-toolkit/tree/main/docs) | Complete configuration documentation |
| [`reusable-workflows.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/reusable-workflows.md) | Complete reusable workflow contracts |
| [`permissions.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/permissions.md) | GitHub Actions permissions |
| [`secrets.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/secrets.md) | Secret inventory and requirements |
| [`variables.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/variables.md) | Repository/environment variables |
| [`migration-checklist.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/migration-checklist.md) | Migration procedure for existing repositories |
| [`k8s/`](https://github.com/Ahmadzadeh920/ci-toolkit/tree/main/k8s) | Kubernetes example configuration |
| [`helm/`](https://github.com/Ahmadzadeh920/ci-toolkit/tree/main/helm) | Helm example configuration |
| [`docker-compose/`](https://github.com/Ahmadzadeh920/ci-toolkit/tree/main/docker-compose) | Docker Compose example configuration |

---

# Summary

`ci-toolkit` provides reusable GitHub Actions workflow contracts while keeping application-specific configuration in the consuming repository.

The key principles are:

- **Reusable workflows live under `.github/workflows/`.**
- **There are currently 11 reusable workflow contracts.**
- **`caller-ci.yml` is an example caller, not a reusable workflow.**
- **Secrets remain in the consuming repository.**
- **Application deployment configuration remains in the consuming repository.**
- **Production workflows should use release tags rather than `main`.**
- **GitHub Actions permissions should follow least privilege.**
- **Kubernetes/k3s deployments use a runner with Kubernetes access already configured.**
- **A repository should select exactly one deployment strategy:**
  - **Docker Compose**
  - **Kubernetes / k3s**
  - **Helm**
- **There is no generic deployment dispatcher.**
- **The toolkit provides pipeline logic; the application repository owns its application and infrastructure configuration.**

Start with the [migration checklist](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/migration-checklist.md), then use the [reusable workflow contracts](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/reusable-workflows.md) to configure the workflows required by your repository.