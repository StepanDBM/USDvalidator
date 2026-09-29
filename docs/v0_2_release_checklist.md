# S-USDv v0.2 Release Checklist

## Source and version

- [ ] Protected `main` is clean and synchronized.
- [ ] Service health reports `0.2.0`.
- [ ] Alembic reports `0008 (head)`.
- [ ] No secret, `.env`, database, cache, bytecode, or temporary launcher is tracked.

## Automated gates

- [ ] `verify_v0_2_readiness.py --full` passes.
- [ ] Complete Python 3.12 suite passes.
- [ ] Ruff lint passes.
- [ ] Ruff format check passes.
- [ ] Bandit has no medium/high finding.
- [ ] `pip check` passes.
- [ ] `pip-audit` has no unhandled advisory.
- [ ] CodeQL Python passes.
- [ ] CodeQL GitHub Actions passes.

## Compatibility

- [ ] Populated `0004` database upgrades to `0008` without catalog, file, validation, or fingerprint loss.
- [ ] Existing validation report schema `1.0.0` remains readable.
- [ ] Existing publish manifest schema `1.0.0` remains readable.
- [ ] Published and deprecated versions remain immutable.
- [ ] Signed-out local OpenUSD workflows remain operational.

## Security and operations

- [ ] Threat review has no unresolved release blocker.
- [ ] Registration policy is explicit for the target environment.
- [ ] Token signing key is externally supplied and at least 32 characters.
- [ ] One and only one worker is enabled per v0.2 deployment.
- [ ] Database and storage backup/restore procedure is documented before staging.
- [ ] HTTPS and managed secrets are required before internet exposure.

## Release commands

```powershell
.\.venv-ci\Scripts\python.exe .\scripts\ci\verify_v0_2_readiness.py --full
.\.venv-ci\Scripts\python.exe -m alembic current
git status
git tag -a v0.2.0-rc.1 -m "S-USDv v0.2.0 release candidate 1"
git push origin v0.2.0-rc.1
```

Do not create the final `v0.2.0` tag until the release candidate is accepted.
