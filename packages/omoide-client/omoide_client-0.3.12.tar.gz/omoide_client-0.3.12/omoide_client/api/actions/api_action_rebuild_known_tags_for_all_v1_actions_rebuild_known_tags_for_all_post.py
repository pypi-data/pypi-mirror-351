from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_action_rebuild_known_tags_for_all_v1_actions_rebuild_known_tags_for_all_post_response_api_action_rebuild_known_tags_for_all_v1_actions_rebuild_known_tags_for_all_post import (
    ApiActionRebuildKnownTagsForAllV1ActionsRebuildKnownTagsForAllPostResponseApiActionRebuildKnownTagsForAllV1ActionsRebuildKnownTagsForAllPost,
)
from ...types import Response


def _get_kwargs() -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": "/v1/actions/rebuild_known_tags_for_all",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    ApiActionRebuildKnownTagsForAllV1ActionsRebuildKnownTagsForAllPostResponseApiActionRebuildKnownTagsForAllV1ActionsRebuildKnownTagsForAllPost
]:
    if response.status_code == 202:
        response_202 = ApiActionRebuildKnownTagsForAllV1ActionsRebuildKnownTagsForAllPostResponseApiActionRebuildKnownTagsForAllV1ActionsRebuildKnownTagsForAllPost.from_dict(
            response.json()
        )

        return response_202
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    ApiActionRebuildKnownTagsForAllV1ActionsRebuildKnownTagsForAllPostResponseApiActionRebuildKnownTagsForAllV1ActionsRebuildKnownTagsForAllPost
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[
    ApiActionRebuildKnownTagsForAllV1ActionsRebuildKnownTagsForAllPostResponseApiActionRebuildKnownTagsForAllV1ActionsRebuildKnownTagsForAllPost
]:
    """Api Action Rebuild Known Tags For All

     Recalculate all known tags for registered user.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ApiActionRebuildKnownTagsForAllV1ActionsRebuildKnownTagsForAllPostResponseApiActionRebuildKnownTagsForAllV1ActionsRebuildKnownTagsForAllPost]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[
    ApiActionRebuildKnownTagsForAllV1ActionsRebuildKnownTagsForAllPostResponseApiActionRebuildKnownTagsForAllV1ActionsRebuildKnownTagsForAllPost
]:
    """Api Action Rebuild Known Tags For All

     Recalculate all known tags for registered user.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ApiActionRebuildKnownTagsForAllV1ActionsRebuildKnownTagsForAllPostResponseApiActionRebuildKnownTagsForAllV1ActionsRebuildKnownTagsForAllPost
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[
    ApiActionRebuildKnownTagsForAllV1ActionsRebuildKnownTagsForAllPostResponseApiActionRebuildKnownTagsForAllV1ActionsRebuildKnownTagsForAllPost
]:
    """Api Action Rebuild Known Tags For All

     Recalculate all known tags for registered user.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ApiActionRebuildKnownTagsForAllV1ActionsRebuildKnownTagsForAllPostResponseApiActionRebuildKnownTagsForAllV1ActionsRebuildKnownTagsForAllPost]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[
    ApiActionRebuildKnownTagsForAllV1ActionsRebuildKnownTagsForAllPostResponseApiActionRebuildKnownTagsForAllV1ActionsRebuildKnownTagsForAllPost
]:
    """Api Action Rebuild Known Tags For All

     Recalculate all known tags for registered user.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ApiActionRebuildKnownTagsForAllV1ActionsRebuildKnownTagsForAllPostResponseApiActionRebuildKnownTagsForAllV1ActionsRebuildKnownTagsForAllPost
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
