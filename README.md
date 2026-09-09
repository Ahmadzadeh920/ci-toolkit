# ci-toolkit

**Versioned, portable reusable GitHub Actions workflows for standardized CI/CD.**

`ci-toolkit` is a reusable GitHub Actions workflow library for centralizing CI/CD, testing, static analysis, security scanning, application builds, Docker image workflows, deployment, notifications, repository synchronization, and branching-strategy resolution.

Instead of duplicating similar GitHub Actions workflows across multiple repositories, application repositories can call the workflows from this repository using GitHub Actions `workflow_call`.

> **Application code, deployment configuration, infrastructure credentials, and secret values remain in the consuming repository. `ci-toolkit` provides the reusable CI/CD workflow contracts.**

---

## Why this exists?

CI/CD workflows are often copied from one repository to another. Over time, those copies become different:

- different tool versions
- different security settings
- different permissions
- different Docker configurations
- different build tooling (Docker, buildpacks, Make) baked into the app repo instead of decoupled from it
- different deployment logic
- different notification mechanisms
- different secret requirements
- different branching/environment-promotion rules

Maintaining those duplicated workflows becomes increasingly difficult as the number of repositories grows.

`ci-toolkit` centralizes the reusable pipeline logic and exposes it through explicit:

- `inputs`
- `secrets`
- `outputs`
- permissions
- runner configuration
- deployment contracts
- branching-strategy contracts

A consuming repository can therefore use a stable workflow such as:

```
jobs:
  test:
    uses: Ahmadzadeh920/ci-toolkit/.github/workflows/reusable-test.yml@v1
```

instead of maintaining its own copy of the complete workflow.

The toolkit is designed to separate:

```
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
| Branch Context Resolution      |
| Test / Lint                    |
| CodeQL                         |
| SonarQube                      |
| Build (Docker / Buildpacks / Make) |
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
- Centralized branching-strategy resolution (trunk-based, GitHub Flow, or Git Flow) without duplicating ref/branch conditionals across every workflow
- Python and general application testing
- Linting and test execution
- CodeQL static analysis
- SonarQube analysis and quality gates
- Docker image building
- Cloud Native Buildpacks builds (no Dockerfile required)
- Make-based builds (compiled binaries, non-containerized artifacts)
- Docker image publishing
- Trivy security scanning
- Slack, Microsoft Teams, and Discord notifications
- Docker Compose deployments
- Kubernetes/k3s deployments
- Helm deployments
- Repository mirroring or branch synchronization

The test workflow is configurable rather than being tied to one specific application structure, while Docker and deployment workflows expose repository-specific paths and configuration through inputs. Branching-strategy resolution is likewise configurable per repository through a single input rather than being hard-coded per workflow. The build step is decoupled from the application in the same way: a repository picks the build workflow matching its packaging method (Docker, Buildpacks, or Make) rather than the toolkit assuming Docker is the only option.

---

## Applications

The toolkit can be used by:

- Python applications
- Django applications
- FastAPI services
- backend services
- microservices
- Dockerized applications
- Buildpacks-compatible applications (any language a Cloud Native Buildpack supports)
- Make-based / compiled-artifact applications
- Kubernetes applications
- Helm-based applications
- Docker Compose applications
- internal tools
- repositories requiring CodeQL or Trivy
- repositories requiring SonarQube quality gates
- repositories that want a single source of truth for "which branch/tag deploys to which environment"

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
- which branching strategy it adopts (the toolkit resolves the *consequences* of that choice, it doesn't impose the choice itself)

---

# Critical structural constraint

GitHub reusable workflows must physically exist under:

```
.github/workflows/
```

in the source repository.

Therefore, this repository must keep reusable workflows here:

```
ci-toolkit/
└── .github/
    └── workflows/
        └── reusable-test.yml
```

A consuming repository references them using:

```
uses: Ahmadzadeh920/ci-toolkit/.github/workflows/reusable-test.yml@v1
```

Do **not** move reusable workflows to:

```
workflows/
```

or:

```
.github/reusable-workflows/
```

or another directory.

The reusable workflow files must remain under:

```
.github/workflows/
```

GitHub resolves reusable workflows from that location.

---

# Repository structure

The current repository structure is:

```
ci-toolkit/
│
├── .github/
│   └── workflows/
│       ├── caller-ci.yml
│       ├── reusable-branch-context.yml
│       ├── reusable-codeql.yml
│       ├── reusable-deploy-docker-compose.yml
│       ├── reusable-deploy-helm.yml
│       ├── reusable-deploy-kubernetes.yml
│       ├── reusable-docker-build.yml
│       ├── reusable-build-buildpacks.yml
│       ├── reusable-build-make.yml
│       ├── reusable-docker-push.yml
│       ├── reusable-notification.yml
│       ├── reusable-sonarqube.yml
│       ├── reusable-sync.yml
│       ├── reusable-test.yml
│       └── reusable-trivy.yml
│
├── docs/
│   ├── branching-strategies.md
│   ├── build-interface.md
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

