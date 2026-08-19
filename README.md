# ci-toolkit

**Reusable, versioned GitHub Actions workflows for standardized CI/CD across multiple repositories.**

`ci-toolkit` is a portable library of reusable GitHub Actions workflows designed to centralize common CI/CD, security, container, deployment, notification, and repository synchronization logic.

Instead of copying and maintaining similar GitHub Actions YAML files in every application repository, consuming repositories can call the workflows from this repository through GitHub Actions `workflow_call`.

The toolkit is designed to keep **application code, deployment configuration, infrastructure credentials, and secrets in the consuming repository**, while this repository provides the reusable CI/CD workflow contracts.

---

## Why this exists?

Maintaining CI/CD pipelines independently in every repository leads to duplicated YAML, inconsistent security settings, different tool versions, and difficult maintenance.

For example, without a shared toolkit, several repositories may each contain their own:

- Python testing and linting workflow
- CodeQL workflow
- SonarQube workflow
- Docker build workflow
- Docker registry authentication
- Trivy security scan
- Deployment workflow
- Notification workflow
- Repository synchronization workflow

Over time, those workflows tend to diverge.

`ci-toolkit` centralizes this logic into reusable workflows with explicit:

- `inputs`
- `secrets`
- `outputs`
- permissions
- runner configuration
- deployment contracts

A consuming repository only needs to provide its repository-specific configuration.

The result is:

```text
Application repositories
        |
        | workflow_call
        v
+----------------------+
|      ci-toolkit      |
|                      |
| Test / Lint          |
| CodeQL               |
| SonarQube            |
| Docker Build         |
| Docker Push          |
| Trivy                |
| Notifications        |
| Deployment           |
| Repository Sync      |
+----------------------+
```

This repository was extracted from the CI/CD architecture originally developed for `auth-gateway-platform`.

---

## Use cases

`ci-toolkit` can be used for:

### Multi-repository CI/CD standardization

Use the same testing, linting, static-analysis, security-scanning, and container workflows across multiple repositories.

### Python and application testing

The reusable test workflow supports configurable dependency installation, linting, testing, coverage collection, and artifact upload.

### Static analysis

Integrate GitHub CodeQL consistently across repositories.

### SonarQube quality analysis

Run SonarQube scans and optionally enforce quality gates using a shared workflow.

### Container pipelines

Build Docker images consistently and optionally:

- load them locally
- save them as artifacts
- push them to an OCI registry
- reuse the image in later jobs

### Container security

Use Trivy for:

- filesystem scanning
- image scanning
- configuration scanning
- SBOM scanning

### Deployment standardization

Deploy applications using one of three supported deployment strategies:

1. **Docker Compose**
2. **Kubernetes / k3s**
3. **Helm**

### Notifications

Send pipeline notifications to:

- Slack
- Microsoft Teams
- Discord

### Repository synchronization

Synchronize branches or repositories using the reusable repository-sync workflow.

---

# Applications

This toolkit is intended for repositories such as:

- Python applications
- Django applications
- FastAPI services
- backend microservices
- Dockerized applications
- Kubernetes applications
- Helm-based applications
- applications deployed with Docker Compose
- internal tools
- services requiring standardized security scanning
- repositories using GitHub Actions as their CI/CD platform

The toolkit is intentionally not tied to one application.

A consuming repository owns its own:

- source code
- Dockerfile
- Docker Compose file
- Kubernetes manifests
- Helm chart
- environment configuration
- secrets
- infrastructure-specific configuration

`ci-toolkit` owns the reusable pipeline logic.

---

# Critical structural constraint

GitHub reusable workflows **must physically exist under `.github/workflows/` in the source repository**.

Therefore, this structure is mandatory:

```text
ci-toolkit/
└── .github/
    └── workflows/
        └── reusable-test.yml
```

A consuming repository references the workflow like this:

```yaml
jobs:
  test:
    uses: Ahmadzadeh920/ci-toolkit/.github/workflows/reusable-test.yml@v1
```

Do **not** move reusable workflows into:

```text
ci-toolkit/workflows/
```

or:

```text
ci-toolkit/.github/reusable-workflows/
```

The reusable workflow files must remain directly under:

```text
.github/workflows/
```

This is a critical repository structure requirement for GitHub Actions reusable workflows.

---

# Repository structure

