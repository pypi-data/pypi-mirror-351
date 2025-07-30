from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostAuthLoginBody")


@_attrs_define
class PostAuthLoginBody:
    """
    Attributes:
        username (Union[Unset, Any]):  Example: any.
        password (Union[Unset, Any]):  Example: any.
        id_client (Union[Unset, Any]):  Example: any.
    """

    username: Union[Unset, Any] = UNSET
    password: Union[Unset, Any] = UNSET
    id_client: Union[Unset, Any] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        username = self.username

        password = self.password

        id_client = self.id_client

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if username is not UNSET:
            field_dict["username"] = username
        if password is not UNSET:
            field_dict["password"] = password
        if id_client is not UNSET:
            field_dict["idClient"] = id_client

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        username = d.pop("username", UNSET)

        password = d.pop("password", UNSET)

        id_client = d.pop("idClient", UNSET)

        post_auth_login_body = cls(
            username=username,
            password=password,
            id_client=id_client,
        )

        post_auth_login_body.additional_properties = d
        return post_auth_login_body

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
