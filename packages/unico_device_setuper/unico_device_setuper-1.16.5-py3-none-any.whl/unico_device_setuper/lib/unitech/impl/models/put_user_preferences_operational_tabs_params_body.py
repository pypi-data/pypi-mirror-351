from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutUserPreferencesOperationalTabsParamsBody")


@_attrs_define
class PutUserPreferencesOperationalTabsParamsBody:
    """
    Attributes:
        producing_place (Union[Unset, Any]):  Example: any.
        segment (Union[Unset, Any]):  Example: any.
        event (Union[Unset, Any]):  Example: any.
    """

    producing_place: Union[Unset, Any] = UNSET
    segment: Union[Unset, Any] = UNSET
    event: Union[Unset, Any] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        producing_place = self.producing_place

        segment = self.segment

        event = self.event

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if producing_place is not UNSET:
            field_dict["producingPlace"] = producing_place
        if segment is not UNSET:
            field_dict["segment"] = segment
        if event is not UNSET:
            field_dict["event"] = event

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        producing_place = d.pop("producingPlace", UNSET)

        segment = d.pop("segment", UNSET)

        event = d.pop("event", UNSET)

        put_user_preferences_operational_tabs_params_body = cls(
            producing_place=producing_place,
            segment=segment,
            event=event,
        )

        put_user_preferences_operational_tabs_params_body.additional_properties = d
        return put_user_preferences_operational_tabs_params_body

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
