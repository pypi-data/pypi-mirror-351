# ruff: noqa: D100, D102, D103, S101, S106

import pytest
from httpx import AsyncClient
from httpx import HTTPError
from pytest_httpx import HTTPXMock

from minimal_activitypub import SearchType
from minimal_activitypub.client_2_server import ActivityPub
from minimal_activitypub.client_2_server import NetworkError


@pytest.mark.asyncio
async def test_search(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        json={
            "accounts": [],
            "hashtags": [],
            "statuses": [
                {
                    "id": "108880211901672326",
                    "created_at": "2022-08-24T22:29:46.493Z",
                    "in_reply_to_id": "108880209317577809",
                    "in_reply_to_account_id": "103641",
                    "sensitive": "false",
                },
            ],
        },
        headers={},
    )
    client = AsyncClient()
    instance = ActivityPub(
        instance="https://instance.url",
        client=client,
        access_token="access_token",
    )
    response = await instance.search(
        query="abc",
        query_type=SearchType.STATUSES,
        account_id="akjsghfa",
        max_id="max-id",
        min_id="min-id",
        limit=12,
        offset=5,
        following=True,
        exclude_unreviewed=True,
    )

    request = httpx_mock.get_request()

    assert request.url == (
        "https://instance.url/api/v2/search?q=abc&type=statuses&resolve=true&following=true&account_id=akjsghfa"
        "&exclude_unreviewed=true&max_id=max-id&min_id=min-id&limit=12&offset=5"
    )
    assert response["statuses"][0].get("id") == "108880211901672326"


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
        await instance.search(query="cats", query_type=SearchType.STATUSES)
