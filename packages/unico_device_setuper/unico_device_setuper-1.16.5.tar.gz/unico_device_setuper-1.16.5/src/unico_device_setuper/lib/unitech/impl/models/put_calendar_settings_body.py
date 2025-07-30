from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutCalendarSettingsBody")


@_attrs_define
class PutCalendarSettingsBody:
    """
    Attributes:
        hour_height (Union[Unset, Any]):  Example: any.
        default_view (Union[Unset, Any]):  Example: any.
    """

    hour_height: Union[Unset, Any] = UNSET
    default_view: Union[Unset, Any] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        hour_height = self.hour_height

        default_view = self.default_view

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if hour_height is not UNSET:
            field_dict["hourHeight"] = hour_height
        if default_view is not UNSET:
            field_dict["defaultView"] = default_view

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        hour_height = d.pop("hourHeight", UNSET)

        default_view = d.pop("defaultView", UNSET)

        put_calendar_settings_body = cls(
            hour_height=hour_height,
            default_view=default_view,
        )

        put_calendar_settings_body.additional_properties = d
        return put_calendar_settings_body

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
