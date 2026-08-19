# Reusable Workflow Contracts

This library ships **11** `workflow_call` reusable workflows. There is no
generic `reusable-docker.yml` or `reusable-deploy.yml` dispatcher — each
concern (build, push, and each deployment target) is a dedicated workflow
with its own explicit contract.

---

## `reusable-test.yml`

Purpose: install dependencies, lint, run tests, collect coverage, upload
artifact.

**Inputs:** `runner`, `python-versions`, `working-directory`,
`requirements-file`, `dependency-manager`, `install-command`, `lint`,
`lint-command`, `run-tests`, `test-command`, `upload-artifacts`,
`artifact-name`, `test-report-path`, `coverage-report-path`, `fail-fast`,
`timeout-minutes`

**Secrets:** none

**Permissions:** `contents: read`

**Outputs:** `artifact-name`, `coverage-report`

---

## `reusable-codeql.yml`

Purpose: CodeQL static analysis.

**Inputs:** `runner`, `languages`, `build-mode`, `build-command`, `queries`,
`category`, `timeout-minutes`

**Secrets:** none

**Permissions:** `actions: read`, `contents: read`, `security-events: write`

---

## `reusable-sonarqube.yml`

Purpose: SonarQube scan and quality gate.

**Inputs:** `runner`, `project-base-dir`, `artifact-name`,
`download-artifact`, `scanner-args`, `quality-gate`, `quality-gate-timeout`,
`fetch-depth`, `timeout-minutes`

**Secrets:** `sonar-token`, `sonar-host-url`, `DEPLOY_KEY`
(`DEPLOY_KEY` is an SSH key passed to `actions/checkout` — see
[`docs/secrets.md`](secrets.md) for why this should be reviewed before v1)

**Permissions:** `contents: read`, `actions: read`

---

## `reusable-docker-build.yml`

Purpose: build a Docker image; optionally push it or save it as an
artifact for a later job.

**Inputs:** `runner`, `registry`, `registry-username`, `image-name`,
`image-tag`, `context`, `dockerfile`, `platforms`, `push`, `load`,
`save-artifact`, `artifact-name`, `cache`

**Secrets:** `registry-password`

**Permissions:** `contents: read`, `packages: write`

**Outputs:** `image`, `digest`, `tags`

---

## `reusable-docker-push.yml`

Purpose: download a Docker image artifact saved by `reusable-docker-build.yml`,
load it, authenticate to a registry, tag and push it.

**Inputs:** `runner`, `registry`, `registry-username`, `image-name`,
`image-tag`, `artifact-name`, `timeout-minutes`

**Secrets:** `registry-password`

**Permissions:** `contents: read`, `packages: write`

**Outputs:** `image`, `digest`

---

## `reusable-trivy.yml`

Purpose: filesystem, image, configuration, or SBOM vulnerability scanning.

**Inputs:** `runner`, `scan-type`, `scan-target`, `download-artifact`,
`artifact-name`, `severity`, `scanners`, `ignore-unfixed`, `exit-code`,
`format`, `upload-sarif`, `upload-artifact`, `report-artifact-name`,
`timeout-minutes`

**Secrets:** none

**Permissions:** `contents: read`, `security-events: write`

**Outputs:** `report`, `format`

---

## `reusable-notification.yml`

Purpose: Slack, Microsoft Teams, or Discord pipeline notifications.

**Inputs:** `runner`, `channel`, `status`, `title`, `message`, `environment`,
`application`, `color`, `include-github-context`

**Secrets:** `slack-webhook`, `teams-webhook`, `discord-webhook`
(provide only the one matching `channel`)

**Permissions:** `contents: read`

---

## Deployment workflows

There is no generic deploy dispatcher. Call the workflow matching your
deployment target directly.

### `reusable-deploy-docker-compose.yml`

Purpose: SSH to a remote host and run Docker Compose.

**Inputs:** `runner`, `environment`, `compose-file`, `image`, `image-tag`,
`remote-directory`, `compose-service`, `timeout-minutes`

**Secrets:** `ssh-host`, `ssh-user`, `ssh-private-key`

**Permissions:** not explicitly declared — defaults apply; grant
`contents: read` from the caller.

See [`examples/docker-compose/docker-compose.yml`](../examples/docker-compose/docker-compose.yml)
for the expected file shape.

### `reusable-deploy-kubernetes.yml`

Purpose: `kubectl apply` a manifest and wait for rollout.

**Inputs:** `runner` (default `k3s`), `application`, `namespace`,
`manifest`, `image-repository`, `image-tag`, `timeout`

**Secrets:** `DEPLOY_KEY` — an SSH key passed to `actions/checkout` so the
manifest repo can be cloned; this is not a Kubernetes credential itself,
the workflow assumes `kubectl` is already configured on the runner (e.g. a
self-hosted `k3s` runner with a local kubeconfig).

See [`examples/kubernetes/deployment.yaml`](../examples/kubernetes/deployment.yaml)
and [`examples/kubernetes/rbac.yaml`](../examples/kubernetes/rbac.yaml) for
the expected manifest shape and the RBAC a deploying service account needs.

### `reusable-deploy-helm.yml`

Purpose: `helm upgrade --install` a chart, with optional automatic rollback.

**Inputs:** `runner` (default `k3s`), `application`, `namespace`,
`helm-chart`, `image-repository`, `image-tag`, `values-file`, `timeout`,
`atomic`

**Secrets:** `DEPLOY_KEY` (same role as above — checkout access, not a
Helm/Kubernetes credential)

See [`examples/helm/`](../examples/helm/) for a minimal chart skeleton.

---

## `reusable-sync.yml`

Purpose: synchronize a source branch into a target repository.

**Inputs:** `runner`, `source-branch`, `target-branch`, `target-repository`,
`sync-tags`, `force-push`, `fetch-depth`, `commit-message`,
`timeout-minutes`

**Secrets:** `target-token`

**Permissions:** `contents: read`

The current implementation creates a target HTTPS remote using the token.
Consider GitHub App authentication or another short-lived credential
mechanism instead of a long-lived PAT in a future revision.
