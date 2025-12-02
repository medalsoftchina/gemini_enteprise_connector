import time
from typing import Mapping, Sequence

from connector.client.serviceme import ServicemeClient
from connector.config import ServicemeAuthSettings
from connector.schema.workspace import Workspace


class FakeGateway:
    def __init__(self) -> None:
        self.tokens: list[str] = []

    def list_workspaces(self, base_url: str, token: str) -> Sequence[Mapping[str, object]]:
        self.tokens.append(token)
        return [{"id": "ws-1", "name": "Alpha"}]

    def list_workspace_files(self, base_url: str, token: str, workspace: Workspace) -> Sequence[Mapping[str, object]]:
        return []

    def download_file_markdown(self, base_url: str, token: str, file_id: str) -> str:
        return ""


def make_settings() -> ServicemeAuthSettings:
    return ServicemeAuthSettings(
        base_url="https://api.example.com",
        client_id="client",
        client_secret="secret",
        account="user@example.com",
    )


def test_serviceme_client_refreshes_access_token_on_expiry() -> None:
    gateway = FakeGateway()
    token_calls = []
    tokens = [
        {"access_token": "token-a", "expires_at_ts": time.time() + 3600},
        {"access_token": "token-b", "expires_at_ts": time.time() + 3600},
    ]

    def provider(base_url: str, client_id: str, client_secret: str, account: str):
        token_calls.append((base_url, client_id, account))
        return tokens.pop(0)

    client = ServicemeClient(make_settings(), gateway=gateway, token_provider=provider)

    client.list_workspaces()  # fetch token-a
    client.list_workspaces()  # reuse token-a
    assert len(token_calls) == 1

    # Force expiry to trigger refresh
    assert client._token_info is not None  # type: ignore[attr-defined]
    client._token_info["expires_at_ts"] = time.time() - 5  # type: ignore[index]
    client.list_workspaces()

    assert len(token_calls) == 2
    assert gateway.tokens == ["token-a", "token-a", "token-b"]


def test_fetch_workspace_documents_downloads_markdown() -> None:
    class Gateway(FakeGateway):
        def __init__(self) -> None:
            super().__init__()
            self.file_calls: list[str] = []
            self.download_calls: list[str] = []

        def list_workspace_files(self, base_url: str, token: str, workspace: Workspace) -> Sequence[Mapping[str, object]]:
            self.file_calls.append(workspace.name)
            return [
                {"id": "file-1", "name": "Doc.md", "size": 10},
                {"id": "file-2", "name": "Doc2.md", "size": 20},
            ]

        def download_file_markdown(self, base_url: str, token: str, file_id: str) -> str:
            self.download_calls.append(file_id)
            return f"# Content {file_id}"

    gateway = Gateway()
    tokens = [{"access_token": "token-a", "expires_at_ts": time.time() + 3600}]

    def provider(*_args, **_kwargs):
        return tokens[0]

    workspace = Workspace.from_payload({"id": "ws-1", "name": "Alpha"})
    client = ServicemeClient(make_settings(), gateway=gateway, token_provider=provider)

    docs = client.fetch_workspace_documents(workspace)

    assert len(docs) == 2
    assert docs[0]["content"] == "# Content file-1"
    assert docs[1]["content"] == "# Content file-2"
    assert gateway.file_calls == ["Alpha"]
    assert gateway.download_calls == ["file-1", "file-2"]
