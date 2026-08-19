# Changelog

All notable changes to this workflow library are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

**Versioning policy for this repo specifically:**

- **MAJOR** (`v2`, `v3`, ...): a `workflow_call` `input`, `secret`, or `output`
  is renamed, removed, or its required/optional status changes in a way that
  breaks existing callers.
- **MINOR** (`v1.1.0`): a new optional input/output is added with a backward
  -compatible default, or a new reusable workflow is added.
- **PATCH** (`v1.0.1`): internal fixes (bug fixes, dependency bumps, doc
  corrections) that don't change the calling contract at all.

Consuming repositories should pin to a tag (e.g. `@v1`), never `@main`.

---

## [Unreleased]

### Considering
- Move `sonar-host-url` from `secrets` to `vars` in `reusable-sonarqube.yml`
  (currently tracked as a known inconsistency — see `docs/secrets.md`).
- Remove the stray `DEPLOY_KEY` requirement from `reusable-sonarqube.yml`.
- Support `GITHUB_TOKEN` directly for GHCR in `reusable-docker-build.yml` /
  `reusable-docker-push.yml`, as an alternative to `registry-password`.
- Investigate OIDC-based authentication for cloud registries/Kubernetes
  (see `docs/oidc.md`).

---

## [1.0.0] - YYYY-MM-DD

### Added
Initial extraction of the reusable workflow library from
`auth-gateway-platform`. Thirteen `workflow_call` workflows and full
supporting documentation:

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
- `ci.yml` from the source repository was intentionally **not** migrated —
  it is a caller workflow, not a reusable one. It remains in
  `auth-gateway-platform` and was updated to reference this library instead.
