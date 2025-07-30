from http import HTTPStatus
from typing import Any, Dict, Optional, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_action_rebuild_computed_tags_v1_actions_rebuild_computed_tags_item_uuid_post_response_api_action_rebuild_computed_tags_v1_actions_rebuild_computed_tags_item_uuid_post import (
    ApiActionRebuildComputedTagsV1ActionsRebuildComputedTagsItemUuidPostResponseApiActionRebuildComputedTagsV1ActionsRebuildComputedTagsItemUuidPost,
)
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    item_uuid: UUID,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": f"/v1/actions/rebuild_computed_tags/{item_uuid}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        ApiActionRebuildComputedTagsV1ActionsRebuildComputedTagsItemUuidPostResponseApiActionRebuildComputedTagsV1ActionsRebuildComputedTagsItemUuidPost,
        HTTPValidationError,
    ]
]:
    if response.status_code == 202:
        response_202 = ApiActionRebuildComputedTagsV1ActionsRebuildComputedTagsItemUuidPostResponseApiActionRebuildComputedTagsV1ActionsRebuildComputedTagsItemUuidPost.from_dict(
            response.json()
        )

        return response_202
    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        ApiActionRebuildComputedTagsV1ActionsRebuildComputedTagsItemUuidPostResponseApiActionRebuildComputedTagsV1ActionsRebuildComputedTagsItemUuidPost,
        HTTPValidationError,
    ]
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    item_uuid: UUID,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[
    Union[
        ApiActionRebuildComputedTagsV1ActionsRebuildComputedTagsItemUuidPostResponseApiActionRebuildComputedTagsV1ActionsRebuildComputedTagsItemUuidPost,
        HTTPValidationError,
    ]
]:
    """Api Action Rebuild Computed Tags

     Recalculate all computed tags for specific user.

    If `including_children` is set to True, this will also affect all
    descendants of the item. This operation potentially can take a lot of time.

    Args:
        item_uuid (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ApiActionRebuildComputedTagsV1ActionsRebuildComputedTagsItemUuidPostResponseApiActionRebuildComputedTagsV1ActionsRebuildComputedTagsItemUuidPost, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        item_uuid=item_uuid,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    item_uuid: UUID,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[
    Union[
        ApiActionRebuildComputedTagsV1ActionsRebuildComputedTagsItemUuidPostResponseApiActionRebuildComputedTagsV1ActionsRebuildComputedTagsItemUuidPost,
        HTTPValidationError,
    ]
]:
    """Api Action Rebuild Computed Tags

     Recalculate all computed tags for specific user.

    If `including_children` is set to True, this will also affect all
    descendants of the item. This operation potentially can take a lot of time.

    Args:
        item_uuid (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ApiActionRebuildComputedTagsV1ActionsRebuildComputedTagsItemUuidPostResponseApiActionRebuildComputedTagsV1ActionsRebuildComputedTagsItemUuidPost, HTTPValidationError]
    """

    return sync_detailed(
        item_uuid=item_uuid,
        client=client,
    ).parsed


async def asyncio_detailed(
    item_uuid: UUID,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[
    Union[
        ApiActionRebuildComputedTagsV1ActionsRebuildComputedTagsItemUuidPostResponseApiActionRebuildComputedTagsV1ActionsRebuildComputedTagsItemUuidPost,
        HTTPValidationError,
    ]
]:
    """Api Action Rebuild Computed Tags

     Recalculate all computed tags for specific user.

    If `including_children` is set to True, this will also affect all
    descendants of the item. This operation potentially can take a lot of time.

    Args:
        item_uuid (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ApiActionRebuildComputedTagsV1ActionsRebuildComputedTagsItemUuidPostResponseApiActionRebuildComputedTagsV1ActionsRebuildComputedTagsItemUuidPost, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        item_uuid=item_uuid,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    item_uuid: UUID,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[
    Union[
        ApiActionRebuildComputedTagsV1ActionsRebuildComputedTagsItemUuidPostResponseApiActionRebuildComputedTagsV1ActionsRebuildComputedTagsItemUuidPost,
        HTTPValidationError,
    ]
]:
    """Api Action Rebuild Computed Tags

     Recalculate all computed tags for specific user.

    If `including_children` is set to True, this will also affect all
    descendants of the item. This operation potentially can take a lot of time.

    Args:
        item_uuid (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ApiActionRebuildComputedTagsV1ActionsRebuildComputedTagsItemUuidPostResponseApiActionRebuildComputedTagsV1ActionsRebuildComputedTagsItemUuidPost, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            item_uuid=item_uuid,
            client=client,
        )
    ).parsed
