from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict

from connector.config import GeminiSettings

try:  # pragma: no cover - optional dependency
    from google.api_core import exceptions as gcp_exceptions
except Exception:  # pragma: no cover
    gcp_exceptions = None  # type: ignore[assignment]

try:  # pragma: no cover - optional dependency
    from google.cloud import discoveryengine_v1 as discoveryengine
except Exception:  # pragma: no cover
    discoveryengine = None  # type: ignore[assignment]

try:  # pragma: no cover - optional dependency
    from google.auth import exceptions as auth_exceptions
except Exception:  # pragma: no cover
    auth_exceptions = None  # type: ignore[assignment]

LOGGER = logging.getLogger(__name__)


class GeminiResourceError(RuntimeError):
    """Raised when Discovery Engine 资源缺失或 SDK 不可用。"""


@dataclass(slots=True)
class GeminiResourceHandles:
    identity_mapping_store_name: str | None
    data_store_name: str


class GeminiResourceManager:
    """Ensure identity mapping store & data store exist for the connector."""

    def __init__(
        self,
        settings: GeminiSettings,
        *,
        identity_client: Any | None = None,
        data_store_client: Any | None = None,
    ) -> None:
        self.settings = settings
        self.identity_client = identity_client
        self.data_store_client = data_store_client
        if self.identity_client is None or self.data_store_client is None:
            self._ensure_clients_available()
        if self.identity_client is None:
            self.identity_client = self._build_identity_client()
        if self.data_store_client is None:
            self.data_store_client = self._build_data_store_client()

    def ensure(self) -> GeminiResourceHandles:
        ims_name: str | None = None
        if self.settings.acl_enabled:
            ims_name = self._ensure_identity_mapping_store()
        data_store_name = self._ensure_data_store(identity_mapping_store=ims_name)
        return GeminiResourceHandles(
            identity_mapping_store_name=ims_name,
            data_store_name=data_store_name,
        )

    # ------------------------------------------------------------------ #
    def _ensure_identity_mapping_store(self) -> str:
        client = self.identity_client
        parent = self._location_path()
        name = self._identity_mapping_store_path()
        try:
            LOGGER.info("查询 Identity Mapping Store: %s", name)
            response = client.get_identity_mapping_store(name=name)
            return getattr(response, "name", name)
        except Exception as exc:
            if not self._is_not_found(exc):
                raise
            LOGGER.info("未找到 Identity Mapping Store，开始创建: %s", name)
            request = {
                "parent": parent,
                "identity_mapping_store": {},
                "identity_mapping_store_id": self.settings.identity_mapping_store_id,
            }
            response = client.create_identity_mapping_store(request=request)
            resolved = getattr(response, "result", lambda: response)()
            return getattr(resolved, "name", name)

    def _ensure_data_store(self, *, identity_mapping_store: str | None) -> str:
        client = self.data_store_client
        name = self._data_store_path(client)
        try:
            LOGGER.info("查询 Data Store: %s", name)
            response = client.get_data_store(name=name)
            return getattr(response, "name", name)
        except Exception as exc:
            if not self._is_not_found(exc):
                raise
            parent = self._collection_path(client)
            LOGGER.info(
                "未找到 Data Store，开始创建: %s (ACL=%s)",
                self.settings.data_store_id,
                self.settings.acl_enabled,
            )
            data_store_payload: Dict[str, Any] = {
                "display_name": self.settings.data_store_display_name or self.settings.data_store_id,
                "acl_enabled": self.settings.acl_enabled,
            }
            if identity_mapping_store:
                data_store_payload["identity_mapping_store"] = identity_mapping_store
            if discoveryengine is not None:
                data_store_payload["industry_vertical"] = discoveryengine.IndustryVertical.GENERIC
                data_store_payload["solution_types"] = [
                    discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH
                ]
                data_store_payload["content_config"] = (
                    discoveryengine.DataStore.ContentConfig.CONTENT_REQUIRED
                )
            request = {
                "parent": parent,
                "data_store": data_store_payload,
                "data_store_id": self.settings.data_store_id,
            }
            operation = client.create_data_store(request=request)
            response = getattr(operation, "result", lambda: operation)()
            return getattr(response, "name", name)

    # ------------------------------------------------------------------ #
    def _location_path(self) -> str:
        if hasattr(self.identity_client, "location_path"):
            return self.identity_client.location_path(
                project=self.settings.project_id,
                location=self.settings.location,
            )
        return f"projects/{self.settings.project_id}/locations/{self.settings.location}"

    def _identity_mapping_store_path(self) -> str:
        if hasattr(self.identity_client, "identity_mapping_store_path"):
            return self.identity_client.identity_mapping_store_path(
                project=self.settings.project_id,
                location=self.settings.location,
                identity_mapping_store=self.settings.identity_mapping_store_id,
            )
        parent = self._location_path()
        return f"{parent}/identityMappingStores/{self.settings.identity_mapping_store_id}"

    def _collection_path(self, client: Any) -> str:
        if hasattr(client, "collection_path"):
            return client.collection_path(
                self.settings.project_id,
                self.settings.location,
                "default_collection",
            )
        parent = f"projects/{self.settings.project_id}/locations/{self.settings.location}"
        return f"{parent}/collections/default_collection"

    def _data_store_path(self, client: Any) -> str:
        if hasattr(client, "data_store_path"):
            return client.data_store_path(
                self.settings.project_id,
                self.settings.location,
                self.settings.data_store_id,
            )
        parent = f"projects/{self.settings.project_id}/locations/{self.settings.location}"
        return f"{parent}/dataStores/{self.settings.data_store_id}"

    @staticmethod
    def _is_not_found(exc: Exception) -> bool:
        if gcp_exceptions and isinstance(exc, gcp_exceptions.NotFound):
            return True
        return getattr(exc, "code", None) == 404

    @staticmethod
    def _ensure_clients_available() -> None:
        if discoveryengine is None:
            raise GeminiResourceError(
                "找不到 google-cloud-discoveryengine，请先安装后再启用自动创建资源功能。"
            )

    def _build_identity_client(self):
        try:
            return discoveryengine.IdentityMappingStoreServiceClient()
        except Exception as exc:  # pragma: no cover - client init
            self._raise_if_credentials_missing(exc, "IdentityMappingStoreServiceClient")
            raise

    def _build_data_store_client(self):
        try:
            return discoveryengine.DataStoreServiceClient()
        except Exception as exc:  # pragma: no cover - client init
            self._raise_if_credentials_missing(exc, "DataStoreServiceClient")
            raise

    def _raise_if_credentials_missing(self, exc: Exception, client_name: str) -> None:
        if auth_exceptions and isinstance(exc, auth_exceptions.DefaultCredentialsError):
            raise GeminiResourceError(
                (
                    f"无法初始化 {client_name}: 未找到 Google Application Default Credentials。"
                    " 请设置 GOOGLE_APPLICATION_CREDENTIALS 或 GOOGLE_APPLICATION_CREDENTIALS_JSON，"
                    "或在 gcloud CLI 中执行 `gcloud auth application-default login` 后重试。"
                )
            ) from exc


def ensure_gemini_resources(settings: GeminiSettings) -> GeminiResourceHandles:
    """
    Ensure required Gemini Discovery Engine resources exist and return their names.
    """
    manager = GeminiResourceManager(settings)
    return manager.ensure()
