from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.register_device_payload import RegisterDevicePayload
from ...models.register_device_response import RegisterDeviceResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    
    body: RegisterDevicePayload,
    authorization: Union[None, Unset, str] = UNSET,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": "/auth/device/registerDevice",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
     client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[RegisterDeviceResponse]:
    if response.status_code == HTTPStatus.OK:
        response_200 = RegisterDeviceResponse.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
     client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[RegisterDeviceResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    
    client: Union[AuthenticatedClient, Client],
    body: RegisterDevicePayload,
    authorization: Union[None, Unset, str] = UNSET,
) -> Response[RegisterDeviceResponse]:
    """
    Args:
        authorization (Union[None, Unset, str]):
        body (RegisterDevicePayload):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RegisterDeviceResponse]
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
    body: RegisterDevicePayload,
    authorization: Union[None, Unset, str] = UNSET,
) -> Optional[RegisterDeviceResponse]:
    """
    Args:
        authorization (Union[None, Unset, str]):
        body (RegisterDevicePayload):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RegisterDeviceResponse
    """

    return sync_detailed(
        client=client,
        body=body,
        authorization=authorization,
    ).parsed


async def detailed_request(
    
    client: Union[AuthenticatedClient, Client],
    body: RegisterDevicePayload,
    authorization: Union[None, Unset, str] = UNSET,
) -> Response[RegisterDeviceResponse]:
    """
    Args:
        authorization (Union[None, Unset, str]):
        body (RegisterDevicePayload):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RegisterDeviceResponse]
    """

    kwargs = _get_kwargs(
        body=body,
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def request(
    
    client: Union[AuthenticatedClient, Client],
    body: RegisterDevicePayload,
    authorization: Union[None, Unset, str] = UNSET,
) -> Optional[RegisterDeviceResponse]:
    """
    Args:
        authorization (Union[None, Unset, str]):
        body (RegisterDevicePayload):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RegisterDeviceResponse
    """

    return (
        await detailed_request(
            client=client,
            body=body,
            authorization=authorization,
        )
    ).parsed
