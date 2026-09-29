# S-USDv v0.2 Release Contract

## Document status

- **Milestone:** Chunk 4.1, Product roadmap and release boundary
- **Target release:** v0.2.0
- **Release name:** Multi-user Service Foundation
- **Status:** Accepted implementation contract
- **Scope owner:** S-USDv product and engineering roadmap

## 1. Purpose

S-USDv v0.2.0 will establish the multi-user and deployment-ready foundation required before container packaging and staging delivery.

The release adds authenticated service access, workspace-scoped ownership, role-based authorization, provider-independent storage boundaries, durable validation work, and project administration foundations while preserving the existing local OpenUSD workflows.

This contract freezes the intended v0.2 boundary before database migrations, API contracts, desktop session behavior, and authorization rules become implementation commitments.

## 2. Current product baseline

The current product already provides:

- A reusable `s_usd_core` validation, extraction, comparison, and reporting engine.
- A FastAPI and SQLAlchemy service under `s_usd_service`.
- A PySide6 desktop application under `s_usd_desktop`.
- Catalog hierarchy: Project → Asset → Stream → Version.
- Stored files and validation history.
- Content fingerprints and publish fingerprints.
- Version lifecycle states: draft, uploaded, validation failed, validated, published, and deprecated.
- Publish protection requiring a passing root-layer validation and a matching content fingerprint.
- Local object storage with verified transfers and reconciliation behavior.
- Local and service-backed desktop workflows.
- Registry-driven validation profiles, structured reports, manifests, comparison domains, and OpenUSD viewport integration where the complete runtime is available.

The current service does not yet define authenticated users, workspace ownership, membership, role-based permissions, durable service-side jobs, or a provider-selection boundary for cloud object storage.

## 3. v0.2 product statement

> S-USDv v0.2 introduces authenticated service access, workspace-scoped collaboration, role-based authorization, provider-independent storage, and durable validation execution while preserving the existing local validation workflow and published validation/report contracts.

## 4. Release principles

### 4.1 Core isolation

`s_usd_core` must remain independent from authentication, HTTP sessions, database users, workspaces, and deployment providers.

```text
s_usd_core
    No identity or authorization knowledge

s_usd_service
    Authenticates requests and enforces authorization

s_usd_desktop
    Maintains an optional service session
```

### 4.2 Local mode remains first-class

A user must be able to open, inspect, validate, compare, batch-process, and export reports for local OpenUSD content without:

- A user account.
- A running API service.
- A database connection.
- A network connection.
- Workspace membership.
- Remote object storage.

### 4.3 Service access is never anonymous

All catalog, file, validation-history, storage-reconciliation, membership, and administration endpoints introduced or protected by v0.2 require authenticated service access, except explicitly public operational endpoints such as health and readiness.

### 4.4 Ownership is explicit

Every service-side project belongs to exactly one workspace. Every service-side resource is authorized through its workspace ownership chain.

### 4.5 Security decisions are server-side

The desktop client may hide unavailable commands for usability, but the service remains the authority. The API must enforce authorization for every protected operation regardless of client behavior.

### 4.6 Compatibility before convenience

Existing report schemas, manifest schemas, validation fingerprints, stored-file checksums, and lifecycle semantics must remain readable and meaningful after migration.

## 5. Required v0.2 capabilities

### 5.1 Identity foundation

v0.2 must include:

- User records with stable identifiers.
- Unique normalized email addresses.
- Display names and account status.
- Password hashing using Argon2id through a reviewed library.
- Short-lived access tokens.
- Rotating refresh sessions.
- Session revocation and logout.
- Current-user endpoint.
- Disabled-user enforcement.
- Authentication audit timestamps.
- Authentication API and security tests.

### 5.2 Workspace authorization

v0.2 must include:

- Workspace records.
- Workspace memberships.
- Exactly one role per membership.
- Roles: Owner, Administrator, Contributor, Viewer.
- Workspace-scoped projects.
- Resource lookups constrained through workspace ownership.
- Role-based catalog, file, validation, publish, and administration policies.
- Authorization matrix and cross-workspace access tests.

