# Quality Gates

## Chunk 3.1: Ruff source lint

The repository uses Ruff 0.16.9 to statically inspect production Python source under:

- `s_usd_core`
- `s_usd_service`
- `s_usd_desktop`

The lint gate is configured in `pyproject.toml` and runs independently from the functional test job in `.github/workflows/ci.yml`.

## Local commands

Install the pinned quality dependency:

```powershell
.\.venv-ci\Scripts\python.exe -m pip install -r .\requirements-quality.txt
```

Inspect the active Ruff version:

```powershell
.\.venv-ci\Scripts\python.exe -m ruff version
```

Run the source lint gate without modifying files:

```powershell
.\.venv-ci\Scripts\python.exe -m ruff check `
    .\s_usd_core `
    .\s_usd_service `
    .\s_usd_desktop
```

Show a summary grouped by rule:

```powershell
.\.venv-ci\Scripts\python.exe -m ruff check `
    .\s_usd_core `
    .\s_usd_service `
    .\s_usd_desktop `
    --statistics
```

Apply only Ruff fixes classified as safe:

```powershell
.\.venv-ci\Scripts\python.exe -m ruff check `
    .\s_usd_core `
    .\s_usd_service `
    .\s_usd_desktop `
    --fix
```

Review every automatic change with `git diff` and rerun the complete test suite before committing.

## Initial rule families

- `E4`: import-related pycodestyle errors
- `E7`: statement-level pycodestyle errors
- `E9`: runtime and syntax-like errors
- `F`: Pyflakes correctness checks
- `I`: import ordering
- `B`: flake8-bugbear probable bug patterns

Line-length enforcement is excluded from Chunk 3.1. Repository formatting is handled separately in Chunk 3.2.