The repository currently contains 14 reusable workflows. `caller-ci.yml`,
`release.yml`, `contract-diff.yml`, and `release.updated.example.yml` are
caller/example workflows demonstrating how a consuming repository wires
these contracts together — they are not part of the 14 reusable workflow
contracts themselves.

### `docker-compose/`

Contains Docker Compose deployment/example configuration.

### `helm/`

Contains Helm-related example configuration.

### `k8s/`

Contains Kubernetes-related example configuration.

### `docs/`

Contains the configuration contracts, branching-strategy reference, build-interface reference, and migration documentation for consuming repositories.

---

# Quick start

Create a workflow in your application repository:

```
.github/workflows/ci.yml
```

Then reference the reusable workflows from `ci-toolkit`.

For example:

```
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

If your repository also needs to know *where* a given ref should deploy, add branch-context resolution:

```
jobs:
  resolve-context:
    uses: Ahmadzadeh920/ci-toolkit/.github/workflows/reusable-branch-context.yml@v1
    with:
      branching-strategy: git-flow   # trunk | github-flow | git-flow

  deploy:
    needs: resolve-context
    if: needs.resolve-context.outputs.should-deploy == 'true'
    uses: Ahmadzadeh920/ci-toolkit/.github/workflows/reusable-deploy-kubernetes.yml@v1
    with:
      namespace: ${{ needs.resolve-context.outputs.environment }}
```

The complete workflow contract, including inputs, secrets, permissions, and outputs, is documented in:

[`docs/reusable-workflows.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/reusable-workflows.md).

The three supported branching strategies and their ref-to-environment mappings are documented in:

[`docs/branching-strategies.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/branching-strategies.md).

The three supported build methods and their common output contract are documented in:

[`docs/build-interface.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/build-interface.md).

### Recommended adoption sequence

1. Choose a branching strategy (`trunk`, `github-flow`, or `git-flow`) — see `docs/branching-strategies.md`.
2. Choose a build method (`reusable-docker-build.yml`, `reusable-build-buildpacks.yml`, or `reusable-build-make.yml`) — see `docs/build-interface.md`.
3. Choose the reusable workflows required by your repository.
4. Pin them to a release tag.
5. Configure their required inputs, including `resolve-context`'s `branching-strategy` (and `main-branch`/`develop-branch` if your branch names differ from the defaults).
6. Create only the required secrets.
7. Configure repository/environment variables where necessary.
8. Configure required GitHub Actions permissions.
9. Select one deployment target if deployment is required.
10. Wire every deploy/release job's `needs:` and `if:` off `resolve-context`'s outputs — and off any quality-gate jobs (test/CodeQL/SonarQube/Trivy/build) you require before deploying.
11. Test the pipeline in a non-production environment.
12. Promote the tested version to production.

The migration checklist documents this process.

---

# Branching Strategy Resolution

Every deploy or release workflow eventually has to answer the same question: **given this branch or tag, which environment should it deploy to, and should it deploy at all?** Answering that inline, per workflow, is how repositories end up with inconsistent and duplicated branch conditionals.

`reusable-branch-context.yml` centralizes that answer. A caller supplies a single `branching-strategy` input; the workflow inspects the triggering ref and returns:

