from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Protocol

from connector.config import build_account_scope


class Clock(Protocol):
    def __call__(self) -> datetime: ...


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class OAuthToken:
    access_token: str
    scope: str
    issued_at: datetime
    expires_at: datetime

    def is_expired(self, *, leeway: int = 0, now: datetime | None = None) -> bool:
        reference = now or _utcnow()
        return reference >= (self.expires_at - timedelta(seconds=leeway))

    def to_header(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.access_token}"}


class SimulatedOAuth2Session:
    """
    用于本地开发 / 集成测试的 OAuth2.0 模拟器。

    - scope 直接由账号派生，确保同一账号始终映射到同一权限域。
    - access token 通过 SHA256(账号 + audience + 时间戳) 生成，不依赖外部服务。
    """

    def __init__(
        self,
        account: str,
        *,
        audience: str | None = None,
        token_ttl: int = 3600,
        clock: Clock | None = None,
    ) -> None:
        if not account:
            raise ValueError("account 不能为空")
        self.account = account.strip()
        self.audience = audience or os.getenv("SERVICEME_BASE_URL", "serviceme")
        self.token_ttl = token_ttl
        self._clock: Clock = clock or _utcnow
        self._token: OAuthToken | None = None

    def issue_token(self) -> OAuthToken:
        scope = build_account_scope(self.account)
        issued_at = self._clock()
        expires_at = issued_at + timedelta(seconds=self.token_ttl)
        payload = f"{scope}:{self.audience}:{int(issued_at.timestamp())}"
        access_token = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        token = OAuthToken(
            access_token=access_token,
            scope=scope,
            issued_at=issued_at,
            expires_at=expires_at,
        )
        self._token = token
        return token

    def get_token(self) -> OAuthToken:
        if self._token and not self._token.is_expired(leeway=30, now=self._clock()):
            return self._token
        return self.issue_token()
