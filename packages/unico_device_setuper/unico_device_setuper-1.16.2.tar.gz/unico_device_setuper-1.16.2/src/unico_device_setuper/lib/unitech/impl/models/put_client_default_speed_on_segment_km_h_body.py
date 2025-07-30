from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutClientDefaultSpeedOnSegmentKmHBody")


@_attrs_define
class PutClientDefaultSpeedOnSegmentKmHBody:
    """
    Attributes:
        new_default_speed_on_segment_km_h (Union[Unset, Any]):  Example: any.
    """

    new_default_speed_on_segment_km_h: Union[Unset, Any] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        new_default_speed_on_segment_km_h = self.new_default_speed_on_segment_km_h

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if new_default_speed_on_segment_km_h is not UNSET:
            field_dict["newDefaultSpeedOnSegmentKmH"] = new_default_speed_on_segment_km_h

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        new_default_speed_on_segment_km_h = d.pop("newDefaultSpeedOnSegmentKmH", UNSET)

        put_client_default_speed_on_segment_km_h_body = cls(
            new_default_speed_on_segment_km_h=new_default_speed_on_segment_km_h,
        )

        put_client_default_speed_on_segment_km_h_body.additional_properties = d
        return put_client_default_speed_on_segment_km_h_body

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
