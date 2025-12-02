from __future__ import annotations

import hashlib
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Mapping, Sequence

import httpx


class ServicemeAPIError(Exception):
    """Base exception for SERVICEME API errors."""


class ServicemeAuthError(ServicemeAPIError):
    """Raised when authentication with SERVICEME fails."""


def _normalize_base_url(base_url: str) -> str:
    """
    Normalize user provided base url.

    Args:
        base_url: Base URL provided by the user.

    Returns:
        A normalized base URL with scheme and without trailing slash.
    """
    cleaned = (base_url or "").strip()
    if not cleaned:
        raise ValueError("Base URL 不能为空")
    if not cleaned.startswith(("http://", "https://")):
        cleaned = f"https://{cleaned}"
    return cleaned.rstrip("/")


def _build_signature(client_id: str, client_secret: str, account: str, timestamp: int, nonce: str) -> str:
    """
    Build MD5 signature required by SERVICEME authentication endpoint.
    """
    message = (
        f"client:{client_id}"
        f"secret:{client_secret}"
        f"account:{account}"
        f"timestamp:{timestamp}"
        f"nonce:{nonce}"
    )
    return hashlib.md5(message.encode("utf-8")).hexdigest()


def obtain_access_token(
    base_url: str,
    client_id: str,
    client_secret: str,
    account: str,
    *,
    timeout: float = 15.0,
) -> Dict[str, Any]:
    """
    Request access token from SERVICEME.
    """
    normalized_base_url = _normalize_base_url(base_url)
    timestamp = int(time.time() * 1000)
    # MD5 签名支持任意 6 位字符，使用随机 hex 保证唯一性
    nonce = secrets.token_hex(3)
    signature = _build_signature(client_id, client_secret, account, timestamp, nonce)

    url = f"{normalized_base_url}/openapi/auth/client_with_account"
    payload = {
        "client": client_id,
        "account": account,
        "timestamp": timestamp,
        "nonce": nonce,
        "signature": signature,
    }

    try:
        response = httpx.post(url, json=payload, timeout=timeout)
    except httpx.HTTPError as exc:
        raise ServicemeAuthError(f"无法连接到 SERVICEME 认证接口: {exc}") from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise ServicemeAuthError(f"认证接口返回了无法解析的响应: {exc}") from exc

    if response.status_code >= 400:
        raise ServicemeAuthError(
            f"认证失败: HTTP {response.status_code} - {data!r}"
        )

    if not data.get("success"):
        message = data.get("msg") or "认证失败，未返回 access_token"
        raise ServicemeAuthError(message)

    token_info = data.get("data") or {}
    access_token = token_info.get("access_token")
    if not access_token:
        raise ServicemeAuthError("认证响应缺少 access_token")

    expires_in = token_info.get("expires_in")
    expires_at_iso = None
    expires_at_ts = None
    if isinstance(expires_in, (int, float)):
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=float(expires_in))
        expires_at_iso = expires_at.isoformat()
        expires_at_ts = int(expires_at.timestamp())

    return {
        "base_url": normalized_base_url,
        "access_token": access_token,
        "expires_in": expires_in,
        "expires_at": expires_at_iso,
        "expires_at_ts": expires_at_ts,
    }


def fetch_workspaces(
    base_url: str,
    access_token: str,
    *,
    timeout: float = 15.0,
) -> List[Dict[str, Any]]:
    """
    Retrieve workspace list from SERVICEME.
    """
    normalized_base_url = _normalize_base_url(base_url)
    url = f"{normalized_base_url}/v1/openapi/workspace/all"
    headers = {"Authorization": f"openapi {access_token}"}

    try:
        response = httpx.get(url, headers=headers, timeout=timeout)
    except httpx.HTTPError as exc:
        raise ServicemeAPIError(f"获取文件空间列表失败: {exc}") from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise ServicemeAPIError(f"文件空间接口返回了无法解析的响应: {exc}") from exc

    if response.status_code >= 400:
        raise ServicemeAPIError(
            f"获取文件空间失败: HTTP {response.status_code} - {data!r}"
        )

    if not data.get("success"):
        message = data.get("msg") or "获取文件空间失败"
        raise ServicemeAPIError(message)

    categories = data.get("data") or []
    workspaces: List[Dict[str, Any]] = []
    for category in categories:
        for workspace in category.get("workspaces") or []:
            workspaces.append(workspace)
    return workspaces


