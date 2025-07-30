# ruff: noqa: D100, D102, D103, S101, S106
from pathlib import Path

import pytest
from httpx import AsyncClient
from httpx import HTTPError
from pytest_httpx import HTTPXMock

from minimal_activitypub.client_2_server import ActivityPub
from minimal_activitypub.client_2_server import NetworkError


@pytest.mark.asyncio
@pytest.mark.httpx_mock(assert_all_responses_were_requested=False)
async def test_post_media(httpx_mock: HTTPXMock) -> None:
    expected_response = {
        "id": "22348641",
        "type": "image",
        "url": "https://files.mastodon.social/media_attachments/files/022/348/641/original/e96382f26c72a29c.jpeg",
        "preview_url": "https://files.mastodon.social/media_attachments/files/022/348/641/small/e96382f26c72a29c.jpeg",
        "remote_url": None,
        "text_url": "https://mastodon.social/media/4Zj6ewxzzzDi0g8JnZQ",
        "meta": {
            "focus": {"x": -0.42, "y": 0.69},
            "original": {"width": 640, "height": 480, "size": "640x480", "aspect": 1.3333333333333333},
            "small": {"width": 461, "height": 346, "size": "461x346", "aspect": 1.3323699421965318},
        },
        "description": "test uploaded via api",
        "blurhash": "UFBWY:8_0Jxv4mx]t8t64.%M-:IUWGWAt6M}",
    }

    httpx_mock.add_response(
        json=expected_response,
        headers={},
    )
    client = AsyncClient()
    instance = ActivityPub(
        instance="https://instance.url",
        client=client,
        access_token="access_token",
    )
    Path("/tmp/dummy").touch(exist_ok=True)  # noqa: S108
    dummy_file = Path("/tmp/dummy").open(mode="rb")  # noqa: S108
    response = await instance.post_media(
        file=dummy_file,
        mime_type="jpg",
        description="Test Description",
        focus=(0.1, 0.5),
    )
    request = httpx_mock.get_request()

    dummy_file.close()

    assert request.url == "https://instance.url/api/v1/media"
    assert request.method == "POST"
    assert response == expected_response


@pytest.mark.asyncio
@pytest.mark.httpx_mock(assert_all_responses_were_requested=False)
async def test_post_media_network_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_exception(HTTPError("Unable to read within timeout"))
    client = AsyncClient()
    Path("/tmp/dummy").touch(exist_ok=True)  # noqa: S108
    dummy_file = Path("/tmp/dummy").open(mode="rb")  # noqa: S108
    instance = ActivityPub(
        instance="https://instance.url",
        client=client,
        access_token="access_token",
    )
    with pytest.raises(NetworkError):
        await instance.post_media(file=dummy_file, mime_type="jpg")

    dummy_file.close()