### 5.3 Desktop authentication

v0.2 must include:

- Service login UI.
- Authenticated connection state.
- Access-token attachment to service requests.
- Transparent token refresh.
- Logout.
- Expired or revoked session handling.
- Workspace selection.
- Clear unauthorized and forbidden failure states.
- Preservation of unauthenticated local mode.

### 5.4 Storage-provider boundary

v0.2 must include:

- Preservation of `LocalObjectStorage` behavior.
- A formal storage-provider protocol or abstract interface.
- Configuration-driven provider creation.
- Verified streaming writes and reads.
- File-size and SHA-256 verification.
- Atomic promotion semantics.
- Cleanup after failed or cancelled transfers.
- Shared provider contract tests.
- An Azure-ready boundary without requiring the Azure implementation to block v0.2.0.

### 5.5 Durable validation jobs

v0.2 must include:

- Persisted job records.
- States: Pending, Running, Cancelling, Cancelled, Succeeded, Failed.
- Requester provenance.
- Workspace and version ownership.
- Idempotency keys.
- Progress persistence.
- Attempt counts and bounded retry policy.
- Heartbeat or liveness information.
- Restart reconciliation for abandoned running work.
- Cancellation contract.
- Safe failure diagnostics.
- Exactly one successful `ValidationRun` result per successful job.

### 5.6 Project administration foundation

v0.2 must include:

- Workspace-scoped projects.
- Project code, name, description, and status.
- Created-by provenance.
- Default validation-profile assignment.
- Project filtering.
- Archive behavior that does not delete immutable history.

## 6. Deferred capabilities

The following capabilities are explicitly outside the v0.2.0 release gate:

- Production Azure Blob Storage provider.
- Microsoft Entra ID, OAuth, or OpenID Connect.
- Password-reset email delivery.
- Multi-factor authentication.
- Personal access tokens or API keys.
- Custom role creation.
- Full retroplanning and timeline visualization.
- Deliverable dependency graphs.
- ShotGrid integration.
- Maya integration.
- Automatic production deployment.
- Multi-region storage or deployment.
- Distributed worker orchestration through Celery, Redis, Kubernetes, or equivalent infrastructure.

These may be delivered in v0.2.1, v0.3, or later milestones without changing the v0.2 foundation.

## 7. Deployment assumptions

### 7.1 v0.2 staging assumptions

- Python 3.12 runtime.
- PostgreSQL for shared staging service data.
- Persistent object storage mounted or provided independently of the service process.
- HTTPS termination outside the application process.
- Secrets supplied through environment variables or a deployment secret manager.
- Database migrations executed before serving application traffic.
- Health and readiness endpoints available without regular user authentication.
- One in-process durable validation worker for the initial staging architecture.
- No anonymous access to catalog, files, validation history, or administration.

### 7.2 Local development assumptions

- SQLite remains supported for local development and tests.
- Local object storage remains supported.
- The desktop can run without the service.
- CI continues to use an isolated test database and temporary storage roots.

### 7.3 Configuration assumptions

Secrets and environment-specific configuration must not be stored in source control or database content intended for export.

Expected future configuration categories include:

```text
Database connection
Token signing key and algorithm
Token issuer and audience
Access and refresh lifetimes
Storage provider selection
Storage provider credentials
Allowed origins and hosts
Operational logging level
Worker recovery and retry values
```

## 8. Compatibility contract

### 8.1 Core behavior

The following local workflows must continue to work without authentication:

- Open local USD stages.
- Build Stage Health reports.
- Run single-file validation.
- Run recursive batch validation.
- Compare local stages.
- Inspect validation targets.
- Use validation profiles and overrides.
- Export reports and manifests.
- Use the OpenUSD viewport when runtime capabilities are available.

### 8.2 Service data

Existing catalog records must migrate without loss:

```text
Project
└── Asset
    └── Stream
        └── Version
            ├── StoredFile
            └── ValidationRun
```

