from pydantic import Field, field_validator

from app.settings.schemas import DescriptionArgs
from app import constants


class UpdateUserBody(DescriptionArgs):
    forbid_actions: list[str] | None = Field(
        None,
        description="Actions to forbid user to do",
        examples=[[constants.ALL_PERMISSIONS]],
    )
    forbid_actions_merge: bool = Field(
        False,
        description="Whether to merge or replace user's forbidden actions",
        examples=[True],
    )
    remove_avatar: bool = Field(
        False, description="Whether to remove user's avatar", examples=[True]
    )
    remove_description: bool = Field(
        False,
        description="Whether to remove user's description",
        examples=[True],
    )
    banned: bool | None = Field(
        None, description="Set user 'banned' status", examples=[True]
    )

    @field_validator("forbid_actions")
    def forbid_actions_validator(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return v

        for i in v:
            assert i in constants.ALL_PERMISSIONS, f"Unknown permission: {i}"

        return v
