from typing import Any, Dict, List, Type, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ItineraryCreationData")


@_attrs_define
class ItineraryCreationData:
    """
    Attributes:
        distance_in_km (float):
        duration_in_ms (float):
        route_parts (List[Any]):
        round_instructions (List[Any]):
    """

    distance_in_km: float
    duration_in_ms: float
    route_parts: List[Any]
    round_instructions: List[Any]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        distance_in_km = self.distance_in_km

        duration_in_ms = self.duration_in_ms

        route_parts = self.route_parts

        round_instructions = self.round_instructions

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "distanceInKm": distance_in_km,
                "durationInMs": duration_in_ms,
                "routeParts": route_parts,
                "roundInstructions": round_instructions,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        distance_in_km = d.pop("distanceInKm")

        duration_in_ms = d.pop("durationInMs")

        route_parts = cast(List[Any], d.pop("routeParts"))

        round_instructions = cast(List[Any], d.pop("roundInstructions"))

        itinerary_creation_data = cls(
            distance_in_km=distance_in_km,
            duration_in_ms=duration_in_ms,
            route_parts=route_parts,
            round_instructions=round_instructions,
        )

        itinerary_creation_data.additional_properties = d
        return itinerary_creation_data

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
