## Chunk 3 baseline

The repository maintains independent functional, quality, dependency, and semantic-security gates.

### Tool versions

- Python 3.12
- Ruff 0.16.9
- Bandit 1.9.4
- pip-audit 2.10.1
- CodeQL Action v4

### Local baseline

- Ruff lint: passing
- Ruff formatting: 277 production files compliant
- Bandit: no active findings
- pip-audit: no known vulnerabilities
- Functional tests: 287 passed

### Hosted CI

The CI workflow runs three independent jobs:

1. Python 3.12 tests
2. Source quality and security
3. Python dependency audit

The CodeQL workflow runs two independent semantic analyses:

1. Python
2. GitHub Actions

### CodeQL coverage

- Python: 379 of 379 files scanned
- GitHub Actions: 2 of 2 workflow files scanned

### Required checks for main

The `main` branch requires the following checks:

- Python 3.12 tests
- Source quality and security
- Python dependency audit
- Analyze Python
- Analyze GitHub Actions

Branches must be up to date with `main` before merging. Force pushes and branch deletion are blocked.

### Exception policy

Security findings must be fixed or reviewed individually. Suppressions must identify the exact rule and include a concrete justification. Broad rule suppression is not accepted.

Dependency vulnerability exceptions must reference a specific advisory identifier and be reviewed when an upstream fix becomes available.


## CI 3 Verification

CI 3 established the following required repository gates:

- Python 3.12 tests
- Ruff source lint
- Ruff source formatting
- Bandit Python security scanning
- pip-audit dependency vulnerability scanning
- CodeQL Python analysis
- CodeQL GitHub Actions analysis

The protected `main` branch requires the configured CI and CodeQL checks to complete successfully before pull requests can be merged.