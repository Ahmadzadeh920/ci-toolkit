# Build Workflow Interface

[#build-workflow-interface](#build-workflow-interface)

This document defines the contract that **every** `reusable-build-*.yml`
workflow in this toolkit must satisfy, regardless of which build tool it
wraps internally (Docker, Cloud Native Buildpacks, Bazel, a Makefile, or a
precompiled/external artifact supplied by another pipeline).

`ci-toolkit` does not ship a generic `reusable-build.yml` dispatcher with a
`backend: docker|buildpacks|bazel` switch — the same way it does not ship a
generic deployment dispatcher (see the "Deployment strategies" section of
the README). Each build backend is a dedicated `workflow_call` workflow
with its own explicit, self-contained inputs. What makes them
interchangeable is not a shared implementation — it's a shared **output
shape** that `reusable-docker-push.yml` and every other downstream
workflow is written against.

A consuming repository's pipeline picks exactly one `reusable-build-*.yml`
matching its toolchain. Everything downstream of that call is written
against this contract, not against any specific backend.

---

## Scope: build produces a local artifact, it does not push

[#scope](#scope)

`reusable-docker-build.yml` never pushes to a registry — it builds locally
(`load` into the runner's Docker daemon), optionally `docker save`s the
result to a tarball, and uploads that tarball as a workflow artifact.
Registry authentication, tagging for a remote registry, pushing, and
resolving a real registry digest are the job of `reusable-docker-push.yml`,
a separate downstream workflow that downloads the artifact by name.

Every `reusable-build-*.yml` workflow follows the same split:

- **Build's job:** produce the artifact (a local image, a binary, a
  bundle) and optionally hand it off as a named workflow artifact.
- **Push's job:** consume that artifact by name, authenticate, and publish
  it. This is out of scope for the build interface itself.

This is why the build contract below has no `push`, `registry`, or
`registry-password` — those inputs/secrets exist on `reusable-docker-push.yml`,
not on the build workflows.

---

## Why this exists

[#why-this-exists](#why-this-exists)

Before this contract existed, the toolkit's build step had one implicit
rule: "there is a Dockerfile at some path, build it." That's fine for
Docker-based services, but a Golden Template used across a polyglot
organization will eventually meet a repository that builds with Buildpacks,
Bazel, a Makefile, or produces a plain binary/tarball with no image at all.
Hard-coding Docker as *the* build mechanism means every one of those
repositories either can't use the toolkit, or has to fake a Dockerfile just
to satisfy the pipeline.

Defining the contract explicitly, in one place, means:

- New build backends can be added without touching `reusable-docker-push.yml`,
  `reusable-trivy.yml`, or any `reusable-deploy-*.yml` workflow.
- Downstream workflows can be written once, against the contract, instead of
  against `reusable-docker-build.yml` specifically.
- A reviewer adding a new build backend has a checklist to verify against,
  instead of having to reverse-engineer what "compatible" means from reading
  `reusable-docker-build.yml`'s source.

---

## Shared inputs

[#shared-inputs](#shared-inputs)

Every `reusable-build-*.yml` workflow must accept the following inputs,
with these exact names and semantics. It may accept additional
backend-specific inputs (e.g. `dockerfile`/`context` for Docker,
`builder-image` for Buildpacks) on top of these.

| Input | Type | Required | Default | Meaning |
| --- | --- | --- | --- | --- |
| `runner` | string | no | `ubuntu-latest` | Runner label the build job executes on. |
| `image-name` | string | yes, if the backend produces an image | — | Local image name (no registry host required — the registry host is added later, by `reusable-docker-push.yml`). |
| `image-tag` | string | no | `latest` | Tag applied to the locally built image. |
| `save-artifact` | boolean | no | `true` | If `true`, upload the build result via `actions/upload-artifact` so a downstream job (typically `reusable-docker-push.yml`) can retrieve it. |
| `artifact-name` | string | no | backend-specific (e.g. `docker-image`) | Name under which the artifact is uploaded. |
| `timeout-minutes` | number | no | `30` | Job timeout. |

There is **no** `push`, `registry`, `registry-username` input and **no**
`registry-password` secret on any build workflow. Pushing is
`reusable-docker-push.yml`'s responsibility.

## Shared outputs

[#shared-outputs](#shared-outputs)

Every `reusable-build-*.yml` workflow must declare exactly these four
`workflow_call` outputs:

| Output | Meaning |
| --- | --- |
| `image-name` | The image name that was built. **Empty string** if this backend produced no image. |
| `image-tag` | The tag that was applied. **Empty string** if this backend produced no image. |
| `image` | `image-name:image-tag` combined. **Empty string** if this backend produced no image. |
| `artifact-name` | The name the build result was (or would be) uploaded under — always populated, even if `save-artifact` was `false`, matching `reusable-docker-build.yml`'s existing behavior. |

A backend must never rename these outputs and must never omit them from
its `workflow_call.outputs` block, even when it sets some of them to an
empty string. Downstream workflows are allowed to assume all four output
keys exist on every build job.

## The empty-output rule

[#the-empty-output-rule](#the-empty-output-rule)

Backends that don't produce a container image (see
`reusable-build-make.yml` as the reference implementation) must set
`image-name`, `image-tag`, and `image` to empty strings. `artifact-name`
is still populated, since the raw build output (a binary, a bundle) is
still uploaded as an artifact even when it isn't a container image.

Downstream workflows must branch on emptiness rather than on which
`reusable-build-*.yml` produced their input. For example, a caller should
skip `reusable-docker-push.yml` or `reusable-trivy.yml` (image scan mode)
when the upstream build job's `image` output is empty — not because "the
Makefile backend was used," but because there is no image to push or scan.

---

## Current implementations

[#current-implementations](#current-implementations)

| Workflow | Backend | Produces an image? |
| --- | --- | --- |
| `reusable-docker-build.yml` | `docker buildx build` from a `Dockerfile`, local build + optional tar artifact | Yes |
| `reusable-build-buildpacks.yml` | Cloud Native Buildpacks (`pack build`), local build + optional tar artifact | Yes |
| `reusable-build-make.yml` | Arbitrary `make`/shell build command | No (artifact only), optionally Yes if a wrapper Dockerfile is supplied |

A consuming repository selects **exactly one** of these per build job,
exactly as it selects exactly one `reusable-deploy-*.yml` workflow.

---

## Adding a new backend

[#adding-a-new-backend](#adding-a-new-backend)

When contributing a new `reusable-build-<backend>.yml`:

1. Name it `reusable-build-<backend>.yml` (existing exception:
   `reusable-docker-build.yml` keeps its original name to avoid a breaking
   rename of a workflow already referenced by consumers).
2. Implement the shared inputs listed above, using identical names — no
   registry/push inputs.
3. Implement the shared outputs listed above, including the empty-string
   convention when not applicable.
4. Do not add a `registry-password` secret or any registry-auth step —
   that belongs in `reusable-docker-push.yml` only.
5. Add an entry to `docs/reusable-workflows.md` under "Build workflows."
6. Add a row to the "Current implementations" table above.
7. Ship as a minor version bump — adding a new workflow file is additive
   and does not require a major version increase.
