from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Sequence

try:  # pragma: no cover - optional dependency
    from dotenv import load_dotenv
except Exception:  # pragma: no cover
    load_dotenv = None  # type: ignore[assignment]

if load_dotenv:
    for candidate in (Path(".env.local"), Path(".env")):
        if candidate.exists():
            load_dotenv(dotenv_path=candidate, override=False)


def _get_env(name: str, default: str | None = None, *, required: bool = False) -> str:
    """Fetch environment variable and normalize whitespace."""
    raw = os.getenv(name, default)
    if raw is None:
        if required:
            raise ValueError(f"环境变量 {name} 未设置")
        return ""
    value = raw.strip()
    if required and not value:
        raise ValueError(f"环境变量 {name} 不能为空")
    return value


def _to_list(value: str | Sequence[str] | None) -> List[str]:
    """Normalize comma separated values to a list."""
    if value is None:
        return []
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return [str(item).strip() for item in value if str(item).strip()]


def _get_bool_env(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"true", "1", "yes", "on"}


def build_account_scope(account: str) -> str:
    """
    根据账号生成唯一 scope。

    约定使用 `serviceme::<account>::full_access` 形式，与模拟 OAuth2.0
    认证过程保持一致，便于下游审计。
    """
    normalized = (account or "").strip().lower()
    if not normalized:
        raise ValueError("账号不能为空，无法生成 scope")
    return f"serviceme::{normalized}::full_access"


@dataclass(slots=True)
class ServicemeAuthSettings:
    base_url: str
    client_id: str
    client_secret: str
    account: str

    @property
    def scope(self) -> str:
        return build_account_scope(self.account)


def _normalize_acl_mode(value: str | None) -> str:
    normalized = (value or "idp_wide").strip().lower()
    valid_modes = {"idp_wide", "principal_list"}
    if normalized not in valid_modes:
        raise ValueError(
            f"GEMINI_ACL_MODE 仅支持 {', '.join(sorted(valid_modes))}，当前为 {value!r}"
        )
    return normalized


@dataclass(slots=True)
class GeminiSettings:
    project_id: str
    location: str = "global"
    data_store_id: str = "serviceme-kb"
    identity_mapping_store_id: str = "serviceme-ims"
    data_store_display_name: str = "SERVICEME Connector"
    auto_create_resources: bool = True
    acl_enabled: bool = False
    default_acl_readers: List[str] = field(default_factory=list)
    acl_mode: str = "idp_wide"


@dataclass(slots=True)
class SyncSettings:
    mode: str = "incremental"
    workspace_ids: List[str] = field(default_factory=list)
    workspace_names: List[str] = field(default_factory=list)
    debug_dump_markdown: bool = False
    debug_dump_dir: str = "tmp"

    def has_workspace_filters(self) -> bool:
        return bool(self.workspace_ids or self.workspace_names)


@dataclass(slots=True)
class ConnectorSettings:
    serviceme: ServicemeAuthSettings
    gemini: GeminiSettings
    sync: SyncSettings

    @classmethod
    def from_env(cls) -> "ConnectorSettings":
        serviceme = ServicemeAuthSettings(
            base_url=_get_env("SERVICEME_BASE_URL", required=True),
            client_id=_get_env("SERVICEME_CLIENT_ID", required=True),
            client_secret=_get_env("SERVICEME_CLIENT_SECRET", required=True),
            account=_get_env("SERVICEME_ACCOUNT", required=True),
        )

        gemini = GeminiSettings(
            project_id=_get_env("GEMINI_PROJECT_ID", required=True),
            location=_get_env("GEMINI_LOCATION", "global"),
            data_store_id=_get_env("GEMINI_DATA_STORE_ID", "serviceme-kb"),
            identity_mapping_store_id=_get_env(
                "GEMINI_IDENTITY_MAPPING_STORE_ID", "serviceme-ims"
            ),
            data_store_display_name=_get_env(
                "GEMINI_DATA_STORE_DISPLAY_NAME", "SERVICEME Connector"
            )
            or "SERVICEME Connector",
            auto_create_resources=_get_bool_env("GEMINI_AUTO_CREATE_RESOURCES", True),
            acl_enabled=_get_bool_env("GEMINI_DATA_STORE_ACL_ENABLED", False),
            default_acl_readers=_to_list(_get_env("GEMINI_DEFAULT_ACL_READERS") or None),
            acl_mode=_normalize_acl_mode(_get_env("GEMINI_ACL_MODE", "idp_wide")),
        )

        sync = SyncSettings(
            mode=_get_env("SYNC_MODE", "incremental"),
            workspace_ids=_to_list(_get_env("SYNC_WORKSPACE_IDS") or None),
            workspace_names=_to_list(_get_env("SYNC_WORKSPACE_NAMES") or None),
            debug_dump_markdown=_get_bool_env("SYNC_DEBUG_DUMP_MARKDOWN", False),
            debug_dump_dir=_get_env("SYNC_DEBUG_DUMP_DIR", "tmp"),
        )

        return cls(serviceme=serviceme, gemini=gemini, sync=sync)

    def describe_workspace_filters(self) -> str:
        """Return human readable description for logging."""
        if not self.sync.has_workspace_filters():
            return "全部文档空间"
        filters: List[str] = []
        if self.sync.workspace_ids:
            filters.append(f"IDs={','.join(self.sync.workspace_ids)}")
        if self.sync.workspace_names:
            filters.append(f"Names={','.join(self.sync.workspace_names)}")
        return " / ".join(filters)
