from datetime import datetime, timedelta, timezone

from connector.config import build_account_scope
from connector.utils.oauth import SimulatedOAuth2Session


class FakeClock:
    def __init__(self, start: datetime) -> None:
        self._current = start

    def advance(self, seconds: int) -> None:
        self._current = self._current + timedelta(seconds=seconds)

    def __call__(self) -> datetime:
        return self._current


def test_build_account_scope_normalizes_account() -> None:
    scope = build_account_scope("User@Example.com ")
    assert scope == "serviceme::user@example.com::full_access"


def test_simulated_session_refreshes_after_expiration() -> None:
    clock = FakeClock(datetime(2024, 11, 27, tzinfo=timezone.utc))
    session = SimulatedOAuth2Session("tester@example.com", token_ttl=60, clock=clock)

    token1 = session.get_token()
    clock.advance(20)
    token2 = session.get_token()
    clock.advance(50)
    token3 = session.get_token()

    assert token1.access_token == token2.access_token  # 未过期，token 重用
    assert token3.access_token != token1.access_token  # 超过 TTL 后应刷新
