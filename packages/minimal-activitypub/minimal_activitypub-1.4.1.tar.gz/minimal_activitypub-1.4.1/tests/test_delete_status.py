# ruff: noqa: D100, D102, D103, S101, S106
from typing import Any

import pytest
from httpx import AsyncClient
from httpx import HTTPError
from pytest_httpx import HTTPXMock

from minimal_activitypub.client_2_server import INSTANCE_TYPE_PLEROMA
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
async def test_delete_status_id(httpx_mock: HTTPXMock, status) -> None:
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
    response = await instance.delete_status(status="1234")

    request = httpx_mock.get_request()

    assert request.url == "https://instance.url/api/v1/statuses/1234"
    assert request.method == "DELETE"
    assert response == status


@pytest.mark.asyncio
async def test_delete_status_status(httpx_mock: HTTPXMock, status) -> None:
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
    response = await instance.delete_status(status=status)

    request = httpx_mock.get_request()

    assert request.url == "https://instance.url/api/v1/statuses/103254193998341330"
    assert request.method == "DELETE"
    assert response == status


@pytest.mark.asyncio
async def test_delete_status_reblogged(httpx_mock: HTTPXMock, status) -> None:
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
    instance.instance_type = INSTANCE_TYPE_PLEROMA
    status["reblogged"] = True
    status["reblog"] = {"id": "123456789"}

    response = await instance.delete_status(status=status)

    request = httpx_mock.get_request()

    assert request.url == "https://instance.url/api/v1/statuses/123456789/unreblog"
    assert request.method == "POST"
    assert response.get("id") == "103254193998341330"


@pytest.mark.asyncio
async def test_delete_status_favourited(httpx_mock: HTTPXMock, status) -> None:
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
    instance.instance_type = INSTANCE_TYPE_PLEROMA
    status["favourited"] = True

    response = await instance.delete_status(status=status)

    request = httpx_mock.get_request()

    assert request.url == "https://instance.url/api/v1/statuses/103254193998341330/unfavourite"
    assert request.method == "POST"
    assert response.get("id") == "103254193998341330"


@pytest.mark.asyncio
async def test_undo_reblog_status_id(httpx_mock: HTTPXMock, status) -> None:
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
    instance.instance_type = INSTANCE_TYPE_PLEROMA
    status["reblogged"] = True

    response = await instance.undo_reblog(status="103254193998341330")

    request = httpx_mock.get_request()

    assert request.url == "https://instance.url/api/v1/statuses/103254193998341330/unreblog"
    assert request.method == "POST"
    assert response.get("id") == "103254193998341330"


@pytest.mark.asyncio
async def test_delete_status_network_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_exception(HTTPError("Unable to read within timeout"))
    client = AsyncClient()
    instance = ActivityPub(
        instance="https://instance.url",
        client=client,
        access_token="access_token",
    )
    with pytest.raises(NetworkError):
        await instance.delete_status(status="111")


@pytest.mark.asyncio
async def test_undo_reblog_network_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_exception(HTTPError("Unable to read within timeout"))
    client = AsyncClient()
    instance = ActivityPub(
        instance="https://instance.url",
        client=client,
        access_token="access_token",
    )
    instance.instance_type = INSTANCE_TYPE_PLEROMA

    with pytest.raises(NetworkError):
        await instance.undo_reblog(status="111")


@pytest.mark.asyncio
async def test_undo_favourite_network_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_exception(HTTPError("Unable to read within timeout"))
    client = AsyncClient()
    instance = ActivityPub(
        instance="https://instance.url",
        client=client,
        access_token="access_token",
    )
    instance.instance_type = INSTANCE_TYPE_PLEROMA

    with pytest.raises(NetworkError):
        await instance.undo_favourite(status="111")
