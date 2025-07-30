from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.client_response import ClientResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    
    authorization: Union[None, Unset, str] = UNSET,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/client/",
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
     client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[List["ClientResponse"]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ClientResponse.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
     client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[List["ClientResponse"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    
    client: Union[AuthenticatedClient, Client],
    authorization: Union[None, Unset, str] = UNSET,
) -> Response[List["ClientResponse"]]:
    """
    Args:
        authorization (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['ClientResponse']]
    """

    kwargs = _get_kwargs(
        authorization=authorization,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    
    client: Union[AuthenticatedClient, Client],
    authorization: Union[None, Unset, str] = UNSET,
) -> Optional[List["ClientResponse"]]:
    """
    Args:
        authorization (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['ClientResponse']
    """

    return sync_detailed(
        client=client,
        authorization=authorization,
    ).parsed


async def detailed_request(
    
    client: Union[AuthenticatedClient, Client],
    authorization: Union[None, Unset, str] = UNSET,
) -> Response[List["ClientResponse"]]:
    """
    Args:
        authorization (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['ClientResponse']]
    """

    kwargs = _get_kwargs(
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def request(
    
    client: Union[AuthenticatedClient, Client],
    authorization: Union[None, Unset, str] = UNSET,
) -> Optional[List["ClientResponse"]]:
    """
    Args:
        authorization (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['ClientResponse']
    """

    return (
        await detailed_request(
            client=client,
            authorization=authorization,
        )
    ).parsed
