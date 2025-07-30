from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostRoutePartsSegmentInLineBody")


@_attrs_define
class PostRoutePartsSegmentInLineBody:
    """
    Attributes:
        drawn_line (Union[Unset, Any]):  Example: any.
    """

    drawn_line: Union[Unset, Any] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        drawn_line = self.drawn_line

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if drawn_line is not UNSET:
            field_dict["drawnLine"] = drawn_line

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        drawn_line = d.pop("drawnLine", UNSET)

        post_route_parts_segment_in_line_body = cls(
            drawn_line=drawn_line,
        )

        post_route_parts_segment_in_line_body.additional_properties = d
        return post_route_parts_segment_in_line_body

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