def fetch_workspace_files(
    base_url: str,
    access_token: str,
    workspace: str,
    *,
    page_size: int = 50,
    timeout: float = 30.0,
) -> List[Dict[str, Any]]:
    """
    列举指定文件空间下的文件列表（自动翻页）。
    """
    normalized_base_url = _normalize_base_url(base_url)
    url = f"{normalized_base_url}/v1/openapi/workspace/file"
    headers = {
        "Authorization": f"openapi {access_token}",
        "Content-Type": "application/json",
    }
    workspace_name = (workspace or "").strip()
    if not workspace_name:
        raise ValueError("workspace 名称不能为空")

    files: List[Dict[str, Any]] = []
    page_index = 1
    while True:
        payload = {
            "workspace": workspace_name,
            "pageIndex": page_index,
            "pageSize": page_size,
        }
        try:
            response = httpx.post(url, headers=headers, json=payload, timeout=timeout)
        except httpx.HTTPError as exc:
            raise ServicemeAPIError(f"获取 workspace={workspace_name} 的文件失败: {exc}") from exc

        try:
            data = response.json()
        except ValueError as exc:
            raise ServicemeAPIError(f"文件列表响应无法解析: {exc}") from exc

        if response.status_code >= 400:
            raise ServicemeAPIError(
                f"获取文件失败: HTTP {response.status_code} - {data!r}"
            )

        if not data.get("success"):
            message = data.get("msg") or "获取文件失败"
            raise ServicemeAPIError(message)

        batch: Sequence[Mapping[str, Any]] = data.get("data") or []
        files.extend(dict(item) for item in batch)
        if len(batch) < page_size:
            break
        page_index += 1
    return files


def download_file_markdown(
    base_url: str,
    access_token: str,
    file_id: str | int,
    *,
    timeout: float = 60.0,
) -> str:
    """
    将 SERVICEME 文件转换为 Markdown 文本。
    """
    normalized_base_url = _normalize_base_url(base_url)
    url = f"{normalized_base_url}/v1/openapi/workspace/file/downloadDocument2MD"
    headers = {
        "Authorization": f"openapi {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/octet-stream",
    }

    payload = {"id": str(file_id)}

    try:
        response = httpx.post(url, headers=headers, json=payload, timeout=timeout)
    except httpx.HTTPError as exc:
        raise ServicemeAPIError(f"下载文件 {file_id} 的 Markdown 失败: {exc}") from exc

    if response.status_code >= 400:
        # 尝试解析错误响应
        message = None
        try:
            data = response.json()
            message = data.get("msg") or data
        except ValueError:
            message = response.text or response.reason_phrase
        raise ServicemeAPIError(
            f"下载文件失败: HTTP {response.status_code} - {message}"
        )

    if not response.content:
        return ""

    encoding = response.encoding or "utf-8"
    try:
        return response.content.decode(encoding)
    except UnicodeDecodeError:
        return response.content.decode("utf-8", errors="replace")


def rag_search(
    base_url: str,
    access_token: str,
    payload: Mapping[str, Any],
    *,
    timeout: float = 30.0,
) -> Mapping[str, Any]:
    """
    Perform RAG query against SERVICEME OpenAPI.

    Args:
        base_url: SERVICEME domain.
        access_token: Access token from authentication.
        payload: Request body including query parameters.

    Returns:
        Mapping containing the `data` payload returned by the API.
    """
    normalized_base_url = _normalize_base_url(base_url)
    url = f"{normalized_base_url}/v1/openapi/rag"
    headers = {
        "Authorization": f"openapi {access_token}",
        "Content-Type": "application/json",
    }

    try:
        response = httpx.post(url, headers=headers, json=dict(payload), timeout=timeout)
    except httpx.HTTPError as exc:
        raise ServicemeAPIError(f"RAG 查询请求失败: {exc}") from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise ServicemeAPIError(f"RAG 查询响应无法解析: {exc}") from exc

    if response.status_code >= 400:
        raise ServicemeAPIError(
            f"RAG 查询失败: HTTP {response.status_code} - {data!r}"
        )

    if not data.get("success"):
        message = data.get("msg") or "RAG 查询失败"
        raise ServicemeAPIError(message)

    return data.get("data") or {}
