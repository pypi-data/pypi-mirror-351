from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutRealisationRoundProofOfPassageIdPpraBody")


@_attrs_define
class PutRealisationRoundProofOfPassageIdPpraBody:
    """
    Attributes:
        containers (Union[Unset, Any]):  Example: any.
        is_collected (Union[Unset, Any]):  Example: any.
        comment (Union[Unset, Any]):  Example: any.
    """

    containers: Union[Unset, Any] = UNSET
    is_collected: Union[Unset, Any] = UNSET
    comment: Union[Unset, Any] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        containers = self.containers

        is_collected = self.is_collected

        comment = self.comment

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if containers is not UNSET:
            field_dict["containers"] = containers
        if is_collected is not UNSET:
            field_dict["isCollected"] = is_collected
        if comment is not UNSET:
            field_dict["comment"] = comment

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        containers = d.pop("containers", UNSET)

        is_collected = d.pop("isCollected", UNSET)

        comment = d.pop("comment", UNSET)

        put_realisation_round_proof_of_passage_id_ppra_body = cls(
            containers=containers,
            is_collected=is_collected,
            comment=comment,
        )

        put_realisation_round_proof_of_passage_id_ppra_body.additional_properties = d
        return put_realisation_round_proof_of_passage_id_ppra_body

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
