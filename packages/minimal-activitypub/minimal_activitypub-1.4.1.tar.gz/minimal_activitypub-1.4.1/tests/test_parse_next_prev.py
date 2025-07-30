# ruff: noqa: D100, D102, D103, S101, S106

from httpx import AsyncClient

from minimal_activitypub.client_2_server import ActivityPub


def test_parse_next_prev_none() -> None:
    client = AsyncClient()
    instance = ActivityPub(
        instance="https://instance.url",
        client=client,
        access_token="access_token",
    )

    instance._parse_next_prev(links=None)

    assert instance.pagination == {
        "next": {"max_id": None, "min_id": None},
        "prev": {"max_id": None, "min_id": None},
    }


def test_parse_next_prev() -> None:
    client = AsyncClient()
    instance = ActivityPub(
        instance="https://instance.url",
        client=client,
        access_token="access_token",
    )
    links = (
        "Link: "
        '<https://mastodon.example/api/v1/endpoint?max_id=7163058>; rel="next", '
        '<https://mastodon.example/api/v1/endpoint?min_id=7275607>; rel="prev"'
    )

    instance._parse_next_prev(links=links)

    assert isinstance(instance.pagination, dict)
    assert instance.pagination["next"]["min_id"] is None
    assert instance.pagination["next"]["max_id"] == "7163058"
    assert instance.pagination["prev"]["min_id"] == "7275607"
    assert instance.pagination["prev"]["max_id"] is None
