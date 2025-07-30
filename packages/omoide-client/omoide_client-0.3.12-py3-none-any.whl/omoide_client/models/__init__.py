"""Contains all the data models used in inputs/outputs"""

from .api_action_copy_image_v1_actions_copy_image_source_item_uuid_to_target_item_uuid_post_response_api_action_copy_image_v1_actions_copy_image_source_item_uuid_to_target_item_uuid_post import (
    ApiActionCopyImageV1ActionsCopyImageSourceItemUuidToTargetItemUuidPostResponseApiActionCopyImageV1ActionsCopyImageSourceItemUuidToTargetItemUuidPost,
)
from .api_action_rebuild_computed_tags_v1_actions_rebuild_computed_tags_item_uuid_post_response_api_action_rebuild_computed_tags_v1_actions_rebuild_computed_tags_item_uuid_post import (
    ApiActionRebuildComputedTagsV1ActionsRebuildComputedTagsItemUuidPostResponseApiActionRebuildComputedTagsV1ActionsRebuildComputedTagsItemUuidPost,
)
from .api_action_rebuild_known_tags_for_all_v1_actions_rebuild_known_tags_for_all_post_response_api_action_rebuild_known_tags_for_all_v1_actions_rebuild_known_tags_for_all_post import (
    ApiActionRebuildKnownTagsForAllV1ActionsRebuildKnownTagsForAllPostResponseApiActionRebuildKnownTagsForAllV1ActionsRebuildKnownTagsForAllPost,
)
from .api_action_rebuild_known_tags_for_anon_v1_actions_rebuild_known_tags_for_anon_post_response_api_action_rebuild_known_tags_for_anon_v1_actions_rebuild_known_tags_for_anon_post import (
    ApiActionRebuildKnownTagsForAnonV1ActionsRebuildKnownTagsForAnonPostResponseApiActionRebuildKnownTagsForAnonV1ActionsRebuildKnownTagsForAnonPost,
)
from .api_action_rebuild_known_tags_for_user_v1_actions_rebuild_known_tags_for_user_user_uuid_post_response_api_action_rebuild_known_tags_for_user_v1_actions_rebuild_known_tags_for_user_user_uuid import (
    ApiActionRebuildKnownTagsForUserV1ActionsRebuildKnownTagsForUserUserUuidPostResponseApiActionRebuildKnownTagsForUserV1ActionsRebuildKnownTagsForUserUserUuidPost,
)
from .api_browse_v1_browse_item_uuid_get_order import ApiBrowseV1BrowseItemUuidGetOrder
from .api_change_parent_item_v1_items_item_uuid_parent_new_parent_uuid_put_response_api_change_parent_item_v1_items_item_uuid_parent_new_parent_uuid_put import (
    ApiChangeParentItemV1ItemsItemUuidParentNewParentUuidPutResponseApiChangeParentItemV1ItemsItemUuidParentNewParentUuidPut,
)
from .api_create_exif_v1_exif_item_uuid_post_response_api_create_exif_v1_exif_item_uuid_post import (
    ApiCreateExifV1ExifItemUuidPostResponseApiCreateExifV1ExifItemUuidPost,
)
from .api_delete_exif_v1_exif_item_uuid_delete_response_api_delete_exif_v1_exif_item_uuid_delete import (
    ApiDeleteExifV1ExifItemUuidDeleteResponseApiDeleteExifV1ExifItemUuidDelete,
)
from .api_delete_item_v1_items_item_uuid_delete_desired_switch import ApiDeleteItemV1ItemsItemUuidDeleteDesiredSwitch
from .api_get_anon_tags_v1_users_anon_known_tags_get_response_api_get_anon_tags_v1_users_anon_known_tags_get import (
    ApiGetAnonTagsV1UsersAnonKnownTagsGetResponseApiGetAnonTagsV1UsersAnonKnownTagsGet,
)
from .api_get_recent_updates_v1_search_recent_updates_get_order import ApiGetRecentUpdatesV1SearchRecentUpdatesGetOrder
from .api_get_user_tags_v1_users_user_uuid_known_tags_get_response_api_get_user_tags_v1_users_user_uuid_known_tags_get import (
    ApiGetUserTagsV1UsersUserUuidKnownTagsGetResponseApiGetUserTagsV1UsersUserUuidKnownTagsGet,
)
from .api_home_v1_home_get_order import ApiHomeV1HomeGetOrder
from .api_item_update_permissions_v1_items_item_uuid_permissions_put_response_api_item_update_permissions_v1_items_item_uuid_permissions_put import (
    ApiItemUpdatePermissionsV1ItemsItemUuidPermissionsPutResponseApiItemUpdatePermissionsV1ItemsItemUuidPermissionsPut,
)
from .api_rename_item_v1_items_item_uuid_name_put_response_api_rename_item_v1_items_item_uuid_name_put import (
    ApiRenameItemV1ItemsItemUuidNamePutResponseApiRenameItemV1ItemsItemUuidNamePut,
)
from .api_search_v1_search_get_order import ApiSearchV1SearchGetOrder
from .api_update_exif_v1_exif_item_uuid_put_response_api_update_exif_v1_exif_item_uuid_put import (
    ApiUpdateExifV1ExifItemUuidPutResponseApiUpdateExifV1ExifItemUuidPut,
)
from .api_update_item_tags_v1_items_item_uuid_tags_put_response_api_update_item_tags_v1_items_item_uuid_tags_put import (
    ApiUpdateItemTagsV1ItemsItemUuidTagsPutResponseApiUpdateItemTagsV1ItemsItemUuidTagsPut,
)
from .api_update_item_v1_items_item_uuid_patch_response_api_update_item_v1_items_item_uuid_patch import (
    ApiUpdateItemV1ItemsItemUuidPatchResponseApiUpdateItemV1ItemsItemUuidPatch,
)
from .api_update_metainfo_v1_metainfo_item_uuid_put_response_api_update_metainfo_v1_metainfo_item_uuid_put import (
    ApiUpdateMetainfoV1MetainfoItemUuidPutResponseApiUpdateMetainfoV1MetainfoItemUuidPut,
)
from .api_upload_item_v1_items_item_uuid_upload_put_response_api_upload_item_v1_items_item_uuid_upload_put import (
    ApiUploadItemV1ItemsItemUuidUploadPutResponseApiUploadItemV1ItemsItemUuidUploadPut,
)
from .apply_as import ApplyAs
from .autocomplete_output import AutocompleteOutput
from .body_api_upload_item_v1_items_item_uuid_upload_put import BodyApiUploadItemV1ItemsItemUuidUploadPut
from .exif_model import EXIFModel
from .exif_model_exif import EXIFModelExif
from .http_validation_error import HTTPValidationError
from .item_delete_output import ItemDeleteOutput
from .item_input import ItemInput
from .item_output import ItemOutput
from .item_output_extras import ItemOutputExtras
from .item_rename_input import ItemRenameInput
from .item_update_input import ItemUpdateInput
from .item_update_tags_input import ItemUpdateTagsInput
from .many_items_output import ManyItemsOutput
from .metainfo_input import MetainfoInput
from .metainfo_input_extras import MetainfoInputExtras
from .metainfo_output import MetainfoOutput
from .one_item_output import OneItemOutput
from .permission import Permission
from .permissions_input import PermissionsInput
from .recent_updates_output import RecentUpdatesOutput
from .search_total_output import SearchTotalOutput
from .user_collection_output import UserCollectionOutput
from .user_input import UserInput
from .user_output import UserOutput
from .user_output_extras import UserOutputExtras
from .user_resource_usage_output import UserResourceUsageOutput
from .user_value_input import UserValueInput
from .validation_error import ValidationError
from .version_output import VersionOutput
from .who_am_i_output import WhoAmIOutput

