# ruff: noqa: D100, D102, D103, S101, S106
from typing import Any

import pytest
from httpx import AsyncClient
from httpx import HTTPError
from pytest_httpx import HTTPXMock

from minimal_activitypub.client_2_server import ActivityPub
from minimal_activitypub.client_2_server import NetworkError


@pytest.fixture
def status() -> Any:  # nocl
    return {
        "id": "103254193998341330",
        "created_at": "2019-12-05T08:19:26.052Z",
        "in_reply_to_id": "null",
        "in_reply_to_account_id": "null",
        "sensitive": "false",
        "spoiler_text": "",
        "visibility": "public",
        "language": "en",
        "uri": "https://mastodon.social/users/trwnh/statuses/103254193998341330",
        "url": "https://mastodon.social/@trwnh/103254193998341330",
        "replies_count": 0,
        "reblogs_count": 0,
        "favourites_count": 0,
        "favourited": False,
        "reblogged": False,
        "muted": "false",
        "bookmarked": "false",
        "pinned": "false",
        "text": "test",
        "reblog": "null",
        "application": {"name": "Web", "website": "null"},
        "account": {
            "id": "14715",
            "username": "trwnh",
            "acct": "trwnh",
            "display_name": "infinite love ⴳ",
        },
        "media_attachments": [
            {
                "id": "22345792",
                "type": "image",
                "url": "https://files.mastodon.social/media_attachments/files/022/345/792/original/57859aede991da25.jpeg",
                "preview_url": "https://files.mastodon.social/media_attachments/files/022/345/792/small/57859aede991da25.jpeg",
                "remote_url": "null",
                "text_url": "https://mastodon.social/media/2N4uvkuUtPVrkZGysms",
                "meta": {
                    "original": {"width": 640, "height": 480, "size": "640x480", "aspect": 1.3333333333333333},
                    "small": {"width": 461, "height": 346, "size": "461x346", "aspect": 1.3323699421965318},
                    "focus": {"x": -0.27, "y": 0.51},
                },
                "description": "test media description",
                "blurhash": "UFBWY:8_0Jxv4mx]t8t64.%M-:IUWGWAt6M}",
            }
        ],
        "mentions": [],
        "tags": [],
        "emojis": [],
        "card": "null",
        "poll": "null",
    }


@pytest.mark.asyncio
async def test_post_status(httpx_mock: HTTPXMock, status) -> None:
    httpx_mock.add_response(
        json=status,
        headers={},
    )
    client = AsyncClient()
    instance = ActivityPub(
        instance="https://instance.url",
        client=client,
        access_token="access_token",
    )
    response = await instance.post_status(
        status="status", media_ids=["media-id-1", "media-id-2"], sensitive=True, spoiler_text="Spoiler for sensitive"
    )

    request = httpx_mock.get_request()

    assert request.url == "https://instance.url/api/v1/statuses"
    assert request.method == "POST"
    assert response == status


@pytest.mark.asyncio
async def test_reblog(httpx_mock: HTTPXMock, status) -> None:
    httpx_mock.add_response(
        json=status,
        headers={},
    )
    client = AsyncClient()
    instance = ActivityPub(
        instance="https://instance.url",
        client=client,
        access_token="access_token",
    )
    response = await instance.reblog(status_id="status")

    request = httpx_mock.get_request()

    assert request.url == "https://instance.url/api/v1/statuses/status/reblog"
    assert request.method == "POST"
    assert response == status


@pytest.mark.asyncio
async def test_post_status_network_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_exception(HTTPError("Unable to read within timeout"))
    client = AsyncClient()
    instance = ActivityPub(
        instance="https://instance.url",
        client=client,
        access_token="access_token",
    )
    with pytest.raises(NetworkError):
        await instance.post_status(status="status")


@pytest.mark.asyncio
async def test_reblog_network_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_exception(HTTPError("Unable to read within timeout"))
    client = AsyncClient()
    instance = ActivityPub(
        instance="https://instance.url",
        client=client,
        access_token="access_token",
    )
    with pytest.raises(NetworkError):
        await instance.reblog(status_id="status")
