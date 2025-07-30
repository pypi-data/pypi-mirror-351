# ruff: noqa: D100, D102, D103, S101, S106

import pytest
from httpx import AsyncClient
from pytest_httpx import HTTPXMock

from minimal_activitypub.client_2_server import ActivityPub
from minimal_activitypub.client_2_server import ClientError
from minimal_activitypub.client_2_server import ConflictError
from minimal_activitypub.client_2_server import ForbiddenError
from minimal_activitypub.client_2_server import GoneError
from minimal_activitypub.client_2_server import NotFoundError
from minimal_activitypub.client_2_server import RatelimitError
from minimal_activitypub.client_2_server import UnauthorizedError
from minimal_activitypub.client_2_server import UnprocessedError


@pytest.mark.asyncio
async def test_unauthorized_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(status_code=401)
    client = AsyncClient()
    instance = ActivityPub(
        instance="https://instance.url",
        client=client,
        access_token="access_token",
    )
    with pytest.raises(UnauthorizedError):
        await instance.get_public_timeline()


@pytest.mark.asyncio
async def test_forbidden_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(status_code=403)
    client = AsyncClient()
    instance = ActivityPub(
        instance="https://instance.url",
        client=client,
        access_token="access_token",
    )
    with pytest.raises(ForbiddenError):
        await instance.get_public_timeline()


@pytest.mark.asyncio
async def test_not_found_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(status_code=404)
    client = AsyncClient()
    instance = ActivityPub(
        instance="https://instance.url",
        client=client,
        access_token="access_token",
    )
    with pytest.raises(NotFoundError):
        await instance.get_public_timeline()


@pytest.mark.asyncio
async def test_conflict_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(status_code=409)
    client = AsyncClient()
    instance = ActivityPub(
        instance="https://instance.url",
        client=client,
        access_token="access_token",
    )
    with pytest.raises(ConflictError):
        await instance.get_public_timeline()


@pytest.mark.asyncio
async def test_gone_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(status_code=410)
    client = AsyncClient()
    instance = ActivityPub(
        instance="https://instance.url",
        client=client,
        access_token="access_token",
    )
    with pytest.raises(GoneError):
        await instance.get_public_timeline()


@pytest.mark.asyncio
async def test_unprocessed_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(status_code=422)
    client = AsyncClient()
    instance = ActivityPub(
        instance="https://instance.url",
        client=client,
        access_token="access_token",
    )
    with pytest.raises(UnprocessedError):
        await instance.get_public_timeline()


@pytest.mark.asyncio
async def test_rate_limit_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(status_code=429)
    client = AsyncClient()
    instance = ActivityPub(
        instance="https://instance.url",
        client=client,
        access_token="access_token",
    )
    with pytest.raises(RatelimitError):
        await instance.get_public_timeline()


@pytest.mark.asyncio
async def test_client_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(status_code=444)
    client = AsyncClient()
    instance = ActivityPub(
        instance="https://instance.url",
        client=client,
        access_token="access_token",
    )
    with pytest.raises(ClientError):
        await instance.get_public_timeline()
