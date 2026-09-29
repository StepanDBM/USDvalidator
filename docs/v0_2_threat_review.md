# S-USDv v0.2 Threat Review

## Scope

This review covers the desktop-to-service trust boundary, authentication and refresh sessions, workspace authorization, catalog and file APIs, provider-neutral object storage, durable validation jobs, project administration, and release operations. Local-only OpenUSD workflows remain outside the service trust boundary.

## Assets and trust boundaries

- Credentials: passwords, password hashes, access tokens, refresh tokens, and signing keys.
- Authorization data: users, workspaces, memberships, roles, project ownership, and platform-administrator flags.
- Production data: uploaded USD bytes, checksums, catalog metadata, validation reports, and publish fingerprints.
- Execution state: validation jobs, attempts, heartbeats, cancellation, and linked ValidationRuns.
- Desktop cache: downloaded service content is untrusted until size and SHA-256 verification passes.

The desktop is untrusted from the service's perspective. The API is the authentication and authorization enforcement point. The database and object store are persistent trust boundaries. `s_usd_core` has no identity authority.

## Reviewed threats and controls

### Credential disclosure and token replay

Passwords use Argon2id through `pwdlib`; plaintext passwords are never persisted. Access tokens are short-lived and audience/issuer checked. Refresh tokens are stored as hashes, rotate on refresh, and reuse revokes the session family. Logout and disabled-user checks are covered by service tests. Signing keys are environment configuration and must not be committed.

Residual risk: local development `.env` files can be copied or exposed by workstation compromise. Staging must use a deployment secret manager and HTTPS termination.

### User enumeration

Login uses a single non-revealing `401 Invalid email or password` response. Registration conflict responses can reveal an existing address and therefore registration should be disabled outside controlled onboarding.

### Cross-workspace access and IDOR

Resource authorization follows Project -> Workspace and Version -> Stream -> Asset -> Project -> Workspace. Valid UUIDs do not grant access. Cross-workspace reads and mutations return non-disclosing failures. The API remains authoritative even when the desktop hides controls.

Residual risk: every new route must call an authorization repository method before returning resource data. Code review and parameterized authorization tests remain mandatory.

### Privilege escalation

Roles are fixed to Viewer, Contributor, Administrator, and Owner. Membership mutation checks prevent Administrators from managing Administrators and preserve at least one Owner. Platform-administrator behavior is explicit. Project administration requires `manage_projects`.

### Uploaded paths and object storage

Relative paths and storage keys reject absolute paths and traversal. Writes stream to temporary content, enforce configured limits, verify size and SHA-256, and promote completed objects atomically. Failed and cancelled transfers remove partial content. Reconciliation detects missing and orphaned objects.

Residual risk: v0.2 ships the local provider only. Any future Azure Blob Storage adapter must pass the same provider contract and use provider-side conditional writes where needed.

### Durable-job duplication and state corruption

Idempotency is unique per workspace, requester, and key. Job state, progress, attempts, heartbeat, and failures are persisted. Startup recovery deterministically requeues or fails abandoned jobs. A successful job and its ValidationRun link commit together.

Residual risk: v0.2 permits one enabled in-process worker per deployment. Multiple replicas require an atomic database claim such as PostgreSQL `FOR UPDATE SKIP LOCKED` before concurrent workers are supported.

### Sensitive diagnostics

API errors use bounded messages and authentication failures are non-revealing. Validation-job exceptions are persisted with bounded error codes and messages. Logs, reports, and error payloads must not contain passwords, signing keys, raw refresh tokens, database credentials, or storage credentials.

## Deferred controls

Microsoft Entra ID, OAuth/OIDC, MFA, password-reset delivery, personal access tokens, production Azure Blob Storage, distributed workers, multi-region deployment, and automatic production deployment remain outside v0.2.0. These omissions are accepted only for the initial foundation release and local or controlled staging usage.

## Release decision

No unresolved threat blocks a local or controlled single-worker v0.2.0 release candidate when all automated quality, dependency, CodeQL, migration, authorization, storage, job-recovery, and desktop-session gates pass. Internet-facing deployment remains blocked until HTTPS, managed secrets, PostgreSQL, allowed-host/origin policy, operational backup, and staging incident procedures are supplied.
