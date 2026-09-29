# S-USDv v0.2 Readiness Report

## Release identity

- Version: `0.2.0`
- Release name: Multi-user Service Foundation
- Schema head: `0008`
- Python baseline: 3.12
- Local database: SQLite
- Initial staging database assumption: PostgreSQL
- Worker topology: one enabled in-process validation worker

## Implemented release contract

- Identity: users, Argon2id password hashes, access tokens, rotating refresh sessions, logout, disabled-account enforcement, and current-user API.
- Authorization: workspaces, one fixed role per membership, server-side permission checks, final-owner protection, and cross-workspace isolation.
- Desktop session: login, token attachment, transparent refresh, logout, workspace selection, and preserved local mode.
- Storage: provider protocol, configuration-driven local provider, verified streaming transfer, safe keys, atomic promotion, cleanup, reconciliation, and shared contract tests.
- Durable validation: persisted jobs, idempotency, progress, attempts, heartbeat, bounded retry, restart recovery, cancellation, safe failure fields, and exactly one linked ValidationRun.
- Project administration: workspace ownership, creator provenance, lifecycle statuses, profile assignment, filtering, archive preservation, and restoration.

## Automated acceptance evidence

The release-candidate gate requires:

1. `python scripts/ci/verify_v0_2_readiness.py --full`
2. Complete test suite passing on Python 3.12.
3. Ruff lint and formatting passing.
4. Bandit passing at medium/high severity threshold.
5. `pip check` passing.
6. `pip-audit` reporting no unhandled advisory.
7. CodeQL Python and GitHub Actions analysis passing.
8. Alembic migration compatibility from a populated `0004` database to `0008`.
9. Protected `main` requiring the hosted checks.

The report is a release gate, not a claim that an arbitrary checkout is ready. Record the final command output and Git commit SHA in the pull request before tagging.

## Manual acceptance

- Sign in and select an authorized workspace in the desktop.
- Confirm local mode works while signed out and disconnected.
- Upload, download, checksum-verify, validate, publish, and reopen a version.
- Submit a durable validation job, observe success, verify exactly one ValidationRun, repeat its idempotency key, cancel a pending job, and restart with an abandoned job fixture.
- Create, filter, place on hold, archive, inspect retained history, reject archived mutation, and restore a project.
- Attempt representative Viewer, Contributor, Administrator, Owner, unauthenticated, and cross-workspace operations.

## Staging blockers that do not block the local release candidate

- PostgreSQL deployment and backup/restore rehearsal.
- HTTPS ingress and trusted-host/CORS policy.
- Managed secret injection and key-rotation procedure.
- Persistent object storage outside the service container.
- Operational logs, metrics, alerting, and incident runbook.

These items block an internet-facing staging or production declaration, but do not invalidate the v0.2 foundation contract.

## Tagging decision

Tag `v0.2.0-rc.1` only from protected `main` after all required checks pass. Tag final `v0.2.0` after the release-candidate checklist, migration rehearsal, and manual acceptance are recorded with no blocking defect.
