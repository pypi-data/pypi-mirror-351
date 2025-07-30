# ruff: noqa: D100, D102, D103, S101

import pytest

from minimal_activitypub.client_2_server import ActivityPub


@pytest.mark.asyncio
async def test_generate_auth_url() -> None:
    url = await ActivityPub.generate_authorization_url(
        instance_url="instance.url",
        client_id="client_id",
        user_agent="user_agent",
    )

    assert (
        url
        == "https://instance.url/oauth/authorize?response_type=code&client_id=client_id&redirect_uri=urn%3Aietf%3Awg%3Aoauth%3A2.0%3Aoob&scope=read+write"
    )
