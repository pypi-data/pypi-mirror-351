# ruff: noqa: D100, D102, D103, S101, S106

import pytest
from httpx import AsyncClient
from httpx import HTTPError
from pytest_httpx import HTTPXMock

from minimal_activitypub.client_2_server import ActivityPub
from minimal_activitypub.client_2_server import NetworkError


@pytest.mark.asyncio
async def test_get_public_timeline(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        json=[
            {
                "id": "108880211901672326",
                "created_at": "2022-08-24T22:29:46.493Z",
                "in_reply_to_id": "108880209317577809",
                "in_reply_to_account_id": "103641",
                "sensitive": "false",
            },
        ],
        headers={},
    )
    client = AsyncClient()
    instance = ActivityPub(
        instance="https://instance.url",
        client=client,
        access_token="access_token",
    )
    response = await instance.get_public_timeline(
        local=True, remote=True, only_media=True, max_id="max-id", since_id="since-id", min_id="min-id"
    )

    request = httpx_mock.get_request()

    assert request.url == (
        "https://instance.url/api/v1/timelines/public?"
        "limit=20&local=true&remote=true&only_media=true&max_id=max-id"
        "&min_id=min-id&since-id=since-id"
    )
    assert response[0].get("id") == "108880211901672326"


@pytest.mark.asyncio
async def test_get_home_timeline(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        json=[
            {
                "id": "108880211901672326",
                "created_at": "2022-08-24T22:29:46.493Z",
                "in_reply_to_id": "108880209317577809",
                "in_reply_to_account_id": "103641",
                "sensitive": "false",
            },
        ],
        headers={},
    )
    client = AsyncClient()
    instance = ActivityPub(
        instance="https://instance.url",
        client=client,
        access_token="access_token",
    )
    response = await instance.get_home_timeline(max_id="max-id", since_id="since-id", min_id="min-id")

    request = httpx_mock.get_request()

    assert request.url == (
        "https://instance.url/api/v1/timelines/home?limit=20&max_id=max-id&min_id=min-id&since-id=since-id"
    )
    assert response[0].get("id") == "108880211901672326"


@pytest.mark.asyncio
async def test_get_hashtag_timeline(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        json=[
            {
                "id": "108880211901672326",
                "created_at": "2022-08-24T22:29:46.493Z",
                "in_reply_to_id": "108880209317577809",
                "in_reply_to_account_id": "103641",
                "sensitive": "false",
            },
        ],
        headers={},
    )
    client = AsyncClient()
    instance = ActivityPub(
        instance="https://instance.url",
        client=client,
        access_token="access_token",
    )
    response = await instance.get_hashtag_timeline(
        hashtag="cats",
        any_tags=["dogs"],
        all_tags=["kittens"],
        none_tags=["dragons"],
        max_id="max-id",
        since_id="since-id",
        min_id="min-id",
    )

    request = httpx_mock.get_request()

    assert request.url == (
        "https://instance.url/api/v1/timelines/tag/:cats?local=false&remote=false&only_media=false&limit=20"
        "&any%5B%5D=dogs&all%5B%5D=kittens&none%5B%5D=dragons&max_id=max-id&since-id=since-id&min_id=min-id"
    )
    assert response[0].get("id") == "108880211901672326"


@pytest.mark.asyncio
async def test_get_public_timeline_network_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_exception(HTTPError("Unable to read within timeout"))
    client = AsyncClient()
    instance = ActivityPub(
        instance="https://instance.url",
        client=client,
        access_token="access_token",
    )
    with pytest.raises(NetworkError):
        await instance.get_public_timeline()


@pytest.mark.asyncio
async def test_get_home_timeline_network_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_exception(HTTPError("Unable to read within timeout"))
    client = AsyncClient()
    instance = ActivityPub(
        instance="https://instance.url",
        client=client,
        access_token="access_token",
    )
    with pytest.raises(NetworkError):
        await instance.get_home_timeline()


@pytest.mark.asyncio
async def test_get_hashtag_timeline_network_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_exception(HTTPError("Unable to read within timeout"))
    client = AsyncClient()
    instance = ActivityPub(
        instance="https://instance.url",
        client=client,
        access_token="access_token",
    )
    with pytest.raises(NetworkError):
        await instance.get_hashtag_timeline(hashtag="cats")
