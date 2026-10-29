"""User schemas for creating and reading user data."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

from app.core.constants import USER_NAME_MAX_LENGTH

# UserName with annotations
UserName = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=USER_NAME_MAX_LENGTH)
]


class UserCreate(BaseModel):
    """Schema for creating a new user."""

    # TRIM: Could add email, password, etc. if needed

    name: UserName


class UserRead(BaseModel):
    """Schema for reading user data."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: UserName  # for consistency with UserCreate, could be 'str


# Unused schema follows... breaks YAGNI, but this is an assignment


class UserUpdate(BaseModel):
    """Schema for updating user data."""

    name: UserName | None = None  # assume extension to partial update


# TRIM: Hard deletion vs soft deletion


class UserDelete(BaseModel):
    """Schema for deleting user data."""

    id: int
