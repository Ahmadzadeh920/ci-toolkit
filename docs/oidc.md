# OpenID Connect (OIDC)

## Overview

OpenID Connect (OIDC) allows GitHub Actions workflows to authenticate to supported external services without storing a long-lived cloud credential as a GitHub secret.

For `ci-toolkit`, OIDC is a **security strategy for future integrations** rather than a currently required authentication mechanism.

The current reusable workflows do **not** request the GitHub Actions OIDC token permission:

```yaml
permissions:
  id-token: write
```

and none of the current deployment workflows performs a cloud-provider OIDC login.

Therefore, **OIDC is not required to use the current `ci-toolkit` workflows**.

GitHub supports OIDC with reusable workflows and can use the reusable workflow identity as part of a cloud trust policy. See the official GitHub documentation for the reusable-workflow OIDC model.

---

# Current authentication model

The current toolkit uses different authentication mechanisms depending on the workflow.

| Workflow | Current authentication |
|---|---|
| Test | `GITHUB_TOKEN` / default GitHub Actions authentication |
| CodeQL | `GITHUB_TOKEN` permissions |
| SonarQube | `sonar-token` and `sonar-host-url` secrets |
| Docker Build | Registry credentials through `registry-password` |
| Docker Push | Registry credentials through `registry-password` |
| Trivy | GitHub token permissions where SARIF upload is enabled |
| Notifications | Webhook secrets |
| Docker Compose | SSH private key + remote SSH credentials + GHCR credentials |
| Kubernetes | Preconfigured `kubectl` on the runner |
| Helm | Preconfigured `kubectl`/Helm on the runner |
| Repository Sync | `target-token` |

The reusable workflow contracts document these current secrets and permissions.

---

# Important: OIDC is not currently used for Kubernetes

The Kubernetes deployment workflow uses:

```yaml
runs-on: ${{ inputs.runner }}
```

with `k3s` as the default runner label.

The workflow then executes:

```bash
kubectl cluster-info
kubectl get nodes
```

and assumes that `kubectl` is already configured on the runner.

This means the current architecture is:

```text
GitHub Actions
      |
      | reusable workflow
      v
Self-hosted runner
      |
      | local kubeconfig
      v
k3s / Kubernetes cluster
```

The workflow does **not** obtain a Kubernetes credential through GitHub OIDC.

The `DEPLOY_KEY` secret used by the Kubernetes workflow is passed to `actions/checkout`; it is not the Kubernetes authentication credential.

---

# Important: OIDC is not currently used for Helm

The Helm workflow also defaults to the `k3s` runner and checks both:

```bash
kubectl version --client
helm version
```

before connecting to the Kubernetes cluster.

It then uses:

```bash
kubectl cluster-info
kubectl get nodes
```

and performs the Helm deployment with:

```bash
helm upgrade --install
```

Therefore, Helm currently relies on the Kubernetes access configured on the runner.

```text
GitHub Actions
      |
      v
Self-hosted k3s runner
      |
      +---- kubectl
      |
      +---- helm
      |
      v
Kubernetes / k3s
```

---

# Where OIDC can be introduced

OIDC is most useful when the deployment target is a service that supports GitHub Actions OIDC federation.

Typical examples include:

- AWS
- Azure
- Google Cloud
- other OIDC-compatible identity providers

Instead of storing a long-lived cloud access key:

```text
GitHub Secret
    |
    v
Long-lived credential
    |
    v
Cloud provider
```

OIDC can provide:

```text
GitHub Actions
    |
    | short-lived OIDC identity token
    v
Cloud identity provider
    |
    | temporary credentials
    v
Cloud resources
```

This reduces the need to maintain long-lived cloud credentials.

---

# Required permission

A workflow using OIDC normally requires:

```yaml
permissions:
  id-token: write
```

Usually this is combined with the minimum permissions required by the workflow, for example:

```yaml
permissions:
  contents: read
  id-token: write
```

`id-token: write` allows the workflow to request an OIDC token. It does not itself grant access to a cloud account.

The cloud provider must separately trust the GitHub Actions identity.

---

# OIDC with reusable workflows

OIDC is particularly useful for `ci-toolkit` because this repository provides reusable deployment workflows.

A future OIDC-enabled deployment workflow could look conceptually like:

```text
Application repository
        |
        | calls
        v
ci-toolkit reusable workflow
        |
        | requests OIDC token
        v
GitHub OIDC provider
        |
        | trusted identity
        v
Cloud IAM role
        |
        v
Deployment target
```

GitHub exposes claims that can be used by the external identity provider to restrict which repositories and reusable workflows may assume a role.

For example, a trust policy can restrict access based on:

```text
repository
organization
branch
environment
reusable workflow
workflow reference
```

This is especially valuable for a shared CI/CD repository.

---

# Recommended future design

If OIDC is added to `ci-toolkit`, it should be implemented as an explicit workflow capability rather than silently enabled for every workflow.

For example:

```yaml
permissions:
  contents: read
  id-token: write
```

should only be granted to workflows that actually require OIDC.

Do not add:

```yaml
permissions:
  id-token: write
```

to every reusable workflow.

Follow least privilege.

---

# OIDC and the three deployment strategies

`ci-toolkit` supports three deployment strategies:

```text
Docker Compose
Kubernetes / k3s
Helm
```

OIDC has a different role for each.

## Docker Compose

The current workflow deploys through SSH:

```text
GitHub Actions
      |
      | SSH private key
      v
Remote Docker host
      |
      v
Docker Compose
```

The workflow currently requires:

```text
ssh-host
ssh-user
ssh-private-key
```

and GHCR credentials.

OIDC is therefore **not currently used** for this deployment strategy.

---

## Kubernetes / k3s

The current workflow assumes the runner already has Kubernetes access:

```text
GitHub Actions
      |
      v
k3s self-hosted runner
      |
      | kubeconfig
      v
k3s
```

OIDC is **not currently used**.

---

## Helm

Helm uses the same underlying Kubernetes access:

```text
GitHub Actions
      |
      v
k3s runner
      |
      | kubeconfig
      v
Kubernetes
      ^
      |
     Helm
```

OIDC is **not currently used**.

---

# Security recommendation

If a future version introduces OIDC, prefer:

```text
short-lived federated credentials
```

over:

```text
long-lived cloud access keys
```

where the target platform supports this model.

The trust policy should be restrictive.

Do not configure a cloud role to trust every repository merely because it uses `ci-toolkit`.

Prefer restricting trust to the intended:

- organization
- repositories
- environments
- branches/tags
- reusable workflow
- workflow reference

GitHub specifically documents using reusable-workflow claims in OIDC trust conditions.

---

# Current status

**OIDC status: Not implemented in the current toolkit.**

Therefore:

- no `id-token: write` permission is currently required;
- no OIDC secret is required;
- Kubernetes does not authenticate through OIDC;
- Helm does not authenticate through OIDC;
- Docker Compose does not authenticate through OIDC;
- adding OIDC should be treated as a future enhancement.

This document should be updated when an OIDC-enabled reusable workflow is introduced.