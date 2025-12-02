import pytest

from connector.config import SyncSettings
from connector.schema.workspace import Workspace
from connector.workflows.workspace_selector import WorkspaceSelector


def make_workspace(idx: int, name: str) -> Workspace:
    return Workspace(id=f"ws-{idx}", name=name, category=None, raw={"id": f"ws-{idx}", "name": name})


def test_selector_filters_by_id() -> None:
    workspaces = [make_workspace(1, "Alpha"), make_workspace(2, "Beta")]
    selector = WorkspaceSelector.from_settings(SyncSettings(workspace_ids=["ws-2"]))

    selected = selector.select(workspaces)

    assert len(selected) == 1
    assert selected[0].name == "Beta"


def test_selector_supports_case_insensitive_names() -> None:
    workspaces = [make_workspace(1, "Alpha"), make_workspace(2, "Beta")]
    selector = WorkspaceSelector.from_settings(SyncSettings(workspace_names=["alpha"]))

    selected = selector.select(workspaces)

    assert len(selected) == 1
    assert selected[0].id == "ws-1"


def test_selector_raises_when_workspace_missing() -> None:
    workspaces = [make_workspace(1, "Alpha")]
    selector = WorkspaceSelector.from_settings(SyncSettings(workspace_ids=["ws-9"]))

    with pytest.raises(ValueError):
        selector.select(workspaces)
