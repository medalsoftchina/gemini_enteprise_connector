"""
Connector package entry point.

The package currently focuses on:
1. 通过模拟的 OAuth2.0 认证获取令牌（基于账号派生 scope）。
2. 在同步期间筛选特定的 SERVICEME 文档空间。
"""

from .config import ConnectorSettings  # noqa: F401
