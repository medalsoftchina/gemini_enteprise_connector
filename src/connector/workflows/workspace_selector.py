from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Sequence

from connector.config import SyncSettings
from connector.schema.workspace import Workspace


def _normalize_ids(values: Iterable[str]) -> set[str]:
    return {str(value).strip() for value in values if str(value).strip()}


def _normalize_names(values: Iterable[str]) -> set[str]:
    return {str(value).strip().lower() for value in values if str(value).strip()}


@dataclass(slots=True)
class WorkspaceSelector:
    ids: set[str] = field(default_factory=set)
    names: set[str] = field(default_factory=set)

    @classmethod
    def from_settings(cls, settings: SyncSettings) -> "WorkspaceSelector":
        return cls(
            ids=_normalize_ids(settings.workspace_ids),
            names=_normalize_names(settings.workspace_names),
        )

    def select(self, workspaces: Sequence[Workspace]) -> List[Workspace]:
        if not self.ids and not self.names:
            return list(workspaces)

        selected: List[Workspace] = []
        pending_ids = set(self.ids)
        pending_names = set(self.names)

        for workspace in workspaces:
            matched = False
            if self.ids and workspace.id in self.ids:
                matched = True
                pending_ids.discard(workspace.id)
            if self.names and workspace.name.lower() in self.names:
                matched = True
                pending_names.discard(workspace.name.lower())
            if matched:
                selected.append(workspace)

        errors: list[str] = []
        if pending_ids:
            errors.append(f"未找到指定的 workspace IDs: {', '.join(sorted(pending_ids))}")
        if pending_names:
            errors.append(f"未找到指定的 workspace 名称: {', '.join(sorted(pending_names))}")
        if errors:
            raise ValueError("；".join(errors))

        return selected

    def describe(self) -> str:
        if not self.ids and not self.names:
            return "全部文件空间"
        parts: List[str] = []
        if self.ids:
            parts.append(f"IDs({', '.join(sorted(self.ids))})")
        if self.names:
            parts.append(f"Names({', '.join(sorted(self.names))})")
        return " & ".join(parts)
