from typing import Dict, List, Mapping, Sequence

from connector.schema.workspace import Workspace
from connector.workflows.sync import SyncManager
from connector.workflows.workspace_selector import WorkspaceSelector


class FakeServicemeClient:
    def __init__(self, workspaces: Sequence[Workspace], documents: Dict[str, Sequence[Mapping[str, object]]]) -> None:
        self._workspaces = list(workspaces)
        self._documents = documents

    def list_workspaces(self) -> List[Workspace]:
        return list(self._workspaces)

    def fetch_workspace_documents(self, workspace: Workspace) -> Sequence[Mapping[str, object]]:
        return self._documents.get(workspace.id, [])


class FakeGeminiService:
    def __init__(self) -> None:
        self.calls: List[Dict[str, object]] = []

    def upsert_documents(self, workspace: Workspace, documents):
        self.calls.append({"workspace": workspace, "document_ids": [doc.id for doc in documents]})
        return len(documents)


def test_sync_manager_only_processes_selected_workspaces() -> None:
    ws_alpha = Workspace(id="alpha", name="Alpha", category=None, raw={"id": "alpha", "name": "Alpha"})
    ws_beta = Workspace(id="beta", name="Beta", category=None, raw={"id": "beta", "name": "Beta"})

    documents = {
        "alpha": [{"id": "doc-1", "title": "Alpha Doc", "content": "alpha"}],
        "beta": [
            {"id": "doc-2", "title": "Beta Doc1", "content": "beta-1"},
            {"id": "doc-3", "title": "Beta Doc2", "content": "beta-2"},
        ],
    }

    serviceme_client = FakeServicemeClient([ws_alpha, ws_beta], documents)
    gemini_service = FakeGeminiService()
    selector = WorkspaceSelector(ids={"beta"})

    manager = SyncManager(serviceme_client, gemini_service, selector)
    result = manager.run()

    assert result.total_documents == 2
    assert len(result.workspaces) == 1
    assert result.workspaces[0].workspace_id == "beta"
    assert gemini_service.calls[0]["document_ids"] == ["doc-2", "doc-3"]