The current repository is organized around reusable workflows, documentation, and deployment examples:

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
│   ├── README.md
│   ├── reusable-workflows.md
│   ├── permissions.md
│   ├── secrets.md
│   ├── variables.md
│   ├── environments.md
│   ├── oidc.md
│   └── migration-checklist.md
│
├── helm/
│   ├── Chart.yaml
│   ├── deployment.yaml
│   └── values.yaml
│
├── k8s/
│   ├── deployment.yaml
│   └── rbac.yaml
│
├── docker-compose/
│   └── docker-compose.yml
│
├── CHANGELOG.md
├── LICENSE.md
└── README.md
```

The repository currently contains Kubernetes examples under `k8s/`, a Helm example under `helm/`, and a Docker Compose example under `docker-compose/`.

### Important distinction

The deployment configuration under:

```text
helm/
k8s/
docker-compose/
```

is **example/configuration material**.

A consuming repository should normally keep its own deployment configuration.

For example:

```text
my-application/
├── .github/
│   └── workflows/
│       └── ci.yml
├── helm/
│   └── my-application/
├── k8s/
└── docker-compose/
```

The reusable workflow receives the appropriate path through its `inputs`.

---

# Deployment strategies

One of the most important design decisions when adopting `ci-toolkit` is selecting the deployment strategy.

There are **three supported deployment strategies**:

```text
                    Application
                         |
             Choose ONE deployment strategy
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
    Docker Compose   Kubernetes/k3s     Helm
       SSH              kubectl         helm
          |              |              |
          v              v              v
     Remote VM       k3s Cluster      Kubernetes
```

## 1. Docker Compose

Use Docker Compose when the application is deployed to a remote server or VM running Docker Compose.

Workflow:

```text
reusable-deploy-docker-compose.yml
```

Typical requirements:

- SSH host
- SSH user
- SSH private key
- Docker Compose file
- remote deployment directory
- Compose service
- container image/tag

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

---

## 2. Kubernetes / k3s

Use Kubernetes when the application is deployed to a Kubernetes cluster.

This includes lightweight Kubernetes distributions such as **k3s**.

The toolkit supports a configurable runner label, with `k3s` commonly used for self-hosted deployment runners.

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

The consuming repository owns its Kubernetes manifests.

For example:

```text
my-app/
└── k8s/
    ├── deployment.yaml
    ├── service.yaml
    └── ingress.yaml
```

The reusable workflow receives:

```yaml
manifest: k8s/
```

It should not assume that every consuming repository has the same Kubernetes directory structure.

---

## 3. Helm

Use Helm when the application is packaged and deployed as a Helm chart.

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

A consuming repository may have:

```text
my-app/
└── helm/
    └── my-app/
        ├── Chart.yaml
        ├── values.yaml
        └── templates/
```

### Choosing between Kubernetes and Helm

Helm is a deployment/package-management strategy on top of Kubernetes.

Therefore:

- choose **Kubernetes** when you want to manage raw Kubernetes manifests directly;
- choose **Helm** when your application is packaged as a Helm chart.

Do not call all three deployment workflows for the same deployment.

The migration documentation recommends selecting exactly one deployment workflow for a consuming repository.

---

# Quick start

## 1. Create a workflow in your application repository

Create:

```text
.github/workflows/ci.yml
```

## 2. Reference a released version

Use a release tag:

```yaml
jobs:
  test:
    uses: Ahmadzadeh920/ci-toolkit/.github/workflows/reusable-test.yml@v1
```

Avoid using:

```yaml
uses: Ahmadzadeh920/ci-toolkit/.github/workflows/reusable-test.yml@main
```

for production pipelines.

Pinning to a release provides a stable workflow contract.

## 3. Configure inputs

Example:

```yaml
jobs:
  test:
    uses: Ahmadzadeh920/ci-toolkit/.github/workflows/reusable-test.yml@v1
    with:
      python-versions: '["3.11", "3.12"]'
      working-directory: services/api
```

## 4. Configure required secrets

Only create the secrets required by the workflow you are using.

For example, Docker publishing may require:

```yaml
secrets:
  registry-password: ${{ secrets.GITHUB_TOKEN }}
```

Deployment workflows have their own deployment-specific credentials.

## 5. Configure permissions

Give each reusable workflow the permissions it requires.

For example, CodeQL requires:

```yaml
permissions:
  actions: read
  contents: read
  security-events: write
```

## 6. Select one deployment strategy

Choose:

```text
Docker Compose
      OR
Kubernetes / k3s
      OR
