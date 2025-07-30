from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="CurrentUserResponse")


@_attrs_define
class CurrentUserResponse:
    """
    Attributes:
        username (str):  Example: string.
        lastname (str):  Example: string.
        firstname (str):  Example: string.
        time_zone_name (str):  Example: string.
        client_id (str):  Example: string.
    """

    username: str
    lastname: str
    firstname: str
    time_zone_name: str
    client_id: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        username = self.username

        lastname = self.lastname

        firstname = self.firstname

        time_zone_name = self.time_zone_name

        client_id = self.client_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "username": username,
                "lastname": lastname,
                "firstname": firstname,
                "timeZoneName": time_zone_name,
                "clientId": client_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        username = d.pop("username")

        lastname = d.pop("lastname")

        firstname = d.pop("firstname")

        time_zone_name = d.pop("timeZoneName")

        client_id = d.pop("clientId")

        current_user_response = cls(
            username=username,
            lastname=lastname,
            firstname=firstname,
            time_zone_name=time_zone_name,
            client_id=client_id,
        )

        current_user_response.additional_properties = d
        return current_user_response

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
