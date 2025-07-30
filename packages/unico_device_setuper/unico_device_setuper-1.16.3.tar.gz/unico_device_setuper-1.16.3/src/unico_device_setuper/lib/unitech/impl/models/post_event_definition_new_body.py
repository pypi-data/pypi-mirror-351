from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostEventDefinitionNewBody")


@_attrs_define
class PostEventDefinitionNewBody:
    """
    Attributes:
        label (Union[Unset, Any]):  Example: any.
        logo_url (Union[Unset, Any]):  Example: any.
        id_event_definition_category (Union[Unset, Any]):  Example: any.
        type (Union[Unset, Any]):  Example: any.
        initial_state (Union[Unset, Any]):  Example: any.
        is_visible_on_uniandco (Union[Unset, Any]):  Example: any.
    """

    label: Union[Unset, Any] = UNSET
    logo_url: Union[Unset, Any] = UNSET
    id_event_definition_category: Union[Unset, Any] = UNSET
    type: Union[Unset, Any] = UNSET
    initial_state: Union[Unset, Any] = UNSET
    is_visible_on_uniandco: Union[Unset, Any] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        label = self.label

        logo_url = self.logo_url

        id_event_definition_category = self.id_event_definition_category

        type = self.type

        initial_state = self.initial_state

        is_visible_on_uniandco = self.is_visible_on_uniandco

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if label is not UNSET:
            field_dict["label"] = label
        if logo_url is not UNSET:
            field_dict["logoUrl"] = logo_url
        if id_event_definition_category is not UNSET:
            field_dict["idEventDefinitionCategory"] = id_event_definition_category
        if type is not UNSET:
            field_dict["type"] = type
        if initial_state is not UNSET:
            field_dict["initialState"] = initial_state
        if is_visible_on_uniandco is not UNSET:
            field_dict["isVisibleOnUniandco"] = is_visible_on_uniandco

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        label = d.pop("label", UNSET)

        logo_url = d.pop("logoUrl", UNSET)

        id_event_definition_category = d.pop("idEventDefinitionCategory", UNSET)

        type = d.pop("type", UNSET)

        initial_state = d.pop("initialState", UNSET)

        is_visible_on_uniandco = d.pop("isVisibleOnUniandco", UNSET)

        post_event_definition_new_body = cls(
            label=label,
            logo_url=logo_url,
            id_event_definition_category=id_event_definition_category,
            type=type,
            initial_state=initial_state,
            is_visible_on_uniandco=is_visible_on_uniandco,
        )

        post_event_definition_new_body.additional_properties = d
        return post_event_definition_new_body

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