Helm
```

Then configure only the corresponding deployment workflow.

## 7. Test before production

Test the integration in a development or staging environment before promoting it to production.

---

# Workflow catalog

The repository currently provides the following reusable workflows:

| Workflow | Purpose |
|---|---|
| `reusable-test.yml` | Install dependencies, lint, run tests, collect coverage, and upload artifacts |
| `reusable-codeql.yml` | GitHub CodeQL static analysis |
| `reusable-sonarqube.yml` | SonarQube analysis and quality gate |
| `reusable-docker-build.yml` | Build Docker images and optionally push/save them |
| `reusable-docker-push.yml` | Load and push a previously built Docker image |
| `reusable-trivy.yml` | Filesystem, image, configuration, and SBOM vulnerability scanning |
| `reusable-notification.yml` | Slack, Microsoft Teams, and Discord notifications |
| `reusable-deploy-docker-compose.yml` | Docker Compose deployment over SSH |
| `reusable-deploy-kubernetes.yml` | Kubernetes deployment using `kubectl` |
| `reusable-deploy-helm.yml` | Helm-based Kubernetes deployment |
| `reusable-sync.yml` | Synchronize/push a branch to another repository |

`caller-ci.yml` is an example caller workflow rather than one of the reusable `workflow_call` contracts.

The detailed contracts, inputs, secrets, permissions, and outputs are maintained in the reusable workflow documentation.

---

# Configuration reference

The complete configuration reference is maintained under the [`docs/`](https://github.com/Ahmadzadeh920/ci-toolkit/tree/main/docs) directory.

## Reusable workflow contracts

See:

[`docs/reusable-workflows.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/reusable-workflows.md)

This document defines the inputs, secrets, permissions, and outputs for each reusable workflow.

## Permissions

See:

[`docs/permissions.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/permissions.md)

Use this document to determine the minimum required `GITHUB_TOKEN` permissions for each workflow.

## Secrets

See:

[`docs/secrets.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/secrets.md)

This documents secret names and their purposes.

**Secret values must never be committed to this repository.**

## Variables

See:

[`docs/variables.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/variables.md)

Use repository or environment variables for non-sensitive configuration where appropriate.

## Environments

See:

[`docs/environments.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/environments.md)

This covers recommended development, staging, and production environment configuration.

## OIDC

See:

[`docs/oidc.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/oidc.md)

This describes where OIDC can replace long-lived credentials and where credentials such as SSH keys or SonarQube tokens may still be required.

---

# Deployment configuration ownership

A reusable workflow should not assume that all repositories have the same infrastructure paths.

For example, the toolkit does **not** require every repository to have:

```text
k8s/
helm/
docker-compose/
```

A consuming repository supplies its own paths.

### Kubernetes

```yaml
with:
  manifest: k8s/
```

### Helm

```yaml
with:
  helm-chart: helm/my-application
  values-file: helm/my-application/values.yaml
```

### Docker Compose

```yaml
with:
  compose-file: docker-compose/docker-compose.yml
```

This separation is important because `ci-toolkit` provides the **pipeline contract**, while the consuming repository owns the actual application deployment configuration.

---

# Versioning

Do not use `main` for production workflow consumption.

Create release tags such as:

```text
v1
v1.1.0
v1.2.0
```

Then consume workflows using:

```yaml
uses: Ahmadzadeh920/ci-toolkit/.github/workflows/reusable-test.yml@v1
```

## Versioning policy

### Major version

Increment the major version for breaking contract changes, including:

- removing an input
- renaming an input
- removing a required secret
- renaming a secret
- changing an output contract
- changing behavior in a way that requires caller changes

Example:

```text
v1 → v2
```

### Minor/patch version

Use minor or patch releases for backward-compatible changes such as:

- adding optional inputs with defaults
- improving documentation
- fixing workflow bugs
- updating implementation details without changing the public contract

Consuming repositories should intentionally upgrade their toolkit version rather than silently tracking `main`.

---

# Security notes

Security is a core requirement of this toolkit.

## Never store secrets in this repository

This repository must never contain:

- private keys
- kubeconfigs
- passwords
- access tokens
- registry credentials
- webhook URLs
- SonarQube tokens
- SSH credentials

Only secret **names and purposes** should be documented.

## Use minimum GitHub permissions

Do not use:

```yaml
permissions: write-all
```

Grant only the permissions required by each workflow.

For example, CodeQL requires security-event write access, while many workflows only need:

```yaml
permissions:
  contents: read
```

## Prefer `GITHUB_TOKEN`

Where supported, prefer the automatically provided:

```text
GITHUB_TOKEN
```

over long-lived personal access tokens.

## Protect deployment credentials

Deployment credentials should be stored as GitHub Actions secrets and, where appropriate, protected through GitHub Environments.

For production deployment, consider:

```text
production environment
        |
        +-- required reviewers
        +-- protected secrets
        +-- deployment restrictions
```

## Self-hosted runners

Kubernetes/k3s deployments may use a self-hosted runner with a label such as:

```yaml
runner: k3s
```

The runner must have the appropriate Kubernetes tooling and access to the target cluster.

The toolkit should not contain cluster-specific credentials or hard-coded infrastructure addresses.

## SSH deployments

Docker Compose deployment uses SSH credentials supplied by the consuming repository.

SSH credentials should be stored as GitHub secrets and should not be committed to Git.

Where possible, manage SSH host keys securely rather than disabling host-key verification.

---

# Migrating an existing repo onto this toolkit

If you already have a repository with its own CI/CD workflows, use the migration checklist:

[`docs/migration-checklist.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/migration-checklist.md)