Existing projects must be assigned deterministically to a bootstrap workspace during migration.

### 8.3 Reports and fingerprints

- `s-usdv.validation_report` schema `1.0.0` remains readable.
- `s-usdv.publish_manifest` schema `1.0.0` remains readable.
- Existing content fingerprints retain their meaning.
- Existing published-content fingerprints retain their meaning.
- Existing stored-file SHA-256 values remain valid.
- Existing validation configuration and check-catalog fingerprints retain their comparison semantics.

### 8.4 Version lifecycle

The lifecycle contract remains:

```text
draft
→ uploaded
→ validation_failed or validated
→ published
→ deprecated
```

Published and deprecated versions remain immutable. Publishing still requires the latest acceptable root-layer validation to match the current content fingerprint.

## 9. Authorization contract

### 9.1 Roles

```text
Viewer
├── Read projects and catalog hierarchy
├── Read validation history
├── Read published reports
└── Download authorized files

Contributor
├── All Viewer permissions
├── Create assets and streams
├── Create draft versions
├── Upload files to mutable versions
├── Delete files from mutable versions
└── Request validation jobs

Administrator
├── All Contributor permissions
├── Create and archive projects
├── Configure project validation policy
├── Publish and deprecate versions
├── Manage Viewer and Contributor memberships
└── Run storage reconciliation

Owner
├── All Administrator permissions
├── Manage Administrators
├── Transfer workspace ownership
└── Deactivate the workspace
```

### 9.2 Invariants

- A workspace always has at least one Owner.
- A user can have at most one active membership per workspace.
- Project resource access is always constrained through workspace membership.
- A valid UUID does not imply authorization.
- Cross-workspace reads and mutations are rejected.
- Published and deprecated immutability rules apply regardless of role.
- Platform-administrator behavior, if implemented, must be explicit and auditable.

## 10. Authentication contract

### 10.1 Credentials

- Passwords are never stored, returned, or logged in plaintext.
- Password hashes use Argon2id through a reviewed dependency.
- Minimum password length is 12 characters.
- Login failure does not reveal whether an email address exists.

### 10.2 Tokens and sessions

Recommended initial policy:

```text
Access token lifetime:      15 minutes
Refresh-session lifetime:   30 days
Clock-skew allowance:       30 seconds
Refresh rotation:           Every successful refresh
Maximum active sessions:    10 per user
```

Access tokens identify the user and session but do not permanently embed workspace permissions. Current membership and role are resolved against service data.

Refresh tokens are stored only as hashes. Reuse of a rotated refresh token revokes the affected session chain.

### 10.3 Responses

- Missing or invalid authentication returns HTTP 401.
- Authenticated users without permission receive HTTP 403, unless the endpoint intentionally uses HTTP 404 to avoid disclosing resource existence.
- Disabled or revoked accounts cannot create or refresh sessions.

## 11. Threat boundaries

### 11.1 Untrusted inputs

Treat the following as untrusted:

- Login and registration values.
- Access and refresh tokens.
- Workspace, project, asset, stream, version, file, and job identifiers.
- Uploaded filenames and relative paths.
- Uploaded file content.
- Validation report payloads submitted by clients.
- Query filters and pagination values.
- Storage keys.
- Desktop-cached service data.

### 11.2 Primary threats

v0.2 must explicitly defend against:

- Credential disclosure.
- Password-hash compromise.
- Token theft and refresh-token replay.
- User enumeration.
- Cross-workspace object access.
- Privilege escalation.
- Insecure direct object references.
- Storage path traversal.
- Partial or corrupted uploads.
- Duplicate validation execution.
- Job-state corruption after restart.
- Sensitive information in logs or error messages.
- Unauthorized publish, deprecate, delete, or reconciliation operations.

### 11.3 Trust boundaries

```text
Desktop client
    Untrusted from the service's perspective

Service API
    Authentication and authorization enforcement point

Database
    Persistent identity, ownership, lifecycle, and job state

Object storage
    Persistent file bytes addressed through validated storage keys

s_usd_core
    Pure domain processing without user/session authority
```