- `environment` — `dev` | `staging` | `prod` (or empty if the ref doesn't map to a deploy)
- `should-deploy` — `'true'` | `'false'`

Every deploy/release job in the caller repository then only ever checks these two outputs — it never needs to know the underlying branch-naming rules.

```
jobs:
  resolve-context:
    uses: Ahmadzadeh920/ci-toolkit/.github/workflows/reusable-branch-context.yml@v1
    with:
      branching-strategy: git-flow
  deploy:
    needs: resolve-context
    if: needs.resolve-context.outputs.should-deploy == 'true'
    uses: Ahmadzadeh920/ci-toolkit/.github/workflows/reusable-deploy-kubernetes.yml@v1
    with:
      namespace: ${{ needs.resolve-context.outputs.environment }}
```

## Supported strategies

| Strategy      | Summary                                                                 |
| ------------- | ------------------------------------------------------------------------ |
| `trunk`       | Single long-lived branch; every push to `main` deploys to `prod`.        |
| `github-flow` | `main` is always deployable; a semver tag on `main` promotes the same build to `prod`. |
| `git-flow`    | `develop`/`release/*` deploy to `staging`; only a semver tag deploys to `prod`. `main` alone does not deploy. |

The full ref-to-environment mapping table for each strategy is documented in [`docs/branching-strategies.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/branching-strategies.md).

## A note on `if:` and quality gates

`resolve-context`'s outputs answer *where* a ref should go, not *whether the code is good enough to go there*. Deploy/release jobs still need their own `needs:`/`if:` wiring against your test, CodeQL, SonarQube, and Trivy jobs. Because assigning a custom `if:` condition to a job replaces GitHub Actions' implicit "only run if all `needs:` succeeded" behavior, remember to explicitly check `needs.<job>.result == 'success'` for every quality gate you depend on — `resolve-context`'s outputs alone are not a substitute for that.

---

# Build Interface

Just as deployment is decoupled from the application repository, **build is decoupled from the application too.** Not every application builds the same way: some ship a `Dockerfile`, some rely on Cloud Native Buildpacks to avoid maintaining one, and some produce a compiled artifact via `make` rather than a container image at all. `ci-toolkit` does not assume Docker is the only build path.

A consuming repository has **three build method options**:

```
                 Application source
                        |
                Choose ONE build method
                        |
       +----------------+----------------+
       |                |                |
       v                v                v
   Dockerfile        Buildpacks         Make
       |                |                |
       v                v                v
reusable-docker-  reusable-build-  reusable-build-
   build.yml       buildpacks.yml     make.yml
       |                |                |
       v                v                v
        common output contract (image-ref / artifact-path)
```

## Important: choose exactly one

For a given application, select exactly one of:

1. **`reusable-docker-build.yml`** — builds from a `Dockerfile` in the repository.
2. **`reusable-build-buildpacks.yml`** — builds using Cloud Native Buildpacks; no `Dockerfile` required.
3. **`reusable-build-make.yml`** — builds via a `Makefile` target, for applications that produce a binary or non-containerized artifact rather than an image.

As with deployment, there is no generic build dispatcher — the consuming repository calls the workflow matching how its application is actually packaged.

## Why decouple build from the application

Downstream jobs — `reusable-trivy.yml`, `reusable-docker-push.yml`, and every deploy workflow — only need a build's *output* (an image reference or artifact path), not knowledge of *how* it was produced. This means:

- A repository can switch from a hand-written `Dockerfile` to Buildpacks (or vice versa) without touching its test, scan, push, or deploy jobs — only the build job call changes.
- New build methods can be added to `ci-toolkit` in the future without any existing caller workflow needing to change.

The exact inputs, secrets, and outputs of each build workflow, and the common output contract all three expose, are documented in [`docs/build-interface.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/build-interface.md).

---

# Deployment Target

A consuming repository has **three deployment target options**:

```
                 Application
                      |
              Choose ONE target
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

The toolkit does **not** provide a generic deployment dispatcher. The consuming repository directly calls the workflow corresponding to its infrastructure. `resolve-context`'s `environment` output feeds whichever of the three you choose (as `namespace`, or as the relevant compose/values-file selector).

---

## Deployment option 1 — Docker Compose

Use Docker Compose when the application runs on a remote Docker host or VM.

Workflow:

```
reusable-deploy-docker-compose.yml
```

The workflow connects to the remote host through SSH and runs Docker Compose. Its configurable inputs include:

```
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

```
ssh-host
ssh-user
ssh-private-key
```

Example:

```
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

```
reusable-deploy-kubernetes.yml
```

The workflow performs `kubectl apply` and waits for the application rollout.

Its main inputs include:

```
runner
application
namespace
manifest
image-repository
image-tag
timeout
```

The default runner is:

```
k3s
```

The workflow assumes that `kubectl` is already configured on the runner, for example through a self-hosted k3s runner with an appropriate local kubeconfig.

Example:

```
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

```
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

```
reusable-deploy-helm.yml
```

The workflow performs:

```
helm upgrade --install
```

with optional automatic rollback.

Its inputs include:

```
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

```
k3s
```

Example:

```
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

```
my-app/
└── helm/
    └── my-app/
        ├── Chart.yaml
        ├── values.yaml
        └── templates/
```

---

# Workflow catalog

`ci-toolkit` currently provides **14 reusable `workflow_call` workflows**.

| Workflow                             | Purpose                                                                       |
| ------------------------------------- | ------------------------------------------------------------------------------ |
| `reusable-branch-context.yml`        | Resolves a branching strategy (trunk / github-flow / git-flow) and the triggering ref into `environment` and `should-deploy` outputs |
| `reusable-test.yml`                  | Install dependencies, lint, run tests, collect coverage, and upload artifacts |
| `reusable-codeql.yml`                | GitHub CodeQL static analysis                                                 |
| `reusable-sonarqube.yml`             | SonarQube analysis and quality gate                                           |
| `reusable-docker-build.yml`          | Build a Docker image from a `Dockerfile` and optionally push/save it          |
| `reusable-build-buildpacks.yml`      | Build an image using Cloud Native Buildpacks (no `Dockerfile` required)       |
| `reusable-build-make.yml`            | Build a compiled/non-containerized artifact via a `Makefile` target           |
| `reusable-docker-push.yml`           | Load a saved image artifact and push it                                       |
| `reusable-trivy.yml`                 | Filesystem, image, configuration, or SBOM vulnerability scanning              |
| `reusable-notification.yml`          | Slack, Microsoft Teams, or Discord notifications                              |
| `reusable-deploy-docker-compose.yml` | Docker Compose deployment over SSH                                            |
| `reusable-deploy-kubernetes.yml`     | Kubernetes deployment using `kubectl`                                         |
| `reusable-deploy-helm.yml`           | Helm-based Kubernetes deployment                                              |
| `reusable-sync.yml`                  | Synchronize a branch into another repository                                  |

`caller-ci.yml`, `release.yml`, `contract-diff.yml`, and `release.updated.example.yml` are caller/example workflows and are not part of the 14 reusable workflow contracts.

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

## Branching strategies

[`docs/branching-strategies.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/branching-strategies.md)