The migration process should include:

1. Confirm that the repository can access `ci-toolkit`.
2. Select the reusable workflows you actually need.
3. Pin workflow references to a release tag.
4. Configure the required `workflow_call` inputs.
5. Create only the required secrets.
6. Configure repository/environment variables.
7. Configure GitHub Environments where required.
8. Configure the necessary GitHub Actions permissions.
9. Select **one** deployment strategy.
10. Move/retain application-specific deployment configuration in the consuming repository.
11. Configure the appropriate runner.
12. Test in development or staging.
13. Promote the tested configuration to production.

The complete checklist is maintained in the migration document.

---

# Recommended migration architecture

For an existing repository, the recommended target structure is:

```text
application-repository/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── k8s/                       # if Kubernetes deployment is selected
│   ├── deployment.yaml
│   └── service.yaml
│
├── helm/                      # if Helm deployment is selected
│   └── application/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
│
├── docker-compose/            # if Compose deployment is selected
│   └── docker-compose.yml
│
└── application source code
```

Only the deployment configuration corresponding to your selected deployment strategy needs to be maintained.

---

# Contributing

Contributions are welcome.

When contributing a reusable workflow:

1. Keep the workflow under `.github/workflows/`.
2. Keep the workflow generic and repository-independent.
3. Avoid hard-coded application paths.
4. Avoid hard-coded infrastructure addresses.
5. Never commit secrets.
6. Define explicit `workflow_call` inputs.
7. Define required secrets clearly.
8. Document required permissions.
9. Update `docs/reusable-workflows.md` when the contract changes.
10. Update `CHANGELOG.md`.
11. Test the workflow before creating a release.

## Contract changes

Changes to the reusable workflow contract must be treated carefully.

Breaking changes include:

- renaming inputs
- removing inputs
- changing required secrets
- removing outputs
- changing required behavior

Breaking changes require a major version.

Backward-compatible additions should use a minor or patch release.

---

# License

This project is licensed under the [MIT License](LICENSE.md).

---

# Related documentation

| Resource | Description |
|---|---|
| [`docs/`](https://github.com/Ahmadzadeh920/ci-toolkit/tree/main/docs) | Complete documentation |
| [`docs/reusable-workflows.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/reusable-workflows.md) | Workflow contracts |
| [`docs/migration-checklist.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/migration-checklist.md) | Migration guide |
| [`docs/permissions.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/permissions.md) | GitHub Actions permissions |
| [`docs/secrets.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/secrets.md) | Secret inventory |
| [`docs/variables.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/variables.md) | Variables inventory |
| [`docs/environments.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/environments.md) | Environment configuration |
| [`docs/oidc.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/oidc.md) | OIDC strategy |
| [`helm/`](https://github.com/Ahmadzadeh920/ci-toolkit/tree/main/helm) | Helm example configuration |
| [`k8s/`](https://github.com/Ahmadzadeh920/ci-toolkit/tree/main/k8s) | Kubernetes example configuration |
| [`docker-compose/`](https://github.com/Ahmadzadeh920/ci-toolkit/tree/main/docker-compose) | Docker Compose example configuration |

---

# Summary

`ci-toolkit` provides reusable CI/CD building blocks while keeping application-specific configuration inside the consuming repository.

The key design principles are:

- **Reusable workflows live in `.github/workflows/`.**
- **Workflow contracts are explicitly documented.**
- **Secrets remain in the consuming repository.**
- **Infrastructure configuration remains in the consuming repository.**
- **Production workflows should use release tags.**
- **Permissions should follow least privilege.**
- **Each application chooses one deployment strategy:**
  - **Docker Compose**
  - **Kubernetes / k3s**
  - **Helm**
- **The toolkit provides pipeline logic; the application repository owns its deployment configuration.**

For a new repository, start with the [migration checklist](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/migration-checklist.md) and then use the [reusable workflow contracts](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/reusable-workflows.md) to configure the workflows you need.