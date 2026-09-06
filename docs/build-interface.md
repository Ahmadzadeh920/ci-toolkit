# Build Workflow Interface

[#build-workflow-interface](#build-workflow-interface)

This document defines the contract that **every** `reusable-build-*.yml`
workflow in this toolkit must satisfy, regardless of which build tool it
wraps internally (Docker, Cloud Native Buildpacks, Bazel, a Makefile, or a
precompiled/external artifact supplied by another pipeline).

`ci-toolkit` does not ship a generic `reusable-build.yml` dispatcher with a
`backend: docker|buildpacks|bazel` switch — the same way it does not ship a
generic deployment dispatcher (see the "Deployment strategies" section of the
README). Each build backend is a dedicated `workflow_call` workflow with its
own explicit, self-contained inputs. What makes them interchangeable is not
a shared implementation — it's a shared **output shape** that every
downstream workflow (`reusable-docker-push.yml`, `reusable-trivy.yml`, the
`reusable-deploy-*.yml` workflows) is written against.

A consuming repository's pipeline picks exactly one `reusable-build-*.yml`
matching its toolchain. Everything downstream of that call is written
against this contract, not against any specific backend.

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
- A reviewer adding a tenth build backend has a checklist to verify against,
  instead of having to reverse-engineer what "compatible" means from reading
  `reusable-docker-build.yml`'s source.

---

## Shared inputs

[#shared-inputs](#shared-inputs)

Every `reusable-build-*.yml` workflow must accept the following inputs,
with these exact names and semantics. It may accept additional
backend-specific inputs (e.g. `dockerfile`/`context` for Docker,
`builder-image` for Buildpacks) on top of these.

| Input | Type | Required | Meaning |
| --- | --- | --- | --- |
| `runner` | string | no | Runner label the build job executes on. |
| `image-name` | string | yes, if the backend produces an image | Image name/repository (without tag), e.g. `ghcr.io/org/app`. |
| `image-tag` | string | yes, if the backend produces an image | Tag to apply to the built image. |
| `registry` | string | no | Registry host to authenticate against when `push: true`. |
| `registry-username` | string | no | Registry username, paired with the `registry-password` secret. |
| `push` | boolean | no (default `false`) | If `true`, the backend must push the resulting image to `registry`. |
| `save-artifact` | boolean | no (default `false`) | If `true`, the backend must upload its build result (image tarball, binary, directory) via `actions/upload-artifact`. |
| `artifact-name` | string | yes, if `save-artifact: true` | Name under which the artifact is uploaded, and the name a downstream job (e.g. `reusable-docker-push.yml`) will use to download it. |

**Secrets:** any backend that supports `push: true` must accept a
`registry-password` secret, named identically to `reusable-docker-build.yml`'s.

## Shared outputs

[#shared-outputs](#shared-outputs)

Every `reusable-build-*.yml` workflow must declare exactly these three
`workflow_call` outputs:

| Output | Meaning |
| --- | --- |
| `image` | Fully qualified image reference (`registry/name:tag`) if the backend produced and pushed/loaded an image. **Empty string** if this build produced no image (e.g. a Makefile backend emitting a binary). |
| `digest` | Content digest of the pushed image (`sha256:...`). **Empty string** if not applicable. |
| `tags` | Newline- or comma-separated list of tags applied to the image. **Empty string** if not applicable. |

A backend must never rename these outputs (e.g. `image-ref` instead of
`image`) and must never omit them from its `workflow_call.outputs` block,
even when it sets them to an empty string. Downstream workflows are allowed
to assume all three output keys exist on every build job.

## The empty-output rule

[#the-empty-output-rule](#the-empty-output-rule)

Backends that don't produce a container image (see
`reusable-build-make.yml` as the reference implementation) must:

1. Set `image` and `digest` to empty strings rather than omitting them.
2. Still populate `artifact-name` when `save-artifact: true`, so that a
   downstream job can retrieve the build result the same way it would
   retrieve a saved Docker image tarball.

Downstream workflows must branch on emptiness rather than on which
`reusable-build-*.yml` produced their input. For example,
`reusable-trivy.yml` in `image` scan mode should be skipped by the caller
(or short-circuit internally) when the upstream build job's `image` output
is empty — not because "the Makefile backend was used," but because there
is no image to scan.

---

## Current implementations

[#current-implementations](#current-implementations)

| Workflow | Backend | Produces an image? |
| --- | --- | --- |
| `reusable-docker-build.yml` | `docker buildx build` from a `Dockerfile` | Yes |
| `reusable-build-buildpacks.yml` | Cloud Native Buildpacks (`pack build`) | Yes |
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
2. Implement the shared inputs and secrets listed above, using identical
   names.
3. Implement the shared outputs listed above, including the empty-string
   convention when not applicable.
4. Add an entry to `docs/reusable-workflows.md` under "Build workflows."
5. Add a row to the "Current implementations" table above.
6. Ship as a minor version bump — adding a new workflow file is additive
   and does not require a major version increase.
