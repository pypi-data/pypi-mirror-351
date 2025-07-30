from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostAuthRegisterBody")


@_attrs_define
class PostAuthRegisterBody:
    """
    Attributes:
        email (Union[Unset, Any]):  Example: any.
        permissions (Union[Unset, Any]):  Example: any.
        sectors (Union[Unset, Any]):  Example: any.
    """

    email: Union[Unset, Any] = UNSET
    permissions: Union[Unset, Any] = UNSET
    sectors: Union[Unset, Any] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        email = self.email

        permissions = self.permissions

        sectors = self.sectors

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if email is not UNSET:
            field_dict["email"] = email
        if permissions is not UNSET:
            field_dict["permissions"] = permissions
        if sectors is not UNSET:
            field_dict["sectors"] = sectors

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        email = d.pop("email", UNSET)

        permissions = d.pop("permissions", UNSET)

        sectors = d.pop("sectors", UNSET)

        post_auth_register_body = cls(
            email=email,
            permissions=permissions,
            sectors=sectors,
        )

        post_auth_register_body.additional_properties = d
        return post_auth_register_body

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