Documents the three supported branching strategies and their complete ref-to-environment mapping tables, plus the Kubernetes namespace-naming convention that `environment` feeds into.

## Build interface

[`docs/build-interface.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/build-interface.md)

Documents the three supported build methods (Docker, Buildpacks, Make), their inputs/secrets, and the common output contract that downstream test/scan/push/deploy jobs rely on regardless of which build method a repository chose.

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

The current checklist specifically covers choosing a branching strategy, selecting the required workflows, configuring inputs and secrets, permissions, runner configuration, and selecting exactly one deployment workflow.

---

# Configuration ownership

A central principle of this toolkit is:

> **Reusable workflow logic belongs in `ci-toolkit`; application-specific configuration belongs in the consuming repository.**

For example, `ci-toolkit` should not assume that every application has:

```
services/api/
k8s/
helm/my-app/
docker-compose/docker-compose.yml
```

Instead, the consuming repository supplies its own paths. Likewise, `ci-toolkit` should not assume every repository uses the same branch names — `reusable-branch-context.yml` accepts `main-branch`/`develop-branch` overrides for repositories that deviate from `main`/`develop` — or the same build tooling, which is why build is split across `reusable-docker-build.yml`, `reusable-build-buildpacks.yml`, and `reusable-build-make.yml` instead of a single Docker-only workflow.

### Kubernetes

```
with:
  manifest: k8s/
```

### Helm

```
with:
  helm-chart: helm/my-app
  values-file: helm/my-app/values.yaml
```

### Docker Compose

```
with:
  compose-file: docker-compose/docker-compose.yml
```

This makes the workflows portable between repositories.

---

# Versioning

Production repositories should **not** consume workflows directly from `main`.

Use release tags such as:

```
v1
v1.1.0
v1.2.0
```

Then reference a stable release:

```
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
- changing what an existing `branching-strategy` value resolves to (e.g. redefining what `git-flow` maps `main` to)

Example:

```
v1 → v2
```

## Minor and patch versions

Use minor or patch releases for backward-compatible changes such as:

- adding optional inputs with defaults
- adding a new `branching-strategy` value without changing existing ones
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

```
permissions:
  actions: read
  contents: read
  security-events: write
```

Do not use:

```
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

```
k3s
```

The runner must have the required Kubernetes tooling and access to the target cluster.

The workflow itself should not contain cluster-specific credentials or hard-coded infrastructure addresses.

## Docker Compose SSH deployment

Docker Compose deployment requires SSH credentials supplied by the consuming repository:

```
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
3. Choose a branching strategy and identify the workflows actually required.
4. Configure all required `workflow_call` inputs, including `reusable-branch-context.yml`'s `branching-strategy`.
5. Create only the required secrets.
6. Configure non-sensitive variables.
7. Configure GitHub Environments where required.
8. Select **exactly one deployment target**.
9. Keep the application's own manifest, Helm chart, or Compose file in the consuming repository.
10. Configure the correct self-hosted runner where required.
11. Configure the required GitHub Actions permissions.
12. Verify registry, SonarQube, deployment, and notification credentials as applicable.
13. Wire deploy/release job `needs:`/`if:` against both `resolve-context`'s outputs and your quality-gate jobs.
14. Test in a non-production environment.
15. Promote the tested workflow version to production.

The repository's migration checklist explicitly recommends choosing one of:

```
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
10. Update `docs/branching-strategies.md` if you add or change a branching-strategy mapping.
11. Update the relevant documentation.
12. Update `CHANGELOG.md`.
13. Test the workflow before creating a release.

## Breaking changes

Changes such as these are breaking changes:

- renaming an input
- removing an input
- renaming a secret
- removing a required secret
- removing an output
- changing a required workflow behavior
- changing an existing branching-strategy's ref-to-environment mapping

Breaking changes should receive a new major version.

Backward-compatible changes should use a minor or patch release.

---

# License

This project is licensed under the [MIT License](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/LICENSE.md).

---

# Documentation

| Resource                                                                                                      | Description                                   |
| ------------------------------------------------------------------------------------------------------------- | --------------------------------------------- |
| [`docs/`](https://github.com/Ahmadzadeh920/ci-toolkit/tree/main/docs)                                         | Complete configuration documentation          |
| [`reusable-workflows.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/reusable-workflows.md)   | Complete reusable workflow contracts          |
| [`branching-strategies.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/branching-strategies.md) | Supported branching strategies and ref→environment mappings |
| [`build-interface.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/build-interface.md) | Supported build methods and their common output contract |
| [`permissions.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/permissions.md)                 | GitHub Actions permissions                    |
| [`secrets.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/secrets.md)                         | Secret inventory and requirements             |
| [`variables.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/variables.md)                     | Repository/environment variables              |
| [`migration-checklist.md`](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/migration-checklist.md) | Migration procedure for existing repositories |
| [`k8s/`](https://github.com/Ahmadzadeh920/ci-toolkit/tree/main/k8s)                                           | Kubernetes example configuration              |
| [`helm/`](https://github.com/Ahmadzadeh920/ci-toolkit/tree/main/helm)                                         | Helm example configuration                    |
| [`docker-compose/`](https://github.com/Ahmadzadeh920/ci-toolkit/tree/main/docker-compose)                     | Docker Compose example configuration          |

---

# Summary

`ci-toolkit` provides reusable GitHub Actions workflow contracts while keeping application-specific configuration in the consuming repository.

The key principles are:

- **Reusable workflows live under `.github/workflows/`.**
- **There are currently 14 reusable workflow contracts.**
- **Build is decoupled from the application, just like deployment: pick one of `reusable-docker-build.yml`, `reusable-build-buildpacks.yml`, or `reusable-build-make.yml`.**
- **`caller-ci.yml` is an example caller, not a reusable workflow.**
- **Secrets remain in the consuming repository.**
- **Application deployment configuration remains in the consuming repository.**
- **Branching-strategy resolution is centralized in `reusable-branch-context.yml`, not duplicated per workflow.**
- **Production workflows should use release tags rather than `main`.**
- **GitHub Actions permissions should follow least privilege.**
- **Kubernetes/k3s deployments use a runner with Kubernetes access already configured.**
- **A repository should select exactly one deployment strategy:**
  - **Docker Compose**
  - **Kubernetes / k3s**
  - **Helm**
- **There is no generic deployment dispatcher.**
- **The toolkit provides pipeline logic; the application repository owns its application and infrastructure configuration.**

Start with the [migration checklist](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/migration-checklist.md), then use the [reusable workflow contracts](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/reusable-workflows.md), [branching strategies reference](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/branching-strategies.md), and [build interface reference](https://github.com/Ahmadzadeh920/ci-toolkit/blob/main/docs/build-interface.md) to configure the workflows required by your repository.
