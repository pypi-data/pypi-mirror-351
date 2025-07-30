# ruff: noqa: D100, D102, D103, S101, S106
from datetime import datetime

import pytest
from httpx import AsyncClient
from whenever import Instant

from minimal_activitypub.client_2_server import ActivityPub
from minimal_activitypub.client_2_server import RatelimitError


@pytest.mark.asyncio
async def test_update_ratelimit() -> None:
    client = AsyncClient()
    instance = ActivityPub(
        instance="https://instance.url",
        client=client,
        access_token="access_token",
    )
    headers = {
        "X-RateLimit-Limit": "300",
        "X-RateLimit-Remaining": "0",
        "X-RateLimit-Reset": (Instant.now().add(minutes=5)).format_common_iso(),
    }

    instance._update_ratelimit(headers=headers)

    assert instance.ratelimit_limit == 300
    assert instance.ratelimit_remaining == 0
    assert isinstance(instance.ratelimit_reset, datetime)

    with pytest.raises(RatelimitError):
        await instance._pre_call_checks()
