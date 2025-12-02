# Gemini Enterprise SERVICEME Custom Connector

This repository bootstraps a **Gemini Enterprise custom connector** that ingests SERVICEME knowledge bases through the SERVICEME OpenAPI and syncs them into [Google Cloud Discovery Engine](https://docs.cloud.google.com/generative-ai-app-builder/docs/reference/rest) data stores. Use it as the reference implementation when you register a bespoke connector inside Gemini Enterprise.

## Connector architecture

- **Fetch** – Use SERVICEME APIs to authenticate, list workspaces, and pull knowledge assets (see `docs/Open API | SERVICEME.md`).
- **Transform** – Normalize payloads into the Discovery Engine [Document](https://docs.cloud.google.com/generative-ai-app-builder/docs/reference/rest/v1/projects.locations.collections.dataStores.branches.documents) format, attach metadata, and build ACLs (`docs/Overview.md` and `docs/Create custom connector.md` outline the expected shape).
- **Sync** – Import data into a Gemini data store through incremental upserts or a GCS-backed full sync (`docs/Overview.md` §Data sync). Support both pure ACLs and identity mapping depending on whether SERVICEME returns Google-recognized principals.
- **Identity & access** – Create/bind an Identity Mapping Store before creating the entity data store, ingest external identities, and tie the mapping store to your data store (`docs/Create custom connector.md` §Identity mapping).
- **Reference set** – Drop additional API specifications (for example, the raw SERVICEME OpenAPI JSON) inside `docs/reference/` to keep design discussions and code changes aligned.

## Repository layout

- `src/connector/` – Production modules for clients, schemas, utilities, and workflows (fetch → transform → sync). The compiled artifacts under `__pycache__` show the expected entry points such as `config.py`, `sync.py`, and workflow helpers.
- `src/utils/serviceme_api.py` – Stand-alone helpers that illustrate how to authenticate, enumerate workspaces, and issue `/v1/openapi/rag` queries via `httpx`.
- `tests/` – Pytest suites mirroring the connector layout (client, utils, workflows) with fixtures derived from the SERVICEME OpenAPI.
- `docs/` – Mirrored product docs from Google (“Overview” + “Create custom connector”) and SERVICEME (“Open API | SERVICEME”). Use `docs/reference/` for any extra specs shared by your stakeholders.

## Prerequisites

1. **Google Cloud project** with billing enabled, Gemini Enterprise access, and Discovery Engine admin permissions.
2. **Google Cloud CLI** installed and initialized (`gcloud init`), or a service account JSON that can be used via `GOOGLE_APPLICATION_CREDENTIALS`.
3. **SERVICEME OpenAPI credentials** – client ID, client secret, and a workspace-scoped account for `/openapi/auth/client_with_account`.
4. **Python 3.11+** plus the ability to create a virtual environment.
5. A clear **data mapping & ACL plan** (which fields to index, whether to use pure ACLs vs. identity mapping).

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt      # keep this file updated via `pip freeze > requirements.txt`
```

Always activate `.venv` before running any Python, test, or lint command. After installing or upgrading dependencies, run `pip freeze > requirements.txt` to lock the environment per the project guidelines.

## Configuration

Create an `.env.local` (or inject the same keys as service/container secrets) with the following variables:

```
SERVICEME_BASE_URL=https://your-serviceme-domain.example.com
SERVICEME_CLIENT_ID=...
SERVICEME_CLIENT_SECRET=...
SERVICEME_ACCOUNT=workspace-sync-user@example.com
GEMINI_PROJECT_ID=gcp-project-id
GEMINI_LOCATION=global                  # honor org policy constraints/gcp.resourceLocations
GEMINI_IDENTITY_MAPPING_STORE_ID=serviceme-ims
GEMINI_DATA_STORE_ID=serviceme-kb
GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/service-account.json  # or GOOGLE_APPLICATION_CREDENTIALS_JSON
SYNC_MODE=incremental|gcs
GCS_BUCKET=optional-staging-bucket      # required when SYNC_MODE=gcs
GCS_BLOB_PREFIX=connectors/serviceme
PORT=8080                               # FastAPI server port
```

> The SERVICEME account limits which workspaces show up in `/v1/openapi/workspace/all`. Request access for every workspace you intend to sync or the run will fail fast before touching Gemini.

## Working with the SERVICEME OpenAPI

`src/utils/serviceme_api.py` demonstrates the key flows described in `docs/Open API | SERVICEME.md`:

```python
from utils.serviceme_api import obtain_access_token, fetch_workspaces, rag_search

auth = obtain_access_token(
    base_url=SERVICEME_BASE_URL,
    client_id=SERVICEME_CLIENT_ID,
    client_secret=SERVICEME_CLIENT_SECRET,
    account=SERVICEME_ACCOUNT,
)

workspaces = fetch_workspaces(
    base_url=auth["base_url"],
    access_token=auth["access_token"],
)

rag_payload = {"query": "最新的安全培训", "workspaceId": workspaces[0]["id"]}
answers = rag_search(
    base_url=auth["base_url"],
    access_token=auth["access_token"],
    payload=rag_payload,
)
```

The helper covers signature generation (MD5 of `client`, `secret`, `account`, `timestamp`, and a random nonce), token expiry tracking, workspace enumeration, and error handling that mirrors SERVICEME’s `success/msg` envelope.

## Syncing data into Gemini Enterprise

1. **Identity store** – Call `IdentityMappingStoreServiceClient` to create or retrieve the store, then import external identities via `ImportIdentityMappingsRequest` (see `docs/Create custom connector.md` §“Retrieve or create identity store” and “Ingest identity mapping…”).
2. **Data store** – Create a Discovery Engine data store bound to the identity mapping store. Set `industry_vertical` (default `GENERIC`) and enable ACLs.
3. **Fetch → Transform → Sync** – Build workflows under `src/connector/workflows/` that:
   - Fetch SERVICEME records in batches or via streaming.
   - Transform them into JSON payloads with `title`, `body`, `url`, metadata, and ACL blocks.
   - Sync into Gemini via incremental upsert (direct API calls) or the recommended comprehensive sync (stage JSONL in GCS, call `ImportDocuments`).

Hybrid strategies are supported: run incremental updates for near-real-time freshness and schedule full GCS syncs to reconcile deletions.

## Local development & tests

```bash
pytest                                  # run unit tests
pytest --cov=src                        # check coverage
ruff check src tests && ruff format src tests
mypy src
# planned orchestration entry point
python -m connector.sync --full         # full sync example (module lives under src/connector/)
```

Ensure `GOOGLE_APPLICATION_CREDENTIALS` or `GOOGLE_APPLICATION_CREDENTIALS_JSON` is set before running commands that touch Discovery Engine.

## Reference materials

- `docs/Overview.md` – High-level description of how custom connectors interact with Gemini.
- `docs/Create custom connector.md` – Step-by-step instructions covering prerequisites, identity stores, and data store provisioning.
- `docs/Open API | SERVICEME.md` – SERVICEME authentication flows, workspace APIs, and RAG request/response examples.
- `docs/reference/` – Reserved for additional API specs (for example, raw OpenAPI/Swagger files) that product teams share with you. Keep this directory updated whenever a contract changes and link the relevant files from future README updates.

Keep the README in sync with those documents whenever an API contract or Google Cloud requirement changes; the docs folder is the single source of truth for connector behavior.
