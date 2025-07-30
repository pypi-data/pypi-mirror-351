from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostRoutePartsProducingPlaceInPolygonBody")


@_attrs_define
class PostRoutePartsProducingPlaceInPolygonBody:
    """
    Attributes:
        polygon (Union[Unset, Any]):  Example: any.
        filters_values (Union[Unset, Any]):  Example: any.
    """

    polygon: Union[Unset, Any] = UNSET
    filters_values: Union[Unset, Any] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        polygon = self.polygon

        filters_values = self.filters_values

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if polygon is not UNSET:
            field_dict["polygon"] = polygon
        if filters_values is not UNSET:
            field_dict["filtersValues"] = filters_values

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        polygon = d.pop("polygon", UNSET)

        filters_values = d.pop("filtersValues", UNSET)

        post_route_parts_producing_place_in_polygon_body = cls(
            polygon=polygon,
            filters_values=filters_values,
        )

        post_route_parts_producing_place_in_polygon_body.additional_properties = d
        return post_route_parts_producing_place_in_polygon_body

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
