from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


def _coalesce_id(payload: Mapping[str, Any]) -> str:
    for key in ("id", "workspaceId", "workspace_id"):
        value = payload.get(key)
        if value:
            return str(value)
    raise ValueError(f"无法在 workspace payload 中找到 ID: {payload}")


def _coalesce_name(payload: Mapping[str, Any]) -> str:
    for key in ("name", "workspaceName", "workspace_name", "title", "description"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
        if value:
            return str(value)
    # fallback: use ID if present
    if payload.get("id"):
        return str(payload["id"])
    raise ValueError(f"无法在 workspace payload 中找到名称: {payload}")


@dataclass(slots=True)
class Workspace:
    id: str
    name: str
    category: str | None = None
    raw: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "Workspace":
        return cls(
            id=_coalesce_id(payload),
            name=_coalesce_name(payload),
            category=payload.get("categoryName") or payload.get("category"),
            raw=dict(payload),
        )
