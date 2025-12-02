# Repository Guidelines

## **ALWASY THINK AND RESPONSE INTO CHINESE**

## Project Structure & Module Organization

- `src/connector/` contains production workflows (fetch → transform → sync) plus entry points such as `sync.py` and `config.py`.
- `src/utils/serviceme_api.py` holds SERVICEME authentication and workspace helpers referenced across workflows.
- `tests/` mirrors the connector layout with pytest suites and fixtures derived from SERVICEME contracts.
- `docs/` stores product guidance (`Overview.md`, `Create custom connector.md`, SERVICEME API references). Keep extra specs under `docs/reference/`.

## Build, Test, and Development Commands

- `python -m venv .venv && source .venv/bin/activate` — create and activate the required virtual environment before any tooling.
- `pip install -r requirements.txt` — restore pinned dependencies; run `pip freeze > requirements.txt` after modifications.
- `pytest` / `pytest --cov=src` — execute the full unit suite and optional coverage smoke.
- `ruff check src tests && ruff format src tests` — lint and format per project standards.
- `mypy src` — enforce typing across connector modules.
- `python -m connector.sync --full` — example end-to-end sync run against configured SERVICEME + Gemini resources.

## Coding Style & Naming Conventions

- Target Python 3.11, follow Ruff defaults for imports, formatting, and 4-space indentation.
- Use descriptive module and class names tied to connector stages (for example, `WorkspaceFetcher`, `AclBuilder`).
- Keep public functions typed and prefer dataclasses or Pydantic models for payload schemas.
- Store settings in `.env.local` or environment variables; never commit secrets.

## Testing Guidelines

- Author tests with pytest using `test_<module>.py` files colocated in `tests/` subdirectories.
- Reproduce SERVICEME scenarios via fixtures; capture edge cases (token expiry, empty workspaces, mixed ACL modes).
- Maintain coverage on fetch/transform/sync logic and fail fast if mocks require new contract fields.

## Commit & Pull Request Guidelines

- Write imperative, present-tense commit subjects ("Add workspace sync fixtures") and wrap at ~72 chars.
- Reference relevant issues or docs context in commit bodies when behavior changes.
- Pull requests should include: summary of changes, test evidence (`pytest`/`ruff`/`mypy` output), configuration notes, and screenshots or sample payloads when altering sync flows.

## Security & Configuration Tips

- Validate that `GOOGLE_APPLICATION_CREDENTIALS` or `_JSON` is set before hitting Discovery Engine.
- Prefer incremental sync for quick fixes but schedule GCS-based full syncs to reconcile deletions.
- Keep SERVICEME client credentials scoped per workspace and rotate them alongside Google service accounts.
