# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["DataExplorerDimensionGroup"]


class DataExplorerDimensionGroup(BaseModel):
    field_code: str = FieldInfo(alias="fieldCode")
    """Field code to group by"""

    meter_id: str = FieldInfo(alias="meterId")
    """Meter ID to group by"""

    group_type: Optional[Literal["ACCOUNT", "DIMENSION", "TIME"]] = FieldInfo(alias="groupType", default=None)
