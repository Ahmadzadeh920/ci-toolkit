# Changelog

All notable changes to this workflow library are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

**Versioning policy for this repo specifically:**

- **MAJOR** (`v2`, `v3`, ...): a `workflow_call` `input`, `secret`, or `output` is renamed, removed, or its required/optional status changes in a way that
  breaks existing callers.
- **MINOR** (`v1.1.0`): a new optional input/output is added with a backward-compatible default, or a new reusable workflow is added.
- **PATCH** (`v1.0.1`): internal fixes (bug fixes, dependency bumps, doc corrections) that don't change the calling contract at all.

Consuming repositories should pin to a tag (e.g. `@v1`), never `@main`. Starting with this release, tags and GitHub Releases are created automatically by `release.yml`, and every pull request is checked by `contract-diff.yml` before it can merge.

---

## [Unreleased]

### Considering

- Move `sonar-host-url` from `secrets` to `vars` in `reusable-sonarqube.yml` (currently tracked as a known inconsistency — see `docs/secrets.md`).
- Remove the stray `DEPLOY_KEY` requirement from `reusable-sonarqube.yml`.
- Support `GITHUB_TOKEN` directly for GHCR in `reusable-docker-build.yml` / `reusable-docker-push.yml`, as an alternative to `registry-password`.
- Investigate OIDC-based authentication for cloud registries/Kubernetes (see `docs/oidc.md`).
- Real rollout-strategy support (rolling / blue-green / canary) as a cross-cutting option available under any deployment target — tracked separately from the naming fix below.

---

## [1.1.0] - 2026-09-08

### Added

**Versioning & release enforcement**
- `release.yml` — publishes a GitHub Release from the matching `CHANGELOG.md` section whenever a `vX.Y.Z` tag is pushed, and re-points the mutable `v1` major tag onto the new commit.
- `contract-diff.yml` + `contract-diff.py` — on every pull request, diffs each workflow's `workflow_call.inputs` / `secrets` / `outputs` against the last released tag. Fails the check if anything required was removed, renamed, or made required-from-optional, **unless** the PR carries the `breaking-change` label.
- `breaking-change` label wired into `contract-diff.yml` as the sanctioned override path for intentional major-version changes.
- Tag protection ruleset on `v*` — restricts who can create/force-move release tags and requires the `contract-diff` check to pass first.

**Build interface decoupling**
- `docs/build-interface.md` ("Build Workflow Interface") — defines the contract a consuming repository must satisfy (produce an image/artifact matching `image`, `image-tag`, `digest`) regardless of which build workflow or tool it uses.
- `reusable-build-buildpacks.yml` — builds an OCI image via Cloud Native Buildpacks instead of a Dockerfile, conforming to the same output contract as `reusable-docker-build.yml`.
- `reusable-build-make.yml` — builds via a `make image` (or configurable target) entrypoint in the consuming repo, for teams with custom or non-Docker build tooling.

**Configurable branching strategy**
- `docs/branching-strategies.md` — documents the supported branching models (`trunk`, `github-flow`, `git-flow`) and the ref → environment mapping for each.
- `reusable-branch-context.yml` — new reusable workflow that resolves a `branching-strategy` input plus the triggering ref into `environment` and `should-deploy` outputs, so deploy jobs gate on this instead of hard-coded branch names.
- `release.updated.example.yml` — updated caller-workflow example showing `reusable-branch-context.yml` feeding its outputs into `reusable-deploy-docker-compose.yml` / `reusable-deploy-kubernetes.yml` / `reusable-deploy-helm.yml`.

### Changed

- Renamed **"Deployment Strategy" → "Deployment Target"** across `README.md` and `docs/`, to stop conflating *where* an app is deployed (Docker Compose / Kubernetes / Helm) with *how* traffic cuts over during a deploy (rolling / blue-green / canary). This is a documentation and heading rename only — no `workflow_call` input, secret, or output name changed.
- Added a "Rollout Strategy (planned)" placeholder section to the README pointing at the `Unreleased → Considering` entry above, so the renamed term has a clear home for future work instead of being reused incorrectly again.

### Documentation

- `docs/reusable-workflows.md` updated with entries for `reusable-build-buildpacks.yml`, `reusable-build-make.yml`, and `reusable-branch-context.yml`.
- `docs/migration-checklist.md` updated to (a) require pinning to a tag produced by the new `release.yml` flow rather than `main`, and (b) reference `docs/build-interface.md` for repositories that don't use a plain Dockerfile.
- `docs/permissions.md` and `docs/secrets.md` updated with any new `GITHUB_TOKEN` permissions or secrets introduced by `release.yml` and `contract-diff.yml`.

### Notes

- This release is **backward-compatible**. All new workflows and docs are additive; existing callers of `reusable-docker-build.yml`, `reusable-deploy-*.yml`, `reusable-test.yml`, etc. require no changes. Tag as `v1.1.0` and move the `v1` mutable tag forward onto it.
- The "Deployment Strategy" → "Deployment Target" rename changes README/doc anchor links (e.g. `#deployment-strategies` → `#deployment-target`). If any consuming repo's documentation deep-links to the old anchor, update that link — this does not affect the workflow contract, only in-repo navigation.
- If a future change renames the *actual* `workflow_call` input (for example, an existing `deployment-strategy:` input key), that must ship as a **major** version and go through `contract-diff.yml` with the `breaking-change` label, per the versioning policy above — the rename in this release intentionally did not touch input keys, only prose/headings.

---

## [1.0.0] - 2026-08-15



### Added

Initial extraction of the reusable workflow library from `auth-gateway-platform`. Thirteen `workflow_call` workflows and full supporting documentation:

- `reusable-test.yml` — install, lint, test, coverage, artifact upload
- `reusable-codeql.yml` — CodeQL static analysis
- `reusable-sonarqube.yml` — SonarQube scan + quality gate
- `reusable-docker-build.yml` — Docker image build (+ optional push/artifact)
- `reusable-docker-push.yml` — push a previously built image artifact
- `reusable-docker.yml` — combined build + push in one workflow
- `reusable-trivy.yml` — filesystem/image/config/SBOM vulnerability scanning
- `reusable-notification.yml` — Slack / Teams / Discord notifications
- `reusable-deploy.yml` — generic deploy dispatcher (Compose / Kubernetes / Helm)
- `reusable-deploy-docker-compose.yml` — Docker Compose deployment over SSH
- `reusable-deploy-kubernetes.yml` — `kubectl`-based Kubernetes deployment
- `reusable-deploy-helm.yml` — Helm chart deployment
- `reusable-sync.yml` — push a branch to a target repository

### Documentation

- `docs/reusable-workflows.md` — full contract (inputs/secrets/outputs) per workflow
- `docs/permissions.md` — minimum `GITHUB_TOKEN` permissions per workflow
- `docs/secrets.md` — secret name/purpose inventory (no values)
- `docs/variables.md` — non-sensitive `vars.*` inventory
- `docs/environments.md` — recommended GitHub Environments setup
- `docs/oidc.md` — OIDC adoption strategy
- `docs/migration-checklist.md` — checklist for onboarding a caller repo

### Notes

- `ci.yml` from the source repository was intentionally **not** migrated — it is a caller workflow, not a reusable one. It remains in `auth-gateway-platform` and was updated to reference this library instead.
