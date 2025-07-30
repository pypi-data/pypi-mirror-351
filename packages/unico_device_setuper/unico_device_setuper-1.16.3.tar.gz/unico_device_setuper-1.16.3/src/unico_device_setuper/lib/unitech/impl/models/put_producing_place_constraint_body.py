from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutProducingPlaceConstraintBody")


@_attrs_define
class PutProducingPlaceConstraintBody:
    """
    Attributes:
        id (Union[Unset, Any]):  Example: any.
        id_producing_place (Union[Unset, Any]):  Example: any.
    """

    id: Union[Unset, Any] = UNSET
    id_producing_place: Union[Unset, Any] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        id_producing_place = self.id_producing_place

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if id_producing_place is not UNSET:
            field_dict["idProducingPlace"] = id_producing_place

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        id_producing_place = d.pop("idProducingPlace", UNSET)

        put_producing_place_constraint_body = cls(
            id=id,
            id_producing_place=id_producing_place,
        )

        put_producing_place_constraint_body.additional_properties = d
        return put_producing_place_constraint_body

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
