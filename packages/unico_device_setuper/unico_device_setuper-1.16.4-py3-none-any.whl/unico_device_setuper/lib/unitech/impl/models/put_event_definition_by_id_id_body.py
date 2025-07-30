from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutEventDefinitionByIdIdBody")


@_attrs_define
class PutEventDefinitionByIdIdBody:
    """
    Attributes:
        label (Union[Unset, Any]):  Example: any.
        type (Union[Unset, Any]):  Example: any.
        logo_url (Union[Unset, Any]):  Example: any.
        is_comment_required (Union[Unset, Any]):  Example: any.
        is_signature_required (Union[Unset, Any]):  Example: any.
        is_picture_required (Union[Unset, Any]):  Example: any.
        id_event_definition_category (Union[Unset, Any]):  Example: any.
        initial_state (Union[Unset, Any]):  Example: any.
        is_visible_on_uniandco (Union[Unset, Any]):  Example: any.
    """

    label: Union[Unset, Any] = UNSET
    type: Union[Unset, Any] = UNSET
    logo_url: Union[Unset, Any] = UNSET
    is_comment_required: Union[Unset, Any] = UNSET
    is_signature_required: Union[Unset, Any] = UNSET
    is_picture_required: Union[Unset, Any] = UNSET
    id_event_definition_category: Union[Unset, Any] = UNSET
    initial_state: Union[Unset, Any] = UNSET
    is_visible_on_uniandco: Union[Unset, Any] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        label = self.label

        type = self.type

        logo_url = self.logo_url

        is_comment_required = self.is_comment_required

        is_signature_required = self.is_signature_required

        is_picture_required = self.is_picture_required

        id_event_definition_category = self.id_event_definition_category

        initial_state = self.initial_state

        is_visible_on_uniandco = self.is_visible_on_uniandco

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if label is not UNSET:
            field_dict["label"] = label
        if type is not UNSET:
            field_dict["type"] = type
        if logo_url is not UNSET:
            field_dict["logoUrl"] = logo_url
        if is_comment_required is not UNSET:
            field_dict["isCommentRequired"] = is_comment_required
        if is_signature_required is not UNSET:
            field_dict["isSignatureRequired"] = is_signature_required
        if is_picture_required is not UNSET:
            field_dict["isPictureRequired"] = is_picture_required
        if id_event_definition_category is not UNSET:
            field_dict["idEventDefinitionCategory"] = id_event_definition_category
        if initial_state is not UNSET:
            field_dict["initialState"] = initial_state
        if is_visible_on_uniandco is not UNSET:
            field_dict["isVisibleOnUniandco"] = is_visible_on_uniandco

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        label = d.pop("label", UNSET)

        type = d.pop("type", UNSET)

        logo_url = d.pop("logoUrl", UNSET)

        is_comment_required = d.pop("isCommentRequired", UNSET)

        is_signature_required = d.pop("isSignatureRequired", UNSET)

        is_picture_required = d.pop("isPictureRequired", UNSET)

        id_event_definition_category = d.pop("idEventDefinitionCategory", UNSET)

        initial_state = d.pop("initialState", UNSET)

        is_visible_on_uniandco = d.pop("isVisibleOnUniandco", UNSET)

        put_event_definition_by_id_id_body = cls(
            label=label,
            type=type,
            logo_url=logo_url,
            is_comment_required=is_comment_required,
            is_signature_required=is_signature_required,
            is_picture_required=is_picture_required,
            id_event_definition_category=id_event_definition_category,
            initial_state=initial_state,
            is_visible_on_uniandco=is_visible_on_uniandco,
        )

        put_event_definition_by_id_id_body.additional_properties = d
        return put_event_definition_by_id_id_body

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
