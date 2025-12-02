from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

from connector.config import GeminiSettings
from connector.schema.document import Document
from connector.schema.workspace import Workspace

try:  # pragma: no cover - optional dependency validated at runtime
    from google.cloud import discoveryengine_v1 as discoveryengine
    from google.cloud.discoveryengine_v1.types import common as discovery_common
except Exception:  # pragma: no cover
    discoveryengine = None  # type: ignore[assignment]
    discovery_common = None  # type: ignore[assignment]

try:  # pragma: no cover
    from google.protobuf import struct_pb2
except Exception:  # pragma: no cover
    struct_pb2 = None  # type: ignore[assignment]

try:  # pragma: no cover
    from google.api_core import exceptions as gcp_exceptions
except Exception:  # pragma: no cover
    gcp_exceptions = None  # type: ignore[assignment]

LOGGER = logging.getLogger(__name__)

# Discovery Engine ContentConfig.CONTENT_REQUIRED 仅允许有限制的 MIME 类型，使用 text/plain
# 可以兼容 Markdown/纯文本内容。
DEFAULT_CONTENT_MIME_TYPE = "text/plain"
# Discovery Engine inline import 对 raw_bytes 有 1 MB 限制，留一点余量避免溢出。
MAX_DOCUMENT_CONTENT_BYTES = 950_000

class GeminiIngestError(RuntimeError):
    """Raised when Discovery Engine ingestion fails."""


