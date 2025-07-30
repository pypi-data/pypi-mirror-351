# ruff: noqa: D100, D102, D103, S101, S106

import pytest
from httpx import AsyncClient
from httpx import HTTPError
from pytest_httpx import HTTPXMock

from minimal_activitypub.client_2_server import INSTANCE_TYPE_PLEROMA
from minimal_activitypub.client_2_server import INSTANCE_TYPE_TAKAHE
from minimal_activitypub.client_2_server import ActivityPub
from minimal_activitypub.client_2_server import NetworkError


@pytest.mark.asyncio
async def test_determine_instance_type_takahe(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        json={
            "version": "takahe v12.3.4",
            "configuration": {
                "statuses": {
                    "max_characters": 500,
                    "max_media_attachments": 10,
                },
                "media_attachments": {
                    "image_size_limit": 1234567,
                    "supported_mime_types": [
                        "jpg",
                        "webp",
                        "mp4",
                    ],
                },
            },
        },
        headers={},
    )
    client = AsyncClient()
    instance = ActivityPub(
        instance="instance.url",
        client=client,
        access_token="access_token",
    )
    await instance.determine_instance_type()

    assert instance.instance_type == INSTANCE_TYPE_TAKAHE
    assert instance.max_status_len == 500
    assert instance.max_attachments == 10
    assert instance.max_att_size == 1234567
    assert "jpg" in instance.supported_mime_types
    assert "webp" in instance.supported_mime_types
    assert "mp4" in instance.supported_mime_types
    assert "mkv" not in instance.supported_mime_types


@pytest.mark.asyncio
async def test_determine_instance_type_pleroma(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        json={
            "version": "Pleroma v37.8.9",
            "max_characters": 1000,
            "max_media_attachments": 20,
            "configuration": {
                "media_attachments": {
                    "image_size_limit": 2345678,
                    "supported_mime_types": [
                        "mkv",
                    ],
                },
            },
        },
        headers={},
    )
    client = AsyncClient()
    instance = ActivityPub(
        instance="instance.url",
        client=client,
        access_token="access_token",
    )
    await instance.determine_instance_type()

    assert instance.instance_type == INSTANCE_TYPE_PLEROMA
    assert instance.max_status_len == 1000
    assert instance.max_attachments == 20
    assert instance.max_att_size == 2345678
    assert instance.supported_mime_types is not None
    assert "jpg" not in instance.supported_mime_types
    assert "webp" not in instance.supported_mime_types
    assert "mp4" not in instance.supported_mime_types
    assert "mkv" in instance.supported_mime_types


@pytest.mark.asyncio
async def test_verify_creds_network_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_exception(HTTPError("Unable to read within timeout"))
    client = AsyncClient()
    instance = ActivityPub(
        instance="https://instance.url",
        client=client,
        access_token="access_token",
    )
    with pytest.raises(NetworkError):
        await instance.determine_instance_type()