## 12. Acceptance criteria

### 12.1 Identity and session acceptance

- A valid active user can authenticate.
- Invalid credentials return a non-revealing 401 response.
- A disabled user cannot authenticate or refresh.
- Access tokens expire after the configured lifetime.
- Refresh tokens rotate after every successful refresh.
- Reusing a rotated token revokes the affected session chain.
- Logout revokes the selected session.
- Passwords and raw refresh tokens never appear in database values, logs, exceptions, or API responses.

### 12.2 Authorization acceptance

- Unauthenticated protected requests return 401.
- Cross-workspace access is rejected.
- Viewers cannot mutate catalog, files, versions, jobs, or memberships.
- Contributors cannot manage memberships or publish versions.
- Administrators cannot remove or demote the final Owner.
- Only permitted roles can publish or deprecate versions.
- Download, validation history, job status, and reconciliation endpoints enforce workspace access.
- Authorization rules have parameterized regression tests for all roles and protected operations.

### 12.3 Desktop acceptance

- A user can connect and sign in.
- Authenticated service calls include the current access token.
- Expired access tokens refresh transparently when the refresh session remains valid.
- Revoked or expired refresh sessions return the desktop to a clear signed-out state.
- Logout removes locally retained session material.
- Workspace selection scopes the visible catalog.
- Local mode remains fully usable without login.

### 12.4 Storage acceptance

- The local provider passes the shared provider contract suite.
- Successful writes reproduce exact bytes, size, and SHA-256.
- Failed writes do not promote partial content.
- Failed replacement preserves the previous complete object.
- Unsafe storage keys are rejected.
- Cancellation removes temporary content.
- Provider selection is configuration-driven.

### 12.5 Durable-job acceptance

- Repeating the same idempotency key does not create duplicate jobs.
- Job state and progress survive service restart.
- Abandoned running jobs are recovered or failed deterministically.
- Cancellation reaches a terminal state.
- Successful jobs create exactly one `ValidationRun`.
- Failure messages are useful but do not leak secrets or internal credentials.
- Job visibility and cancellation enforce workspace permissions.

### 12.6 Migration and compatibility acceptance

- Alembic upgrades an existing `0004` database without losing catalog, stored-file, validation-run, or fingerprint data.
- Existing projects are assigned to a documented bootstrap workspace.
- Existing reports and manifests remain readable.
- Existing published and deprecated versions remain immutable.
- Local mode remains operational.
- Existing tests remain green or are deliberately updated with documented contract changes.

### 12.7 Quality-gate acceptance

Before v0.2.0 release candidate tagging:

- Ruff lint passes.
- Ruff formatting passes.
- Bandit passes at the configured blocking threshold.
- pip-audit reports no unhandled advisories.
- CodeQL Python analysis completes.
- CodeQL GitHub Actions analysis completes.
- Authentication, authorization, storage, migration, desktop-session, and job-recovery tests pass.
- The complete hosted CI workflow passes.
- Required checks protect `main`.

## 13. Planned migration boundary

The first v0.2 schema migration is expected to introduce or prepare:

```text
users
refresh_sessions
workspaces
workspace_memberships
projects.workspace_id
projects.created_by_user_id
```

A later migration in the same milestone may introduce:

```text
validation_jobs
project status and default validation profile
additional audit timestamps
```

Migration details are implementation work for Chunks 4.2, 4.3, 4.6, and 4.7. This contract defines the required behavior but does not prematurely freeze column-level implementation beyond required ownership and session relationships.

## 14. Release exit decision

v0.2.0 may be declared ready only when every required capability and acceptance criterion in this contract is implemented or explicitly removed through a reviewed contract revision.

Deferred capabilities do not block v0.2.0.

Changes to this release boundary require a dedicated documentation commit explaining:

- What changed.
- Why the original contract is no longer appropriate.
- Which migrations, APIs, clients, tests, or security assumptions are affected.
