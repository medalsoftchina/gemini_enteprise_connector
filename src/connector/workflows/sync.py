from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import List, Mapping, Sequence

from connector.client.gemini import GeminiIngestService
from connector.client.serviceme import ServicemeClient
from connector.config import ConnectorSettings
from connector.schema.document import Document
from connector.schema.workspace import Workspace
from connector.utils.debug_dump import MarkdownDumpManager
from connector.utils.gemini_resources import ensure_gemini_resources
from connector.workflows.workspace_selector import WorkspaceSelector

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class WorkspaceSyncSummary:
    workspace_id: str
    workspace_name: str
    document_count: int


@dataclass(slots=True)
class SyncResult:
    total_documents: int
    workspaces: List[WorkspaceSyncSummary] = field(default_factory=list)


class SyncManager:
    def __init__(
        self,
        serviceme_client: ServicemeClient,
        gemini_service: GeminiIngestService,
        selector: WorkspaceSelector,
        debug_dumper: MarkdownDumpManager | None = None,
    ) -> None:
        self.serviceme_client = serviceme_client
        self.gemini_service = gemini_service
        self.selector = selector
        self.debug_dumper = debug_dumper

    def run(self) -> SyncResult:
        workspaces = self.serviceme_client.list_workspaces()
        selected_workspaces = self.selector.select(workspaces)

        summaries: List[WorkspaceSyncSummary] = []
        total = 0

        for workspace in selected_workspaces:
            raw_documents = self.serviceme_client.fetch_workspace_documents(workspace)
            if self.debug_dumper:
                self.debug_dumper.dump(workspace, raw_documents)
            documents = self._transform_documents(workspace, raw_documents)
            synced_count = self.gemini_service.upsert_documents(workspace, documents)
            total += synced_count
            summaries.append(
                WorkspaceSyncSummary(
                    workspace_id=workspace.id,
                    workspace_name=workspace.name,
                    document_count=synced_count,
                )
            )

        return SyncResult(total_documents=total, workspaces=summaries)

    @staticmethod
    def _transform_documents(workspace: Workspace, payloads: Sequence[Mapping[str, object]]) -> List[Document]:
        return [Document.from_serviceme_payload(workspace, payload) for payload in payloads]


def run_sync_from_env() -> SyncResult:
    LOGGER.info("加载配置并初始化连接器设置")
    settings = ConnectorSettings.from_env()
    if settings.gemini.auto_create_resources:
        LOGGER.info("自动创建/检查 Gemini 资源（Identity Mapping Store & Data Store）")
        ensure_gemini_resources(settings.gemini)
    else:
        LOGGER.info("跳过 Gemini 资源自动创建 (GEMINI_AUTO_CREATE_RESOURCES=false)")
    LOGGER.info("初始化 SERVICEME 客户端并拉取文档空间")
    debug_dumper: MarkdownDumpManager | None = None
    if settings.sync.debug_dump_markdown:
        debug_dumper = MarkdownDumpManager(
            enabled=True,
            root_dir=settings.sync.debug_dump_dir,
        )
        debug_dumper.prepare_run_dir()
    serviceme_client = ServicemeClient(settings.serviceme, debug_dumper=debug_dumper)
    gemini_service = GeminiIngestService(settings.gemini)
    selector = WorkspaceSelector.from_settings(settings.sync)
    manager = SyncManager(serviceme_client, gemini_service, selector, debug_dumper)
    LOGGER.info("开始执行同步流程")
    result = manager.run()
    LOGGER.info("同步完成，共处理 %s 个文档", result.total_documents)
    return result
