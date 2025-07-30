from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostProducingPlaceDistinctByContainersIdsBody")


@_attrs_define
class PostProducingPlaceDistinctByContainersIdsBody:
    """
    Attributes:
        index_ofproducing_place_a (Union[Unset, Any]):  Example: any.
        index_ofproducing_place_b (Union[Unset, Any]):  Example: any.
    """

    index_ofproducing_place_a: Union[Unset, Any] = UNSET
    index_ofproducing_place_b: Union[Unset, Any] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        index_ofproducing_place_a = self.index_ofproducing_place_a

        index_ofproducing_place_b = self.index_ofproducing_place_b

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if index_ofproducing_place_a is not UNSET:
            field_dict["indexOf(producingPlaceA"] = index_ofproducing_place_a
        if index_ofproducing_place_b is not UNSET:
            field_dict["indexOf(producingPlaceB"] = index_ofproducing_place_b

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        index_ofproducing_place_a = d.pop("indexOf(producingPlaceA", UNSET)

        index_ofproducing_place_b = d.pop("indexOf(producingPlaceB", UNSET)

        post_producing_place_distinct_by_containers_ids_body = cls(
            index_ofproducing_place_a=index_ofproducing_place_a,
            index_ofproducing_place_b=index_ofproducing_place_b,
        )

        post_producing_place_distinct_by_containers_ids_body.additional_properties = d
        return post_producing_place_distinct_by_containers_ids_body

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
