from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Mapping, Sequence

from connector.schema.workspace import Workspace

LOGGER = logging.getLogger(__name__)


class MarkdownDumpManager:
    """Dump fetched markdown documents to disk for debugging."""

    def __init__(self, *, enabled: bool, root_dir: str) -> None:
        self.enabled = enabled
        self.root_dir = Path(root_dir)
        self.run_dir: Path | None = None

    def prepare_run_dir(self) -> None:
        if not self.enabled:
            return
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        run_dir = self.root_dir / timestamp
        run_dir.mkdir(parents=True, exist_ok=True)
        self.run_dir = run_dir
        LOGGER.info("Markdown dump 目录: %s", run_dir)

    def dump(self, workspace: Workspace, documents: Sequence[Mapping[str, object]]) -> None:
        if not self.enabled or not documents:
            return
        if self.run_dir is None:
            self.prepare_run_dir()
        if self.run_dir is None:
            return
        workspace_name = _sanitize_component(f"{workspace.id}-{workspace.name}")
        workspace_dir = self.run_dir / workspace_name
        workspace_dir.mkdir(parents=True, exist_ok=True)
        for payload in documents:
            content = str(payload.get("content") or "")
            relative_path = _build_relative_path(payload)
            target_path = workspace_dir / relative_path
            target_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                target_path.write_text(content, encoding="utf-8")
            except OSError as exc:
                LOGGER.warning("无法写入调试文件 %s: %s", target_path, exc)
            debug_info = payload.get("_debug_download")
            if debug_info:
                self._write_curl_script(target_path, debug_info)

    def _write_curl_script(self, markdown_path: Path, debug_info: Mapping[str, object]) -> None:
        url = str(debug_info.get("url") or "")
        authorization = str(debug_info.get("authorization") or "openapi <ACCESS_TOKEN>")
        body = debug_info.get("body") or {}
        try:
            body_json = json.dumps(body, ensure_ascii=False)
        except (TypeError, ValueError):
            body_json = "{}"
        curl_lines = [
            "curl --location \'{}\'".format(url),
            "  --header 'Authorization: {}'".format(authorization),
            "  --header 'Content-Type: application/json'",
            "  --data '{}'".format(body_json.replace("'", "'\\''")),
        ]
        script_path = markdown_path.with_suffix(markdown_path.suffix + ".curl.sh")
        try:
            script_path.write_text(" \\\n".join(curl_lines) + "\n", encoding="utf-8")
        except OSError as exc:
            LOGGER.warning("无法写入调试 cURL 文件 %s: %s", script_path, exc)


def _build_relative_path(payload: Mapping[str, object]) -> Path:
    raw_path = str(payload.get("fullPath") or payload.get("path") or "").strip()
    components = [part for part in raw_path.split("/") if part]
    if not components:
        filename = _default_filename(payload)
        components = [filename]
    else:
        components = [_sanitize_component(part) for part in components]
        if components[-1].endswith("/") or not components[-1]:
            components[-1] = _default_filename(payload)
    rel = Path(*components)
    if rel.suffix == "":
        rel = rel.with_suffix(".md")
    return rel


def _default_filename(payload: Mapping[str, object]) -> str:
    name = payload.get("name") or payload.get("title")
    if name:
        return f"{_sanitize_component(str(name))}.md"
    file_id = payload.get("id") or payload.get("fileId") or "document"
    return f"{_sanitize_component(str(file_id))}.md"


def _sanitize_component(component: str) -> str:
    replacements = ["..", os.sep, os.altsep or ""]
    value = component.strip()
    for bad in replacements:
        value = value.replace(bad, "_")
    cleaned = "".join(ch if ch.isalnum() or ch in {"-", "_", "."} else "_" for ch in value)
    return cleaned or "document"
