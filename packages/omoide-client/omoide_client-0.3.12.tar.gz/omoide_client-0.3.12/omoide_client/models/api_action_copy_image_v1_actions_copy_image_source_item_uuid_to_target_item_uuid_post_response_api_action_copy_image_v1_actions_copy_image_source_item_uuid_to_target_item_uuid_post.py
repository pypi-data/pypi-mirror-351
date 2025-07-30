from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar(
    "T",
    bound="ApiActionCopyImageV1ActionsCopyImageSourceItemUuidToTargetItemUuidPostResponseApiActionCopyImageV1ActionsCopyImageSourceItemUuidToTargetItemUuidPost",
)


@_attrs_define
class ApiActionCopyImageV1ActionsCopyImageSourceItemUuidToTargetItemUuidPostResponseApiActionCopyImageV1ActionsCopyImageSourceItemUuidToTargetItemUuidPost:
    """ """

    additional_properties: Dict[str, Union[List[str], str]] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        field_dict: Dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            if isinstance(prop, list):
                field_dict[prop_name] = prop

            else:
                field_dict[prop_name] = prop

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        api_action_copy_image_v1_actions_copy_image_source_item_uuid_to_target_item_uuid_post_response_api_action_copy_image_v1_actions_copy_image_source_item_uuid_to_target_item_uuid_post = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():

            def _parse_additional_property(data: object) -> Union[List[str], str]:
                try:
                    if not isinstance(data, list):
                        raise TypeError()
                    additional_property_type_1 = cast(List[str], data)

                    return additional_property_type_1
                except:  # noqa: E722
                    pass
                return cast(Union[List[str], str], data)

            additional_property = _parse_additional_property(prop_dict)

            additional_properties[prop_name] = additional_property

        api_action_copy_image_v1_actions_copy_image_source_item_uuid_to_target_item_uuid_post_response_api_action_copy_image_v1_actions_copy_image_source_item_uuid_to_target_item_uuid_post.additional_properties = additional_properties
        return api_action_copy_image_v1_actions_copy_image_source_item_uuid_to_target_item_uuid_post_response_api_action_copy_image_v1_actions_copy_image_source_item_uuid_to_target_item_uuid_post

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Union[List[str], str]:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Union[List[str], str]) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
