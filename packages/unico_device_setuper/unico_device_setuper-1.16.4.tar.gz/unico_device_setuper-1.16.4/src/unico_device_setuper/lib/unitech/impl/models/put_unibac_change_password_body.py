from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutUnibacChangePasswordBody")


@_attrs_define
class PutUnibacChangePasswordBody:
    """
    Attributes:
        password (Union[Unset, Any]):  Example: any.
        new_password (Union[Unset, Any]):  Example: any.
    """

    password: Union[Unset, Any] = UNSET
    new_password: Union[Unset, Any] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        password = self.password

        new_password = self.new_password

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if password is not UNSET:
            field_dict["password"] = password
        if new_password is not UNSET:
            field_dict["newPassword"] = new_password

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        password = d.pop("password", UNSET)

        new_password = d.pop("newPassword", UNSET)

        put_unibac_change_password_body = cls(
            password=password,
            new_password=new_password,
        )

        put_unibac_change_password_body.additional_properties = d
        return put_unibac_change_password_body

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
