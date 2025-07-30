# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["Identity"]


class Identity(BaseModel):
    id: int

    type: Literal["User"] = FieldInfo(alias="type_")

    username: str

    avatar_url: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    email: Optional[str] = None

    email_verified: Optional[bool] = None

    external: Optional[bool] = None

    external_source: Optional[str] = None

    external_updated_at: Optional[str] = None

    last_login: Optional[str] = None

    updated_at: Optional[str] = None
