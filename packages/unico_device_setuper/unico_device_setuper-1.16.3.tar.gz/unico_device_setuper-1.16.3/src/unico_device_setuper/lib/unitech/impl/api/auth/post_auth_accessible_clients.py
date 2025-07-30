from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.accessible_clients_payload import AccessibleClientsPayload
from ...models.accessible_clients_response_item import AccessibleClientsResponseItem
from ...types import UNSET, Response, Unset


def _get_kwargs(
    
    body: AccessibleClientsPayload,
    authorization: Union[None, Unset, str] = UNSET,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": "/auth/accessibleClients",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
     client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[List["AccessibleClientsResponseItem"], str]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for componentsschemas_accessible_clients_response_item_data in _response_200:
            componentsschemas_accessible_clients_response_item = AccessibleClientsResponseItem.from_dict(
                componentsschemas_accessible_clients_response_item_data
            )

            response_200.append(componentsschemas_accessible_clients_response_item)

        return response_200
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        response_401 = cast(str, response.json())
        return response_401
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
     client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[List["AccessibleClientsResponseItem"], str]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    
    client: Union[AuthenticatedClient, Client],
    body: AccessibleClientsPayload,
    authorization: Union[None, Unset, str] = UNSET,
) -> Response[Union[List["AccessibleClientsResponseItem"], str]]:
    """
    Args:
        authorization (Union[None, Unset, str]):
        body (AccessibleClientsPayload):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[List['AccessibleClientsResponseItem'], str]]
    """

    kwargs = _get_kwargs(
        body=body,
        authorization=authorization,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    
    client: Union[AuthenticatedClient, Client],
    body: AccessibleClientsPayload,
    authorization: Union[None, Unset, str] = UNSET,
) -> Optional[Union[List["AccessibleClientsResponseItem"], str]]:
    """
    Args:
        authorization (Union[None, Unset, str]):
        body (AccessibleClientsPayload):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[List['AccessibleClientsResponseItem'], str]
    """

    return sync_detailed(
        client=client,
        body=body,
        authorization=authorization,
    ).parsed


async def detailed_request(
    
    client: Union[AuthenticatedClient, Client],
    body: AccessibleClientsPayload,
    authorization: Union[None, Unset, str] = UNSET,
) -> Response[Union[List["AccessibleClientsResponseItem"], str]]:
    """
    Args:
        authorization (Union[None, Unset, str]):
        body (AccessibleClientsPayload):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[List['AccessibleClientsResponseItem'], str]]
    """

    kwargs = _get_kwargs(
        body=body,
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def request(
    
    client: Union[AuthenticatedClient, Client],
    body: AccessibleClientsPayload,
    authorization: Union[None, Unset, str] = UNSET,
) -> Optional[Union[List["AccessibleClientsResponseItem"], str]]:
    """
    Args:
        authorization (Union[None, Unset, str]):
        body (AccessibleClientsPayload):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[List['AccessibleClientsResponseItem'], str]
    """

    return (
        await detailed_request(
            client=client,
            body=body,
            authorization=authorization,
        )
    ).parsed