@dataclass(slots=True)
class GeminiIngestService:
    """
    把标准化的 Document 通过 Discovery Engine DocumentService 导入到 Data Store。
    """

    settings: GeminiSettings
    branch_id: str = "default_branch"
    document_client: Optional["discoveryengine.DocumentServiceClient"] = field(default=None, repr=False)
    _reconciliation_mode: object = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        if discoveryengine is None or struct_pb2 is None:
            raise GeminiIngestError(
                "google-cloud-discoveryengine 或 protobuf 未安装，无法推送文档。"
            )
        if self.document_client is None:
            self.document_client = discoveryengine.DocumentServiceClient()
        self._reconciliation_mode = discoveryengine.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL

    def upsert_documents(self, workspace: Workspace, documents: Sequence[Document]) -> int:
        if not documents:
            return 0
        client = self.document_client
        if client is None:  # pragma: no cover - defensive
            raise GeminiIngestError("DocumentServiceClient 尚未初始化")

        proto_docs = [self._to_proto(doc) for doc in documents]
        parent = client.branch_path(
            project=self.settings.project_id,
            location=self.settings.location,
            data_store=self.settings.data_store_id,
            branch=self.branch_id,
        )
        request = discoveryengine.ImportDocumentsRequest(
            parent=parent,
            inline_source=discoveryengine.ImportDocumentsRequest.InlineSource(documents=proto_docs),
            reconciliation_mode=self._reconciliation_mode,
        )
        try:
            operation = client.import_documents(request=request)
            response = operation.result()
        except Exception as exc:  # pragma: no cover - network error
            if gcp_exceptions and isinstance(exc, gcp_exceptions.GoogleAPICallError):
                raise GeminiIngestError(f"导入文档失败: {exc.message}") from exc
            raise GeminiIngestError(f"导入文档失败: {exc}") from exc

        success = self._evaluate_operation(operation, response, workspace, len(documents))
        LOGGER.info(
            "已向 Data Store %s 推送 %s/%s 篇文档（workspace=%s）",
            self.settings.data_store_id,
            success,
            len(documents),
            workspace.id,
        )
        return success

    def _to_proto(self, document: Document) -> "discoveryengine.Document":
        struct_payload = document.to_discovery_document()["structData"]
        struct_data = struct_pb2.Struct()
        struct_data.update(struct_payload)
        doc_kwargs: Dict[str, object] = {
            "id": document.id,
            "struct_data": struct_data,
            "content": self._build_content(document),
        }
        if self.settings.acl_enabled:
            doc_kwargs["acl_info"] = self._build_acl(document)
        return discoveryengine.Document(**doc_kwargs)

    def _build_content(self, document: Document) -> "discoveryengine.Document.Content":
        """Construct raw content required by CONTENT_REQUIRED data stores."""
        text = document.content or ""
        if not text.strip():
            text = document.title or document.workspace_name or document.id
        encoded = text.encode("utf-8")
        if len(encoded) > MAX_DOCUMENT_CONTENT_BYTES:
            LOGGER.warning(
                "文档 %s (workspace=%s) 内容超过 %s 字节，将按 Discovery Engine 上限截断",
                document.id,
                document.workspace_id,
                MAX_DOCUMENT_CONTENT_BYTES,
            )
            encoded = encoded[:MAX_DOCUMENT_CONTENT_BYTES]
        return discoveryengine.Document.Content(
            mime_type=DEFAULT_CONTENT_MIME_TYPE,
            raw_bytes=encoded,
        )

    def _build_acl(self, document: Document) -> "discoveryengine.Document.AclInfo":
        mode = self.settings.acl_mode
        if mode == "idp_wide":
            return discoveryengine.Document.AclInfo(
                readers=[
                    discoveryengine.Document.AclInfo.AccessRestriction(idp_wide=True)
                ]
            )
        if mode == "principal_list":
            principals = self._resolve_acl_principals(document)
            if not principals:
                raise GeminiIngestError(
                    "未从文档或配置中解析到任何 ACL 成员，"
                    "请设置 GEMINI_DEFAULT_ACL_READERS 或在 payload metadata 中提供 aclReaders。"
                )
            restriction = discoveryengine.Document.AclInfo.AccessRestriction(
                principals=principals
            )
            return discoveryengine.Document.AclInfo(readers=[restriction])
        raise GeminiIngestError(f"不支持的 ACL 模式: {mode}")

    def _resolve_acl_principals(self, document: Document) -> List["discovery_common.Principal"]:
        candidate_ids = self._collect_acl_reader_ids(document)
        principals: List["discovery_common.Principal"] = []
        for identifier in candidate_ids:
            normalized = identifier.strip()
            if not normalized:
                continue
            principal = discovery_common.Principal()
            if normalized.startswith("group:"):
                principal.group_id = normalized.split(":", 1)[1]
            elif normalized.startswith("external:"):
                principal.external_entity_id = normalized.split(":", 1)[1]
            else:
                principal.user_id = normalized
            principals.append(principal)
        return principals

    def _collect_acl_reader_ids(self, document: Document) -> List[str]:
        readers = self._coerce_acl_list(document.metadata.get("aclReaders"))
        if not readers:
            readers = list(self.settings.default_acl_readers)
        return readers

    @staticmethod
    def _coerce_acl_list(value: object) -> List[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        if isinstance(value, (list, tuple, set)):
            items: List[str] = []
            for element in value:
                text = str(element).strip()
                if text:
                    items.append(text)
            return items
        return []

    def _evaluate_operation(
        self,
        operation: object,
        response: object,
        workspace: Workspace,
        expected_count: int,
    ) -> int:
        metadata = self._extract_operation_metadata(operation)
        failure_count = int(getattr(metadata, "failure_count", 0) or 0)
        success_count = int(getattr(metadata, "success_count", 0) or 0)
        total_count = int(getattr(metadata, "total_count", 0) or 0)

        error_messages = self._collect_error_messages(response)
        if failure_count or error_messages:
            details: List[str] = []
            if failure_count:
                details.append(
                    f"failure_count={failure_count}, total_count={total_count or expected_count}"
                )
            if error_messages:
                details.append(f"samples={' | '.join(error_messages)}")
            raise GeminiIngestError(
                "Discovery Engine 文档导入失败"
                f"（workspace={workspace.id}）: {'; '.join(details)}"
            )

        if success_count <= 0:
            success_count = expected_count
        return success_count

    @staticmethod
    def _collect_error_messages(response: object) -> List[str]:
        messages: List[str] = []
        if not response:
            return messages
        error_samples = getattr(response, "error_samples", None)
        if not error_samples:
            return messages
        for status in list(error_samples)[:3]:
            message = getattr(status, "message", "") or str(status)
            messages.append(message)
        return messages

    @staticmethod
    def _extract_operation_metadata(operation: object) -> Optional[object]:
        metadata = getattr(operation, "metadata", None)
        if callable(metadata):
            try:
                return metadata()
            except TypeError:
                return None
        return metadata
