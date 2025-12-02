from connector.schema.workspace import Workspace


def test_workspace_name_falls_back_to_id_when_empty() -> None:
    payload = {"id": "ws-empty", "name": "", "description": ""}
    workspace = Workspace.from_payload(payload)
    assert workspace.name == "ws-empty"
