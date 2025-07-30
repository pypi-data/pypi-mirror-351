# ruff: noqa: D100, D102, D103, S101, S106

import pytest
from httpx import AsyncClient
from httpx import HTTPError
from pytest_httpx import HTTPXMock

from minimal_activitypub.client_2_server import ActivityPub
from minimal_activitypub.client_2_server import NetworkError


@pytest.mark.asyncio
async def test_validate_authorization_code(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        json={"access_token": "acc-token"},
        headers={},
    )
    client = AsyncClient()
    response = await ActivityPub.validate_authorization_code(
        client=client,
        instance_url="https://instance.url",
        authorization_code="123456",
        client_id="client-id",
        client_secret="client-secret",
    )

    request = httpx_mock.get_request()

    assert request.url == "https://instance.url/oauth/token"
    assert response == "acc-token"


@pytest.mark.asyncio
async def test_validate_authorization_code_network_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_exception(HTTPError("Unable to read within timeout"))
    client = AsyncClient()
    with pytest.raises(NetworkError):
        _token = await ActivityPub.validate_authorization_code(
            client=client,
            instance_url="instance.url",
            authorization_code="123456",
            client_id="client-id",
            client_secret="client-secret",
        )
