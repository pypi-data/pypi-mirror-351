from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostItineraryNewBody")


@_attrs_define
class PostItineraryNewBody:
    """
    Attributes:
        itinerary_payload (Union[Unset, Any]):  Example: any.
    """

    itinerary_payload: Union[Unset, Any] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        itinerary_payload = self.itinerary_payload

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if itinerary_payload is not UNSET:
            field_dict["itineraryPayload"] = itinerary_payload

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        itinerary_payload = d.pop("itineraryPayload", UNSET)

        post_itinerary_new_body = cls(
            itinerary_payload=itinerary_payload,
        )

        post_itinerary_new_body.additional_properties = d
        return post_itinerary_new_body

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
