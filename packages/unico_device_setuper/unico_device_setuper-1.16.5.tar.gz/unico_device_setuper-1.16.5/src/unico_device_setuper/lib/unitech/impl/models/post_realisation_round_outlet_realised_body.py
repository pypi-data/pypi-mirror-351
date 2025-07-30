from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostRealisationRoundOutletRealisedBody")


@_attrs_define
class PostRealisationRoundOutletRealisedBody:
    """
    Attributes:
        round_realisation_id (Union[Unset, Any]):  Example: any.
        id_outlet (Union[Unset, Any]):  Example: any.
    """

    round_realisation_id: Union[Unset, Any] = UNSET
    id_outlet: Union[Unset, Any] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        round_realisation_id = self.round_realisation_id

        id_outlet = self.id_outlet

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if round_realisation_id is not UNSET:
            field_dict["roundRealisationId"] = round_realisation_id
        if id_outlet is not UNSET:
            field_dict["idOutlet"] = id_outlet

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        round_realisation_id = d.pop("roundRealisationId", UNSET)

        id_outlet = d.pop("idOutlet", UNSET)

        post_realisation_round_outlet_realised_body = cls(
            round_realisation_id=round_realisation_id,
            id_outlet=id_outlet,
        )

        post_realisation_round_outlet_realised_body.additional_properties = d
        return post_realisation_round_outlet_realised_body

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
