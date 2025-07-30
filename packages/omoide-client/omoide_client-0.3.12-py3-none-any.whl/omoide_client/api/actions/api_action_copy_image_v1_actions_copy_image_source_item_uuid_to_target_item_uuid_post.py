from http import HTTPStatus
from typing import Any, Dict, Optional, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.api_action_copy_image_v1_actions_copy_image_source_item_uuid_to_target_item_uuid_post_response_api_action_copy_image_v1_actions_copy_image_source_item_uuid_to_target_item_uuid_post import (
    ApiActionCopyImageV1ActionsCopyImageSourceItemUuidToTargetItemUuidPostResponseApiActionCopyImageV1ActionsCopyImageSourceItemUuidToTargetItemUuidPost,
)
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    source_item_uuid: UUID,
    target_item_uuid: UUID,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": f"/v1/actions/copy_image/{source_item_uuid}/to/{target_item_uuid}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        ApiActionCopyImageV1ActionsCopyImageSourceItemUuidToTargetItemUuidPostResponseApiActionCopyImageV1ActionsCopyImageSourceItemUuidToTargetItemUuidPost,
        HTTPValidationError,
    ]
]:
    if response.status_code == 202:
        response_202 = ApiActionCopyImageV1ActionsCopyImageSourceItemUuidToTargetItemUuidPostResponseApiActionCopyImageV1ActionsCopyImageSourceItemUuidToTargetItemUuidPost.from_dict(
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
        ApiActionCopyImageV1ActionsCopyImageSourceItemUuidToTargetItemUuidPostResponseApiActionCopyImageV1ActionsCopyImageSourceItemUuidToTargetItemUuidPost,
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
    source_item_uuid: UUID,
    target_item_uuid: UUID,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[
    Union[
        ApiActionCopyImageV1ActionsCopyImageSourceItemUuidToTargetItemUuidPostResponseApiActionCopyImageV1ActionsCopyImageSourceItemUuidToTargetItemUuidPost,
        HTTPValidationError,
    ]
]:
    """Api Action Copy Image

     Copy image from one item to another.

    This will invoke copying of content, preview and a thumbnail.

    Args:
        source_item_uuid (UUID):
        target_item_uuid (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ApiActionCopyImageV1ActionsCopyImageSourceItemUuidToTargetItemUuidPostResponseApiActionCopyImageV1ActionsCopyImageSourceItemUuidToTargetItemUuidPost, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        source_item_uuid=source_item_uuid,
        target_item_uuid=target_item_uuid,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    source_item_uuid: UUID,
    target_item_uuid: UUID,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[
    Union[
        ApiActionCopyImageV1ActionsCopyImageSourceItemUuidToTargetItemUuidPostResponseApiActionCopyImageV1ActionsCopyImageSourceItemUuidToTargetItemUuidPost,
        HTTPValidationError,
    ]
]:
    """Api Action Copy Image

     Copy image from one item to another.

    This will invoke copying of content, preview and a thumbnail.

    Args:
        source_item_uuid (UUID):
        target_item_uuid (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ApiActionCopyImageV1ActionsCopyImageSourceItemUuidToTargetItemUuidPostResponseApiActionCopyImageV1ActionsCopyImageSourceItemUuidToTargetItemUuidPost, HTTPValidationError]
    """

    return sync_detailed(
        source_item_uuid=source_item_uuid,
        target_item_uuid=target_item_uuid,
        client=client,
    ).parsed


async def asyncio_detailed(
    source_item_uuid: UUID,
    target_item_uuid: UUID,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[
    Union[
        ApiActionCopyImageV1ActionsCopyImageSourceItemUuidToTargetItemUuidPostResponseApiActionCopyImageV1ActionsCopyImageSourceItemUuidToTargetItemUuidPost,
        HTTPValidationError,
    ]
]:
    """Api Action Copy Image

     Copy image from one item to another.

    This will invoke copying of content, preview and a thumbnail.

    Args:
        source_item_uuid (UUID):
        target_item_uuid (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ApiActionCopyImageV1ActionsCopyImageSourceItemUuidToTargetItemUuidPostResponseApiActionCopyImageV1ActionsCopyImageSourceItemUuidToTargetItemUuidPost, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        source_item_uuid=source_item_uuid,
        target_item_uuid=target_item_uuid,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    source_item_uuid: UUID,
    target_item_uuid: UUID,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[
    Union[
        ApiActionCopyImageV1ActionsCopyImageSourceItemUuidToTargetItemUuidPostResponseApiActionCopyImageV1ActionsCopyImageSourceItemUuidToTargetItemUuidPost,
        HTTPValidationError,
    ]
]:
    """Api Action Copy Image

     Copy image from one item to another.

    This will invoke copying of content, preview and a thumbnail.

    Args:
        source_item_uuid (UUID):
        target_item_uuid (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ApiActionCopyImageV1ActionsCopyImageSourceItemUuidToTargetItemUuidPostResponseApiActionCopyImageV1ActionsCopyImageSourceItemUuidToTargetItemUuidPost, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            source_item_uuid=source_item_uuid,
            target_item_uuid=target_item_uuid,
            client=client,
        )
    ).parsed
