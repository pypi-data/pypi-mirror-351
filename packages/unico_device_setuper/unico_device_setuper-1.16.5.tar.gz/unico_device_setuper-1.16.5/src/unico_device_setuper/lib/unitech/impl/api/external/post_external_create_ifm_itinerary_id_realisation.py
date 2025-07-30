from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.post_external_create_ifm_itinerary_id_realisation_body import (
    PostExternalCreateIFMItineraryIdRealisationBody,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    id_realisation: str,
    
    body: PostExternalCreateIFMItineraryIdRealisationBody,
    authorization: Union[None, Unset, str] = UNSET,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": f"/external/createIFMItinerary/{id_realisation}",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response( client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Any]:
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response( client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Any]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id_realisation: str,
    
    client: Union[AuthenticatedClient, Client],
    body: PostExternalCreateIFMItineraryIdRealisationBody,
    authorization: Union[None, Unset, str] = UNSET,
) -> Response[Any]:
    """
    Args:
        id_realisation (str):
        authorization (Union[None, Unset, str]):
        body (PostExternalCreateIFMItineraryIdRealisationBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        id_realisation=id_realisation,
        body=body,
        authorization=authorization,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def detailed_request(
    id_realisation: str,
    
    client: Union[AuthenticatedClient, Client],
    body: PostExternalCreateIFMItineraryIdRealisationBody,
    authorization: Union[None, Unset, str] = UNSET,
) -> Response[Any]:
    """
    Args:
        id_realisation (str):
        authorization (Union[None, Unset, str]):
        body (PostExternalCreateIFMItineraryIdRealisationBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        id_realisation=id_realisation,
        body=body,
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
