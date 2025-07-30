# ruff: noqa: D100, D102, D103, S101, S106

import pytest
from httpx import AsyncClient
from httpx import HTTPError
from pytest_httpx import HTTPXMock

from minimal_activitypub.client_2_server import ActivityPub
from minimal_activitypub.client_2_server import NetworkError


@pytest.mark.asyncio
async def test_create_app(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        json={
            "client_id": "client-id",
            "client_secret": "client-secret",
        },
        headers={},
    )
    client = AsyncClient()
    client_id, client_secret = await ActivityPub.create_app(
        client=client,
        instance_url="https://instance.url",
    )

    request = httpx_mock.get_request()

    assert request.url == "https://instance.url/api/v1/apps"
    assert client_id == "client-id"
    assert client_secret == "client-secret"  # noqa: S105


@pytest.mark.asyncio
async def test_create_app_network_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_exception(HTTPError("Unable to read within timeout"))
    client = AsyncClient()
    with pytest.raises(NetworkError):
        _token = await ActivityPub.create_app(
            client=client,
            instance_url="instance.url",
        )
