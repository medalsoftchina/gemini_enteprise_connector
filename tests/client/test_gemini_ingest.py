from __future__ import annotations

import pytest
from google.cloud import discoveryengine_v1 as discoveryengine
from google.rpc import status_pb2

from connector.client import gemini
from connector.client.gemini import GeminiIngestError, GeminiIngestService
from connector.config import GeminiSettings
from connector.schema.document import Document
from connector.schema.workspace import Workspace


class _FakeOperation:
    def __init__(self, response=None, metadata=None) -> None:
        self._response = response
        self._metadata = metadata

    def result(self):  # pragma: no cover - helper
        return self._response

    @property
    def metadata(self):  # pragma: no cover - helper
        return self._metadata


class _FakeDocumentClient:
    def __init__(self, operation: _FakeOperation | None = None) -> None:
        self._operation = operation or _FakeOperation()

    def branch_path(self, project: str, location: str, data_store: str, branch: str) -> str:  # pragma: no cover - helper
        return f"projects/{project}/locations/{location}/dataStores/{data_store}/branches/{branch}"

    def import_documents(self, *_, **__):  # pragma: no cover - helper
        return self._operation


def _build_settings(**overrides) -> GeminiSettings:
    params = dict(project_id="proj", location="global", data_store_id="ds")
    params.update(overrides)
    return GeminiSettings(**params)


def _build_service(operation: _FakeOperation | None = None, settings: GeminiSettings | None = None) -> GeminiIngestService:
    settings = settings or _build_settings()
    return GeminiIngestService(settings=settings, document_client=_FakeDocumentClient(operation))


def _sample_document(content: str = "Hello") -> Document:
    return Document(
        id="doc-1",
        title="Sample",
        content=content,
        workspace_id="ws-1",
        workspace_name="Workspace",
        metadata={},
        source_payload={},
    )


def _sample_workspace() -> Workspace:
    return Workspace(id="ws-1", name="Workspace", category=None, raw={})


def test_to_proto_adds_markdown_content() -> None:
    service = _build_service(settings=_build_settings(acl_mode="idp_wide", acl_enabled=True))
    proto = service._to_proto(_sample_document("Markdown content"))

    assert proto.content.mime_type == gemini.DEFAULT_CONTENT_MIME_TYPE
    assert proto.content.raw_bytes == b"Markdown content"
    assert proto.acl_info.readers[0].idp_wide is True


def test_to_proto_truncates_large_payload() -> None:
    service = _build_service()
    oversized = "A" * (gemini.MAX_DOCUMENT_CONTENT_BYTES + 123)
    proto = service._to_proto(_sample_document(oversized))

    assert len(proto.content.raw_bytes) == gemini.MAX_DOCUMENT_CONTENT_BYTES


def test_upsert_documents_uses_success_count_from_metadata() -> None:
    metadata = type("Meta", (), {"success_count": 2, "failure_count": 0, "total_count": 2})()
    operation = _FakeOperation(
        response=discoveryengine.ImportDocumentsResponse(),
        metadata=metadata,
    )
    service = _build_service(operation)

    count = service.upsert_documents(_sample_workspace(), [_sample_document(), _sample_document("B")])

    assert count == 2


def test_upsert_documents_raises_when_failure_count_present() -> None:
    metadata = type("Meta", (), {"success_count": 0, "failure_count": 1, "total_count": 1})()
    operation = _FakeOperation(
        response=discoveryengine.ImportDocumentsResponse(),
        metadata=metadata,
    )
    service = _build_service(operation)

    with pytest.raises(GeminiIngestError) as exc:
        service.upsert_documents(_sample_workspace(), [_sample_document()])
    assert "failure_count=1" in str(exc.value)


def test_upsert_documents_raises_when_error_samples_present() -> None:
    response = discoveryengine.ImportDocumentsResponse()
    response.error_samples.append(status_pb2.Status(message="invalid document"))
    metadata = type("Meta", (), {"success_count": 0, "failure_count": 0, "total_count": 1})()
    operation = _FakeOperation(response=response, metadata=metadata)
    service = _build_service(operation)

    with pytest.raises(GeminiIngestError) as exc:
        service.upsert_documents(_sample_workspace(), [_sample_document()])
    assert "invalid document" in str(exc.value)
def test_build_acl_principal_list_uses_defaults() -> None:
    settings = _build_settings(
        acl_mode="principal_list",
        default_acl_readers=["user@example.com", "group:team@example.com"],
        acl_enabled=True,
    )
    service = _build_service(settings=settings)

    proto = service._to_proto(_sample_document("content"))

    restriction = proto.acl_info.readers[0]
    principals = restriction.principals
    assert principals[0].user_id == "user@example.com"
    assert principals[1].group_id == "team@example.com"


def test_build_acl_principal_list_raises_when_empty() -> None:
    settings = _build_settings(acl_mode="principal_list", acl_enabled=True)
    service = _build_service(settings=settings)

    with pytest.raises(GeminiIngestError):
        service._to_proto(_sample_document("content"))


def test_to_proto_skips_acl_when_disabled() -> None:
    service = _build_service(settings=_build_settings(acl_enabled=False))
    proto = service._to_proto(_sample_document("content"))

    assert "acl_info" not in proto
