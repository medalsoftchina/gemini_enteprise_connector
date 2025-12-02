from __future__ import annotations

import json
import logging
import os

from connector.workflows.sync import run_sync_from_env


def _configure_logging() -> None:
    if logging.getLogger().handlers:
        return
    level = os.getenv("CONNECTOR_LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def main() -> None:
    _configure_logging()
    logging.getLogger(__name__).info("启动 SERVICEME -> Gemini 同步任务")
    result = run_sync_from_env()
    summary = {
        "total_documents": result.total_documents,
        "workspaces": [
            {
                "workspace_id": item.workspace_id,
                "workspace_name": item.workspace_name,
                "document_count": item.document_count,
            }
            for item in result.workspaces
        ],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
