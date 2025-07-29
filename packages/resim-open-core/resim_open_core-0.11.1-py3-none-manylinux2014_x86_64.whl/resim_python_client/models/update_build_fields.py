from typing import Any, Dict, Type, TypeVar, Tuple, Optional, BinaryIO, TextIO, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import Union
from ..types import UNSET, Unset






T = TypeVar("T", bound="UpdateBuildFields")


@_attrs_define
class UpdateBuildFields:
    """ 
        Attributes:
            branch_id (Union[Unset, str]):
            description (Union[Unset, str]): [DEPRECATED] This field was previously used to set the build's name. If both
                'description' and 'name' are provided, 'name' will take precedence. In a future version, this field will be
                repurposed to store the build's description.
            long_description (Union[Unset, str]): [DEPRECATED] This field is temporarily being used to set the build's
                description. In a future version, the `description` field will be used instead.
            name (Union[Unset, str]): The name of the build. This replaces the previous usage of 'description'.
     """

    branch_id: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    long_description: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        branch_id = self.branch_id

        description = self.description

        long_description = self.long_description

        name = self.name


        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if branch_id is not UNSET:
            field_dict["branchID"] = branch_id
        if description is not UNSET:
            field_dict["description"] = description
        if long_description is not UNSET:
            field_dict["longDescription"] = long_description
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict



    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        branch_id = d.pop("branchID", UNSET)

        description = d.pop("description", UNSET)

        long_description = d.pop("longDescription", UNSET)

        name = d.pop("name", UNSET)

        update_build_fields = cls(
            branch_id=branch_id,
            description=description,
            long_description=long_description,
            name=name,
        )


        update_build_fields.additional_properties = d
        return update_build_fields

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