__all__ = (
    "ApiActionCopyImageV1ActionsCopyImageSourceItemUuidToTargetItemUuidPostResponseApiActionCopyImageV1ActionsCopyImageSourceItemUuidToTargetItemUuidPost",
    "ApiActionRebuildComputedTagsV1ActionsRebuildComputedTagsItemUuidPostResponseApiActionRebuildComputedTagsV1ActionsRebuildComputedTagsItemUuidPost",
    "ApiActionRebuildKnownTagsForAllV1ActionsRebuildKnownTagsForAllPostResponseApiActionRebuildKnownTagsForAllV1ActionsRebuildKnownTagsForAllPost",
    "ApiActionRebuildKnownTagsForAnonV1ActionsRebuildKnownTagsForAnonPostResponseApiActionRebuildKnownTagsForAnonV1ActionsRebuildKnownTagsForAnonPost",
    "ApiActionRebuildKnownTagsForUserV1ActionsRebuildKnownTagsForUserUserUuidPostResponseApiActionRebuildKnownTagsForUserV1ActionsRebuildKnownTagsForUserUserUuidPost",
    "ApiBrowseV1BrowseItemUuidGetOrder",
    "ApiChangeParentItemV1ItemsItemUuidParentNewParentUuidPutResponseApiChangeParentItemV1ItemsItemUuidParentNewParentUuidPut",
    "ApiCreateExifV1ExifItemUuidPostResponseApiCreateExifV1ExifItemUuidPost",
    "ApiDeleteExifV1ExifItemUuidDeleteResponseApiDeleteExifV1ExifItemUuidDelete",
    "ApiDeleteItemV1ItemsItemUuidDeleteDesiredSwitch",
    "ApiGetAnonTagsV1UsersAnonKnownTagsGetResponseApiGetAnonTagsV1UsersAnonKnownTagsGet",
    "ApiGetRecentUpdatesV1SearchRecentUpdatesGetOrder",
    "ApiGetUserTagsV1UsersUserUuidKnownTagsGetResponseApiGetUserTagsV1UsersUserUuidKnownTagsGet",
    "ApiHomeV1HomeGetOrder",
    "ApiItemUpdatePermissionsV1ItemsItemUuidPermissionsPutResponseApiItemUpdatePermissionsV1ItemsItemUuidPermissionsPut",
    "ApiRenameItemV1ItemsItemUuidNamePutResponseApiRenameItemV1ItemsItemUuidNamePut",
    "ApiSearchV1SearchGetOrder",
    "ApiUpdateExifV1ExifItemUuidPutResponseApiUpdateExifV1ExifItemUuidPut",
    "ApiUpdateItemTagsV1ItemsItemUuidTagsPutResponseApiUpdateItemTagsV1ItemsItemUuidTagsPut",
    "ApiUpdateItemV1ItemsItemUuidPatchResponseApiUpdateItemV1ItemsItemUuidPatch",
    "ApiUpdateMetainfoV1MetainfoItemUuidPutResponseApiUpdateMetainfoV1MetainfoItemUuidPut",
    "ApiUploadItemV1ItemsItemUuidUploadPutResponseApiUploadItemV1ItemsItemUuidUploadPut",
    "ApplyAs",
    "AutocompleteOutput",
    "BodyApiUploadItemV1ItemsItemUuidUploadPut",
    "EXIFModel",
    "EXIFModelExif",
    "HTTPValidationError",
    "ItemDeleteOutput",
    "ItemInput",
    "ItemOutput",
    "ItemOutputExtras",
    "ItemRenameInput",
    "ItemUpdateInput",
    "ItemUpdateTagsInput",
    "ManyItemsOutput",
    "MetainfoInput",
    "MetainfoInputExtras",
    "MetainfoOutput",
    "OneItemOutput",
    "Permission",
    "PermissionsInput",
    "RecentUpdatesOutput",
    "SearchTotalOutput",
    "UserCollectionOutput",
    "UserInput",
    "UserOutput",
    "UserOutputExtras",
    "UserResourceUsageOutput",
    "UserValueInput",
    "ValidationError",
    "VersionOutput",
    "WhoAmIOutput",
)
