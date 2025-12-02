from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Mapping, Protocol, Sequence

from connector.config import ServicemeAuthSettings
from connector.schema.workspace import Workspace
from connector.utils.debug_dump import MarkdownDumpManager
from utils import serviceme_api

LOGGER = logging.getLogger(__name__)


class ServicemeGateway(Protocol):
    def list_workspaces(self, base_url: str, token: str) -> Sequence[Mapping[str, object]]: ...

    def list_workspace_files(self, base_url: str, token: str, workspace: Workspace) -> Sequence[Mapping[str, object]]: ...

    def download_file_markdown(self, base_url: str, token: str, file_id: str) -> str: ...


class HTTPServicemeGateway:
    def list_workspaces(self, base_url: str, token: str) -> Sequence[Mapping[str, object]]:
        return serviceme_api.fetch_workspaces(base_url, token)

    def list_workspace_files(self, base_url: str, token: str, workspace: Workspace) -> Sequence[Mapping[str, object]]:
        workspace_name = workspace.name or workspace.id
        return serviceme_api.fetch_workspace_files(base_url, token, workspace_name)

    def download_file_markdown(self, base_url: str, token: str, file_id: str) -> str:
        return serviceme_api.download_file_markdown(base_url, token, file_id)


@dataclass(slots=True)
class ServicemeClient:
    settings: ServicemeAuthSettings
    gateway: ServicemeGateway = HTTPServicemeGateway()
    token_provider: Callable[
        [str, str, str, str], Dict[str, object]
    ] = serviceme_api.obtain_access_token
    _token_info: Dict[str, object] | None = field(default=None, init=False, repr=False)
    debug_dumper: MarkdownDumpManager | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        # slot placeholder ensures attribute exists even if dataclass skips __dict__
        self._token_info = None

    def _access_token(self) -> str:
        if self._token_info and not self._is_expired(self._token_info):
            return str(self._token_info["access_token"])

        token_info = self.token_provider(
            self.settings.base_url,
            self.settings.client_id,
            self.settings.client_secret,
            self.settings.account,
        )
        self._token_info = token_info
        return str(token_info["access_token"])

    @staticmethod
    def _is_expired(token_info: Mapping[str, object], *, leeway: int = 30) -> bool:
        expires_at_ts = token_info.get("expires_at_ts")
        if isinstance(expires_at_ts, (int, float)):
            return expires_at_ts - leeway <= time.time()
        expires_in = token_info.get("expires_in")
        if isinstance(expires_in, (int, float)) and expires_in > 0:
            return False
        return True

    def list_workspaces(self) -> List[Workspace]:
        token = self._access_token()
        payloads = self.gateway.list_workspaces(self.settings.base_url, token)
        return [Workspace.from_payload(item) for item in payloads]

    def fetch_workspace_documents(self, workspace: Workspace) -> Sequence[Mapping[str, object]]:
        token = self._access_token()
        files = self.gateway.list_workspace_files(self.settings.base_url, token, workspace)
        documents: List[Mapping[str, object]] = []
        for file_meta in files:
            file_id = file_meta.get("id")
            if not file_id:
                LOGGER.debug(
                    "跳过 workspace=%s 中缺少 ID 的文件: %s",
                    workspace.id,
                    file_meta,
                )
                continue
            normalized_id = self._to_string_file_id(file_id)
            markdown = self.gateway.download_file_markdown(self.settings.base_url, token, normalized_id)
            payload = dict(file_meta)
            payload.setdefault("title", file_meta.get("name"))
            payload["content"] = markdown
            payload["_debug_download"] = self._build_debug_download_info(normalized_id)
            documents.append(payload)
        LOGGER.debug(
            "Fetched %s documents from workspace %s (%s)",
            len(documents),
            workspace.id,
            workspace.name,
        )
        return documents

    def _to_string_file_id(self, file_id: object) -> str:
        return str(file_id)

    def _build_debug_download_info(self, file_id: str) -> Dict[str, object] | None:
        if not self.debug_dumper or not self.debug_dumper.enabled:
            return None
        token_info = self._token_info or {}
        base_url = str(token_info.get("base_url") or self.settings.base_url)
        url = f"{base_url.rstrip('/')}/v1/openapi/workspace/file/downloadDocument2MD"
        token = token_info.get("access_token", "")
        request_body = {"id": file_id}
        return {
            "url": url,
            "authorization": f"openapi {token}",
            "body": request_body,
        }
