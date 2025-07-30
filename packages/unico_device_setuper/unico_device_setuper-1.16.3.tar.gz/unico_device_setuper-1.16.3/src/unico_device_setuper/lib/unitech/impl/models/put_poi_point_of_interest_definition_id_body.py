from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutPoiPointOfInterestDefinitionIdBody")


@_attrs_define
class PutPoiPointOfInterestDefinitionIdBody:
    """
    Attributes:
        label (Union[Unset, Any]):  Example: any.
        logo_url (Union[Unset, Any]):  Example: any.
    """

    label: Union[Unset, Any] = UNSET
    logo_url: Union[Unset, Any] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        label = self.label

        logo_url = self.logo_url

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if label is not UNSET:
            field_dict["label"] = label
        if logo_url is not UNSET:
            field_dict["logoUrl"] = logo_url

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        label = d.pop("label", UNSET)

        logo_url = d.pop("logoUrl", UNSET)

        put_poi_point_of_interest_definition_id_body = cls(
            label=label,
            logo_url=logo_url,
        )

        put_poi_point_of_interest_definition_id_body.additional_properties = d
        return put_poi_point_of_interest_definition_id_body

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
