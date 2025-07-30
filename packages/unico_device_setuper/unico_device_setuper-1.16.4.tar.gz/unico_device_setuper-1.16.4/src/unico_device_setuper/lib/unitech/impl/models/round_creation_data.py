from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.round_creation_data_type import RoundCreationDataType
from ..types import UNSET, Unset

T = TypeVar("T", bound="RoundCreationData")


@_attrs_define
class RoundCreationData:
    """
    Attributes:
        label (str):  Example: string.
        stream_labels (List[str]):  Example: ['string'].
        sector_ids (List[str]):  Example: ['id'].
        operator_ids (List[str]):  Example: ['id'].
        type (RoundCreationDataType):
        start_date (str):  Example: date.
        itinerary_planified (Any):
        round_slots (List[Any]):
        id_depot (str):  Example: id.
        id_outlet (str):  Example: id.
        id_driver (Union[Unset, str]):  Example: id.
        id_vehicle (Union[Unset, str]):  Example: id.
    """

    label: str
    stream_labels: List[str]
    sector_ids: List[str]
    operator_ids: List[str]
    type: RoundCreationDataType
    start_date: str
    itinerary_planified: Any
    round_slots: List[Any]
    id_depot: str
    id_outlet: str
    id_driver: Union[Unset, str] = UNSET
    id_vehicle: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        label = self.label

        stream_labels = self.stream_labels

        sector_ids = self.sector_ids

        operator_ids = self.operator_ids

        type = self.type.value

        start_date = self.start_date

        itinerary_planified = self.itinerary_planified

        round_slots = self.round_slots

        id_depot = self.id_depot

        id_outlet = self.id_outlet

        id_driver = self.id_driver

        id_vehicle = self.id_vehicle

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "label": label,
                "streamLabels": stream_labels,
                "sectorIds": sector_ids,
                "operatorIds": operator_ids,
                "type": type,
                "startDate": start_date,
                "itineraryPlanified": itinerary_planified,
                "roundSlots": round_slots,
                "idDepot": id_depot,
                "idOutlet": id_outlet,
            }
        )
        if id_driver is not UNSET:
            field_dict["idDriver"] = id_driver
        if id_vehicle is not UNSET:
            field_dict["idVehicle"] = id_vehicle

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        label = d.pop("label")

        stream_labels = cast(List[str], d.pop("streamLabels"))

        sector_ids = cast(List[str], d.pop("sectorIds"))

        operator_ids = cast(List[str], d.pop("operatorIds"))

        type = RoundCreationDataType(d.pop("type"))

        start_date = d.pop("startDate")

        itinerary_planified = d.pop("itineraryPlanified")

        round_slots = cast(List[Any], d.pop("roundSlots"))

        id_depot = d.pop("idDepot")

        id_outlet = d.pop("idOutlet")

        id_driver = d.pop("idDriver", UNSET)

        id_vehicle = d.pop("idVehicle", UNSET)

        round_creation_data = cls(
            label=label,
            stream_labels=stream_labels,
            sector_ids=sector_ids,
            operator_ids=operator_ids,
            type=type,
            start_date=start_date,
            itinerary_planified=itinerary_planified,
            round_slots=round_slots,
            id_depot=id_depot,
            id_outlet=id_outlet,
            id_driver=id_driver,
            id_vehicle=id_vehicle,
        )

        round_creation_data.additional_properties = d
        return round_creation_data

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
