from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping
from uuid import uuid4

from connector.schema.workspace import Workspace


def _coalesce_doc_id(payload: Mapping[str, Any]) -> str:
    for key in ("id", "docId", "documentId"):
        value = payload.get(key)
        if value:
            return str(value)
    return str(uuid4())


def _coalesce_text(payload: Mapping[str, Any]) -> str:
    for key in ("content", "body", "answer", "text"):
        value = payload.get(key)
        if value:
            return str(value)
    return ""


def _coalesce_title(workspace: Workspace, payload: Mapping[str, Any]) -> str:
    for key in ("title", "name", "summary"):
        value = payload.get(key)
        if value:
            return str(value)
    return workspace.name


@dataclass(slots=True)
class Document:
    id: str
    title: str
    content: str
    workspace_id: str
    workspace_name: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    source_payload: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_serviceme_payload(cls, workspace: Workspace, payload: Mapping[str, Any]) -> "Document":
        metadata = {
            "workspaceId": workspace.id,
            "workspaceName": workspace.name,
            "sourceUrl": payload.get("url") or payload.get("source"),
            "fileId": payload.get("id"),
            "fileName": payload.get("name"),
            "filePath": payload.get("fullPath"),
            "fileSize": payload.get("size"),
            "tags": payload.get("tags"),
            "chunkingState": payload.get("chunkingState"),
            "previewState": payload.get("previewState"),
        }
        if isinstance(payload.get("metadata"), Mapping):
            metadata.update(payload["metadata"])  # type: ignore[arg-type]
        return cls(
            id=_coalesce_doc_id(payload),
            title=_coalesce_title(workspace, payload),
            content=_coalesce_text(payload),
            workspace_id=workspace.id,
            workspace_name=workspace.name,
            metadata=metadata,
            source_payload=dict(payload),
        )

    def to_discovery_document(self) -> Dict[str, Any]:
        """Build payload expected by Discovery Engine Document service."""
        return {
            "id": self.id,
            "structData": {
                "title": self.title,
                "content": self.content,
                "workspaceId": self.workspace_id,
                "workspaceName": self.workspace_name,
                "metadata": self.metadata,
            },
        }
